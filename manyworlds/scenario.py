"""Defines the Scenario Class"""
from __future__ import annotations # in order to support type[] annotations in Python 3.8

import re
import igraph as ig  # type: ignore
from typing import Optional, Union

from .step import Step, Prerequisite, Action, Assertion


class Scenario:
    """A BDD Scenario"""

    SCENARIO_PATTERN : re.Pattern = re.compile("Scenario: (?P<scenario_name>.*)")
    """
    re.Pattern

    The string "Scenario: ", followed by arbitrary string
    """

    name : str
    graph: ig.Graph
    vertex : ig.Vertex
    steps : list[Step]
    _validated : bool

    def __init__(self,
            name : str,
            graph : ig.Graph,
            parent_scenario : Optional['Scenario'] = None
        ) -> None:
        """Constructor method

        Parameters
        ----------
        name : str
            The name of the scenario

        graph : igraph.Graph
            The graph

        parent_scenario: Scenario (optional)
            The parent scenario to connect the new scenario to
        """

        self.name = name.strip()
        self.graph = graph
        self.vertex = graph.add_vertex()
        self.vertex["scenario"] = self
        self.steps = []
        self._validated = False

        if parent_scenario is not None:
            self.graph.add_edge(
                parent_scenario.vertex,
                self.vertex
            )

    @property
    def validated(self) -> bool:
        """The "validated" property

        Used to keep track of which scenarios had their assertions written
        to an output scenario already so that assertions are not run multiple
        times.

        Returns
        -------
        bool
            Whether or not this scenario has been validated
        """
        return self._validated

    @validated.setter
    def validated(self, value : bool) -> None:
        """The validated property setter

        Parameters
        ----------
        value : bool
            Whether or not this scenario has been validated

        """
        self._validated = value

    def prerequisites(self) -> list[Step]:
        """Returns all steps of type Prerequisite

        Returns
        -------
        list[Prerequisite]
            List of steps of type Prerequisite
        """

        return self.steps_of_type(Prerequisite)

    def actions(self) -> list[Step]:
        """Returns all steps of type Action

        Returns
        -------
        list[Action]
            List of steps of type Action
        """

        return self.steps_of_type(Action)

    def assertions(self) -> list[Step]:
        """Returns all steps of type Assertion

        Returns
        ----------
        list
            list[Assertion]
                List of steps of type Assertion
        """

        return self.steps_of_type(Assertion)

    def steps_of_type(self,
            step_type : Union[type[Prerequisite], type[Action], type[Assertion]]
        ) -> list[Step]:
        """Returns all steps of the passed in type

        Parameters
        ----------
        step_class : {Prerequisite, Action, Assertion}
            A step subclass

        Returns
        -------
        list[Step]
            All steps of the passed in type
        """

        return [st for st in self.steps if type(st) is step_type]

    def __str__(self) -> str:
        """Returns a string representation of the Scenario instance for terminal output.

        Returns
        -------
        str
            String representation of the Scenario instance
        """

        return "<Scenario: {} ({} prerequisites, {} actions, {} assertions)>".format(
            self.name,
            len(self.prerequisites()),
            len(self.actions()),
            len(self.assertions()),
        )

    def __repr__(self) -> str:
        """Returns a string representation of the Scenario instance for terminal output.

        Returns
        -------
        str
            String representation of the Scenario instance
        """

        return self.__str__()

    def ancestors(self) -> list["Scenario"]:
        """Returns the scenario"s ancestors, starting with a root scenario

        Returns
        -------
        list[Scenario]
            List of scenarios
        """

        ancestors = self.graph.neighborhood(
            self.vertex,
            mode="IN",
            order=1000,
            mindist=1,
        )
        ancestors.reverse()
        return [vx["scenario"] for vx in self.graph.vs(ancestors)]

    def path_scenarios(self) -> list["Scenario"]:
        """Returns the complete scenario path from the root scenario to
        (and including) self.

        Returns
        -------
        list[Scenario]
            List of scenarios. The last scenario is self
        """

        return self.ancestors() + [self]

    def level(self) -> int:
        """Returns the scenario"s level in the scenario tree.

        Root scenario =  Level 1

        Returns
        -------
        int
            The scenario"s level
        """

        return self.graph.neighborhood_size(self.vertex, mode="IN", order=1000)

    def is_organizational(self) -> bool:
        """Returns whether the scenario is an "organizational" scenario.

        "Organizational" scenarios are used for grouping only.
        They do not have any assertions.

        Returns
        ----------
        bool
            Whether the scenario is an "organizational" scenario
        """

        return len(self.assertions()) == 0

    def index(self) -> Optional[int]:
        """Returns the "index" of the scenario.

        The scenario"s vertical position in the feature file.

        Returns
        ----------
        int
            Index of self
        """

        return self.vertex.index

    def is_closed(self) -> bool:
        """Returns whether or not the scenario is "closed".

        A scenario is "closed" if additional child scenarios cannot
        be added which is the case when there is a "later" (higher index)
        scenario with a lower indentation level in the feature file.

        Returns
        ----------
        bool
            Whether or not the scenario is "closed"
        """

        later_scenario_at_same_or_lower_indentation_level = next(
            (
                vx
                for vx in self.graph.vs()
                if vx.index > self.index()
                and self.graph.neighborhood_size(vx, mode="IN", order=1000)
                <= self.level()
            ),
            None,
        )
        return later_scenario_at_same_or_lower_indentation_level is not None
