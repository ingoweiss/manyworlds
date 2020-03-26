import re
from manyworlds.scenario import Scenario
from manyworlds.step import Step

class ScenarioTree:
    '''a tree of BDD scenarios'''

    TAB_SIZE = 4
    indentation_pattern = rf'(?P<indentation>( {{{TAB_SIZE}}})*)'
    scenario_pattern = r'Scenario: (?P<scenario_name>.*)'
    step_pattern = r'(?P<step_type>Given|When|Then|And|But) (I )?(?P<step_name>.*)'
    SCENARIO_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, scenario_pattern))
    STEP_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, step_pattern))

    def __init__(self, file):
        self.scenarios = []
        self.parse_file(file)

    def parse_file(self, file):
        with open(file) as f:
            raw_lines = [l.rstrip('\n') for l in f.readlines() if not l.strip() == ""]
        current_scenarios = {}
        for line_num, line in enumerate(raw_lines):
            scenario_match = self.SCENARIO_LINE_PATTERN.match(line)
            step_match = self.STEP_LINE_PATTERN.match(line)
            if scenario_match:
                new_scenario = Scenario(scenario_match['scenario_name'],
                                        level=len(scenario_match['indentation']) / self.TAB_SIZE,
                                        id=line_num)
                current_scenarios[new_scenario.level] = new_scenario
                self.add_scenario(new_scenario)
                if not new_scenario.is_root():
                    current_scenarios[new_scenario.level-1].add_child(new_scenario)
            elif step_match:
                level = len(step_match['indentation']) / self.TAB_SIZE
                current_scenario = current_scenarios[level]
                if step_match['step_type'] in ['Given', 'When']:
                    new_step_type = 'action'
                elif step_match['step_type'] == 'Then':
                    new_step_type = 'assertion'
                elif step_match['step_type'] in ['And', 'But']:
                    last_step = max(current_scenario.steps(), key=lambda s: s.id)
                    new_step_type = last_step.type
                new_step = Step('I ' + step_match['step_name'],
                                type=new_step_type,
                                id=line_num)
                if new_step.type == 'action':
                    current_scenario.add_action(new_step)
                elif new_step.type == 'assertion':
                    current_scenario.add_assertion(new_step)
            else:
                raise ValueError('Unable to parse line: ' + line.strip())

    def root_scenarios(self):
        return [s for s in self.scenarios if s.is_root()]

    def leaf_scenarios(self):
        return [s for s in self.scenarios if s.is_leaf()]

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
                f.write("Scenario: {}\n".format(scenario.long_name()))
                given_actions = [a
                                 for s in scenario.ancestors()
                                 for a in s.actions]
                for action_num, action in enumerate(given_actions):
                    conjunction = ('Given' if action_num == 0 else 'And')
                    f.write("{} {}\n".format(conjunction, action.name))
                for action_num, action in enumerate(scenario.actions):
                    conjunction = ('When' if action_num == 0 else 'And')
                    f.write("{} {}\n".format(conjunction, action.name))
                for assertion_num, assertion in enumerate(scenario.assertions):
                    conjunction = ('Then' if assertion_num == 0 else 'And')
                    f.write("{} {}\n".format(conjunction, assertion.name))
                f.write("\n")

    # One scenario per leaf scenario in tree, resulting in:
    # 1. multiple when/then pairs per scenario (generally considered an anti-pattern)
    # 2. fewer scenarios
    # 3. No duplication of actions
    def flatten_relaxed(self, file):
        with open(file, 'w') as f:
            for scenario in self.leaf_scenarios():
                f.write("Scenario: {}\n".format(scenario.long_name()))
                given_scenarios = [s for s in scenario.ancestors() if s.given]
                given_actions = [a
                                 for s in given_scenarios
                                 for a in s.actions]
                for action_num, action in enumerate(given_actions):
                    conjunction = ('Given' if action_num == 0 else 'And')
                    f.write("{} {}\n".format(conjunction, action.name))
                new_scenarios = [s for s in scenario.lineage() if not s.given]
                for new_scenario in new_scenarios:
                    for action_num, action in enumerate(new_scenario.actions):
                        conjunction = ('When' if action_num == 0 else 'And')
                        f.write("{} {}\n".format(conjunction, action.name))
                    for assertion_num, assertion in enumerate(new_scenario.assertions):
                        conjunction = ('Then' if assertion_num == 0 else 'And')
                        f.write("{} {}\n".format(conjunction, assertion.name))
                    new_scenario.mark_as_given()
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
                    f.write('{} --> {}({})\n'.format(scenario.parent.id,
                                                     scenario.id,
                                                     scenario.name))
