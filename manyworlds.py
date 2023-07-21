"""Defines the ScenarioForest Class"""
import re
from igraph import Graph
import pdb

class ScenarioForest:
    """A collection of one or more directed trees the vertices of which represent BDD scenarios

    :param graph: A graph
    :type graph: class:`igraph.Graph`
    """

    TAB_SIZE = 4
    indentation_pattern = rf'(?P<indentation>( {{{TAB_SIZE}}})*)'
    scenario_pattern = r'Scenario: (?P<scenario_name>.*)'
    step_pattern = r'(?P<step_type>Given|When|Then|And|But) (?P<step_name>.*)'
    table_pattern = r'| ([^|]* +|)+'
    SCENARIO_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, scenario_pattern))
    STEP_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, step_pattern))
    TABLE_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, table_pattern))

    def __init__(self, graph):
        """Constructor method
        """
        self.graph = graph

    @classmethod
    def from_file(cls, file_path):
        """Create a scenario tree instance from an indented feature file

        Scan the indented file line by line and:
        1. Keep track of the last scenario encountered at each indentation level
        2. Any scenario encountered is added as a child to the last scenario encounterd
           at the parent level
        3. Any action or assertion encountered is added to the last scenarion encountered
           at that level

        :param file_path: Fath to indented feature file
        :type file_path: str
        :return: A new instance of manyworlds.ScenarioForest
        :rtype: class:'manyworlds.ScenarioForest'
        """
        graph = Graph(directed=True)
        with open(file_path) as indented_file:
            raw_lines = [l.rstrip('\n') for l in indented_file.readlines() if not l.strip() == ""]
        current_scenarios = {} # used to keep track of last scenario encountered at each level
        current_table = None
        current_step = None

        # Scan the file line by line
        for line in raw_lines:

            # Determine whether line is scenario, actio or assertion
            scenario_match = cls.SCENARIO_LINE_PATTERN.match(line)
            step_match = cls.STEP_LINE_PATTERN.match(line)
            table_match = cls.TABLE_LINE_PATTERN.match(line)
            if not (scenario_match or step_match or table_match):
                raise ValueError('Unable to parse line: ' + line.strip())

            if (scenario_match or step_match) and current_table:
                current_step['data'] = current_table
                current_table = None

            if scenario_match: # Line is scenario
                current_level = int(len((scenario_match)['indentation']) / cls.TAB_SIZE)
                print(('' if current_level == 0 else '   '*current_level + '└─ ') + scenario_match['scenario_name'])

                current_scenario = graph.add_vertex(name=scenario_match['scenario_name'],
                                                    actions=[],
                                                    assertions=[])
                current_scenarios[current_level] = current_scenario
                if current_level > 0:
                    current_scenario_parent = current_scenarios[current_level-1]
                    graph.add_edge(current_scenario_parent, current_scenario)

            elif step_match: # Line is action or assertion
                current_scenario = current_scenarios[current_level]
                if step_match['step_type'] in ['Given', 'When']:
                    new_step_type = 'action'
                elif step_match['step_type'] == 'Then':
                    new_step_type = 'assertion'
                elif step_match['step_type'] in ['And', 'But']:
                    new_step_type = current_step['type']
                new_step = {'name': step_match['step_name'], 'type': new_step_type}
                if new_step_type == 'action':
                    current_scenario['actions'].append(new_step)
                elif new_step_type == 'assertion':
                    current_scenario['assertions'].append(new_step)
                current_step = new_step

            elif table_match: # Line is table
                if current_table == None:
                    current_table = []
                row = [s.strip() for s in line.split('|')[1:-1]]
                current_table.append(row)

        # In case the file ends with a data table:
        if current_table:
            current_step['data'] = current_table

        return ScenarioForest(graph)

    def root_scenarios(self):
        """Return the root scenarios of the scenario forest (the vertices with no incoming edges)'

        :return: A list of igraph.Vertex
        :rtype: list
        """
        return [v for v in self.graph.vs if v.indegree() == 0]

    def possible_paths_from_source(self, source_scenario, leaf_destinations_only=False):
        """Return paths from a source vertex to vertices that are reachable from the source vertex

        :param source_scenario: Source (root) vertex. First element of all paths returned
        :type source_scenario: class:'igraph.Vertex'
        :param leaf_destinations_only: If True, return paths to leaf scenarios only
        :type leaf_destinations_only: bool, optionsl
        """
        destinations = self.graph.neighborhood(source_scenario,
                                               mode='OUT',
                                               order=100)
        if leaf_destinations_only:
            destinations = [v for v in destinations
                            if self.graph.vs[v].outdegree() == 0]
        paths = self.graph.get_all_shortest_paths(source_scenario,
                                                  to=destinations,
                                                  mode='OUT')
        return paths

    @classmethod
    def write_scenario_steps(cls, file_handle, steps, conjunction):
        """Write formatted scenario steps to file

        :param file_handle: The file to which to write the steps
        :type file_handle: class:'io.TextIOWrapper'
        :param steps: The steps to write
        :type steps: list of str
        :param conjunction: The conjunction to use (either 'Given', 'When' or 'Then')
        :type conjunction: str
        """
        for step_num, step in enumerate(steps):
            conjunction = (conjunction if step_num == 0 else 'And')
            file_handle.write("{} {}\n".format(conjunction, step['name']))
            if 'data' in step.keys():
                table = step['data']
                col_widths = [max([len(cell) for cell in col]) for col in list(zip(*table))]
                for row in table:
                    padded_row = [row[col_num].ljust(col_width) for col_num, col_width in enumerate(col_widths)]
                    file_handle.write("    | {} |\n".format(" | ".join(padded_row)))


    @classmethod
    def write_scenario_name(cls, file_handle, path_scenarios):
        """Write formatted scenario name to file

        :param file_handle: The file to which to write the scenario name
        :type file_handle: class:'io.TextIOWrapper'
        :param path_scenarios: The scenarios/vertices on the path
        :type path_scenarios: list of class:'igraph.Vertex'
        """
        path_name = ' > '.join([v['name'] for v in path_scenarios])
        file_handle.write("Scenario: {}\n".format(path_name))

    def flatten(self, file, mode='strict'):
        """Write a flat (no indentation) feature file representing the scenario forest

        :param file: Path to flat feature file to be written
        :type file: str
        :param mode: Flattening mode. Either 'strict' or 'relaxed'
        :type mode: str
        """
        if mode == 'strict':
            self.flatten_strict(file)
        elif mode == 'relaxed':
            self.flatten_relaxed(file)

    def flatten_strict(self, file_path):
        """Write a flat (no indentation) feature file representing the forest using the 'strict' flattening mode

        The 'strict' flattening mode writes one scenario per vertex in the tree, resulting in
        a feature file with one set of 'When' steps followed by one set of 'Then' steps (generally recommended)

        :param file_path: Path to flat feature file
        :type file_path: str
        """
        with open(file_path, 'w') as flat_file:
            for root_scenario in self.root_scenarios():
                possible_paths = self.possible_paths_from_source(root_scenario)
                for path in possible_paths:
                    path_scenarios = self.graph.vs[path]

                    if not path_scenarios[-1]['assertions']:
                        continue # don't ouput scenario unless it has assertions

                    ScenarioForest.write_scenario_name(flat_file, path_scenarios)
                    given_actions = [a
                                     for s in path_scenarios[:-1]
                                     for a in s['actions']]
                    ScenarioForest.write_scenario_steps(flat_file,
                                                        given_actions,
                                                        'Given')
                    destination_scenario = path_scenarios[-1]
                    ScenarioForest.write_scenario_steps(flat_file,
                                                        destination_scenario['actions'],
                                                        'When')
                    ScenarioForest.write_scenario_steps(flat_file,
                                                        destination_scenario['assertions'],
                                                        'Then')
                    flat_file.write("\n")

    def flatten_relaxed(self, file_path):
        """Write a flat (no indentation) feature file representing the tree using the 'relaxed' flattening mode

        The 'relaxed' flattening mode writes one scenario per leaf vertex in the tree, resulting in
        a feature file with multiple alternating sets of "When" and "Then" steps per (generally considered an anti-pattern)

        :param file_path: Path to flat feature file
        :type file_path: str
        """
        with open(file_path, 'w') as flat_file:
            given_scenarios = []
            for root_scenario in self.root_scenarios():
                possible_paths = self.possible_paths_from_source(root_scenario,
                                                                 leaf_destinations_only=True)
                for path in possible_paths:
                    path_scenarios = self.graph.vs[path]

                    if not path_scenarios[-1]['assertions']:
                        continue # don't ouput scenario unless it has assertions

                    ScenarioForest.write_scenario_name(flat_file, path_scenarios)
                    given_actions = [a
                                     for s in path_scenarios if s in given_scenarios
                                     for a in s['actions']]
                    ScenarioForest.write_scenario_steps(flat_file, given_actions, 'Given')
                    for path_scenario in [s for s in path_scenarios if s not in given_scenarios]:
                        ScenarioForest.write_scenario_steps(flat_file,
                                                            path_scenario['actions'],
                                                            'When')
                        ScenarioForest.write_scenario_steps(flat_file,
                                                            path_scenario['assertions'],
                                                            'Then')
                        given_scenarios.append(path_scenario)
                    flat_file.write("\n")

    def graph_mermaid(self, file_path):
        """Write a description of a graph visualizing the scenario tree using the 'Mermaid' syntax

        :parmam file_path: Path to Mermaid file to be written
        :type file_path: strex
        """
        with open(file_path, 'w') as mermaid_file:
            mermaid_file.write("graph TD\n")
            for scenario in self.graph.vs:
                mermaid_file.write('{}({})\n'.format(scenario.index, scenario['name']))
            for edge in self.graph.es:
                mermaid_file.write('{} --> {}\n'.format(edge.source_vertex.index,
                                                        edge.target_vertex.index))
