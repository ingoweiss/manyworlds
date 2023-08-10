"""Defines the Scenario Class"""
import re
import igraph as ig

from .step import Step, Prerequisite, Action, Assertion

class Scenario:
    """A BDD Scenario"""

    def __init__(self, name, vertex):
        """Constructor method

        Parameters
        ----------
        name : str
            The name of the scenario

        vertex : igraph.Vertex
            The vertex representing the scenario's position in a scenario tree
       """

        self.name = name.strip()
        self.vertex = vertex
        self.graph = vertex.graph
        self.steps = []

    def prerequisites(self):
        """Return all steps of type Prerequisite

        Returns
        ----------
        list
            list[Prerequisite]. List of steps of type Prerequisite
        """

        return self.steps_of_class(Prerequisite)

    def actions(self):
        """Return all steps of type Action

        Returns
        ----------
        list
            list[Action]. List of steps of type Action
        """

        return self.steps_of_class(Action)

    def assertions(self):
        """Return all steps of type Assertion

        Returns
        ----------
        list
            list[Assertion]. List of steps of type Assertion
        """

        return self.steps_of_class(Assertion)

    def steps_of_class(self, step_class):
        """Return all steps of the supplied type

        Parameters
        ----------
        step_class : {Prerequisite, Action, Assertion}
            A step subclass

        Returns
        ----------
        list
            list[Step]. List of steps of type Assertion
        """

        return [st for st in self.steps if type(st) is step_class]

    def __str__(self):
        """Return a string representation of the Scenario instance for terminal output

        Returns
        ----------
        str
            String representation of the Scenario instance
        """

        return "<Scenario: {} ({} prerequisites, {} actions, {} assertions)>".format(self.name, len(self.prerequisites()), len(self.actions()), len(self.assertions()))

    def __repr__(self):
        """Return a string representation of the Scenario instance for terminal output

        Returns
        ----------
        str
            String representation of the Scenario instance
        """

        return self.__str__()

    def ancestors(self):
        """Return the scenario's ancestors, starting with the root scenario

        Returns
        ----------
        list
            list[Scenario]. List of scenarios
        """

        ancestors = self.graph.neighborhood(self.vertex, mode='IN', order=1000, mindist=1)
        ancestors.reverse()
        return [vx['scenario'] for vx in self.graph.vs(ancestors)]

    def level(self):
        """Return the scenario's level in the scenario tree.

        Level 1 = root scenario

        Returns
        ----------
        int
            The scenario's level
        """

        return self.graph.neighborhood_size(self.vertex, mode="IN", order=1000)

    def is_breadcrumb(self):
        """Return whether the scenario is an 'organizational' scenario used for grouping only

        Returns
        ----------
        bool
        """

        return len(self.assertions()) == 0

    def format(self):
        """Return a string representation of the Scenario instance for feature file output

        Returns
        ----------
        str
            String representation of the Scenario instance
        """

        breadcrumbs = [sc.name for sc in self.ancestors() if sc.is_breadcrumb()]
        breadcrumbs_string = ''
        if breadcrumbs:
            breadcrumbs_string = ' > '.join(breadcrumbs) + ' > '
        return "Scenario: " + breadcrumbs_string + self.name
