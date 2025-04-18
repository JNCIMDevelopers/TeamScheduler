from datetime import date
from typing import List


class Preacher:
    """
    A class to represent a preacher and their associated information.

    Attributes:
        name (str): The name of the preacher.
        graphics_support (str): The graphics support person associated with the preacher.
        dates (List[date]): A list of dates when the preacher is scheduled to preach.
    """

    def __init__(self, name: str, graphics_support: str, dates: List[date] = []):
        """
        Initializes the Preacher with a name, graphics support, and optionally a list of preaching dates.

        Args:
            name (str): The name of the preacher.
            graphics_support (str): The graphics support person or team associated with the preacher.
            dates (List[date], optional): A list of dates when the preacher is scheduled to preach. Defaults to an empty list.
        """
        self.name: str = name
        self.graphics_support: str = graphics_support
        self.dates: List[date] = dates

    def __str__(self) -> str:
        """
        Returns a string representation of the Preacher, including their name, graphics support, and preaching dates.

        Returns:
            str: A string representation of the Preacher.
        """
        preaching_dates_str = ", ".join(
            [date.strftime("%B-%d-%Y") for date in self.dates]
        )

        return f"""Name: {self.name}
            Graphics Support: {self.graphics_support}
            Preaching Dates: {preaching_dates_str}"""
