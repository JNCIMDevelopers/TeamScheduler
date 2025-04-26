# Standard Library Imports
from datetime import date

# Local Imports
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role
from schedule_builder.models.person_status import PersonStatus
from schedule_builder.eligibility.rules import ConsecutiveAssignmentLimitRule


class PersonStatusChecker:
    """
    Utility class to check the status of a team member on a given date.
    """

    @staticmethod
    def get_status(person: Person, check_date: date) -> PersonStatus:
        """
        Returns the status of a team member on a specific date.

        Args:
            person (Person): The team member to check.
            check_date (date): The date to check the status for.

        Returns:
            PersonStatus: The status for the given date.
        """
        if person.on_leave:
            return PersonStatus.ONLEAVE
        elif check_date in person.blockout_dates:
            return PersonStatus.BLOCKEDOUT
        elif check_date in person.assigned_dates:
            return PersonStatus.ASSIGNED
        elif check_date in person.preaching_dates:
            return PersonStatus.PREACHING
        elif not ConsecutiveAssignmentLimitRule().is_eligible(
            person=person, role=Role.LYRICS, event_date=check_date
        ):
            return PersonStatus.BREAK
        elif Role.WORSHIPLEADER in person.roles and check_date in person.teaching_dates:
            return PersonStatus.TEACHING
        else:
            return PersonStatus.UNASSIGNED
