import sys
import pdb
import filecmp
sys.path.insert(0, '..')

import manyworlds as mw

def test_parse():
    tree = mw.ScenarioTree('test/fixtures/scenarios_tree.feature')
    assert len(tree.root_scenarios()) == 1
    bulk_change_scenario = tree.root_scenarios()[0].children[0].children[1].children[1]
    assert bulk_change_scenario.name == 'Bulk change permissions'
    assert len(bulk_change_scenario.actions) == 2
    assert len(bulk_change_scenario.assertions) == 2

def test_flatten_strict():
    tree = mw.ScenarioTree('test/fixtures/scenarios_tree.feature')
    tree.flatten('test/out/scenarios_flat_strict.feature')
    assert filecmp.cmp('test/out/scenarios_flat_strict.feature', 'test/fixtures/scenarios_flat_strict.feature')

def test_flatten_relaxed():
    tree = mw.ScenarioTree('test/fixtures/scenarios_tree.feature')
    tree.flatten('test/out/scenarios_flat_relaxed.feature', mode='relaxed')
    assert filecmp.cmp('test/out/scenarios_flat_relaxed.feature', 'test/fixtures/scenarios_flat_relaxed.feature')

def test_graph():
    tree = mw.ScenarioTree('test/fixtures/scenarios_tree.feature')
    tree.graph('test/out/scenarios_graph.mermaid.txt')
    assert filecmp.cmp('test/out/scenarios_graph.mermaid.txt', 'test/fixtures/scenarios_graph.mermaid.txt')