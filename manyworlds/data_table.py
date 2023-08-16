"""Defines the DataTable class"""
import re

class DataTable:
    """A Gherkin data table"""

    data_table_row_pattern = r'\| ([^|]* +\|)+'

    def __init__(self, header_row):
        """Constructor method

        Parameters
        ----------
        name : str
            The name of the step

        data : list, optional
            list[dict]. List of dict representing a data table

        comment : str, optional
            A comment

        Returns
        ----------
        None
        """
        self.header_row = header_row
        self.rows = []

    def to_list_of_list(self):
        return [self.header_row] + self.rows

    def to_list_of_dict(self):
        return [dict(zip(self.header_row, row)) for row in self.rows]

    @classmethod
    def parse_line(cls, line):
        return [s.strip() for s in line.split('|')[1:-1]]