"""Defines the Step Class and subclasses"""
import re

class Step:
    """A BDD scenario step"""

    step_pattern = r'(?P<conjunction>Given|When|Then|And|But) (?P<name>[^#]+)(# (?P<comment>.+))?'
    table_pattern = r'| ([^|]* +|)+'

    @classmethod
    def parse(cls, string:str, previous_step=None) -> None:
        match = re.compile(Step.step_pattern).match(string)
        conjunction = match['conjunction']
        if conjunction in ['And', 'But']:
            conjunction = previous_step.conjunction

        step_class = {
            'Given': Prerequisite,
            'When': Action,
            'Then': Assertion
        }[conjunction]
        return step_class(match['name'], comment=match['comment'])

    def __init__(self, name:str, data:list[dict]=None, comment:str=None) -> None:
        """Constructor method

        Parameters
        ----------
        name : str
            the name of the step

        data : list[dict], optional
            list of dict representing a data table

        comment : str, optional
            a comment
       """
        self.name = name.strip()
        self.type = type
        self.data = data
        self.comment = comment

    def format(self, first_of_type:bool=True) -> str:
        """Return a string representation of the Scenario instance for feature file output

        Returns
        ----------
        str
            string representation of the Scenario instance
        """
        conjunction = (self.conjunction if first_of_type else ' And')
        return conjunction + ' ' + self.name

    def __str__(self) -> str:
        """Return a string representation of the Scenario instance for terminal output

        Returns
        ----------
        str
            string representation of the Scenario instance
        """
        return "<{}: {}>".format(self.__class__.__name__, (self.name[0].upper() + self.name[1:]))

    def __repr__(self) -> str:
        """Return a string representation of the Scenario instance for terminal output

        Returns
        ----------
        str
            string representation of the Scenario instance
        """
        return self.__str__()

class Prerequisite(Step):
    """A BDD scenario prerequisite ("Given") step"""
    def __init__(self, name:str, data:dict=None, comment:str=None) -> None:
       self.conjunction = 'Given'
       super().__init__(name, data=data, comment=comment)

class Action(Step):
    """A BDD scenario action ("When") step"""
    def __init__(self, name:str, data:dict=None, comment:str=None) -> None:
       self.conjunction = 'When'
       super().__init__(name, data=data, comment=comment)

class Assertion(Step):
    """A BDD scenario assertion ("Then") step"""
    def __init__(self, name:str, data:dict=None, comment:str=None) -> None:
       self.conjunction = 'Then'
       super().__init__(name, data=data, comment=comment)
