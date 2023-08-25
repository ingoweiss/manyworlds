"""Defines the Step Class and subclasses"""

import re
from typing import Optional, Union, Literal

from .data_table import DataTable


class Step:
    """A BDD scenario step"""

    STEP_PATTERN: re.Pattern = re.compile(
        "(?P<conjunction>Given|When|Then|And|But) (?P<name>[^#]+)(# (?P<comment>.+))?"
    )

    name: str
    conjunction: Literal["Given", "When", "Then"]
    data: Optional[DataTable]
    comment: Optional[str]

    """
    re.Pattern

    A conjunction ("Given", "When", ...), followed by an arbitrary string,
    followed by an optional comment
    """

    def __init__(
        self, name: str, data: Optional[DataTable] = None, comment: Optional[str] = None
    ) -> None:
        """Constructor method

        Parameters
        ----------
        name : str
            The name of the step

        data : DataTable, optional
            A data table

        comment : str, optional
            A comment
        """

        self.name = name.strip()
        self.data = data
        self.comment = comment

    def format(self, first_of_type: bool = True) -> str:
        """Returns a string representation of the Step instance
        for feature file output.

        Uses "And" as a conjunction if the step is not the first
        of its type.

        Parameters
        ----------
        first_of_type : bool
            Whether or not the step is the first of it"s type

        Returns
        -------
        str
            String representation of the Step instance
        """

        return "{conjunction} {name}".format(
            conjunction=self.conjunction if first_of_type else " And", name=self.name
        )

    def __str__(self) -> str:
        """Return. a string representation of the Step instance
        for terminal output.

        Returns
        -------
        str
            String representation of the Step instance
        """

        return "<{type}: {name}>".format(
            type=self.__class__.__name__, name=(self.name[0].upper() + self.name[1:])
        )

    def __repr__(self) -> str:
        """Return a string representation of the Step instance
        for terminal output.

        Returns
        -------
        str
            String representation of the Step instance
        """

        return self.__str__()


class Prerequisite(Step):
    """A BDD scenario prerequisite ("Given") step"""

    def __init__(
        self, name: str, data: Optional[DataTable] = None, comment: Optional[str] = None
    ) -> None:
        self.conjunction = "Given"
        super().__init__(name, data=data, comment=comment)


class Action(Step):
    """A BDD scenario action ("When") step"""

    def __init__(
        self, name: str, data: Optional[DataTable] = None, comment: Optional[str] = None
    ) -> None:
        self.conjunction = "When"
        super().__init__(name, data=data, comment=comment)


class Assertion(Step):
    """A BDD scenario assertion ("Then") step"""

    def __init__(
        self, name: str, data: Optional[DataTable] = None, comment: Optional[str] = None
    ) -> None:
        self.conjunction = "Then"
        super().__init__(name, data=data, comment=comment)
