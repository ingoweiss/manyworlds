"""Test the Feature class"""

import os
import filecmp

import pytest

import manyworlds as mw


@pytest.fixture(scope="session", autouse=True)
def clear_out_directory():
    """Delete all files in test/out"""
    folder = os.path.dirname(os.path.realpath(__file__)) + "/out"
    for filename in os.listdir(folder):
        if not filename == ".gitignore":
            file_path = os.path.join(folder, filename)
            os.unlink(file_path)
    yield


def test_find():
    feature = mw.Feature.from_file("test/fixtures/in/feature.feature")

    # Finds existing root scenario:
    root_scenario = feature.find("View users")
    assert type(root_scenario) == mw.scenario.Scenario

    # Does not find anything if first name provided is not a root scenario:
    root_scenario = feature.find("Select user")
    assert root_scenario is None

    # Finds existing non-root scenario
    non_root_scenario = feature.find("View users", "Bulk operations", "Select user")
    assert non_root_scenario is not None

    # Does not find non-existing non-root scenario (path scenario missing)
    non_root_scenario = feature.find("View users", "Select user")
    assert non_root_scenario is None


def test_from_file():
    """Test the structure of the feature graph after using the 'from_file' method"""
    feature = mw.Feature.from_file("test/fixtures/in/feature.feature")

    assert feature.name == "User Deactivation"
    assert len(feature.description) == 3

    assert len(feature.root_scenarios()) == 1

    # root scenario:
    root_scenario = feature.find("View users")
    assert root_scenario.name == "View users"
    assert len(root_scenario.prerequisites()) == 1
    assert len(root_scenario.actions()) == 1
    assert len(root_scenario.assertions()) == 1
    data = root_scenario.prerequisites()[0].data.to_list_of_dict()
    assert len(data) == 4
    assert data[2]["Name"] == "Connie"
    assert data[2]["Status"] == "Active"

    # leaf scenario:
    leaf_scenario = feature.find(
        "View users",
        "Bulk operations",
        "Select user",
        "Select multiple users",
        "Bulk deactivate users",
        "Confirm bulk deactivation of users",
    )
    assert leaf_scenario.name == "Confirm bulk deactivation of users"
    assert len(leaf_scenario.prerequisites()) == 0
    assert len(leaf_scenario.actions()) == 1
    assert len(leaf_scenario.assertions()) == 2
    assert leaf_scenario.comment == 'by clicking "OK"'


def test_flatten_strict():
    """Test the 'flatten' method in 'strict' mode"""
    feature = mw.Feature.from_file("test/fixtures/in/feature.feature")
    feature.flatten("test/out/scenarios_flat_strict.feature")
    assert filecmp.cmp(
        "test/out/scenarios_flat_strict.feature",
        "test/fixtures/out/scenarios_flat_strict.feature",
    )


def test_flatten_strict_with_comments():
    """Test the 'flatten' method in 'strict' mode with comments turned on"""
    feature = mw.Feature.from_file("test/fixtures/in/feature.feature")
    feature.flatten(
        "test/out/scenarios_flat_strict_with_comments.feature", comments=True
    )
    assert filecmp.cmp(
        "test/out/scenarios_flat_strict_with_comments.feature",
        "test/fixtures/out/scenarios_flat_strict_with_comments.feature",
    )


def test_flatten_relaxed():
    """Test the 'flatten' method in 'relaxed' mode"""
    feature = mw.Feature.from_file("test/fixtures/in/feature.feature")
    feature.flatten("test/out/scenarios_flat_relaxed.feature", mode="relaxed")
    assert filecmp.cmp(
        "test/out/scenarios_flat_relaxed.feature",
        "test/fixtures/out/scenarios_flat_relaxed.feature",
    )


def test_flatten_relaxed_with_comments():
    """Test the 'flatten' method in 'relaxed' mode with comments turned on"""
    feature = mw.Feature.from_file("test/fixtures/in/feature.feature")
    feature.flatten("test/out/scenarios_flat_relaxed_with_comments.feature", mode="relaxed", comments=True)
    assert filecmp.cmp(
        "test/out/scenarios_flat_relaxed_with_comments.feature",
        "test/fixtures/out/scenarios_flat_relaxed_with_comments.feature",
    )


def test_organizational_scenarios():
    """Test the correct output of organizational scenarios"""
    feature = mw.Feature.from_file(
        "test/fixtures/in/feature_with_organizational_scenarios.feature"
    )
    feature.flatten(
        "test/out/scenarios_flat_strict_with_organizational_scenarios.feature",
        mode="strict",
    )
    assert filecmp.cmp(
        "test/out/scenarios_flat_strict_with_organizational_scenarios.feature",
        "test/fixtures/out/scenarios_flat_strict_with_organizational_scenarios.feature",
    )
