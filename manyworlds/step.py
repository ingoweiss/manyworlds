"""Defines the ScenarioForest Class"""
import re

class Step:

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

    def __init__(self, name:str, data:dict=None, comment:str=None) -> None:
        """Constructor method
        """
        self.name = name.strip()
        self.type = type
        self.data = data
        self.comment = comment

    def format(self, first_of_type:bool=True) -> str:
        conjunction = (self.conjunction if first_of_type else ' And')
        return conjunction + ' ' + self.name

    def __str__(self) -> str:
        return "<{}: {}>".format(self.__class__.__name__, (self.name[0].upper() + self.name[1:]))

    def __repr__(self) -> str:
        return self.__str__()

class Prerequisite(Step):
    def __init__(self, name:str, data:dict=None, comment:str=None) -> None:
       self.conjunction = 'Given'
       super().__init__(name, data=data, comment=comment)

class Action(Step):
    def __init__(self, name:str, data:dict=None, comment:str=None) -> None:
       self.conjunction = 'When'
       super().__init__(name, data=data, comment=comment)

class Assertion(Step):
    def __init__(self, name:str, data:dict=None, comment:str=None) -> None:
       self.conjunction = 'Then'
       super().__init__(name, data=data, comment=comment)
