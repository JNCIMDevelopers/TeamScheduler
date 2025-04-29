# Standard Library Imports
from datetime import date, timedelta
from typing import Optional

# Local Imports
from .eligibility_rule import EligibilityRule
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.role import Role


class RoleCapabilityRule(EligibilityRule):
    """
    Rule to check if a person is capable of fulfilling the role based on their assigned roles.
    """

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        return role in person.roles


class OnLeaveRule(EligibilityRule):
    """
    Rule to check if a person is on leave.
    """

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        return not person.on_leave


class BlockoutDateRule(EligibilityRule):
    """
    Rule to check if a person has blocked out the event date.
    """

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        return event_date not in person.blockout_dates


class PreachingDateRule(EligibilityRule):
    """
    Rule to check if a person is scheduled to preach on the event date.
    """

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        return event_date not in person.preaching_dates


class RoleTimeWindowRule(EligibilityRule):
    """
    Rule to enforce time windows between consecutive role assignments.
    """

    WORSHIP_LEADER_ROLE_TIME_WINDOW = timedelta(weeks=4)
    SUNDAY_SCHOOL_TEACHER_ROLE_TIME_WINDOW = timedelta(weeks=4)
    EMCEE_ROLE_TIME_WINDOW = timedelta(weeks=2)

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        time_window = None
        if role == Role.WORSHIPLEADER:
            time_window = self.WORSHIP_LEADER_ROLE_TIME_WINDOW
        elif role == Role.SUNDAYSCHOOLTEACHER:
            time_window = self.SUNDAY_SCHOOL_TEACHER_ROLE_TIME_WINDOW
        elif role == Role.EMCEE:
            time_window = self.EMCEE_ROLE_TIME_WINDOW
        else:
            return True

        last_assigned_date = person.last_assigned_dates[role]

        return (
            last_assigned_date is None or event_date - last_assigned_date > time_window
        )


class ConsecutiveAssignmentLimitRule(EligibilityRule):
    """
    Rule to limit consecutive assignments for a person.
    """

    CONSECUTIVE_ASSIGNMENTS_LIMIT = 3

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        # Calculate the start date of the time window
        time_window = timedelta(weeks=self.CONSECUTIVE_ASSIGNMENTS_LIMIT)
        past_reference_date = event_date - time_window

        # Get all assigned dates within time window
        all_dates = person.assigned_dates + person.preaching_dates
        dates_within_time_window = [
            date for date in all_dates if past_reference_date <= date <= event_date
        ]

        return len(dates_within_time_window) < self.CONSECUTIVE_ASSIGNMENTS_LIMIT


class ConsecutiveRoleAssignmentLimitRule(EligibilityRule):
    """
    Rule to limit consecutive assignments of the same person for a specific role.
    """

    def __init__(self, assignment_limit: int):
        self.assignment_limit = assignment_limit
        self.time_window = timedelta(weeks=assignment_limit)

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        # Get all assigned dates for the person within the time window
        past_assigned_dates = [
            assigned_date
            for assigned_date in person.role_assigned_dates[role]
            if event_date - assigned_date <= self.time_window
        ]

        return len(past_assigned_dates) < self.assignment_limit


class WorshipLeaderTeachingRule(EligibilityRule):
    """
    Rule to prevent a worship leader from teaching on the same date.
    """

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        if role == Role.WORSHIPLEADER:
            return event_date not in person.teaching_dates
        return True


class WorshipLeaderPreachingConflictRule(EligibilityRule):
    """
    Rule to prevent a worship leader from being assigned when they are scheduled to preach within a specific time window.
    """

    PREACHING_TIME_WINDOW = timedelta(weeks=1)

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        if role == Role.WORSHIPLEADER:
            next_date = person.get_next_preaching_date(event_date)

            # Check if the next preaching date is within the preaching time window
            return bool(
                next_date is None or next_date - event_date > self.PREACHING_TIME_WINDOW
            )
        return True


class LuluEmceeRule(EligibilityRule):
    """
    Special rule: Assign Lulu for the EMCEE role only when Pastor Edmund is preaching.
    """

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        if person.name == "Lulu" and role == Role.EMCEE:
            return preacher is not None and preacher.name == "Edmund"
        return True


class GeeWorshipLeaderRule(EligibilityRule):
    """
    Special rule: Prevent Gee from being assigned as worship leader when Kris is preaching.
    """

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        if person.name == "Gee" and role == Role.WORSHIPLEADER:
            return preacher is None or preacher.name != "Kris"
        return True
