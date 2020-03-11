import re
import pdb
from manyworlds import scenario as sc
from manyworlds import step as st

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
                new_scenario = sc.Scenario(scenario_name, level=scenario_level, id=line_num)
                current_scenarios[new_scenario.level] = new_scenario
                self.add_scenario(new_scenario)
                if new_scenario.is_root():
                    self.add_root(new_scenario)
                else:
                    current_scenarios[new_scenario.level-1].add_child(new_scenario)
            elif step_match:
                step_level = len(step_match['indentation']) / ScenarioTree.INDENTATION
                current_scenario = current_scenarios[step_level]
                step_name = step_match['step_name']
                step_type = step_match['step_type']
                if step_type in ['Given', 'When']:
                    new_step_type = 'action'
                elif step_type == 'Then':
                    new_step_type = 'assertion'
                elif step_type in ['And', 'But']:
                    existing_steps = (current_scenario.actions + current_scenario.assertions)
                    last_step = sorted(existing_steps, key=lambda s: s.id, reverse=False)[-1]
                    new_step_type = last_step.type
                new_step = st.Step('I ' + step_name, id=line_num, type=new_step_type)
                if new_step.type == 'action':
                    current_scenario.add_action(new_step)
                elif new_step.type == 'assertion':
                    current_scenario.add_assertion(new_step)

    def add_root(self, root):
        self.roots.append(root)

    def add_scenario(self, scenario):
        self.scenarios.append(scenario)

    def flatten(self, file):
        with open(file, 'w') as f:
            for scenario in self.scenarios:
                ancestry = [scenario]
                parent = scenario.parent
                while parent:
                    ancestry.insert(0, parent)
                    parent = parent.parent
                f.write("Scenario: " + " > ".join([s.name for s in ancestry]) + "\n")
                ancestry_actions = [a for actions in [s.actions for s in ancestry] for a in actions]
                for action_num in range(len(ancestry_actions)):
                    conjunction = ('When' if action_num == 0 else 'And')
                    f.write(conjunction + " " + ancestry_actions[action_num].name + "\n")
                for assertion_num in range(len(scenario.assertions)):
                    conjunction = ('Then' if assertion_num == 0 else 'And')
                    f.write(conjunction + " " + scenario.assertions[assertion_num].name + "\n")
                f.write("\n")
    
