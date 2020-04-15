import filecmp
import manyworlds as mw

def test_parse():
    tree = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    assert len(tree.root_scenarios()) == 1
    bulk_change_scenario = tree.root_scenarios()[0].successors()[0].successors()[1].successors()[1]
    assert bulk_change_scenario['name'] == 'Bulk change permissions'
    assert len(bulk_change_scenario['actions']) == 2
    assert len(bulk_change_scenario['assertions']) == 2

def test_flatten_strict():
    tree = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    tree.flatten('test/out/scenarios_flat_strict.feature')
    assert filecmp.cmp('test/out/scenarios_flat_strict.feature', 'test/fixtures/scenarios_flat_strict.feature')

def test_flatten_relaxed():
    tree = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    tree.flatten('test/out/scenarios_flat_relaxed.feature', mode='relaxed')
    assert filecmp.cmp('test/out/scenarios_flat_relaxed.feature', 'test/fixtures/scenarios_flat_relaxed.feature')

def test_graph_mermaid():
    tree = mw.ScenarioForest.from_file('test/fixtures/scenarios_forest.feature')
    tree.graph_mermaid('test/out/scenarios_graph.mermaid.txt')
    assert filecmp.cmp('test/out/scenarios_graph.mermaid.txt', 'test/fixtures/scenarios_graph.mermaid.txt')
