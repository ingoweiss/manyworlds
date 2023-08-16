"""Defines the DataTable class"""

class DataTable:
    """A Gherkin data table"""

    data_table_row_pattern = r'\| ([^|]* +\|)+'

    def __init__(self, header_row):
        """Constructor method

        Parameters
        ----------
        header_row : list of str
            The header row
        """

        self.header_row = header_row
        self.rows = []

    def to_list_of_list(self):
        """Return a list of list of str representation of itself

        Returns
        -------
        list of list of str
            The list of list of str representation of itself
        """

        return [self.header_row] + self.rows

    def to_list_of_dict(self):
        """Return a list of dict representation of itself

        Returns
        -------
        list of dict
            The list of dict representation of itself
        """

        return [dict(zip(self.header_row, row)) for row in self.rows]

    @classmethod
    def parse_line(cls, line):
        """Parse a pipe delimited data table line into a list of str

        Parameters
        ----------
        line : str
            A pipe delimited data table line

        Returns
        -------
        list of str
        """

        return [s.strip() for s in line.split('|')[1:-1]]