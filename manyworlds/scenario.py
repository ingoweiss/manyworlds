"""Defines the ScenarioForest Class"""
import re
import igraph as ig

from .step import Step, Prerequisite, Action, Assertion

class Scenario:
    """A BDD Scenario

    :param name: The name of the scenario
    :type name: string
    :param vertex: The iGraph vertex associated with the scenario
    :type name: class: igraph.Vertex
    """

    def __init__(self, name=str, vertex=ig.Vertex) -> None:
        """Constructor method
        """
        self.name = name.strip()
        self.vertex = vertex
        self.graph = vertex.graph
        self.steps = []

    def prerequisites(self) -> list:
        return self.steps_of_class(Prerequisite)

    def actions(self) -> list:
        return self.steps_of_class(Action)

    def assertions(self) -> list:
        return self.steps_of_class(Assertion)

    def steps_of_class(self, step_class:Step) -> list:
        return [st for st in self.steps if type(st) is step_class]

    def __str__(self) -> str:
        return "<Scenario: {} ({} prerequisites, {} actions, {} assertions)>".format(self.name, len(self.prerequisites()), len(self.actions()), len(self.assertions()))

    def __repr__(self) -> str:
        return self.__str__()

    def ancestors(self) -> list:
        ancestors = self.graph.neighborhood(self.vertex, mode='IN', order=1000, mindist=1)
        ancestors.reverse()
        return [vx['scenario'] for vx in self.graph.vs(ancestors)]

    def level(self) -> int:
        return self.graph.neighborhood_size(self.vertex, mode="IN", order=1000)

    def is_breadcrumb(self) -> bool:
        return len(self.assertions()) == 0

    def format(self) -> str:
        breadcrumbs = [sc.name for sc in self.ancestors() if sc.is_breadcrumb()]
        breadcrumbs_string = ''
        if breadcrumbs:
            breadcrumbs_string = ' > '.join(breadcrumbs) + ' > '
        return "Scenario: " + breadcrumbs_string + self.name
