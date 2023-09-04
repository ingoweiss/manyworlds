"""Test the Step class"""

import pytest

import manyworlds as mw


@pytest.fixture(scope="module")
def given_step():
    """load a representative root scenario"""
    forest = mw.Feature.from_file("test/fixtures/in/scenario_forest.feature")
    return forest.find("View users").steps[0]


def test_repr(given_step):
    assert given_step.__repr__() == "<Prerequisite: The following users:>"


def test_format(given_step):
    assert given_step.format() == "Given the following users:"
    assert given_step.format(first_of_type=False) == " And the following users:"
