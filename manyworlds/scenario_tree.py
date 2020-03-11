import re
import pdb
from manyworlds import scenario as sc

class ScenarioTree:
    
    SCENARIO_PATTERN = re.compile("^(?P<indentation> *)Scenario: (?P<scenario_name>.*)")
    STEP_PATTERN = re.compile("^(?P<indentation> *)(?P<step_type>Given|When|Then|And|But) (I )?(?P<step_name>.*)")
    INDENTATION = 4

    def __init__(self, file):
        self.scenarios = []
        self.roots = []
        self.parse_file(file)

    def parse_file(self, file):        
        with open(file) as f:
            raw_lines = [l for l in f.readlines() if not l.strip() == ""]
        current_scenarios = {}
        for line_num in range(len(raw_lines)):
            this_line = raw_lines[line_num]
            scenario_match = ScenarioTree.SCENARIO_PATTERN.match(this_line)
            step_match     = ScenarioTree.STEP_PATTERN.match(this_line)
            if not (scenario_match or step_match):
                raise ValueError('Unable to parse line: ' + this_line.strip())
            if scenario_match:
                scenario_name = scenario_match['scenario_name']
                scenario_level = len(scenario_match['indentation']) / ScenarioTree.INDENTATION
                new_node = sc.Scenario(scenario_name, level=scenario_level, id=line_num)
                current_scenarios[new_node.level] = new_node
                self.add_scenario(new_node)
                if new_node.is_root():
                    self.add_root(new_node)
                else:
                    current_scenarios[new_node.level-1].add_child(new_node)
            elif step_match:
                step_level = len(step_match['indentation']) / ScenarioTree.INDENTATION
                current_scenario = current_scenarios[step_level]
                step_name = step_match['step_name']
                step_type = step_match['step_type']
                if step_type == 'When' or step_type == 'Given':
                    current_scenario.add_action('I ' + step_name)
                else:
                    current_scenario.add_assertion('I ' + step_name)

    def add_root(self, root):
        self.roots.append(root)

    def add_scenario(self, scenario):
        self.scenarios.append(scenario)
