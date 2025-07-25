import random
from typing import Dict
from typing import List
from typing import Tuple

import networkx as nx
import pandas as pd


def sample_pert(minimum: float, mode: float, maximum: float) -> float:
    """Samples a value from a PERT distribution given min, mode, max."""
    if minimum == maximum:
        return minimum
    mean = (minimum + 4 * mode + maximum) / 6
    variance = ((maximum - minimum) / 6) ** 2
    alpha = ((mean - minimum) * (2 * mean - minimum - maximum)) / variance
    beta = alpha * (maximum - mean) / (mean - minimum)
    return random.betavariate(alpha, beta) * (maximum - minimum) + minimum


def parse_dependencies(dep_str: str) -> List[Tuple[str, str]]:
    """
    Parses a dependency string like "2FS;3SS" into a list of (task_id, type) tuples.
    Supports FS, SS, FF, SF formats.
    """
    if not dep_str:
        return []
    deps = dep_str.split(";")
    result = []
    for dep in deps:
        if len(dep) < 3:
            continue
        task_id = dep[:-2]
        dep_type = dep[-2:]
        result.append((task_id, dep_type))
    return result


def build_graph(df: pd.DataFrame) -> nx.DiGraph:
    """
    Builds a directed graph from a DataFrame with columns:
    ID, Min, Most Likely, Max, Dependency
    """
    G = nx.DiGraph()
    for _, row in df.iterrows():
        node_id = str(row["ID"])
        G.add_node(
            node_id,
            min=float(row["Min"]),
            mode=float(row["Most Likely"]),
            max=float(row["Max"]),
        )
    for _, row in df.iterrows():
        target = str(row["ID"])
        dependencies = parse_dependencies(str(row.get("Dependency", "")))
        for source, dep_type in dependencies:
            G.add_edge(source, target, type=dep_type)
    return G


def compute_schedule(G: nx.DiGraph, sampled_durations: Dict[str, float]) -> Dict[str, float]:
    start_times: Dict[str, float] = {}
    finish_times: Dict[str, float] = {}
    for node in nx.topological_sort(G):
        preds = list(G.predecessors(node))
        if not preds:
            start_times[node] = 0.0
        else:
            starts: List[float] = []
            for pred in preds:
                pred_start = start_times.get(pred, 0.0)
                pred_finish = finish_times.get(pred, 0.0)
                link_type = G.edges[pred, node]["type"]
                if link_type == "FS":
                    starts.append(pred_finish)
                elif link_type == "SS":
                    starts.append(pred_start)
                elif link_type == "FF":
                    starts.append(pred_finish - sampled_durations[node])
                elif link_type == "SF":
                    starts.append(pred_start - sampled_durations[node])
            start_times[node] = max(starts)
        finish_times[node] = start_times[node] + sampled_durations[node]
    return finish_times


def estimate_critical_path(G: nx.DiGraph, iterations: int) -> Tuple[Tuple[str, ...], float]:
    path_counts: Dict[Tuple[str, ...], int] = {}
    for _ in range(iterations):
        sampled: Dict[str, float] = {
            node: sample_pert(data["min"], data["mode"], data["max"])
            for node, data in G.nodes(data=True)
        }
        finish_times = compute_schedule(G, sampled)
        latest_node = max(finish_times, key=lambda x: finish_times[x])
        source_nodes = [n for n in G.nodes if G.in_degree(n) == 0]

        longest_path: Tuple[str, ...] = ()
        longest_duration: float = 0.0
        for source in source_nodes:
            try:
                for path in nx.all_simple_paths(G, source=source, target=latest_node):
                    duration = sum(sampled[n] for n in path)
                    if duration > longest_duration:
                        longest_duration = duration
                        longest_path = tuple(path)
            except nx.NetworkXNoPath:
                continue

        path_counts[longest_path] = path_counts.get(longest_path, 0) + 1

    most_common = max(path_counts, key=lambda k: path_counts[k])
    confidence = path_counts[most_common] / iterations
    return most_common, confidence
