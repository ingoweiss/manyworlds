"""Defines the Scenario Class"""
import re
import igraph as ig

from .step import Step, Prerequisite, Action, Assertion

class Scenario:
    """A BDD Scenario

    :param name: The name of the scenario
    :type name: string
    :param vertex: The iGraph vertex associated with the scenario
    :type vertex: class: igraph.Vertex
    """

    def __init__(self, name:str, vertex:ig.Vertex) -> None:
        """Constructor method

        Parameters
        ----------
        name : str
            the name of the scenario

        vertex : igraph.Vertex
            the vertex representing the scenario's position in a scenario tree
       """
        self.name = name.strip()
        self.vertex = vertex
        self.graph = vertex.graph
        self.steps = []

    def prerequisites(self) -> list[Prerequisite]:
        """Return all steps of type Prerequisite

        Returns
        ----------
        list[Prerequisite]
            list of steps of type Prerequisite
        """
        return self.steps_of_class(Prerequisite)

    def actions(self) -> list[Action]:
        """Return all steps of type Action

        Returns
        ----------
        list[Action]
            list of steps of type Action
        """
        return self.steps_of_class(Action)

    def assertions(self) -> list[Assertion]:
        """Return all steps of type Assertion

        Returns
        ----------
        list[Assertion]
            list of steps of type Assertion
        """
        return self.steps_of_class(Assertion)

    def steps_of_class(self, step_class:Step) -> list[Step]:
        """Return all steps of the supplied type

        Parameters
        ----------
        step_class : {Prerequisite, Action, Assertion}
            a step subclass

        Returns
        ----------
        list[Step]
            list of steps of type Assertion
        """
        return [st for st in self.steps if type(st) is step_class]

    def __str__(self) -> str:
        """Return a string representation of the Scenario instance for terminal output

        Returns
        ----------
        str
            string representation of the Scenario instance
        """
        return "<Scenario: {} ({} prerequisites, {} actions, {} assertions)>".format(self.name, len(self.prerequisites()), len(self.actions()), len(self.assertions()))

    def __repr__(self) -> str:
        """Return a string representation of the Scenario instance for terminal output

        Returns
        ----------
        str
            string representation of the Scenario instance
        """
        return self.__str__()

    def ancestors(self) -> list:
        """Return the scenario's ancestors, starting with a root scenario

        Returns
        ----------
        list[Scenario]
            list of scenarios
        """
        ancestors = self.graph.neighborhood(self.vertex, mode='IN', order=1000, mindist=1)
        ancestors.reverse()
        return [vx['scenario'] for vx in self.graph.vs(ancestors)]

    def level(self) -> int:
        """Return the scenario's level in the scenario tree, with 1 meaning root

        Returns
        ----------
        int
            the scenario's level
        """
        return self.graph.neighborhood_size(self.vertex, mode="IN", order=1000)

    def is_breadcrumb(self) -> bool:
        """Return whether the scenario is an 'organizational' scenario used for grouping only

        Returns
        ----------
        bool
        """
        return len(self.assertions()) == 0

    def format(self) -> str:
        """Return a string representation of the Scenario instance for feature file output

        Returns
        ----------
        str
            string representation of the Scenario instance
        """
        breadcrumbs = [sc.name for sc in self.ancestors() if sc.is_breadcrumb()]
        breadcrumbs_string = ''
        if breadcrumbs:
            breadcrumbs_string = ' > '.join(breadcrumbs) + ' > '
        return "Scenario: " + breadcrumbs_string + self.name
