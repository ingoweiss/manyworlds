"""Test handling of invalid input files"""

import pytest

import manyworlds as mw


def test_invalid_file_mis_spelled_conjunction():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            "test/fixtures/in/invalid/invalid_conjunction.feature"
        )
    assert (
        str(error_info.value)
        == 'Unable to parse line 2: Whenx I go to "Users" # mis-spelled conjunction'
    )


def test_invalid_file_invalid_indentation():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            "test/fixtures/in/invalid/invalid_indentation.feature"
        )
    assert (
        str(error_info.value) == "Invalid indentation at line 5: Scenario: "
        "Indented using 3 spaces instead of 4"
    )


def test_invalid_file_excessive_indentation():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            "test/fixtures/in/invalid/excessive_indentation.feature"
        )
    assert (
        str(error_info.value) == "Excessive indentation at line: Scenario: "
        "Indented 2 instead of 1 levels"
    )


def test_invalid_file_excessive_step_indentation():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            "test/fixtures/in/invalid/excessive_step_indentation.feature"
        )
    assert str(error_info.value) == "Invalid indentation at line: " "I see users"

def test_invalid_file_feature_after_scenario():
    """Test that the correct error is raised when attempting to parse invalid files"""
    with pytest.raises(mw.exceptions.InvalidFeatureFileError) as error_info:
        mw.ScenarioForest.from_file(
            "test/fixtures/in/invalid/feature_after_scenario.feature"
        )
    assert str(error_info.value) == "Feature line is allowed only at beginning of file but was encountered at line 5: Feature: User Deactivation"
