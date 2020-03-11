import sys
import pdb
import filecmp
sys.path.insert(0, '..')

from manyworlds import scenario_tree as st

def test_parse():
    tree = st.ScenarioTree('test/fixtures/nested_feature.feature')
    assert len(tree.roots) == 1
    bulk_change_scenario = tree.roots[0].children[0].children[1].children[1]
    assert bulk_change_scenario.name == 'Bulk change permissions'
    assert len(bulk_change_scenario.actions) == 2
    assert len(bulk_change_scenario.assertions) == 2

def test_flatten():
    tree = st.ScenarioTree('test/fixtures/nested_feature.feature')
    tree.flatten('test/out/flat_feature.feature')
    filecmp.cmp('test/out/flat_feature.feature', 'test/fixtures/flat_feature.feature')