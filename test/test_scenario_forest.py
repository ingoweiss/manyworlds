"""Test the ScenarioForest class"""

import os
import filecmp
import pdb

import pytest

from src.manyworlds.scenario_forest import ScenarioForest

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
    forest = ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    assert len(forest.root_scenarios()) == 1

    root_scenario = forest.find('Users')
    assert root_scenario.name == 'Users'
    assert len(root_scenario.prerequisites()) == 1
    assert len(root_scenario.actions()) == 1
    assert len(root_scenario.assertions()) == 1
    data = root_scenario.prerequisites()[0].data
    assert len(data) == 4
    assert data[2]['Name'] == 'Connie'
    assert data[2]['Status'] == 'Active'

    leaf_scenario = forest.find('Users', 'Select user', 'Select another user', 'Bulk change permissions')
    # pdb.set_trace()
    assert leaf_scenario.name == 'Bulk change permissions'
    assert len(leaf_scenario.prerequisites()) == 0
    assert len(leaf_scenario.actions()) == 2
    assert len(leaf_scenario.assertions()) == 2

def test_flatten_strict():
    """Test the 'flatten' method in 'strict' mode"""
    forest = ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.flatten('test/out/scenarios_flat_strict.feature')
    assert filecmp.cmp('test/out/scenarios_flat_strict.feature',
                       'test/fixtures/scenarios_flat_strict.feature')

def test_flatten_relaxed():
    """Test the 'flatten' method in 'relaxed' mode"""
    forest = ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.flatten('test/out/scenarios_flat_relaxed.feature', mode='relaxed')
    assert filecmp.cmp('test/out/scenarios_flat_relaxed.feature',
                       'test/fixtures/scenarios_flat_relaxed.feature')

def test_graph_mermaid():
    """Test the 'graph_mermaid' method"""
    forest = ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.graph_mermaid('test/out/scenarios_graph.mermaid.txt')
    assert filecmp.cmp('test/out/scenarios_graph.mermaid.txt',
                       'test/fixtures/scenarios_graph.mermaid.txt')
