"""Defines the ScenarioForest Class"""
import re
from igraph import Graph
import pdb

class Scenario:
    """A BDD Scenario

    :param name: The name of the scenario
    :type name: string
    :param vertex: The iGraph vertex associated with the scenario
    :type name: class: igraph.Vertex
    """

    def __init__(self, name, vertex):
        """Constructor method
        """
        self.name = name.strip()
        self.vertex = vertex
        self.steps = []

    def prerequisites(self):
        return self.steps_of_class(Prerequisite)

    def actions(self):
        return self.steps_of_class(Action)

    def assertions(self):
        return self.steps_of_class(Assertion)

    def steps_of_class(self, step_class):
        return [st for st in self.steps if type(st) is step_class]

class Step:

    step_pattern = r'(?P<conjunction>Given|When|Then|And|But) (?P<name>[^#]+)(# (?P<comment>.+))?'

    @classmethod
    def parse(cls, string, previous_step=None):
        match = re.compile(Step.step_pattern).match(string)
        conjunction = match['conjunction']
        if conjunction in ['And', 'But']:
            conjunction = previous_step.conjunction

        step_class = {
            'Given': Prerequisite,
            'When': Action,
            'Then': Assertion
        }[conjunction]
        return step_class(match['name'], comment=match['comment'])

    def __init__(self, name, data=None, comment=None):
        """Constructor method
        """
        self.name = name.strip()
        self.type = type
        self.data = data
        self.comment = comment

    def conjunction(self):
        return Step.type_to_conjunction_mapping[self.type]

    def format(self, first_of_type=True):
        conjunction = (self.conjunction if first_of_type else 'And')
        return conjunction + ' ' + self.name

    def __str__(self):
        return "<{}>".format(self.format())

    def __repr__(self):
        return self.__str__()

class Prerequisite(Step):
    def __init__(self, name, data=None, comment=None):
       self.conjunction = 'Given'
       super().__init__(name, data=data, comment=comment)

class Action(Step):
    def __init__(self, name, data=None, comment=None):
       self.conjunction = 'When'
       super().__init__(name, data=data, comment=comment)

class Assertion(Step):
    def __init__(self, name, data=None, comment=None):
       self.conjunction = 'Then'
       super().__init__(name, data=data, comment=comment)

