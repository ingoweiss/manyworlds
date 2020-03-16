import sys
import pdb
import filecmp
sys.path.insert(0, '..')

from manyworlds import scenario_tree as st

def test_parse():
    tree = st.ScenarioTree('test/fixtures/scenarios_tree.feature')
    assert len(tree.roots) == 1
    bulk_change_scenario = tree.roots[0].children[0].children[1].children[1]
    assert bulk_change_scenario.name == 'Bulk change permissions'
    assert len(bulk_change_scenario.actions) == 2
    assert len(bulk_change_scenario.assertions) == 2

def test_flatten_strict():
    tree = st.ScenarioTree('test/fixtures/scenarios_tree.feature')
    tree.flatten('test/out/scenarios_flat_strict.feature')
    filecmp.cmp('test/out/scenarios_flat_strict.feature', 'test/fixtures/scenarios_flat_strict.feature')

def test_graph():
    tree = st.ScenarioTree('test/fixtures/scenarios_tree.feature')
    tree.graph('test/out/scenarios_graph.mermaid.txt')
    filecmp.cmp('test/out/scenarios_graph.mermaid.txt', 'test/fixtures/scenarios_graph.mermaid.txt')