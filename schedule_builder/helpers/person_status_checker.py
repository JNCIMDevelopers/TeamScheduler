# Standard Library Imports
from datetime import date

# Local Imports
from config import CONSECUTIVE_ASSIGNMENTS_LIMIT
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role
from schedule_builder.models.person_status import PersonStatus
from schedule_builder.util.assignment_checker import (
    has_exceeded_consecutive_assignments,
)


class PersonStatusChecker:
    """
    Utility class to check the status of a team member on a given date.
    """

    @staticmethod
    def get_status(person: Person, check_date: date) -> PersonStatus:
        """
        Returns the status of a team member on a specific date.

        Args:
            person (Person): The team member whose status is being checked.
            check_date (date): The date for which to check the status.

        Returns:
            PersonStatus: The status of the team member on the given date.
        """
        if person.on_leave:
            return PersonStatus.ONLEAVE

        if check_date in person.blockout_dates:
            return PersonStatus.BLOCKEDOUT

        if check_date in person.assigned_dates:
            return PersonStatus.ASSIGNED

        if check_date in person.preaching_dates:
            return PersonStatus.PREACHING

        if has_exceeded_consecutive_assignments(
            assigned_dates=person.assigned_dates,
            preaching_dates=person.preaching_dates,
            reference_date=check_date,
            limit=CONSECUTIVE_ASSIGNMENTS_LIMIT,
        ):
            return PersonStatus.BREAK

        if Role.WORSHIPLEADER in person.roles and check_date in person.teaching_dates:
            return PersonStatus.TEACHING

        return PersonStatus.UNASSIGNED
