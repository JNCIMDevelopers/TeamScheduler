# Standard Library Imports
from datetime import date, timedelta
from typing import List

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

    Class-Level Constants:
        PREACHING_TIME_WINDOW (timedelta): Time window for assigning a preaching role (default: 1 week).
        CONSECUTIVE_ASSIGNMENTS_LIMIT (int): Limit for consecutive assigned event dates (default: 3).

    Methods:
        assign_event(date): Assigns the person to an event on the given date.
        get_next_preaching_date(reference_date): Returns the next preaching date after the given reference date.
        was_not_assigned_too_recently_to_role(role, date): Checks if the person was not assigned to a role too recently.
        is_unavailable_due_to_preaching(reference_date): Checks if the person is unavailable due to an upcoming preaching date.
        assigned_too_many_times_recently(reference_date): Checks if the person has been assigned too many times recently.
    """
    PREACHING_TIME_WINDOW = timedelta(weeks=1)
    CONSECUTIVE_ASSIGNMENTS_LIMIT = 3

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
        self.last_assigned_dates = {role: None for role in roles}
        self.role_assigned_dates = {role: [] for role in roles}

    def assign_event(self, date: date, role: Role) -> None:
        """
        Assigns the person to an event on the given date.

        Args:
            date (date): The date of the event.
        """
        self.assigned_dates.append(date)
        self.last_assigned_dates[role] = date
        self.role_assigned_dates[role].append(date)

    def get_next_preaching_date(self, reference_date: date) -> date:
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

    def is_unavailable_due_to_preaching(self, reference_date: date) -> bool:
        """
        Checks if the person is unavailable due to an upcoming preaching date.

        Args:
            reference_date (date): The reference date to check.

        Returns:
            bool: True if the person is unavailable due to preaching, False otherwise.
        """
        next_date = self.get_next_preaching_date(reference_date)
        return bool(next_date and next_date - reference_date <= Person.PREACHING_TIME_WINDOW)

    def assigned_too_many_times_recently(self, reference_date: date) -> bool:
        """
        Checks if the person has been assigned too many times recently.

        Args:
            reference_date (date): The reference date to check.

        Returns:
            bool: True if the person has been assigned too many times recently, False otherwise.
        """
        # Calculate the start date of the time window
        time_window = timedelta(weeks=Person.CONSECUTIVE_ASSIGNMENTS_LIMIT)
        past_reference_date = reference_date - time_window

        # Get all assigned dates within time window
        all_dates = self.assigned_dates + self.preaching_dates
        dates_within_time_window = [
            date for date in all_dates if past_reference_date <= date <= reference_date
        ]

        return len(dates_within_time_window) >= Person.CONSECUTIVE_ASSIGNMENTS_LIMIT

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
