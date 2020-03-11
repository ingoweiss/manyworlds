import sys
sys.path.insert(0, '..')

from manyworlds import scenario_tree as st

def test_answer():
    st.ScenarioTree('fixtures/feature.feature')
    assert 1 == 1