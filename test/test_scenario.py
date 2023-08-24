"""Test the Scenario class"""

import pytest

import manyworlds as mw


@pytest.fixture(scope="module")
def root_scenario():
    """load a representative root scenario"""
    forest = mw.ScenarioForest.from_file("test/fixtures/in/scenario_forest.feature")
    return forest.find("View users")


@pytest.fixture(scope="module")
def leaf_scenario():
    """load a representative leaf scenario"""
    forest = mw.ScenarioForest.from_file("test/fixtures/in/scenario_forest.feature")
    return forest.find(
        "View users",
        "Bulk operations",
        "Select user",
        "Select multiple users",
        "Bulk deactivate users",
        "Confirm bulk deactivation of users",
    )


def test_repr(root_scenario, leaf_scenario):
    assert (
        root_scenario.__repr__() == "<Scenario: View users "
        "(1 prerequisites, 1 actions, 1 assertions)>"
    )
    assert (
        leaf_scenario.__repr__() == "<Scenario: Confirm bulk deactivation of users "
        "(0 prerequisites, 1 actions, 2 assertions)>"
    )


def test_level(root_scenario, leaf_scenario):
    assert root_scenario.level() == 1
    assert leaf_scenario.level() == 6


def test_ancestors(root_scenario, leaf_scenario):
    assert len(root_scenario.ancestors()) == 0
    assert len(leaf_scenario.ancestors()) == 5
