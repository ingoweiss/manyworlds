import sys
import pdb
sys.path.insert(0, '..')

from manyworlds import scenario_tree as st

def test_scenario_tree():
    tree = st.ScenarioTree('test/fixtures/nested_feature.feature')
    assert len(tree.roots) == 1
    bulk_change_scenario = tree.roots[0].children[0].children[1].children[1]
    assert bulk_change_scenario.name == 'Bulk change permissions'
    assert len(bulk_change_scenario.actions) == 2
    assert len(bulk_change_scenario.assertions) == 2