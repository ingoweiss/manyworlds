"""Defines the DataTable and DataTableRow classes"""

import re
from typing import Optional

class DataTableRow:
    """A Gherkin data table row"""

    values : list[str]
    comment : Optional[str]

    def __init__(self, values : list[str], comment : Optional[str] = None):
        """Constructor method
        
        Parameters
        ----------
        values : list[str]
            The header row

        comment : str
            Comment (optional)
        """

        self.values = values
        self.comment = comment


class DataTable:
    """A Gherkin data table"""

    TABLE_ROW_PATTERN = re.compile(
        "(?P<table_row>\| ([^|]* +\|)+)( # (?P<comment>.+))?"
    )
    """Pipe-delimited list of values, followed by an optional comment"""

    header_row : DataTableRow
    rows : list[DataTableRow]

    def __init__(self, header_row : DataTableRow) -> None:
        """Constructor method

        Parameters
        ----------
        header_row : DataTableRow
            The header row
        """

        self.header_row = header_row
        self.rows = []

    def to_list_of_list(self) -> list[list[str]]:
        """Returns a list of list of str representation of itself

        First row is header row

        Returns
        -------
        list[list[str]]
            The list of list of str representation of itself
        """

        return [self.header_row.values] + [row.values for row in self.rows]

    def to_list_of_dict(self) -> list[dict]:
        """Returns a list of dict representation of itself

        Returns
        -------
        list[dict]
            The list of dict representation of itself
        """

        return [dict(zip(self.header_row.values, row.values)) for row in self.rows]

    def to_list(self) -> list[DataTableRow]:
        """Returns a list of DataTableRow representation of itself

        Returns
        -------
        list[DataTableRow]
            The list of DataTableRow representation of itself
        """

        return [self.header_row] + self.rows

    @classmethod
    def parse_line(cls, line : str) -> Optional[DataTableRow]:
        """Parses a pipe delimited data table line into a DataTableRow

        Parameters
        ----------
        line : str
            A pipe delimited data table line

        Returns
        -------
        DataTableRow
        """

        match = DataTable.TABLE_ROW_PATTERN.match(line)

        if match:
            values = [s.strip() for s in match.group("table_row").split("|")[1:-1]]
            comment = match.group("comment")
            return DataTableRow(values, comment)
        else:
            return None
