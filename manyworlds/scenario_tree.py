import re
import pdb
from manyworlds.scenario import Scenario
from manyworlds.step import Step

class ScenarioTree:

    SCENARIO_PATTERN = re.compile("^(?P<indentation> *)Scenario: (?P<scenario_name>.*)")
    STEP_PATTERN = re.compile("^(?P<indentation> *)(?P<step_type>Given|When|Then|And|But) (I )?(?P<step_name>.*)")
    INDENTATION = 4

    def __init__(self, file):
        self.scenarios = []
        self.parse_file(file)

    def parse_file(self, file):
        with open(file) as f:
            raw_lines = [l for l in f.readlines() if not l.strip() == ""]
        current_scenarios = {}
        for line_num in range(len(raw_lines)):
            this_line = raw_lines[line_num]
            scenario_match = ScenarioTree.SCENARIO_PATTERN.match(this_line)
            step_match = ScenarioTree.STEP_PATTERN.match(this_line)
            if scenario_match:
                scenario_name = scenario_match['scenario_name']
                scenario_level = len(scenario_match['indentation']) / ScenarioTree.INDENTATION
                new_scenario = Scenario(scenario_name, level=scenario_level, id=line_num)
                current_scenarios[new_scenario.level] = new_scenario
                self.add_scenario(new_scenario)
                if not new_scenario.is_root():
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
                new_step = Step('I ' + step_name, id=line_num, type=new_step_type)
                if new_step.type == 'action':
                    current_scenario.add_action(new_step)
                elif new_step.type == 'assertion':
                    current_scenario.add_assertion(new_step)
            else:
                raise ValueError('Unable to parse line: ' + this_line.strip())

    def root_scenarios(self):
        return [s for s in self.scenarios if s.is_root()]

    def add_scenario(self, scenario):
        self.scenarios.append(scenario)

    def flatten(self, file, strict=True):
        if strict:
            self.flatten_strict(file)
        else:
            self.flatten_relaxed(file)

    # One scenario per scenario in tree, resulting in:
    # 1. one when/then pair per scenario (generally recommended)
    # 2. more scenarios
    # 3. Duplication of actions
    def flatten_strict(self, file):
        with open(file, 'w') as f:
            for scenario in self.scenarios:
                ancestors = scenario.ancestors()
                lineage = ancestors + [scenario]
                f.write("Scenario: " + " > ".join([s.name for s in lineage]) + "\n")
                ancestor_actions = [a for actions in [s.actions for s in ancestors] for a in actions]
                for action_num in range(len(ancestor_actions)):
                    conjunction = ('Given' if action_num == 0 else 'And')
                    f.write(conjunction + " " + ancestor_actions[action_num].name + "\n")
                for action_num in range(len(scenario.actions)):
                    conjunction = ('When' if action_num == 0 else 'And')
                    f.write(conjunction + " " + scenario.actions[action_num].name + "\n")
                for assertion_num in range(len(scenario.assertions)):
                    conjunction = ('Then' if assertion_num == 0 else 'And')
                    f.write(conjunction + " " + scenario.assertions[assertion_num].name + "\n")
                f.write("\n")

    # One scenario per leaf scenario in tree, resulting in:
    # 1. multiple when/then pairs per scenario (generally considered an anti-pattern)
    # 2. fewer scenarios
    # 3. No duplication of actions
    def flatten_relaxed(self, file):
        with open(file, 'w') as f:
            scenarios = [s for s in self.scenarios if s.is_leaf()]
            for scenario in scenarios:
                lineage = scenario.ancestors() + [scenario]
                f.write("Scenario: " + " > ".join([s.name for s in lineage]) + "\n")
                given_scenarios = [s for s in lineage if s.given]
                given_actions = [a for actions in [s.actions for s in given_scenarios] for a in actions]
                for action_num in range(len(given_actions)):
                    conjunction = ('Given' if action_num == 0 else 'And')
                    f.write(conjunction + " " + given_actions[action_num].name + "\n")
                new_scenarios = [s for s in lineage if not s.given]
                for scenario in new_scenarios:
                    for action_num in range(len(scenario.actions)):
                        conjunction = ('When' if action_num == 0 else 'And')
                        f.write(conjunction + " " + scenario.actions[action_num].name + "\n")
                    for assertion_num in range(len(scenario.assertions)):
                        conjunction = ('Then' if assertion_num == 0 else 'And')
                        f.write(conjunction + " " + scenario.assertions[assertion_num].name + "\n")
                    scenario.mark_as_given()
                f.write("\n")

    def graph(self, file):
        with open(file, 'w') as f:
            f.write("graph TD\n")
            for scenario in self.scenarios:
                # actions = ['fa:fa-angle-down {}'.format(a) for a in scenario.actions]
                # assertions = ['fa:fa-check {}'.format(a) for a in scenario.assertions]
                if not scenario.parent:
                    f.write('{}({})\n'.format(scenario.id, scenario.name))
                else:
                    f.write('{} --> {}({})\n'.format(scenario.parent.id, scenario.id, scenario.name))
