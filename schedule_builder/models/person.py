# Standard Library Imports
from datetime import date
from typing import List, Optional

# Local Imports
from ..models.role import Role


class Person:
    """
    A class to represent a person and their associated roles and availability information.

    Attributes:
        name (str): The name of the person.
        roles (List[Role]): The roles that the person can perform.
        blockout_dates (List[date]): The dates when the person is unavailable.
        preaching_dates (List[date]): The dates when the person is scheduled to preach.
        teaching_dates (List[date]): The dates when the person is scheduled to teach.
        on_leave (bool): Indicates if the person is on leave.
        assigned_dates (List[date]): The dates when the person has been assigned to an event.
        last_assigned_dates (dict): A dictionary mapping each role to the last date the person was assigned to that role.

    Methods:
        assign_event(date): Assigns the person to an event on the given date.
        get_next_preaching_date(reference_date): Returns the next preaching date after the given reference date.
    """

    def __init__(
        self,
        name: str,
        roles: List[Role],
        blockout_dates: List[date] = [],
        preaching_dates: List[date] = [],
        teaching_dates: List[date] = [],
        on_leave: bool = False,
    ):
        """
        Initializes the Person with a name, roles, and optionally blockout dates, preaching dates, teaching dates, and leave status.

        Args:
            name (str): The name of the person.
            roles (List[Role]): The roles that the person can perform.
            blockout_dates (List[date], optional): The dates when the person is unavailable. Defaults to an empty list.
            preaching_dates (List[date], optional): The dates when the person is scheduled to preach. Defaults to an empty list.
            teaching_dates (List[date], optional): The dates when the person is scheduled to teach. Defaults to an empty list.
            on_leave (bool, optional): Indicates if the person is on leave. Defaults to False.
        """
        self.name: str = name
        self.roles: List[Role] = roles
        self.blockout_dates: List[date] = blockout_dates
        self.preaching_dates: List[date] = preaching_dates
        self.teaching_dates: List[date] = teaching_dates
        self.on_leave = on_leave
        self.assigned_dates: List[date] = []
        self.last_assigned_dates: dict[Role, Optional[date]] = {role: None for role in roles}
        self.role_assigned_dates: dict[Role, List[date]] = {role: [] for role in roles}

    def assign_event(self, date: date, role: Role) -> None:
        """
        Assigns the person to an event on the given date.

        Args:
            date (date): The date of the event.
        """
        self.assigned_dates.append(date)
        self.last_assigned_dates[role] = date
        self.role_assigned_dates[role].append(date)

    def get_next_preaching_date(self, reference_date: date) -> Optional[date]:
        """
        Returns the next preaching date on or after the given reference date.

        Args:
            reference_date (date): The reference date to find the next preaching date.

        Returns:
            date: The next preaching date, or None if there are no future preaching dates.
        """
        if not self.preaching_dates:
            return None

        future_dates = [d for d in self.preaching_dates if d >= reference_date]
        return min(future_dates, default=None)

    def __str__(self) -> str:
        """
        Returns a string representation of the Person, including their roles and availability information.

        Returns:
            str: A string representation of the Person.
        """
        roles_str = ", ".join([role for role in self.roles])
        blockout_dates_str = ", ".join(
            [date.strftime("%B-%d-%Y") for date in self.blockout_dates]
        )
        preaching_dates_str = ", ".join(
            [date.strftime("%B-%d-%Y") for date in self.preaching_dates]
        )
        teaching_dates_str = ", ".join(
            [date.strftime("%B-%d-%Y") for date in self.teaching_dates]
        )
        assigned_dates_str = ", ".join(
            [date.strftime("%B-%d-%Y") for date in self.assigned_dates]
        )
        on_leave_str = "Yes" if self.on_leave else "No"

        return f"""Name: {self.name}
            Roles: {roles_str}
            Blockout Dates: {blockout_dates_str}
            Preaching Dates: {preaching_dates_str}
            Teaching Dates: {teaching_dates_str}
            On Leave: {on_leave_str}
            Assigned Dates: {assigned_dates_str}"""
