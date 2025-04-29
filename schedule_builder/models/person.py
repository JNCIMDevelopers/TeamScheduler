# Standard Library Imports
from datetime import date
from typing import List, Optional

# Local Imports
from ..models.role import Role


class Person:
    """
    A class to represent a person and their associated roles and availability information.
    """

    def __init__(
        self,
        name: str,
        roles: List[Role],
        blockout_dates: Optional[List[date]] = None,
        preaching_dates: Optional[List[date]] = None,
        teaching_dates: Optional[List[date]] = None,
        on_leave: bool = False,
    ):
        """
        Initializes the Person with a name, roles, and optionally blockout dates, preaching dates, teaching dates, and leave status.
        """
        self.name: str = name
        self.roles: List[Role] = roles
        self.blockout_dates: List[date] = blockout_dates if blockout_dates else []
        self.preaching_dates: List[date] = preaching_dates if preaching_dates else []
        self.teaching_dates: List[date] = teaching_dates if teaching_dates else []
        self.on_leave = on_leave
        self.assigned_dates: List[date] = []
        self.last_assigned_dates: dict[Role, Optional[date]] = {
            role: None for role in roles
        }
        self.role_assigned_dates: dict[Role, List[date]] = {role: [] for role in roles}

    def assign_event(self, event_date: date, role: Role) -> None:
        """
        Assigns the person to an event on the given date for a specified role.

        Args:
            event_date (date): The date of the event.
            role (Role): The role to assign to the person.
        """
        self.assigned_dates.append(event_date)
        self.last_assigned_dates[role] = event_date
        self.role_assigned_dates[role].append(event_date)

    def get_next_preaching_date(self, reference_date: date) -> Optional[date]:
        """
        Returns the next preaching date on or after the given reference date.

        Args:
            reference_date (date): The reference date to find the next preaching date.

        Returns:
            date: The next preaching date or None if no future preaching dates exist.
        """
        if not self.preaching_dates:
            return None

        future_dates = [d for d in self.preaching_dates if d >= reference_date]
        return min(future_dates, default=None)

    def __str__(self) -> str:
        """
        Returns a string representation of the person, including their roles and availability information.

        Returns:
            str: A formatted string of the person's details (name, roles, dates, leave status).
        """
        roles_str = ", ".join(self.roles)
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
