"""Defines the ScenarioForest Class"""

import re
import igraph as ig  # type: ignore
from typing import Optional, TextIO, Literal, List, Tuple

from .scenario import Scenario
from .step import Step, Prerequisite, Action, Assertion
from .data_table import DataTable, DataTableRow
from .exceptions import InvalidFeatureFileError


class ScenarioForest:
    """A collection of one or more directed trees
    the vertices of which represent BDD scenarios."""

    TAB_SIZE: int = 4
    """
    int

    The number of spaces per indentation level
    """

    FEATURE_PATTERN: re.Pattern = re.compile("^Feature: (?P<feature_name>.*)")
    """
    re.Pattern

    The string "Feature: ", followed by arbitrary string
    """

    graph: ig.Graph
    name: Optional[str]
    description: List[str]

    def __init__(self) -> None:
        """Constructor method"""

        self.graph = ig.Graph(directed=True)
        self.name = None
        self.description = []

    @classmethod
    def split_line(cls, raw_line: str) -> Tuple[int, str]:
        """Splits a raw feature file line into the indentation part and the line part.

        Parameters
        ----------
        raw_line : str
            The raw feature file line including indentation and newline

        Returns
        -------
        tuple[int, str]
            The indentation part and the line part (without newline) as a tuple
        """

        line: str = raw_line.rstrip()
        line_wo_indentation: str = line.lstrip()
        indentation: int = len(line) - len(line_wo_indentation)
        return (indentation, line_wo_indentation)

    def parse_step_line(self, line: str) -> Optional[Step]:
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

        match: Optional[re.Match] = Step.STEP_PATTERN.match(line)
        if match is None:
            return None

        conjunction, name, comment = match.group("conjunction", "name", "comment")

        if conjunction in ["And", "But"]:
            previous_step = self.scenarios()[-1].steps[-1]
            conjunction = previous_step.conjunction

        if conjunction == "Given":
            return Prerequisite(name, comment=comment)
        elif conjunction == "When":
            return Action(name, comment=comment)
        else:  # conjunction == "Then"
            return Assertion(name, comment=comment)

    @classmethod
    def from_file(cls, file_path) -> "ScenarioForest":
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
                if raw_line.strip() == "":
                    continue  # Skip empty lines

                indentation: int
                line: str
                indentation, line = cls.split_line(raw_line)

                # (1) Determine and validate indentation level:
                if indentation % cls.TAB_SIZE == 0:
                    level: int = int(indentation / cls.TAB_SIZE) + 1
                else:
                    raise InvalidFeatureFileError(
                        "Invalid indentation at line {line_no}: {line}".format(
                            line_no=line_no + 1, line=line
                        )
                    )

                # (2) Parse line:

                # Feature line?
                feature_match: Optional[re.Match] = cls.FEATURE_PATTERN.match(line)
                if feature_match is not None:
                    forest.name = feature_match["feature_name"]
                    continue

                # Scenario line?
                scenario_match: Optional[re.Match] = Scenario.SCENARIO_PATTERN.match(line)
                if scenario_match is not None:
                    forest.append_scenario(scenario_match.group("scenario_name"), at_level=level)
                    continue

                # Step line?
                new_step: Optional[Step] = forest.parse_step_line(line)
                if new_step:
                    forest.append_step(new_step, at_level=level)
                    continue

                # Data table line?
                new_data_row: Optional[DataTableRow] = DataTable.parse_line(line)
                if new_data_row:
                    forest.append_data_row(new_data_row, at_level=level)
                    continue

                # Feature description line?
                if forest.name is not None and len(forest.scenarios()) == 0:
                    forest.description.append(line)
                    continue

                # Not a valid line!
                raise InvalidFeatureFileError(
                    "Unable to parse line {line_no}: {line}".format(
                        line_no=line_no + 1, line=line
                    )
                )

        return forest

    def append_scenario(self, scenario_name: str, at_level: int) -> Scenario:
        """Append a scenario to the scenario forest.

        Parameters
        ----------
        scenario : Scenario
            The scenario to append

        at_level : int
            The indentation level of the scenario in the input file.
            Used for indentation validation.
        """

        if at_level > 1:  # Non-root scenario:
            # Find the parent to connect scenario to:
            parent_level: int = at_level - 1
            parent_level_scenarios: List[Scenario] = [
                sc
                for sc in self.scenarios()
                if sc.level() == parent_level and not sc.is_closed()
            ]
            if len(parent_level_scenarios) > 0:
                return Scenario(
                    scenario_name,
                    self.graph,
                    parent_scenario=parent_level_scenarios[-1],
                )
            else:
                raise InvalidFeatureFileError(
                    "Excessive indentation at line: Scenario: {name}".format(
                        name=scenario_name
                    )
                )

        else:  # Root scenario:
            return Scenario(scenario_name, self.graph)

    def append_step(self, step: Step, at_level: int) -> None:
        """Appends a step to the scenario forest.

        Parameters
        ----------
        step : Prerequisite or Action or Assertion
            The Step subclass instance to append

        at_level : int
            The level at which to add the step.
            Used for indentation validation.
        """

        # Ensure the indentation level of the step matches
        # the last scenario indentation level
        last_scenario: Scenario = self.scenarios()[-1]
        if at_level == last_scenario.level():
            last_scenario.steps.append(step)
        else:
            raise InvalidFeatureFileError(
                "Invalid indentation at line: {name}".format(name=step.name)
            )

    def append_data_row(self, data_row: DataTableRow, at_level: int) -> None:
        """Appends a data row to the scenario forest.

        Adds a data table to the last step if necessary
        Otherwise adds row to data table.

        Parameters
        ----------
        data_row : DataTableRow
            The data row to append

        at_level : int
            The level at which to add the data row.
            Used for indentation validation.
        """

        last_step: Step = self.scenarios()[-1].steps[-1]
        if last_step.data:
            # Row is an additional row for an existing table
            last_step.data.rows.append(data_row)
        else:
            # Row is the header row of a new table
            last_step.data = DataTable(data_row)

    @classmethod
    def write_scenario_name(
        cls, file_handle: TextIO, scenarios: List[Scenario]
    ) -> None:
        """Writes formatted scenario name to the end of a "relaxed" flat feature file.

        Parameters
        ----------
        file_handle : TextIO
            The file to which to append the scenario name

        scenarios : List[Scenario]
            Organizational and validated scenarios along the path
        """

        # (1) Group consecutive regular or organizational scenarios:
        groups: List[List[Scenario]] = []

        # Function for determining whether a scenario can be added to a current group:
        def group_available_for_scenario(
            gr: List[List[Scenario]], sc: Scenario
        ) -> bool:
            return (
                len(gr) > 0
                and len(gr[-1]) > 0
                and gr[-1][-1].is_organizational() == sc.is_organizational()
            )

        for sc in scenarios:
            if group_available_for_scenario(groups, sc):
                groups[-1].append(sc)  # add to current group
            else:
                groups.append([sc])  # start new group

        # (2) Format each group to strings:
        group_strings: List[str] = []

        for group in groups:
            if group[-1].is_organizational():
                group_strings.append(
                    "[{}]".format(" / ".join([sc.name for sc in group]))
                )
            else:
                group_strings.append(" > ".join([sc.name for sc in group]))

        # (3) Assemble and write name:
        file_handle.write(
            "Scenario: {scenario_name}\n".format(scenario_name=" ".join(group_strings))
        )

    @classmethod
    def write_scenario_steps(
        cls, file_handle: TextIO, steps: List[Step], comments: bool = False
    ) -> None:
        """Writes formatted scenario steps to the end of the flat feature file.

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the steps

        steps : List[Step]
            Steps to append to file_handle

        comments: bool
            Whether or not to write comments
        """

        last_step: Optional[Step] = None
        for step_num, step in enumerate(steps):
            first_of_type = (
                last_step is None or last_step.conjunction != step.conjunction
            )
            file_handle.write(step.format(first_of_type=first_of_type) + "\n")
            if comments and step.comment:
                file_handle.write("# {comment}\n".format(comment=step.comment))
            if step.data:
                ScenarioForest.write_data_table(file_handle, step.data, comments)
            last_step = step

    @classmethod
    def write_data_table(
        cls, file_handle: TextIO, data_table: DataTable, comments: bool = False
    ) -> None:
        """Writes formatted data table to the end of the flat feature file.

        Parameters
        ----------
        file_handle : io.TextIOWrapper
            The file to which to append the data table

        data_table : DataTable
            A data table

        comments : bool
            Whether or not to write comments
        """

        # Determine column widths to accommodate all values:
        col_widths: List[int] = [
            max([len(cell) for cell in col])
            for col in list(zip(*data_table.to_list_of_list()))
        ]

        for row in data_table.to_list():
            # pad values with spaces to column width:
            padded_row: List[str] = [
                row.values[col_num].ljust(col_width)
                for col_num, col_width in enumerate(col_widths)
            ]

            # add column enclosing pipes:
            table_row_string: str = "    | {columns} |".format(
                columns=" | ".join(padded_row)
            )

            # add comments:
            if comments and row.comment:
                table_row_string += " # {comment}".format(comment=row.comment)

            # write line:
            file_handle.write(table_row_string + "\n")

    def flatten(
        self,
        file_path: str,
        mode: Literal["strict", "relaxed"] = "strict",
        comments: bool = False,
    ) -> None:
        """Writes a flat (no indentation) feature file representing the scenario forest.

        Parameters
        ----------
        file_path : str
            Path to flat feature file to be written

        mode : {"strict", "relaxed"}, default="strict"
            Flattening mode. Either "strict" or "relaxed"

        comments : bool, default = False
            Whether or not to write comments
        """

        if mode == "strict":
            self.flatten_strict(file_path, comments=comments)
        elif mode == "relaxed":
            self.flatten_relaxed(file_path, comments=comments)

    def flatten_strict(self, file_path: str, comments: bool = False) -> None:
        """Write. a flat (no indentation) feature file representing the forest
        using the "strict" flattening mode.

        The "strict" flattening mode writes one scenario per vertex in the tree,
        resulting in a feature file with one set of "When" steps followed by one
        set of "Then" steps (generally recommended).

        Parameters
        ----------
        file_path : str
            Path to flat feature file

        comments : bool, default = False
            Whether or not to write comments
        """

        with open(file_path, "w") as flat_file:
            for scenario in [
                sc for sc in self.scenarios() if not sc.is_organizational()
            ]:
                # Scenario name:
                scenarios_for_naming: List[Scenario] = [
                    sc
                    for sc in scenario.path_scenarios()
                    if sc.is_organizational() or sc == scenario
                ]
                ScenarioForest.write_scenario_name(flat_file, scenarios_for_naming)

                ancestor_scenarios = scenario.ancestors()
                steps: List[Step] = []
                # collect prerequisites from all scenarios along the path
                steps += [st for sc in ancestor_scenarios for st in sc.prerequisites()]
                # collect actions from all scenarios along the path
                steps += [st for sc in ancestor_scenarios for st in sc.actions()]
                # add all steps from the destination scenario only
                steps += scenario.steps

                # Write steps:
                ScenarioForest.write_scenario_steps(flat_file, steps, comments=comments)
                flat_file.write("\n")  # Empty line to separate scenarios

    def flatten_relaxed(self, file_path: str, comments: bool = False) -> None:
        """Writes a flat (no indentation) feature file representing the forest
        using the "relaxed" flattening mode.

        The "relaxed" flattening mode writes one scenario per leaf vertex in the tree,
        resulting in a feature file with multiple consecutive sets of "When" and "Then"
        steps per scenario (generally considered an anti-pattern).

        Parameters
        ----------
        file_path : str
            Path to flat feature file

        comments : bool, default = False
            Whether or not to write comments
        """

        with open(file_path, "w") as flat_file:
            for scenario in self.leaf_scenarios():
                steps: List[Step] = []
                # organizational and validated scenarios used for naming:
                scenarios_for_naming: List[Scenario] = []
                for path_scenario in scenario.path_scenarios():
                    steps += path_scenario.prerequisites()
                    steps += path_scenario.actions()
                    if path_scenario.is_organizational():
                        scenarios_for_naming.append(path_scenario)
                    elif not path_scenario.validated:
                        steps += path_scenario.assertions()
                        path_scenario.validated = True
                        scenarios_for_naming.append(path_scenario)

                ScenarioForest.write_scenario_name(flat_file, scenarios_for_naming)
                # Write steps:
                ScenarioForest.write_scenario_steps(flat_file, steps, comments=comments)
                flat_file.write("\n")  # Empty line to separate scenarios

    def find(self, *scenario_names: List[str]) -> Optional[Scenario]:
        """Finds and returns a scenario by the names of all scenarios along the path
        from a root scenario to the destination scenario.

        Used in tests only

        Parameters
        ----------
        scenario_names : List[str]
            List of scenario names

        Returns
        -------
        Scenario or None
            The found scenario, or None if none found
        """

        # Root scenario:
        scenario: Optional[Scenario] = next(
            (sc for sc in self.root_scenarios() if sc.name == scenario_names[0]), None
        )
        if scenario is None:
            return None

        # Root descendant scenarios:
        for scenario_name in scenario_names[1:]:
            scenario = next(
                (
                    vt["scenario"]
                    for vt in scenario.vertex.successors()
                    if vt["scenario"].name == scenario_name
                ),
                None,
            )
            if scenario is None:
                return None

        return scenario

    def scenarios(self) -> List[Scenario]:
        """Returns all scenarios

        Returns
        -------
        List[Scenario]
            All scenarios in index order
        """

        return [vx["scenario"] for vx in self.graph.vs]

    def root_scenarios(self) -> List[Scenario]:
        """Returns the root scenarios (scenarios with vertices without incoming edges).

        Returns
        -------
        List[Scenario]
            All root scenarios in index order
        """
        return [vx["scenario"] for vx in self.graph.vs if vx.indegree() == 0]

    def leaf_scenarios(self) -> List[Scenario]:
        """Returns the leaf scenarios (scenarios with vertices without outgoing edges).

        Returns
        -------
        List[Scenario]
            All leaf scenarios in index order
        """
        return [vx["scenario"] for vx in self.graph.vs if vx.outdegree() == 0]
