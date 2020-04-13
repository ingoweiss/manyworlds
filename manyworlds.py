'''Defines the ScenarioTree Class'''
import re
from igraph import Graph

class ScenarioTree:
    '''A tree of BDD scenarios'''

    TAB_SIZE = 4
    indentation_pattern = rf'(?P<indentation>( {{{TAB_SIZE}}})*)'
    scenario_pattern = r'Scenario: (?P<scenario_name>.*)'
    step_pattern = r'(?P<step_type>Given|When|Then|And|But) (?P<step_name>.*)'
    SCENARIO_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, scenario_pattern))
    STEP_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, step_pattern))

    def __init__(self, graph):
        '''
        Init method for the ScenarioTree Class

        Parameters:
        graph (igraph.Graph instance): graph representing the scenario tree

        Returns:
        Instance of ScenarioTree
        '''
        self.graph = graph

    @classmethod
    def from_file(cls, file):
        '''
        Create a scenario tree from an indented feature file

        Parameters:
        file (string): Path to indented feature file
        '''
        graph = Graph(directed=True)
        with open(file) as indented_file:
            raw_lines = [l.rstrip('\n') for l in indented_file.readlines() if not l.strip() == ""]
        # 'current_scenarios' keeps track of the last ('current') scenario encountered at each
        # level. Any action/assertion encountered at a given level will be added to that level's
        # 'current' scenario
        current_scenarios = {}
        for line in raw_lines:
            scenario_match = cls.SCENARIO_LINE_PATTERN.match(line)
            step_match = cls.STEP_LINE_PATTERN.match(line)
            if not (scenario_match or step_match):
                raise ValueError('Unable to parse line: ' + line.strip())
            current_level = len((scenario_match or step_match)['indentation']) / cls.TAB_SIZE
            if scenario_match:
                current_scenario = graph.add_vertex(name=scenario_match['scenario_name'],
                                                    actions=[],
                                                    assertions=[])
                current_scenarios[current_level] = current_scenario
                if current_level > 0:
                    current_scenario_parent = current_scenarios[current_level-1]
                    graph.add_edge(current_scenario_parent, current_scenario)
            elif step_match:
                current_scenario = current_scenarios[current_level]
                if step_match['step_type'] in ['Given', 'When']:
                    new_step_type = 'action'
                elif step_match['step_type'] == 'Then':
                    new_step_type = 'assertion'
                elif step_match['step_type'] in ['And', 'But']:
                    new_step_type = last_step_type
                new_step = step_match['step_name']
                if new_step_type == 'action':
                    current_scenario['actions'].append(new_step)
                elif new_step_type == 'assertion':
                    current_scenario['assertions'].append(new_step)
                last_step_type = new_step_type
        return ScenarioTree(graph)

    def root_scenarios(self):
        '''Return the root scenarios of the scenario tree (the ones with level=0 and no parent)'''
        return [v for v in self.graph.vs if v.indegree() == 0]

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
            for root_scenario in self.root_scenarios():
                possible_destinations = self.graph.neighborhood(root_scenario,
                                                                mode='OUT',
                                                                order=100)
                possible_paths = self.graph.get_all_shortest_paths(root_scenario,
                                                                   to=possible_destinations,
                                                                   mode='OUT')
                for path in possible_paths:
                    path_scenarios = self.graph.vs[path]
                    path_name = ' > '.join([v['name'] for v in path_scenarios])
                    flat_file.write("Scenario: {}\n".format(path_name))
                    given_actions = [a
                                     for s in path_scenarios[:-1]
                                     for a in s['actions']]
                    for action_num, action in enumerate(given_actions):
                        conjunction = ('Given' if action_num == 0 else 'And')
                        flat_file.write("{} {}\n".format(conjunction, action))
                    destination_scenario = path_scenarios[-1]
                    for action_num, action in enumerate(destination_scenario['actions']):
                        conjunction = ('When' if action_num == 0 else 'And')
                        flat_file.write("{} {}\n".format(conjunction, action))
                    for assertion_num, assertion in enumerate(destination_scenario['assertions']):
                        conjunction = ('Then' if assertion_num == 0 else 'And')
                        flat_file.write("{} {}\n".format(conjunction, assertion))
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
            given_scenarios = []
            for root_scenario in self.root_scenarios():
                possible_destinations = self.graph.neighborhood(root_scenario,
                                                                mode='OUT',
                                                                order=100)
                possible_leaf_destinations = [v for v in possible_destinations
                                              if self.graph.vs[v].outdegree() == 0]
                possible_paths = self.graph.get_all_shortest_paths(root_scenario,
                                                                   to=possible_leaf_destinations,
                                                                   mode='OUT')
                for path in possible_paths:
                    path_scenarios = self.graph.vs[path]
                    path_name = ' > '.join([v['name'] for v in path_scenarios])
                    flat_file.write("Scenario: {}\n".format(path_name))
                    given_actions = [a
                                     for s in path_scenarios if s in given_scenarios
                                     for a in s['actions']]
                    for action_num, action in enumerate(given_actions):
                        conjunction = ('Given' if action_num == 0 else 'And')
                        flat_file.write("{} {}\n".format(conjunction, action))
                    for path_scenario in [s for s in path_scenarios if s not in given_scenarios]:
                        for action_num, action in enumerate(path_scenario['actions']):
                            conjunction = ('When' if action_num == 0 else 'And')
                            flat_file.write("{} {}\n".format(conjunction, action))
                        for assertion_num, assertion in enumerate(path_scenario['assertions']):
                            conjunction = ('Then' if assertion_num == 0 else 'And')
                            flat_file.write("{} {}\n".format(conjunction, assertion))
                        given_scenarios.append(path_scenario)
                    flat_file.write("\n")

    def graph_mermaid(self, file):
        '''
        Writes a description of a graph visualizing the scenario tree using the 'Mermaid' syntax

        Parameters:
        file (string): Path to Mermaid file
        '''
        with open(file, 'w') as mermaid_file:
            mermaid_file.write("graph TD\n")
            for scenario in self.graph.vs:
                mermaid_file.write('{}({})\n'.format(scenario.index, scenario['name']))
            for edge in self.graph.es:
                mermaid_file.write('{} --> {}\n'.format(edge.source_vertex.index,
                                                        edge.target_vertex.index))
