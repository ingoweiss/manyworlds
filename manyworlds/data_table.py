"""Defines the DataTable and DataTableRow classes"""

import re
from typing import Optional, List


class DataTableRow:
    """A Gherkin data table row"""

    values: List[str]
    comment: Optional[str]

    def __init__(self, values: List[str], comment: Optional[str] = None):
        """Constructor method

        Parameters
        ----------
        values : List[str]
            The header row

        comment : str
            Comment (optional)
        """

        self.values = values
        self.comment = comment


class DataTable:
    """A Gherkin data table"""

    TABLE_ROW_PATTERN = re.compile(
        r"""
        ^                                  # start of line
        (?P<table_row>\| (?:[^|]+[ ]+\|)+) # pipe-delimited list of values
        (?:[ ]+\#[ ](?P<comment>.+))?      # optional comment
        $                                  # end of line
        """,
        re.VERBOSE,
    )
    """
    re.Pattern

    Pattern describing a Gherkin data table row
    followed by an optional comment
    """

    header_row: DataTableRow
    rows: List[DataTableRow]

    def __init__(self, header_row: DataTableRow) -> None:
        """Constructor method

        Parameters
        ----------
        header_row : DataTableRow
            The header row
        """

        self.header_row = header_row
        self.rows = []

    def to_list_of_list(self) -> List[List[str]]:
        """Returns a list of list of str representation of itself

        First row is header row

        Returns
        -------
        List[List[str]]
            The list of list of str representation of itself
        """

        return [self.header_row.values] + [row.values for row in self.rows]

    def to_list_of_dict(self) -> List[dict]:
        """Returns a list of dict representation of itself

        Returns
        -------
        List[dict]
            The list of dict representation of itself
        """

        return [dict(zip(self.header_row.values, row.values)) for row in self.rows]

    def to_list(self) -> List[DataTableRow]:
        """Returns a list of DataTableRow representation of itself

        Returns
        -------
        List[DataTableRow]
            The list of DataTableRow representation of itself
        """

        return [self.header_row] + self.rows

    @classmethod
    def parse_line(cls, line: str) -> Optional[DataTableRow]:
        """Parses a pipe delimited data table line into a DataTableRow

        Parameters
        ----------
        line : str
            A pipe delimited data table line

        Returns
        -------
        DataTableRow
        """

        match: Optional[re.Match] = DataTable.TABLE_ROW_PATTERN.match(line)

        if match:
            values = [s.strip() for s in match.group("table_row").split("|")[1:-1]]
            comment = match.group("comment")
            return DataTableRow(values, comment)
        else:
            return None
