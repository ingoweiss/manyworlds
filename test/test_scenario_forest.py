"""Test the ScenarioForest class"""

import os
import filecmp
import pdb

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

    root_scenario = forest.find('View users')
    assert root_scenario.name == 'View users'
    assert root_scenario.level() == 1
    assert len(root_scenario.ancestors()) == 0
    assert len(root_scenario.prerequisites()) == 1
    assert len(root_scenario.actions()) == 1
    assert len(root_scenario.assertions()) == 1
    data = root_scenario.prerequisites()[0].data
    assert len(data) == 4
    assert data[2]['Name'] == 'Connie'
    assert data[2]['Status'] == 'Active'

    leaf_scenario = forest.find('View users', 'Bulk operations', 'Select user', 'Select multiple users', 'Bulk deactivate users', 'Confirm bulk deactivation of users')
    assert leaf_scenario.name == 'Confirm bulk deactivation of users'
    assert leaf_scenario.level() == 6
    assert len(leaf_scenario.ancestors()) == 5
    assert len(leaf_scenario.prerequisites()) == 0
    assert len(leaf_scenario.actions()) == 1
    assert len(leaf_scenario.assertions()) == 2

def test_flatten_strict():
    """Test the 'flatten' method in 'strict' mode"""
    forest = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.flatten('test/out/scenarios_flat_strict.feature')
    assert filecmp.cmp('test/out/scenarios_flat_strict.feature',
                       'test/fixtures/scenarios_flat_strict.feature')

def test_flatten_strict_with_comments():
    """Test the 'flatten' method in 'strict' mode with comments turned on"""
    forest = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.flatten('test/out/scenarios_flat_strict_with_comments.feature', comments=True)
    assert filecmp.cmp('test/out/scenarios_flat_strict_with_comments.feature',
                       'test/fixtures/scenarios_flat_strict_with_comments.feature')
def test_flatten_relaxed():
    """Test the 'flatten' method in 'relaxed' mode"""
    forest = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.flatten('test/out/scenarios_flat_relaxed.feature', mode='relaxed')
    assert filecmp.cmp('test/out/scenarios_flat_relaxed.feature',
                       'test/fixtures/scenarios_flat_relaxed.feature')

def test_flatten_relaxed_with_comments():
    """Test the 'flatten' method in 'relaxed' mode with comments turned on"""
    forest = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    forest.flatten('test/out/scenarios_flat_relaxed_with_comments.feature', comments=True)
    assert filecmp.cmp('test/out/scenarios_flat_relaxed_with_comments.feature',
                       'test/fixtures/scenarios_flat_relaxed_with_comments.feature')
