"""Defines the ScenarioForest Class"""
import re
from igraph import Graph
import pdb

from .scenario import Scenario
from .step import Step, Prerequisite, Action, Assertion

class ScenarioForest:
    """A collection of one or more directed trees the vertices of which represent BDD scenarios

    :param graph: A graph
    :type graph: class:`igraph.Graph`
    """

    TAB_SIZE = 4
    indentation_pattern = rf'(?P<indentation>( {{{TAB_SIZE}}})*)'
    scenario_pattern = r'Scenario: (?P<scenario_name>.*)'

    SCENARIO_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, scenario_pattern))
    STEP_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, Step.step_pattern))
    TABLE_LINE_PATTERN = re.compile("^{}{}$".format(indentation_pattern, Step.table_pattern))

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

            # Determine whether line is scenario, step or table row
            scenario_match = cls.SCENARIO_LINE_PATTERN.match(line)
            step_match = cls.STEP_LINE_PATTERN.match(line)
            table_match = cls.TABLE_LINE_PATTERN.match(line)
            if not (scenario_match or step_match or table_match):
                raise ValueError('Unable to parse line: ' + line.strip())

            # close and record any open data table
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
                    # Connect to parent scenario
                    current_scenario_parent = current_scenarios[current_level-1]
                    graph.add_edge(current_scenario_parent.vertex, current_scenario.vertex)

            elif step_match: # Line is action or assertion
                current_scenario = current_scenarios[current_level]
                new_step = Step.parse(step_match[0].strip(), previous_step=current_step)
                current_scenario.steps.append(new_step)
                current_step = new_step

            elif table_match: # Line is table row
                if current_table == None:
                    current_table = []
                row = [s.strip() for s in line.split('|')[1:-1]]
                current_table.append(row)

        # In case the file ends with a data table:
        if current_table:
            current_step.data = ScenarioForest.data_table_list_to_dict(current_table)

        return ScenarioForest(graph)

    @classmethod
    def write_scenario_steps(cls, file_handle, steps, comments=False):
        """Write formatted scenario steps to file

        :param file_handle: The file to which to write the steps
        :type file_handle: class:'io.TextIOWrapper'
        :param steps: The steps to write
        :type steps: list of Step
        """
        last_step = None
        for step_num, step in enumerate(steps):
            first_of_type = (last_step == None or last_step.conjunction != step.conjunction)
            file_handle.write(step.format(first_of_type=first_of_type) + "\n")
            if comments and step.comment:
                file_handle.write("# " + step.comment + "\n")
            if step.data:
                ScenarioForest.write_data_table(file_handle, step.data)
            last_step = step

    @classmethod
    def write_data_table(cls, file_handle, data_table):
        data = ScenarioForest.data_table_dict_to_list(data_table)
        col_widths = [max([len(cell) for cell in col]) for col in list(zip(*data))]
        for row in data:
            padded_row = [row[col_num].ljust(col_width) for col_num, col_width in enumerate(col_widths)]
            file_handle.write("    | {} |\n".format(" | ".join(padded_row)))

    def flatten(self, file, mode='strict', comments=False):
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

    def flatten_strict(self, file_path, comments=False):
        """Write a flat (no indentation) feature file representing the forest using the 'strict' flattening mode

        The 'strict' flattening mode writes one scenario per vertex in the tree, resulting in
        a feature file with one set of 'When' steps followed by one set of 'Then' steps (generally recommended)

        :param file_path: Path to flat feature file
        :type file_path: str
        """
        with open(file_path, 'w') as flat_file:
            for scenario in [sc for sc in self.scenarios() if not sc.is_breadcrumb()]:
                flat_file.write(scenario.format() + "\n")

                ancestor_scenarios = scenario.ancestors()
                steps=[]
                # collect prerequisites from all scenarios along the path
                steps += [st
                            for sc in ancestor_scenarios
                            for st in sc.prerequisites()]
                # collect actions from all scenarios along the path
                steps += [st
                            for sc in ancestor_scenarios
                            for st in sc.actions()]
                # add all steps from the destination scenario only
                steps += scenario.steps
                ScenarioForest.write_scenario_steps(flat_file, steps, comments=comments)
                flat_file.write("\n")

    def flatten_relaxed(self, file_path, comments=False):
        """Write a flat (no indentation) feature file representing the tree using the 'relaxed' flattening mode

        The 'relaxed' flattening mode writes one scenario per leaf vertex in the tree, resulting in
        a feature file with multiple alternating sets of "When" and "Then" steps per (generally considered an anti-pattern)

        :param file_path: Path to flat feature file
        :type file_path: str
        """
        with open(file_path, 'w') as flat_file:
            tested_scenarios = []
            for scenario in self.leaf_scenarios():
                flat_file.write(scenario.format() + "\n")

                path_scenarios = scenario.ancestors() + [scenario]
                steps=[]
                for path_scenario in path_scenarios:
                    steps += path_scenario.prerequisites()
                    steps += path_scenario.actions()
                    if path_scenario not in tested_scenarios:
                        steps += path_scenario.assertions()
                        tested_scenarios.append(path_scenario)

                ScenarioForest.write_scenario_steps(flat_file, steps, comments=comments)
                flat_file.write("\n")

    def find(self, *scenario_names):

        scenario = next(sc for sc in self.root_scenarios() if sc.name == scenario_names[0])
        for scenario_name in scenario_names[1:]:
            scenario = next(vt['scenario'] for vt in scenario.vertex.successors() if vt['scenario'].name == scenario_name)

        return scenario

    def scenarios(self):
        """Return the scenarios of the scenario forest

        :return: A list of manyworlds.Scenario
        :rtype: list
        """
        return [vx['scenario'] for vx in self.graph.vs]

    def root_scenarios(self):
        """Return the root scenarios of the scenario forest (the vertices with no incoming edges)

        :return: A list of manyworlds.Scenario
        :rtype: list
        """
        return [vx['scenario'] for vx in self.graph.vs if vx.indegree() == 0]

    def leaf_scenarios(self):
        """Return the leaf scenarios of the scenario forest (the vertices with no outgoing edges)

        :return: A list of manyworlds.Scenario
        :rtype: list
        """
        return [vx['scenario'] for vx in self.graph.vs if vx.outdegree() == 0]
