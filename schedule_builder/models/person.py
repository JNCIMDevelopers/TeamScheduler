# Standard Library Imports
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

# Local Imports
from ..models.role import Role


@dataclass
class Person:
    """
    A class to represent a person and their associated roles and availability information.
    """

    name: str
    roles: List[Role]
    blockout_dates: List[date] = field(default_factory=list)
    preaching_dates: List[date] = field(default_factory=list)
    teaching_dates: List[date] = field(default_factory=list)
    on_leave: bool = False

    assigned_dates: List[date] = field(default_factory=list, init=False)
    last_assigned_dates: dict = field(default_factory=dict, init=False)
    role_assigned_dates: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        """
        Initializes the `last_assigned_dates` and `role_assigned_dates` attributes.

        `last_assigned_dates` is a dictionary mapping roles to `None`, and
        `role_assigned_dates` is a dictionary mapping roles to empty lists.
        """
        self.last_assigned_dates = {role: None for role in self.roles}
        self.role_assigned_dates = {role: [] for role in self.roles}

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
