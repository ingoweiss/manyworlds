"""Defines the DataTable and DataTableRow classes"""

import re


class DataTable:
    """A Gherkin data table"""

    TABLE_ROW_PATTERN = re.compile(
        "(?P<table_row>\| ([^|]* +\|)+)( # (?P<comment>.+))?"
    )
    """Pipe-delimited list of values, followed by an optional comment"""

    def __init__(self, header_row):
        """Constructor method

        Parameters
        ----------
        header_row : list[str]
            The header row
        """

        self.header_row = header_row
        self.rows = []

    def to_list_of_list(self):
        """Returns a list of list of str representation of itself

        First row is header row

        Returns
        -------
        list[list[str]]
            The list of list of str representation of itself
        """

        return [self.header_row.values] + [row.values for row in self.rows]

    def to_list_of_dict(self):
        """Returns a list of dict representation of itself

        Returns
        -------
        list[dict]
            The list of dict representation of itself
        """

        return [dict(zip(self.header_row.values, row.values)) for row in self.rows]

    def to_list(self):
        """Returns a list of DataTableRow representation of itself

        Returns
        -------
        list[DataTableRow]
            The list of DataTableRow representation of itself
        """

        return [self.header_row] + self.rows

    @classmethod
    def parse_line(cls, line):
        """Parses a pipe delimited data table line into a list of str

        Parameters
        ----------
        line : str
            A pipe delimited data table line

        Returns
        -------
        list[str]
        """
        match = DataTable.TABLE_ROW_PATTERN.match(line)
        values = [s.strip() for s in match["table_row"].split("|")[1:-1]]
        comment = match["comment"]
        return DataTableRow(values, comment)


class DataTableRow:
    """A Gherkin data table row"""

    def __init__(self, values, comment=None):
        self.values = values
        self.comment = comment
