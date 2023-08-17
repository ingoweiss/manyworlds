"""Defines the ScenarioForest Class"""
import re
import igraph as ig

from .scenario   import Scenario
from .step       import Step, Prerequisite, Action, Assertion
from .data_table import DataTable
from .exceptions import InvalidFeatureFileError

class ScenarioForest:
    """A collection of one or more directed trees
    the vertices of which represent BDD scenarios."""

    TAB_SIZE = 4
    LINE_PATTERN = re.compile('(?P<indentation> *)(?P<line>.*)\n')

    def __init__(self):
        """Constructor method"""

        self.graph = ig.Graph(directed=True)

    @classmethod
    def split_line(cls, raw_line):
        """Splits a raw feature file line into the indentation part and the line part.

        Parameters
        ----------
        raw_line : str
            The raw feature file line including indentation and newline

        Returns
        -------
        (str, str)
            The indentation part and the line part (without newline) as a tuple
        """

        match = cls.LINE_PATTERN.match(raw_line)
        return (match['indentation'], match['line'])

    def parse_line(self, line):
        """Parses a feature file line into an appropriate instance.

        Parameters
        ----------
        line : str
            The feature file line (without indentation and newline)

        Returns
        -------
        Scenario or Prerequisite or Action or Assertion or list
            An instance representing the line
        """

        if re.compile(Scenario.scenario_pattern).match(line):
            return Scenario.parse_line(line)
        elif re.compile(Step.step_pattern).match(line):
            return self.parse_step_line(line)
        elif re.compile(DataTable.data_table_row_pattern).match(line):
            return DataTable.parse_line(line)
        else:
            return None

    def parse_step_line(self, line):
        """Parses a feature file step line into the appropriate
        Step subclass instance.

        If the line begins with "And" then the step type is determined
        by the type of the last step.

        Parameters
        ----------
        line : str
            The step line (without indentation and newline)

        Returns
        -------
        Prerequisite or Action or Assertion
            An instance of a Step subclass
        """

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
        """Parses an indented feature file into a ScenarioForest instance.

        Parameters
        ----------
        file_path : str
            The path to the feature file

        Returns
        -------
        ScenarioForest
            A new ScenarioForest instance
        """

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
                    raise InvalidFeatureFileError(
                        "Invalid indentation at line {}: {}".format(line_no+1, line)
                    )

                # determine what kind of line this is:
                parsed_line = forest.parse_line(line)
                # Scenario line:
                if isinstance(parsed_line, Scenario):
                    forest.append_scenario(parsed_line, at_level=level)
                # Step line:
                elif isinstance(parsed_line, Step):
                    forest.append_step(parsed_line, at_level=level)
                # Data table line:
                elif isinstance(parsed_line, list):
                    forest.append_data_row(parsed_line, at_level=level)
                # Not a valid line:
                else:
                    raise InvalidFeatureFileError(
                        "Unable to parse line {}: {}".format(line_no+1, line)
                    )

        return forest

    def append_scenario(self, scenario, at_level):
        """Append a scenario to the scenario forest.

        Parameters
        ----------
        scenario : Scenario
            The scenario to append

        at_level : int
            The level at which to add the scenario.
            Used for indentation validation.
        """

        if at_level > 1: # Non-root scenario:

            # Find the parent to connect scenario to:
            parent_level = at_level-1
            scenarios_at_parent_level = [
                sc for sc in self.scenarios()
                if sc.level() == parent_level
                and not sc.is_closed()
            ]
            if not scenarios_at_parent_level:
                raise InvalidFeatureFileError(
                    "Excessive indentation at line: Scenario: {}".format(scenario.name)
                )
            else:
                last_scenario_at_parent_level = scenarios_at_parent_level[-1]

            # add vertex to scenario:
            vertex = self.graph.add_vertex()
            vertex['scenario'] = scenario
            scenario.vertex = vertex
            scenario.graph = vertex.graph

            # connect scenario to parent:
            self.graph.add_edge(
                last_scenario_at_parent_level.vertex,
                scenario.vertex
            )
        else: # root scenario:

            # add vertex to scenario:
            vertex = self.graph.add_vertex()
            vertex['scenario'] = scenario
            scenario.vertex = vertex
            scenario.graph = vertex.graph

    def append_step(self, step, at_level):
        """Appends a step to the scenario forest.

        Parameters
        ----------
        step : Prerequisite or Action or Assertion
            The Step subclass instance to append

        at_level : int
            The level at which to add the step.
            Used for indentation validation.
        """

        last_scenario = self.scenarios()[-1]
        last_scenario.steps.append(step)

    def append_data_row(self, data_row, at_level):
        """Appends a data row to the scenario forest.

        Adds a data table to the last step if necessary
        Otherwise adds row to data table.

        Parameters
        ----------
        data_row : list[str]
            The data row to append

        at_level : int
            The level at which to add the data row.
            Used for indentation validation.
        """

        # TODO: Extract methods 'last_scenario' and 'last_step'
        last_step = self.scenarios()[-1].steps[-1]
        if last_step.data:
            # row is an additional row for an existing table
            last_step.data.rows.append(data_row)
        else:
            # row is the header row of a new table
            last_step.data = DataTable(data_row)

    @classmethod
    def write_scenario_name_strict(cls, file_handle, scenario):
        """Writes formatted scenario name to the end of a 'strict' flat feature file.

        Uses both any organizatinal scenarios and the validated scenario.

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the scenario

        scenario : Scenario
            Scenario to append to file_handle
        """

        file_handle.write("Scenario: " + scenario.name_with_breadcrumbs() + "\n")

    @classmethod
    def write_scenario_name_relaxed(cls, file_handle, path_scenarios):
        """Writes formatted scenario name to the end of a 'relaxed' flat feature file.

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the scenario name

        path_scenarios : list[Scenario]
            Organizational and validated scenarios along the path
        """

        scenario_name = ' > '.join([sc.name for sc in path_scenarios])
        file_handle.write("Scenario: " + scenario_name + "\n")

    @classmethod
    def write_scenario_steps(cls, file_handle, steps, comments=False):
        """Writes formatted scenario steps to the end of the flat feature file.

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the steps

        steps : list[Step]
            Steps to append to file_handle

        comments: bool
            Whether or not to write comments
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
        """Writes formatted data table to the end of the flat feature file.

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the data table

        data_table : list[dict]
            List of dict representation of the data table
        """

        # TODO: Use the DataTable instance as parameter instead
        data = data_table.to_list_of_list()
        col_widths = [max([len(cell) for cell in col]) for col in list(zip(*data))]
        for row in data:
            padded_row = [
                row[col_num].ljust(col_width)
                for col_num, col_width in enumerate(col_widths)
            ]
            file_handle.write("    | {} |\n".format(" | ".join(padded_row)))

    def flatten(self, file_path, mode='strict', comments=False):
        """Writes a flat (no indentation) feature file representing the scenario forest.

        Parameters
        ----------
        file_path : str
            Path to flat feature file to be written

        mode : {'strict', 'relaxed'}, default='strict'
            Flattening mode. Either 'strict' or 'relaxed'

        comments : bool, default = False
            Whether or not to write comments
        """

        if mode == 'strict':
            self.flatten_strict(file_path, comments=comments)
        elif mode == 'relaxed':
            self.flatten_relaxed(file_path, comments=comments)

    def flatten_strict(self, file_path, comments=False):
        """Write. a flat (no indentation) feature file representing the forest
        using the 'strict' flattening mode.

        The 'strict' flattening mode writes one scenario per vertex in the tree,
        resulting in a feature file with one set of 'When' steps followed by one
        set of 'Then' steps (generally recommended).

        Parameters
        ----------
        file_path : str
            Path to flat feature file

        comments : bool, default = False
            Whether or not to write comments
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
        """Writes a flat (no indentation) feature file representing the forest
        using the 'relaxed' flattening mode.

        The 'relaxed' flattening mode writes one scenario per leaf vertex in the tree,
        resulting in a feature file with multiple consecutive sets of "When" and "Then"
        steps per scenario (generally considered an anti-pattern).

        Parameters
        ----------
        file_path : str
            Path to flat feature file

        comments : bool, default = False
            Whether or not to write comments
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
        """Finds and returns a scenario by the names of all scenarios along the path
        from a root scenario to the destination scenario.

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

        return scenario # TODO: Return None if none found

    def scenarios(self):
        """Returns all scenarios

        Returns
        -------
        list[Scenario]
            All scenarios in index order
        """

        return [vx['scenario'] for vx in self.graph.vs]

    def root_scenarios(self):
        """Returns the root scenarios (scenarios with vertices without incoming edges).

        Returns
        -------
        list[Scenario]
            All root scenarios in index order
        """
        return [vx['scenario'] for vx in self.graph.vs if vx.indegree() == 0]

    def leaf_scenarios(self):
        """Returns the leaf scenarios (scenarios with vertices without outgoing edges).

        Returns
        -------
        list[Scenario]
            All leaf scenarios in index order
        """
        return [vx['scenario'] for vx in self.graph.vs if vx.outdegree() == 0]
