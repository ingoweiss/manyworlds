'''Defines the ScenarioTree Class'''
import re
from manyworlds.scenario import Scenario
from manyworlds.step import Step

class ScenarioTree:
    '''A tree of BDD scenarios'''

    TAB_SIZE = 4
    indentation_pattern = rf'(?P<indentation>( {{{TAB_SIZE}}})*)'
    scenario_pattern = r'Scenario: (?P<scenario_name>.*)'
    step_pattern = r'(?P<step_type>Given|When|Then|And|But) (?P<step_name>.*)'
    SCENARIO_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, scenario_pattern))
    STEP_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, step_pattern))

    def __init__(self, file):
        '''
        Init method for the ScenarioTree Class

        Parameters:
        file (string): Path to indented feature file

        Returns:
        Instance of ScenarioTree
        '''
        self.scenarios = []
        self.parse_file(file)

    def parse_file(self, file):
        '''Parse indented feature file into a tree of Scenario instances'''
        with open(file) as indented_file:
            raw_lines = [l.rstrip('\n') for l in indented_file.readlines() if not l.strip() == ""]
        # current_scenarios keeps track of the last ('current') scenario encountered at each level.
        # Any action/assertion encountered at a given level will be added to that level's 'current' scenario
        current_scenarios = {}
        for line_num, line in enumerate(raw_lines):
            scenario_match = self.SCENARIO_LINE_PATTERN.match(line)
            step_match = self.STEP_LINE_PATTERN.match(line)
            if scenario_match or step_match:
                level = len((scenario_match or step_match)['indentation']) / self.TAB_SIZE
            if scenario_match:
                new_scenario = Scenario(scenario_match['scenario_name'],
                                        level=level,
                                        id=line_num)
                current_scenarios[new_scenario.level] = new_scenario
                self.add_scenario(new_scenario)
                if not new_scenario.is_root():
                    current_scenarios[new_scenario.level-1].add_child(new_scenario)
            elif step_match:
                current_scenario = current_scenarios[level]
                if step_match['step_type'] in ['Given', 'When']:
                    new_step_type = 'action'
                elif step_match['step_type'] == 'Then':
                    new_step_type = 'assertion'
                elif step_match['step_type'] in ['And', 'But']:
                    new_step_type = current_scenario.steps()[-1].type
                new_step = Step(step_match['step_name'],
                                type=new_step_type,
                                id=line_num)
                if new_step.type == 'action':
                    current_scenario.add_action(new_step)
                elif new_step.type == 'assertion':
                    current_scenario.add_assertion(new_step)
            else:
                raise ValueError('Unable to parse line: ' + line.strip())

    def root_scenarios(self):
        '''Return the root scenarios of the scenario tree (the ones with level=0 and no parent)'''
        return [s for s in self.scenarios if s.is_root()]

    def leaf_scenarios(self):
        '''Return the leaf scenarios of the scenario tree (the ones with no children)'''
        return [s for s in self.scenarios if s.is_leaf()]

    def add_scenario(self, scenario):
        '''Add a scenrio instance to the tree'''
        self.scenarios.append(scenario)

    def flatten(self, file, mode='strict'):
        '''
        Write a flat (no indentation) feature file representing the scenario tree.

        Parameters:
        file (string): Path to flat feature file
        mode (string): Either 'strict' or 'relaxed'
        '''
        if mode == 'strict':
            self.flatten_strict(file)
        elif mode == 'relaxed':
            self.flatten_relaxed(file)

    def flatten_strict(self, file):
        '''
        Writes a flat (no indentation) feature file representing the tree using the 'strict' mode.

        The 'strict' mode writes one scenario per scenario in the tree.
        This results in a feature file with:
        1. One when/then pair per scenario (generally recommended)
        2. More scenarios
        3. More duplicate (given) actions

        Parameters:
        file (string): Path to flat feature file
        '''
        with open(file, 'w') as flat_file:
            for scenario in self.scenarios:
                flat_file.write("Scenario: {}\n".format(scenario.long_name()))
                given_actions = [a
                                 for s in scenario.ancestors()
                                 for a in s.actions]
                for action_num, action in enumerate(given_actions):
                    conjunction = ('Given' if action_num == 0 else 'And')
                    flat_file.write("{} {}\n".format(conjunction, action.name))
                for action_num, action in enumerate(scenario.actions):
                    conjunction = ('When' if action_num == 0 else 'And')
                    flat_file.write("{} {}\n".format(conjunction, action.name))
                for assertion_num, assertion in enumerate(scenario.assertions):
                    conjunction = ('Then' if assertion_num == 0 else 'And')
                    flat_file.write("{} {}\n".format(conjunction, assertion.name))
                flat_file.write("\n")

    def flatten_relaxed(self, file):
        '''
        Writes a flat (no indentation) feature file representing the tree using the 'relaxed' mode.

        The 'relaxed' mode writes one scenario per leaf scenario in the tree.
        This results in a feature file with:
        1. Multiple when/then pairs per scenario (generally considered an anti-pattern)
        2. Fewer scenarios
        3. Fewer duplicate (given) actions

        Parameters:
        file (string): Path to flat feature file
        '''
        with open(file, 'w') as flat_file:
            for scenario in self.leaf_scenarios():
                flat_file.write("Scenario: {}\n".format(scenario.long_name()))
                given_scenarios = [s for s in scenario.ancestors() if s.given]
                given_actions = [a
                                 for s in given_scenarios
                                 for a in s.actions]
                for action_num, action in enumerate(given_actions):
                    conjunction = ('Given' if action_num == 0 else 'And')
                    flat_file.write("{} {}\n".format(conjunction, action.name))
                new_scenarios = [s for s in scenario.lineage() if not s.given]
                for new_scenario in new_scenarios:
                    for action_num, action in enumerate(new_scenario.actions):
                        conjunction = ('When' if action_num == 0 else 'And')
                        flat_file.write("{} {}\n".format(conjunction, action.name))
                    for assertion_num, assertion in enumerate(new_scenario.assertions):
                        conjunction = ('Then' if assertion_num == 0 else 'And')
                        flat_file.write("{} {}\n".format(conjunction, assertion.name))
                    new_scenario.mark_as_given()
                flat_file.write("\n")

    def graph(self, file):
        '''
        Writes a description of a graph visualizing the scenario tree using the 'Mermaid' syntax

        Parameters:
        file (string): Path to Mermaid file
        '''
        with open(file, 'w') as mermaid_file:
            mermaid_file.write("graph TD\n")
            for scenario in self.scenarios:
                # actions = ['fa:fa-angle-down {}'.format(a) for a in scenario.actions]
                # assertions = ['fa:fa-check {}'.format(a) for a in scenario.assertions]
                if not scenario.parent:
                    mermaid_file.write('{}({})\n'.format(scenario.id, scenario.name))
                else:
                    mermaid_file.write('{} --> {}({})\n'.format(scenario.parent.id,
                                                                scenario.id,
                                                                scenario.name))
