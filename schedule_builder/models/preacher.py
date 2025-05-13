from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class Preacher:
    """
    A class to represent a preacher and their associated information.
    """

    name: str
    graphics_support: str
    dates: List[date] = field(default_factory=list)

    def __str__(self) -> str:
        """
        Returns a string representation of the Preacher, including their name, graphics support, and preaching dates.
        """
        preaching_dates_str = ", ".join(
            [date.strftime("%B-%d-%Y") for date in self.dates]
        )

        return f"""Name: {self.name}
            Graphics Support: {self.graphics_support}
            Preaching Dates: {preaching_dates_str}"""
