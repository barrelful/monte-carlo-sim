import pandas as pd

from src.simulation import build_graph
from src.simulation import parse_dependencies
from src.simulation import sample_pert


def test_sample_pert_range() -> None:
    for _ in range(50):
        val = sample_pert(2, 4, 7)
        assert 2 <= val <= 7


def test_parse_dependencies() -> None:
    assert parse_dependencies("2FS;3SS") == [("2", "FS"), ("3", "SS")]
    assert parse_dependencies("4FF-5SF") == [("4", "FF"), ("5", "SF")]
    assert parse_dependencies("") == []


def test_graph_building() -> None:
    data = {
        "ID": [1, 2],
        "Min": [1, 2],
        "Most Likely": [2, 3],
        "Max": [3, 4],
        "Dependency": ["", "1FS"],
    }
    df = pd.DataFrame(data)
    G = build_graph(df)
    assert set(G.nodes) == {"1", "2"}
    assert G.has_edge("1", "2")
