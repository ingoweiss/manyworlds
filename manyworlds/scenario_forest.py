"""Defines the ScenarioForest Class"""
import re
import igraph as ig
import pdb

from .scenario import Scenario
from .step import Step, Prerequisite, Action, Assertion
from .data_table import DataTable
from .exceptions import InvalidFeatureFileError

class ScenarioForest:
    """A collection of one or more directed trees
    the vertices of which represent BDD scenarios"""

    TAB_SIZE = 4
    LINE_PATTERN = re.compile('(?P<indentation> *)(?P<line>.*)\n')
    indentation_pattern = rf'(?P<indentation>( {{{TAB_SIZE}}})*)'

    SCENARIO_LINE_PATTERN = re.compile("^{}{}$".format(
        indentation_pattern,
        Scenario.scenario_pattern
    ))
    STEP_LINE_PATTERN = re.compile("^{}{}$".format(
        indentation_pattern,
        Step.step_pattern
    ))
    TABLE_LINE_PATTERN = re.compile("^{}{}$".format(
        indentation_pattern,
        Step.table_pattern
    ))

    def __init__(self):
        """Constructor method

        Parameters
        ----------
        graph : igraph.Graph
            The graph representing the set of scenario trees
        """

        self.graph = ig.Graph(directed=True)

    @classmethod
    def data_table_list_to_dict(cls, data_table):
        """Convert a data table from list of list to list of dict

        Parameters
        ----------
        data_table : list
            List of (equal-length) list of str. The first list is used as headers

        Returns
        -------
        list
            List of dict
        """

        header_row = data_table[0]
        return [dict(zip(header_row, row)) for row in data_table[1:]]

    @classmethod
    def data_table_dict_to_list(cls, data_table):
        """Convert a data table from list of dict to list of list

        Parameters
        ----------
        data_table : list
            List of dict

        Returns
        -------
        list
            List of (equal-length) list of str. The first list is used for headers
        """

        return [list(data_table[0].keys())]\
             + [list(row.values()) for row in data_table]

    @classmethod
    def split_line(cls, line):
        match = cls.LINE_PATTERN.match(line)
        return (match['indentation'], match['line'])

    def parse_line(self, line):
        if re.compile(Scenario.scenario_pattern).match(line):
            return Scenario.parse_line(line)
        elif re.compile(Step.step_pattern).match(line):
            return self.parse_step(line)
        elif re.compile(DataTable.data_table_row_pattern).match(line):
            return DataTable.parse_line(line)

    def parse_step(self, line):
        match = re.compile(Step.step_pattern).match(line)
        conjunction = match['conjunction']
        if conjunction in ['And', 'But']:
            previous_step = self.scenarios()[-1].steps[-1]
            step_type = type(previous_step)
        else:
            step_type = {
                'Given': Prerequisite,
                'When' : Action,
                'Then' : Assertion
            }[conjunction]
        return step_type(match['name'], comment=match['comment'])

    @classmethod
    def from_file(cls, file_path):
        forest = ScenarioForest()
        with open(file_path) as indented_file:
            for line_no, raw_line in enumerate(indented_file.readlines()):
                if raw_line.strip() == '':
                    continue #skip empty lines

                indentation, line = cls.split_line(raw_line)

                # validate indentation:
                if len(indentation) % cls.TAB_SIZE == 0:
                    level = int(len(indentation) / cls.TAB_SIZE) + 1
                else:
                    raise InvalidFeatureFileError("Invalid indentation at line {}".format(line_no))

                # determine what kind of line this is:
                parsed_line = forest.parse_line(line)
                # Scenario line:
                if isinstance(parsed_line, Scenario):
                    forest.append_scenario(parsed_line, at_level=level)
                # Step:
                elif isinstance(parsed_line, Step):
                    forest.append_step(parsed_line, at_level=level)
                # Data table line:
                elif isinstance(parsed_line, list):
                    forest.append_data_row(parsed_line, at_level=level)
                # Not a valid line:
                else:
                    raise InvalidFeatureFileError("Unable to parse line {}: {}".format(line_no+1, line))

        return forest

    def append_scenario(self, scenario, at_level):
        if at_level > 1:
            parent_level = at_level-1
            last_scenario_at_parent_level = [sc for sc in self.scenarios() if sc.level() == parent_level][-1]
            vertex = self.graph.add_vertex()
            vertex['scenario'] = scenario
            scenario.vertex = vertex
            scenario.graph = vertex.graph
            self.graph.add_edge(
                last_scenario_at_parent_level.vertex,
                scenario.vertex
            )
        else:
            vertex = self.graph.add_vertex()
            vertex['scenario'] = scenario
            scenario.vertex = vertex
            scenario.graph = vertex.graph

        return scenario

    def append_step(self, step, at_level):
        last_scenario = self.scenarios()[-1]
        last_scenario.steps.append(step)
        return True

    def append_data_row(self, data_row, at_level):
        last_step = self.scenarios()[-1].steps[-1]
        if last_step.data:
            last_step.data.rows.append(data_row)
        else:
            last_step.data = DataTable(data_row)

    @classmethod
    def from_file_old(cls, file_path):
        """Create a scenario tree instance from an indented feature file

        Scans the indented file line by line and:
        1. Keeps track of the last scenario encountered at each indentation level
        2. Any scenario encountered is added as a child to the last scenario encounterd
           at the parent level
        3. Any prerequisite, action or assertion encountered is added to the last
           scenario encountered at that level
        4. Any data table encountered is added to the current step

        Parameters
        ----------
        file_path : str
            Path to the indented feature file

        Returns
        -------
        ScenarioForest
            Instance of ScenarioForest
        """

        graph = ig.Graph(directed=True)
        with open(file_path) as indented_file:
            non_empty_lines = [
                ln.rstrip('\n') for ln in indented_file.readlines()\
                if not ln.strip() == ""
            ]
        # used to keep track of last scenario encountered at each level:
        current_scenarios = {}
        current_table = None
        current_step = None

        # Scan the file line by line
        for line in non_empty_lines:

            # Determine whether line is scenario, step or table row
            scenario_match = cls.SCENARIO_LINE_PATTERN.match(line)
            step_match = cls.STEP_LINE_PATTERN.match(line)
            table_match = cls.TABLE_LINE_PATTERN.match(line)
            if not (scenario_match or step_match or table_match):
                raise InvalidFeatureFileError('Unable to parse line: ' + line.strip())

            # close and record any open data table
            if (scenario_match or step_match) and current_table:
                current_step.data = ScenarioForest\
                                    .data_table_list_to_dict(current_table)
                current_table = None

            if scenario_match: # Line is scenario
                current_level = int(
                    len((scenario_match)['indentation']) / cls.TAB_SIZE
                )

                current_scenario_vertex = graph.add_vertex()
                current_scenario = Scenario(
                    scenario_match['scenario_name'],
                    current_scenario_vertex
                )
                current_scenario_vertex['scenario'] = current_scenario
                current_scenarios[current_level] = current_scenario
                if current_level > 0:
                    # Connect to parent scenario
                    current_scenario_parent = current_scenarios[current_level-1]
                    graph.add_edge(
                        current_scenario_parent.vertex,
                        current_scenario.vertex
                    )

            elif step_match: # Line is action or assertion
                current_scenario = current_scenarios[current_level]
                new_step = Step.parse(
                    step_match[0].strip(),
                    previous_step=current_step
                )
                current_scenario.steps.append(new_step)
                current_step = new_step

            elif table_match: # Line is table row
                if current_table is None:
                    current_table = []
                row = [s.strip() for s in line.split('|')[1:-1]]
                current_table.append(row)

        # In case the file ends with a data table:
        if current_table:
            current_step.data = ScenarioForest.data_table_list_to_dict(current_table)

        return ScenarioForest(graph)

    @classmethod
    def write_scenario_name_strict(cls, file_handle, scenario):
        """Write formatted scenario name to the end of a 'strict' flat feature file

        Uses both any organizatinal scenarios and the validated scenario

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the scenario

        scenario : Scenario
            Scenario to append to file_handle

        Returns
        -------
        None
        """

        file_handle.write("Scenario: " + scenario.name_with_breadcrumbs() + "\n")

    @classmethod
    def write_scenario_name_relaxed(cls, file_handle, path_scenarios):
        """Write formatted scenario name to the end of a 'relaxed' flat feature file

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the scenario name

        path_scenarios : list
            List of Scenario. Organizational and validated scenarios along the path

        Returns
        -------
        None
        """

        scenario_name = ' > '.join([sc.name for sc in path_scenarios])
        file_handle.write("Scenario: " + scenario_name + "\n")

    @classmethod
    def write_scenario_steps(cls, file_handle, steps, comments=False):
        """Write formatted scenario steps to the end of the flat feature file

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the steps

        steps : list
            List of Step. Steps to append to file_handle

        comments: bool
            Whether or not to write comments

        Returns
        -------
        None
        """

        last_step = None
        for step_num, step in enumerate(steps):
            first_of_type = (
                last_step is None
                or last_step.conjunction != step.conjunction
            )
            file_handle.write(step.format(first_of_type=first_of_type) + "\n")
            if comments and step.comment:
                file_handle.write("# " + step.comment + "\n")
            if step.data:
                ScenarioForest.write_data_table(file_handle, step.data)
            last_step = step

    @classmethod
    def write_data_table(cls, file_handle, data_table):
        """Write formatted data table to the end of the flat feature file

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the data table

        data_table : list
            List of dict

        Returns
        -------
        None
        """

        data = data_table.to_list_of_list()
        col_widths = [max([len(cell) for cell in col]) for col in list(zip(*data))]
        for row in data:
            padded_row = [
                row[col_num].ljust(col_width)
                for col_num, col_width in enumerate(col_widths)
            ]
            file_handle.write("    | {} |\n".format(" | ".join(padded_row)))

    def flatten(self, file_path, mode='strict', comments=False):
        """Write a flat (no indentation) feature file representing the scenario forest

        Parameters
        ----------
        file_path : str
            Path to flat feature file to be written

        mode : {'strict', 'relaxed'}, default='strict'
            Flattening mode. Either 'strict' or 'relaxed'

        comments : str, default = False
            Whether or not to write comments

        Returns
        -------
        None
        """

        if mode == 'strict':
            self.flatten_strict(file_path, comments=comments)
        elif mode == 'relaxed':
            self.flatten_relaxed(file_path, comments=comments)

    def flatten_strict(self, file_path, comments=False):
        """Write a flat (no indentation) feature file representing the forest
        using the 'strict' flattening mode

        The 'strict' flattening mode writes one scenario per vertex in the tree,
        resulting in a feature file with one set of 'When' steps followed by one
        set of 'Then' steps (generally recommended)

        Parameters
        ----------
        file_path : str
            Path to flat feature file

        comments : bool
            Whether or not to write comments

        Returns
        -------
        None
        """

        with open(file_path, 'w') as flat_file:
            for scenario in [
                sc for sc in self.scenarios()
                if not sc.organizational_only()
            ]:
                ScenarioForest.write_scenario_name_strict(flat_file, scenario)

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
                ScenarioForest.write_scenario_steps(
                    flat_file,
                    steps,
                    comments=comments
                )
                flat_file.write("\n")

    def flatten_relaxed(self, file_path, comments=False):
        """Write a flat (no indentation) feature file representing the forest
        using the 'relaxed' flattening mode

        The 'relaxed' flattening mode writes one scenario per leaf vertex in the tree,
        resulting in a feature file with multiple alternating sets of "When" and "Then"
        steps per (generally considered an anti-pattern)

        Parameters
        ----------
        file_path : str
            Path to flat feature file

        comments : bool
            Whether or not to write comments

        Returns
        -------
        None
        """

        with open(file_path, 'w') as flat_file:
            for scenario in self.leaf_scenarios():

                steps=[]
                # organizational and validated scenarios used for naming:
                scenarios_for_naming = []
                for path_scenario in scenario.path_scenarios():
                    steps += path_scenario.prerequisites()
                    steps += path_scenario.actions()
                    if path_scenario.organizational_only():
                        scenarios_for_naming.append(path_scenario)
                    elif not path_scenario.validated:
                        steps += path_scenario.assertions()
                        path_scenario.validated = True
                        scenarios_for_naming.append(path_scenario)

                ScenarioForest.write_scenario_name_relaxed(
                    flat_file,
                    scenarios_for_naming
                )
                ScenarioForest.write_scenario_steps(
                    flat_file,
                    steps,
                    comments=comments
                )
                flat_file.write("\n")

    def find(self, *scenario_names):
        """Find a scenario by the names of all scenarios along the path
        from a root scenario to the destination scenario

        Parameters
        ----------
        scenario_names : list[str]
            List of scenario names

        Returns
        -------
        Scenario
            The found scenario
        """

        scenario = next(
            sc for sc in self.root_scenarios()
            if sc.name == scenario_names[0]
        )
        for scenario_name in scenario_names[1:]:
            scenario = next(
                vt['scenario'] for vt in scenario.vertex.successors()
                if vt['scenario'].name == scenario_name
            )

        return scenario

    def scenarios(self):
        """Return all scenarios

        Returns
        -------
        list
            list[Scenario]. All scenarios
        """

        return [vx['scenario'] for vx in self.graph.vs]

    def root_scenarios(self):
        """Return the root scenarios (scenarios with vertices without incoming edges)

        Returns
        -------
        list
            list[Scenario]. All root scenarios
        """
        return [vx['scenario'] for vx in self.graph.vs if vx.indegree() == 0]

    def leaf_scenarios(self):
        """Return the leaf scenarios (scenarios with vertices without outgoing edges)

        Returns
        -------
        list
            list[Scenario]. All leaf scenarios
        """
        return [vx['scenario'] for vx in self.graph.vs if vx.outdegree() == 0]
