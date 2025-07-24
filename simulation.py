import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend to avoid display issues
import matplotlib.pyplot as plt
import networkx as nx
import re

# Sample from a PERT distribution using beta approximation
def sample_pert(minimum, mode, maximum, lamb=4.0):
    alpha = 1 + lamb * (mode - minimum) / (maximum - minimum)
    beta = 1 + lamb * (maximum - mode) / (maximum - minimum)
    return np.random.beta(alpha, beta) * (maximum - minimum) + minimum

# Parse dependencies like "2FS;3SS"
def parse_dependencies(dep_str):
    if not dep_str or pd.isna(dep_str):
        return []
    dep_list = re.split(r"[;,-]", dep_str)
    parsed = []
    for dep in dep_list:
        match = re.match(r"(\d+)\s*(FS|SS|FF|SF)?", dep.strip(), re.IGNORECASE)
        if match:
            pred, dep_type = match.group(1), match.group(2) or "FS"
            parsed.append((pred.strip(), dep_type.upper()))
    return parsed

# Build graph and annotate edge constraints
def build_graph(df):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        task_id = str(row["ID"]).strip()
        G.add_node(task_id,
                   min=float(row["Min"]),
                   mode=float(row["Most Likely"]),
                   max=float(row["Max"]))
        for pred_id, dep_type in parse_dependencies(row.get("Dependency", "")):
            G.add_edge(pred_id, task_id, type=dep_type)
    return G

# Compute schedule based on sampled durations and dependencies
def compute_schedule(G, sampled_durations):
    start_times = {}
    finish_times = {}
    for node in nx.topological_sort(G):
        preds = list(G.predecessors(node))
        if not preds:
            start_times[node] = 0
        else:
            starts = []
            for pred in preds:
                pred_start = start_times.get(pred, 0)
                pred_finish = finish_times.get(pred, 0)
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

# Run Monte Carlo simulation
def simulate_project_duration(G, iterations):
    durations = []
    for _ in range(iterations):
        sampled = {
            node: sample_pert(data["min"], data["mode"], data["max"])
            for node, data in G.nodes(data=True)
        }
        finish_times = compute_schedule(G, sampled)
        durations.append(max(finish_times.values()))
    return durations

# Estimate critical path via frequency
def estimate_critical_path(G, iterations):
    path_counts = {}
    for _ in range(iterations):
        sampled = {
            node: sample_pert(data["min"], data["mode"], data["max"])
            for node, data in G.nodes(data=True)
        }
        finish_times = compute_schedule(G, sampled)
        latest_node = max(finish_times, key=lambda x: finish_times[x])
        source_nodes = [n for n in G.nodes if G.in_degree(n) == 0]

        longest_path = []
        longest_duration = 0
        for source in source_nodes:
            try:
                for path in nx.all_simple_paths(G, source=source, target=latest_node):
                    duration = sum(sampled[n] for n in path)
                    if duration > longest_duration:
                        longest_duration = duration
                        longest_path = path
            except nx.NetworkXNoPath:
                continue

        key = tuple(longest_path)
        path_counts[key] = path_counts.get(key, 0) + 1

    most_common = max(path_counts, key=path_counts.get)
    confidence = path_counts[most_common] / iterations
    return most_common, confidence


# Plot results to file
def plot_results(durations):
    plt.figure(figsize=(10, 6))
    plt.hist(durations, bins=50, alpha=0.7, label="Histogram")
    plt.axvline(np.mean(durations), color="r", linestyle="--", label=f"Mean: {np.mean(durations):.2f}")
    plt.axvline(np.percentile(durations, 90), color="g", linestyle="--", label=f"90th %ile: {np.percentile(durations, 90):.2f}")
    plt.title("Project Duration Distribution")
    plt.xlabel("Duration")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("duration_histogram.png")
    plt.close()

    sorted_durations = np.sort(durations)
    cdf = np.arange(len(sorted_durations)) / len(sorted_durations)
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_durations, cdf, label="CDF")
    plt.title("Cumulative Distribution Function")
    plt.xlabel("Duration")
    plt.ylabel("Probability")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("duration_cdf.png")
    plt.close()

# Run full pipeline
def run_simulation(input_file, iterations):
    df = pd.read_csv(input_file)

    df = df.rename(columns={
        "Activity Id": "ID",
        "Optimistic Estimate": "Min",
        "Most Likely Estimate": "Most Likely",
        "Pessimistic Estimate": "Max",
        "Dependency": "Dependency"
    })

    for col in ["Min", "Most Likely", "Max"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["ID", "Min", "Most Likely", "Max"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    G = build_graph(df)
    durations = simulate_project_duration(G, iterations)
    critical_path, confidence = estimate_critical_path(G, 1000)

    print("--- Simulation Results ---")
    print(f"Mean Duration: {np.mean(durations):.2f}")
    print(f"Median Duration: {np.median(durations):.2f}")
    print(f"90th Percentile Duration: {np.percentile(durations, 90):.2f}")
    print(f"Most Likely Critical Path: {' -> '.join(critical_path)}")
    print(f"Confidence in Critical Path: {confidence*100:.1f}%")

    pd.DataFrame({"Simulated Duration": durations}).to_csv("monte_carlo_results.csv", index=False)
    plot_results(durations)
