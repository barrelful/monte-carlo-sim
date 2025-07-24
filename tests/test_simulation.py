import pytest
from src.simulation import sample_pert, parse_dependencies, build_graph
import pandas as pd

def test_sample_pert_range():
    for _ in range(50):
        val = sample_pert(2, 4, 7)
        assert 2 <= val <= 7

def test_parse_dependencies():
    assert parse_dependencies("2FS;3SS") == [('2', 'FS'), ('3', 'SS')]
    assert parse_dependencies("4FF-5SF") == [('4', 'FF'), ('5', 'SF')]
    assert parse_dependencies("") == []

def test_graph_building():
    data = {
        "ID": [1, 2],
        "Min": [1, 2],
        "Most Likely": [2, 3],
        "Max": [3, 4],
        "Dependency": ["", "1FS"]
    }
    df = pd.DataFrame(data)
    G = build_graph(df)
    assert set(G.nodes) == {'1', '2'}
    assert G.has_edge('1', '2')