class ScenarioForest:
    """A collection of one or more directed trees the vertices of which represent BDD scenarios

    :param graph: A graph
    :type graph: class:`igraph.Graph`
    """

    TAB_SIZE = 4
    indentation_pattern = rf'(?P<indentation>( {{{TAB_SIZE}}})*)'
    scenario_pattern = r'Scenario: (?P<scenario_name>.*)'

    table_pattern = r'| ([^|]* +|)+'
    SCENARIO_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, scenario_pattern))
    STEP_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, Step.step_pattern))
    TABLE_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, table_pattern))

    def __init__(self, graph):
        """Constructor method
        """
        self.graph = graph

    @classmethod
    def data_table_list_to_dict(cls, data_table):
        header_row = data_table[0]
        return [dict(zip(header_row, row)) for row in data_table[1:]]

    @classmethod
    def data_table_dict_to_list(cls, data_table):
        return [list(data_table[0].keys())] + [list(row.values()) for row in data_table]

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
                current_step.data = ScenarioForest.data_table_list_to_dict(current_table)
                current_table = None

            if scenario_match: # Line is scenario
                current_level = int(len((scenario_match)['indentation']) / cls.TAB_SIZE)

                current_scenario_vertex = graph.add_vertex()
                current_scenario = Scenario(scenario_match['scenario_name'], current_scenario_vertex)
                current_scenario_vertex['scenario'] = current_scenario
                current_scenarios[current_level] = current_scenario
                if current_level > 0:
                    current_scenario_parent = current_scenarios[current_level-1]
                    graph.add_edge(current_scenario_parent.vertex, current_scenario.vertex)

            elif step_match: # Line is action or assertion
                current_scenario = current_scenarios[current_level]
                new_step = Step.parse(step_match[0].strip(), previous_step=current_step)
                current_scenario.steps.append(new_step)
                current_step = new_step

            elif table_match: # Line is table
                if current_table == None:
                    current_table = []
                row = [s.strip() for s in line.split('|')[1:-1]]
                current_table.append(row)

        # In case the file ends with a data table:
        if current_table:
            current_step.data = current_table

        return ScenarioForest(graph)

    def root_scenarios(self):
        """Return the root scenarios of the scenario forest (the vertices with no incoming edges)'

        :return: A list of igraph.Vertex
        :rtype: list
        """
        return [vx['scenario'] for vx in self.graph.vs if vx.indegree() == 0]

    def possible_paths_from_source(self, source_scenario, leaf_destinations_only=False):
        """Return paths from a source vertex to vertices that are reachable from the source vertex

        :param source_scenario: Source (root) vertex. First element of all paths returned
        :type source_scenario: class:'igraph.Vertex'
        :param leaf_destinations_only: If True, return paths to leaf scenarios only
        :type leaf_destinations_only: bool, optionsl
        """
        destination_vertices = self.graph.neighborhood(source_scenario.vertex,
                                               mode='OUT',
                                               order=100)
        if leaf_destinations_only:
            destination_vertices = [vx for vx in destination_vertices
                            if self.graph.vs[vx].outdegree() == 0]
        paths = self.graph.get_all_shortest_paths(source_scenario.vertex,
                                                  to=destination_vertices,
                                                  mode='OUT')
        return paths

    @classmethod
    def write_scenario_steps(cls, file_handle, steps, comments='off'):
        """Write formatted scenario steps to file

        :param file_handle: The file to which to write the steps
        :type file_handle: class:'io.TextIOWrapper'
        :param steps: The steps to write
        :type steps: list of Step
        """
        last_step = None
        for step_num, step in enumerate(steps):
            first_of_type = (last_step == None or last_step.conjunction != step.conjunction)
            # pdb.set_trace()
            file_handle.write(step.format(first_of_type=first_of_type) + "\n")
            if comments == 'on' and step.comment:
                file_handle.write("# " + step.comment + "\n")
            if step.data:
                data = ScenarioForest.data_table_dict_to_list(step.data)
                col_widths = [max([len(cell) for cell in col]) for col in list(zip(*data))]
                for row in data:
                    padded_row = [row[col_num].ljust(col_width) for col_num, col_width in enumerate(col_widths)]
                    file_handle.write("    | {} |\n".format(" | ".join(padded_row)))
            last_step = step


    @classmethod
    def write_scenario_name(cls, file_handle, path_scenarios, destination_scenario):
        """Write formatted scenario name to file

        :param file_handle: The file to which to write the scenario name
        :type file_handle: class:'io.TextIOWrapper'
        :param path_scenarios: The scenarios/vertices on the path
        :type path_scenarios: list of class:'igraph.Vertex'
        """
        breadcrumbs = [sc.name for sc in path_scenarios if not sc.assertions()]
        breadcrumbs_string = ''
        if breadcrumbs:
            breadcrumbs_string = ' > '.join(breadcrumbs) + ' > '
        scenario_name = breadcrumbs_string + destination_scenario.name
        file_handle.write("Scenario: {}\n".format(scenario_name))

    def flatten(self, file, mode='strict', comments='off'):
        """Write a flat (no indentation) feature file representing the scenario forest

        :param file: Path to flat feature file to be written
        :type file: str
        :param mode: Flattening mode. Either 'strict' or 'relaxed'
        :type mode: str
        """
        if mode == 'strict':
            self.flatten_strict(file, comments=comments)
        elif mode == 'relaxed':
            self.flatten_relaxed(file, comments=comments)

    def flatten_strict(self, file_path, comments='off'):
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
                    scenarios = [vx['scenario'] for vx in self.graph.vs[path]]
                    path_scenarios = scenarios[:-1]
                    destination_scenario = scenarios[-1]

                    if not (destination_scenario.assertions()):
                        continue # don't ouput scenario unless it has assertions

                    ScenarioForest.write_scenario_name(flat_file, path_scenarios, destination_scenario)

                    steps=[]
                    # if path_scenarios:
                    #     steps += [st
                    #               for sc in path_scenarios
                    #               for st in sc['prerequisites'] + sc['actions']]
                    # else:
                    #     steps += destination_scenario['prerequisites']
                    steps += [st
                              for sc in scenarios
                              for st in sc.prerequisites()]
                    steps += [st
                              for sc in scenarios
                              for st in sc.actions()]
                    steps += destination_scenario.assertions()
                    ScenarioForest.write_scenario_steps(flat_file, steps, comments=comments)
                    flat_file.write("\n")

    def flatten_relaxed(self, file_path, comments='off'):
        """Write a flat (no indentation) feature file representing the tree using the 'relaxed' flattening mode

        The 'relaxed' flattening mode writes one scenario per leaf vertex in the tree, resulting in
        a feature file with multiple alternating sets of "When" and "Then" steps per (generally considered an anti-pattern)

        :param file_path: Path to flat feature file
        :type file_path: str
        """
        with open(file_path, 'w') as flat_file:
            tested_scenarios = []
            for root_scenario in self.root_scenarios():
                possible_paths = self.possible_paths_from_source(root_scenario,
                                                                 leaf_destinations_only=True)
                for path in possible_paths:

                    scenarios = [vx['scenario'] for vx in self.graph.vs[path]]
                    path_scenarios = scenarios[:-1]
                    destination_scenario = scenarios[-1]

                    if not (destination_scenario.assertions()):
                        continue # don't ouput scenario unless it has assertions

                    ScenarioForest.write_scenario_name(flat_file, path_scenarios, destination_scenario)

                    steps=[]
                    for scenario in scenarios:
                        steps += scenario.prerequisites()
                        steps += scenario.actions()
                        if scenario not in tested_scenarios:
                            steps += scenario.assertions()
                        tested_scenarios.append(scenario)

                    ScenarioForest.write_scenario_steps(flat_file, steps, comments=comments)
                    flat_file.write("\n")

    def graph_mermaid(self, file_path):
        """Write a description of a graph visualizing the scenario tree using the 'Mermaid' syntax

        :parmam file_path: Path to Mermaid file to be written
        :type file_path: strex
        """
        with open(file_path, 'w') as mermaid_file:
            mermaid_file.write("graph TD\n")
            for scenario in self.graph.vs:
                mermaid_file.write('{}({})\n'.format(scenario.index, scenario['scenario'].name))
            for edge in self.graph.es:
                mermaid_file.write('{} --> {}\n'.format(edge.source_vertex.index,
                                                        edge.target_vertex.index))

    def find(self, *scenario_names):

        scenario = next(sc for sc in self.root_scenarios() if sc.name == scenario_names[0])
        for scenario_name in scenario_names[1:]:
            scenario = next(vt['scenario'] for vt in scenario.vertex.successors() if vt['scenario'].name == scenario_name)

        return scenario
