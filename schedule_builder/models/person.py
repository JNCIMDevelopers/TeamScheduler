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
        WORSHIP_LEADER_ROLE_TIME_WINDOW (timedelta): Time window for assigning a worship leader role (default: 4 weeks).
        SUNDAY_SCHOOL_TEACHER_ROLE_TIME_WINDOW (timedelta): Time window for assigning a Sunday school teacher role (default: 4 weeks).
        EMCEE_ROLE_TIME_WINDOW (timedelta): Time window for assigning an emcee role (default: 2 weeks).
        PREACHING_TIME_WINDOW (timedelta): Time window for assigning a preaching role (default: 1 week).
        CONSECUTIVE_ASSIGNMENTS_LIMIT (int): Limit for consecutive assigned event dates (default: 3).

    Methods:
        assign_event(date): Assigns the person to an event on the given date.
        get_next_preaching_date(reference_date): Returns the next preaching date after the given reference date.
        was_not_assigned_too_recently_to_role(role, date): Checks if the person was not assigned to a role too recently.
        is_unavailable_due_to_preaching(reference_date): Checks if the person is unavailable due to an upcoming preaching date.
        assigned_too_many_times_recently(reference_date): Checks if the person has been assigned too many times recently.
    """
    WORSHIP_LEADER_ROLE_TIME_WINDOW = timedelta(weeks=4)
    SUNDAY_SCHOOL_TEACHER_ROLE_TIME_WINDOW = timedelta(weeks=4)
    EMCEE_ROLE_TIME_WINDOW = timedelta(weeks=2)
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

    def assign_event(self, date: date, role: Role) -> None:
        """
        Assigns the person to an event on the given date.

        Args:
            date (date): The date of the event.
        """
        self.assigned_dates.append(date)
        self.last_assigned_dates[role] = date

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

        future_dates = [
            preaching_date
            for preaching_date in self.preaching_dates
            if preaching_date >= reference_date
        ]
        if not future_dates:
            return None

        return min(future_dates, key=lambda x: abs(x - reference_date))

    def was_not_assigned_too_recently_to_role(self, role: Role, date: date) -> bool:
        """
        Checks if the person was not assigned to a role too recently.

        Args:
            role (Role): The role to check.
            date (date): The date of the event.

        Returns:
            bool: True if the person was not assigned to the role too recently, False otherwise.
        """
        if role == Role.WORSHIPLEADER:
            return (
                self.last_assigned_dates[role] is None
                or date - self.last_assigned_dates[role] > Person.WORSHIP_LEADER_ROLE_TIME_WINDOW
            )
        elif role == Role.SUNDAYSCHOOLTEACHER:
            return (
                self.last_assigned_dates[role] is None
                or date - self.last_assigned_dates[role] > Person.SUNDAY_SCHOOL_TEACHER_ROLE_TIME_WINDOW
            )
        elif role == Role.EMCEE:
            return (
                self.last_assigned_dates[role] is None
                or date - self.last_assigned_dates[role] > Person.EMCEE_ROLE_TIME_WINDOW
            )
        return True

    def is_unavailable_due_to_preaching(self, reference_date: date) -> bool:
        """
        Checks if the person is unavailable due to an upcoming preaching date.

        Args:
            reference_date (date): The reference date to check.

        Returns:
            bool: True if the person is unavailable due to preaching, False otherwise.
        """
        if not self.preaching_dates:
            return False

        # Unavailable if date is too close to next preaching date based on time window
        next_date = self.get_next_preaching_date(reference_date)
        if next_date and next_date - reference_date <= Person.PREACHING_TIME_WINDOW:
            return True

        return False

    def assigned_too_many_times_recently(self, reference_date: date) -> bool:
        """
        Checks if the person has been assigned too many times recently.

        Args:
            reference_date (date): The reference date to check.

        Returns:
            bool: True if the person has been assigned too many times recently, False otherwise.
        """
        if not self.assigned_dates and not self.preaching_dates:
            return False

        # Check if total assigned/preaching dates is less than the limit
        if (len(self.assigned_dates or []) + len(self.preaching_dates or []) < Person.CONSECUTIVE_ASSIGNMENTS_LIMIT):
            return False

        # Calculate the past date outside of the consecutive assignment limit
        past_reference_date = reference_date - timedelta(weeks=Person.CONSECUTIVE_ASSIGNMENTS_LIMIT)

        # Count dates assigned within past time window
        all_dates = set(self.assigned_dates + self.preaching_dates)
        dates_between_count = sum(
            1 for date in all_dates if past_reference_date <= date <= reference_date
        )

        return dates_between_count >= Person.CONSECUTIVE_ASSIGNMENTS_LIMIT

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
