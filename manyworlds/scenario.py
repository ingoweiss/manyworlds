"""Defines the Scenario Class"""

from .step import Prerequisite, Action, Assertion

class Scenario:
    """A BDD Scenario"""

    scenario_pattern = r'Scenario: (?P<scenario_name>.*)'

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
        self._validated = False
    
    @property
    def validated(self):
        """The validated property"""
        return self._validated

    @validated.setter
    def validated(self, value):
        """The validated property setter"""
        self._validated = value

    def prerequisites(self):
        """Return all steps of type Prerequisite

        Returns
        ----------
        list
            list[Prerequisite]. List of steps of type Prerequisite
        """

        return self.steps_of_type(Prerequisite)

    def actions(self):
        """Return all steps of type Action

        Returns
        ----------
        list
            list[Action]. List of steps of type Action
        """

        return self.steps_of_type(Action)

    def assertions(self):
        """Return all steps of type Assertion

        Returns
        ----------
        list
            list[Assertion]. List of steps of type Assertion
        """

        return self.steps_of_type(Assertion)

    def steps_of_type(self, step_type):
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

        return [st for st in self.steps if type(st) is step_type]

    def __str__(self):
        """Return a string representation of the Scenario instance for terminal output

        Returns
        ----------
        str
            String representation of the Scenario instance
        """

        return "<Scenario: {} ({} prerequisites, {} actions, {} assertions)>".format(
            self.name,
            len(self.prerequisites()),
            len(self.actions()),
            len(self.assertions())
        )

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

        ancestors = self.graph.neighborhood(
            self.vertex,
            mode='IN',
            order=1000,
            mindist=1
        )
        ancestors.reverse()
        return [vx['scenario'] for vx in self.graph.vs(ancestors)]

    def path_scenarios(self):
        """Return the complete scenario path from the root scenario to self

        Returns
        ----------
        list
            list[Scenario]. List of scenarios
        """

        return self.ancestors() + [self]

    def organizational_only_ancestors(self):
        """Return the scenario's ancestors that are organizational only

        Returns
        ----------
        list
            list[Scenario]. List of scenarios
        """

        return [sc for sc in self.ancestors() if sc.organizational_only()]

    def level(self):
        """Return the scenario's level in the scenario tree.

        Level 1 = root scenario

        Returns
        ----------
        int
            The scenario's level
        """

        return self.graph.neighborhood_size(self.vertex, mode="IN", order=1000)

    def organizational_only(self):
        """Return whether the scenario is an 'organizational' scenario

        'Organizational' scenarios are used for grouping only.
        They do not have any assertions

        Returns
        ----------
        bool
        """

        return len(self.assertions()) == 0

    def name_with_breadcrumbs(self):
        """Return a name of the Scenario prepended with 'breadcrumbs'

        Breadcrumbs are the scenario's organizational ancestor names joined by ' > '

        Returns
        ----------
        str
            String representation of the Scenario instance
        """

        breadcrumbs = ''.join(
            [sc.name + ' > ' for sc in self.organizational_only_ancestors()]
        )
        return breadcrumbs + self.name
