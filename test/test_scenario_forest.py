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
    forest = mw.ScenarioForest.from_file('test/fixtures/in/scenario_forest.feature')
    assert len(forest.root_scenarios()) == 1

    root_scenario = forest.find('View users')
    assert root_scenario.__repr__() \
        == '<Scenario: View users '\
           '(1 prerequisites, 1 actions, 1 assertions)>'
    assert root_scenario.name == 'View users'
    assert root_scenario.level() == 1
    assert len(root_scenario.ancestors()) == 0
    assert len(root_scenario.prerequisites()) == 1
    assert len(root_scenario.actions()) == 1
    assert len(root_scenario.assertions()) == 1
    data = root_scenario.prerequisites()[0].data.to_list_of_dict()
    assert len(data) == 4
    assert data[2]['Name'] == 'Connie'
    assert data[2]['Status'] == 'Active'
    action = root_scenario.actions()[0]
    assert action.__repr__() == '<Action: I go to "Users">'

    leaf_scenario = forest.find(
        'View users',
        'Bulk operations',
        'Select user',
        'Select multiple users',
        'Bulk deactivate users',
        'Confirm bulk deactivation of users'
    )
    assert leaf_scenario.__repr__() \
        == '<Scenario: Confirm bulk deactivation of users '\
           '(0 prerequisites, 1 actions, 2 assertions)>'
    assert leaf_scenario.name == 'Confirm bulk deactivation of users'
    assert leaf_scenario.level() == 6
    assert len(leaf_scenario.ancestors()) == 5
    assert len(leaf_scenario.prerequisites()) == 0
    assert len(leaf_scenario.actions()) == 1
    assert len(leaf_scenario.assertions()) == 2
    assertion = leaf_scenario.assertions()[0]
    assert assertion.__repr__() == '<Assertion: I see "0 users selected">'

def test_flatten_strict():
    """Test the 'flatten' method in 'strict' mode"""
    forest = mw.ScenarioForest.from_file('test/fixtures/in/scenario_forest.feature')
    forest.flatten('test/out/scenarios_flat_strict.feature')
    assert filecmp.cmp('test/out/scenarios_flat_strict.feature',
                       'test/fixtures/out/scenarios_flat_strict.feature')

def test_flatten_strict_with_comments():
    """Test the 'flatten' method in 'strict' mode with comments turned on"""
    forest = mw.ScenarioForest.from_file('test/fixtures/in/scenario_forest.feature')
    forest.flatten(
        'test/out/scenarios_flat_strict_with_comments.feature',
        comments=True
    )
    assert filecmp.cmp('test/out/scenarios_flat_strict_with_comments.feature',
                       'test/fixtures/out/scenarios_flat_strict_with_comments.feature')
def test_flatten_relaxed():
    """Test the 'flatten' method in 'relaxed' mode"""
    forest = mw.ScenarioForest.from_file('test/fixtures/in/scenario_forest.feature')
    forest.flatten('test/out/scenarios_flat_relaxed.feature', mode='relaxed')
    assert filecmp.cmp('test/out/scenarios_flat_relaxed.feature',
                       'test/fixtures/out/scenarios_flat_relaxed.feature')

def test_flatten_relaxed_with_comments():
    """Test the 'flatten' method in 'relaxed' mode with comments turned on"""
    forest = mw.ScenarioForest.from_file('test/fixtures/in/scenario_forest.feature')
    forest.flatten(
        'test/out/scenarios_flat_relaxed_with_comments.feature',
        mode='relaxed',
        comments=True
    )
    assert filecmp.cmp('test/out/scenarios_flat_relaxed_with_comments.feature',
                       'test/fixtures/out/scenarios_flat_relaxed_with_comments.feature')

def test_invalid_file_mis_spelled_conjunction():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            'test/fixtures/in/invalid/mis-spelled_conjunction.feature'
        )
    assert str(error_info.value) \
        == 'Unable to parse line 2: Whenx I go to "Users" # mis-spelled conjunction'

def test_invalid_file_invalid_indentation():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            'test/fixtures/in/invalid/invalid_indentation.feature'
        )
    assert str(error_info.value) \
        == 'Invalid indentation at line 5: Scenario: '\
           'Indented using 3 spaces instead of 4'

def test_invalid_file_excessive_indentation():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            'test/fixtures/in/invalid/excessive_indentation.feature'
        )
    assert str(error_info.value) \
        == 'Excessive indentation at line: Scenario: '\
           'Indented 2 instead of 1 levels'

def test_invalid_file_excessive_step_indentation():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            'test/fixtures/in/invalid/excessive_step_indentation.feature'
        )
    assert str(error_info.value) \
        == 'Invalid indentation at line: '\
           'I see users'

def test_organizational_scenarios():
    """Test the correct output of organizational scenarios"""
    forest = mw.ScenarioForest.from_file(
        'test/fixtures/in/scenario_forest_with_organizational_scenarios.feature'
    )
    forest.flatten(
        'test/out/scenarios_flat_strict_with_organizational_scenarios.feature',
        mode='strict'
    )
    assert filecmp.cmp(
        'test/out/scenarios_flat_strict_with_organizational_scenarios.feature',
        'test/fixtures/out/scenarios_flat_strict_with_organizational_scenarios.feature'
    )
