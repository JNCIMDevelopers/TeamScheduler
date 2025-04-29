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

        if not ConsecutiveAssignmentLimitRule().is_eligible(
            person=person, role=Role.LYRICS, event_date=check_date
        ):
            return PersonStatus.BREAK

        if Role.WORSHIPLEADER in person.roles and check_date in person.teaching_dates:
            return PersonStatus.TEACHING

        return PersonStatus.UNASSIGNED
