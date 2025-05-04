# Standard Library Imports
from datetime import timedelta

# Local Imports
from config import (
    WORSHIP_LEADER_ROLE_TIME_WINDOW_WEEKS,
    SUNDAY_SCHOOL_TEACHER_ROLE_TIME_WINDOW_WEEKS,
    EMCEE_ROLE_TIME_WINDOW_WEEKS,
    PREACHING_TIME_WINDOW_WEEKS,
    CONSECUTIVE_ASSIGNMENTS_LIMIT,
)
from .eligibility_rule import EligibilityRule
from ..models.event import Event
from ..models.person import Person
from ..models.role import Role
from ..util.assignment_checker import has_exceeded_consecutive_assignments


class RoleCapabilityRule(EligibilityRule):
    """
    Rule to check if a person is capable of fulfilling the role based on their assigned roles.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        return role in person.roles


class OnLeaveRule(EligibilityRule):
    """
    Rule to check if a person is on leave.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        return not person.on_leave


class BlockoutDateRule(EligibilityRule):
    """
    Rule to check if a person has blocked out the event date.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        return event.date not in person.blockout_dates


class PreachingDateRule(EligibilityRule):
    """
    Rule to check if a person is scheduled to preach on the event date.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        return event.date not in person.preaching_dates


class RoleTimeWindowRule(EligibilityRule):
    """
    Rule to enforce time windows between consecutive role assignments.
    """

    WORSHIP_LEADER_ROLE_TIME_WINDOW = timedelta(
        weeks=WORSHIP_LEADER_ROLE_TIME_WINDOW_WEEKS
    )
    SUNDAY_SCHOOL_TEACHER_ROLE_TIME_WINDOW = timedelta(
        weeks=SUNDAY_SCHOOL_TEACHER_ROLE_TIME_WINDOW_WEEKS
    )
    EMCEE_ROLE_TIME_WINDOW = timedelta(weeks=EMCEE_ROLE_TIME_WINDOW_WEEKS)

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
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
            last_assigned_date is None or event.date - last_assigned_date > time_window
        )


class ConsecutiveAssignmentLimitRule(EligibilityRule):
    """
    Rule to limit consecutive assignments for a person.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        return not has_exceeded_consecutive_assignments(
            assigned_dates=person.assigned_dates,
            preaching_dates=person.preaching_dates,
            reference_date=event.date,
            limit=CONSECUTIVE_ASSIGNMENTS_LIMIT,
        )


class ConsecutiveRoleAssignmentLimitRule(EligibilityRule):
    """
    Rule to limit consecutive assignments of the same person for every role.
    """

    def __init__(self, assignment_limit: int):
        self.assignment_limit = assignment_limit
        self.time_window = timedelta(weeks=assignment_limit)

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        # Get all assigned dates for the person within the time window
        past_assigned_dates = [
            assigned_date
            for assigned_date in person.role_assigned_dates[role]
            if event.date - assigned_date <= self.time_window
        ]

        return len(past_assigned_dates) < self.assignment_limit


class WorshipLeaderTeachingRule(EligibilityRule):
    """
    Rule to prevent a worship leader from teaching on the same date.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if role == Role.WORSHIPLEADER:
            return event.date not in person.teaching_dates
        return True


class WorshipLeaderPreachingConflictRule(EligibilityRule):
    """
    Rule to prevent a worship leader from being assigned when they are scheduled to preach within a specific time window.
    """

    PREACHING_TIME_WINDOW = timedelta(weeks=PREACHING_TIME_WINDOW_WEEKS)

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if role == Role.WORSHIPLEADER:
            next_date = person.get_next_preaching_date(event.date)

            # Check if the next preaching date is within the preaching time window
            return bool(
                next_date is None or next_date - event.date > self.PREACHING_TIME_WINDOW
            )
        return True


class LuluEmceeRule(EligibilityRule):
    """
    Special Rule 1: Assign Lulu for the EMCEE role only when Pastor Edmund is preaching.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if person.name == "Lulu" and role == Role.EMCEE:
            preacher = event.get_assigned_preacher
            return preacher is not None and preacher.name == "Edmund"
        return True


class GeeWorshipLeaderRule(EligibilityRule):
    """
    Special Rule 2: Prevent Gee from being assigned as worship leader when Kris is preaching.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if person.name == "Gee" and role == Role.WORSHIPLEADER:
            preacher = event.get_assigned_preacher
            return preacher is None or preacher.name != "Kris"
        return True


class KrisAcousticRule(EligibilityRule):
    """
    Special Rule 3: Assign Kris to ACOUSTIC role when Gee is assigned to worship lead.
    """

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if role != Role.ACOUSTIC:
            return True

        worship_leader = event.get_person_by_name(name=event.roles[Role.WORSHIPLEADER])
        if worship_leader and worship_leader.name == "Gee":
            return person.name == "Kris"

        return True
