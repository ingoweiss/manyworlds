"""Defines the Scenario Class"""
# needed to support "type[]" class type annotations in Python 3.8:
from __future__ import annotations

import re
import igraph as ig  # type: ignore
from typing import Optional, Union, List

from .step import Step, Prerequisite, Action, Assertion


class Scenario:
    """A BDD Scenario"""

    SCENARIO_PATTERN: re.Pattern = re.compile("^Scenario: (?P<scenario_name>.*)")
    """
    re.Pattern

    The string "Scenario: ", followed by arbitrary string
    """

    name: str
    graph: ig.Graph
    vertex: ig.Vertex
    steps: List[Step]
    _validated: bool

    def __init__(
        self, name: str, graph: ig.Graph, parent_scenario: Optional["Scenario"] = None
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
            self.graph.add_edge(parent_scenario.vertex, self.vertex)

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
    def validated(self, value: bool) -> None:
        """The validated property setter

        Parameters
        ----------
        value : bool
            Whether or not this scenario has been validated

        """

        self._validated = value

    def prerequisites(self) -> List[Step]:
        """Returns all steps of type Prerequisite

        Returns
        -------
        List[Prerequisite]
            List of steps of type Prerequisite
        """

        return self.steps_of_type(Prerequisite)

    def actions(self) -> List[Step]:
        """Returns all steps of type Action

        Returns
        -------
        List[Action]
            List of steps of type Action
        """

        return self.steps_of_type(Action)

    def assertions(self) -> List[Step]:
        """Returns all steps of type Assertion

        Returns
        ----------
        list
            List[Assertion]
                List of steps of type Assertion
        """

        return self.steps_of_type(Assertion)

    def steps_of_type(
        self, step_type: Union[type[Prerequisite], type[Action], type[Assertion]]
    ) -> List[Step]:
        """Returns all steps of the passed in type

        Parameters
        ----------
        step_class : {Prerequisite, Action, Assertion}
            A step subclass

        Returns
        -------
        List[Step]
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

    def ancestors(self) -> List["Scenario"]:
        """Returns the scenario's ancestors, starting with a root scenario

        Returns
        -------
        List[Scenario]
            List of scenarios
        """

        ancestors: List[ig.Vertex] = self.graph.neighborhood(
            self.vertex,
            mode="IN",
            order=1000,
            mindist=1,
        )
        ancestors.reverse()
        return [vx["scenario"] for vx in self.graph.vs(ancestors)]

    def parent(self) -> Optional[Scenario]:
        """Returns the scenario's parent scenario, if one exists

        Returns
        -------
        Scenario, optional
            The parent scenario
        """

        parents: List[ig.Vertex] = self.graph.neighborhood(
            self.vertex, mode="IN", order=1, mindist=1
        )
        if len(parents) == 1:
            return self.graph.vs[parents[0]]["scenario"]
        else:
            return None

    def children(self) -> List[Scenario]:
        """Returns the scenario's child scenarios

        Returns
        -------
        List[Scenario]
            The child scenarios
        """

        children: List[ig.Vertex] = self.graph.neighborhood(
            self.vertex, mode="OUT", order=1, mindist=1
        )
        return [vx["scenario"] for vx in self.graph.vs(children)]

    def siblings(self) -> List[Scenario]:
        """Returns the scenario's sibling scenarios

        The scenario's parent's children (including self)

        Returns
        -------
        List[Scenario]
            The sibling scenarios
        """

        parent: Optional[Scenario] = self.parent()
        if parent is not None:
            return parent.children()
        else:
            return [vx["scenario"] for vx in self.graph.vs if vx.indegree() == 0]
            # TODO: This duplicates the implementation of
            # ScenarioForest#root_scenarios() but Scenario does not currently
            # have access to its feature. Might want to change that

    def path_scenarios(self) -> List["Scenario"]:
        """Returns the complete scenario path from the root scenario to
        (and including) self.

        Returns
        -------
        List[Scenario]
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

        return self.vertex.index  # TODO: start at index 1 (instead of 0)

    def is_closed(self) -> bool:
        """Returns whether or not the scenario is "closed".

        A scenario is "closed" if additional child scenarios cannot be added
        which is the case when there is a "later" (higher index) scenario
        with a lower or equal indentation level in the feature file.

        Returns
        ----------
        bool
            Whether or not the scenario is "closed"
        """

        # Later scenario with lower or equal indentation level:
        closing_scenario: Optional[Scenario] = next(
            (
                vx
                for vx in self.graph.vs()
                if vx.index > self.index()
                and self.graph.neighborhood_size(vx, mode="IN", order=1000)
                <= self.level()
            ),
            None,
        )
        return closing_scenario is not None
