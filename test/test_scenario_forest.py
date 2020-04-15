"""Test the ScenarioForest class"""

import os
import filecmp

import pytest

import manyworlds as mw

@pytest.fixture(scope='session', autouse=True)
def clear_out_directory():
    """Delete all files in test/out"""
    folder = os.path.dirname(os.path.realpath(__file__)) + '/out'
    for filename in os.listdir(folder):
        if not filename == '.gitignore':
            file_path = os.path.join(folder, filename)
            os.unlink(file_path)
    yield

def test_parse():
    """Test the structure of the forest graph after using the 'from_file' method"""
    forest = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    assert len(forest.root_scenarios()) == 1
    scenario = forest.root_scenarios()[0].successors()[0].successors()[1].successors()[1]
    assert scenario['name'] == 'Bulk change permissions'
    assert len(scenario['actions']) == 2
    assert len(scenario['assertions']) == 2

def test_flatten_strict():
    """Test the 'flatten' method in 'strict' mode"""
    forest = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.flatten('test/out/scenarios_flat_strict.feature')
    assert filecmp.cmp('test/out/scenarios_flat_strict.feature',
                       'test/fixtures/scenarios_flat_strict.feature')

def test_flatten_relaxed():
    """Test the 'flatten' method in 'relaxed' mode"""
    forest = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.flatten('test/out/scenarios_flat_relaxed.feature', mode='relaxed')
    assert filecmp.cmp('test/out/scenarios_flat_relaxed.feature',
                       'test/fixtures/scenarios_flat_relaxed.feature')

def test_graph_mermaid():
    """Test the 'graph_mermaid' method"""
    forest = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.graph_mermaid('test/out/scenarios_graph.mermaid.txt')
    assert filecmp.cmp('test/out/scenarios_graph.mermaid.txt',
                       'test/fixtures/scenarios_graph.mermaid.txt')
