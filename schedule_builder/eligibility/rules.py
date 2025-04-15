# Standard Library Imports
from datetime import date, timedelta

# Local Imports
from .eligibility_rule import EligibilityRule
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.role import Role


class RoleCapabilityRule(EligibilityRule):
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        return role in person.roles

class OnLeaveRule(EligibilityRule):
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        return not person.on_leave

class BlockoutDateRule(EligibilityRule):
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        return event_date not in person.blockout_dates

class PreachingDateRule(EligibilityRule):
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        return event_date not in person.preaching_dates

class RoleTimeWindowRule(EligibilityRule):
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        time_window = None
        if role == Role.WORSHIPLEADER:
            time_window = timedelta(weeks=4)
        elif role == Role.SUNDAYSCHOOLTEACHER:
            time_window = timedelta(weeks=4)
        elif role == Role.EMCEE:
            time_window = timedelta(weeks=2)
        else:
            return True

        last_assigned_date = person.last_assigned_dates[role]

        return (
            last_assigned_date is None
            or event_date - last_assigned_date > time_window
        )

class ConsecutiveAssignmentLimitRule(EligibilityRule):
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        return not person.assigned_too_many_times_recently(reference_date=event_date)

class ConsecutiveRoleAssignmentLimitRule(EligibilityRule):
    def __init__(self, assignment_limit: int):
        self.assignment_limit = assignment_limit
        self.time_window = timedelta(weeks=assignment_limit) 

    def is_eligible(self, person: Person, role: Role, event_date: date, preacher=None) -> bool:
        # Get all assigned dates for the person within the time window
        past_assigned_dates = [
            assigned_date
            for assigned_date in person.role_assigned_dates[role]
            if event_date - assigned_date <= self.time_window
        ]

        return len(past_assigned_dates) < self.assignment_limit

class WorshipLeaderTeachingRule(EligibilityRule):
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        if role == Role.WORSHIPLEADER:
            return event_date not in person.teaching_dates
        return True

class WorshipLeaderPreachingConflictRule(EligibilityRule):
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        if role == Role.WORSHIPLEADER:
            return not person.is_unavailable_due_to_preaching(reference_date=event_date)
        return True

class LuluEmceeRule(EligibilityRule):
    """
    Special Rule: Assign Lulu for Emcee only when Pastor Edmund is preaching.
    """
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        if person.name == "Lulu" and role == Role.EMCEE:
            return preacher is not None and preacher.name == "Edmund"
        return True

class GeeWorshipLeaderRule(EligibilityRule):
    """
    Special Rule: Do not assign Gee for worship leading when Kris is preaching.
    """
    def is_eligible(self, person: Person, role: Role, event_date: date, preacher: Preacher = None) -> bool:
        if person.name == "Gee" and role == Role.WORSHIPLEADER:
            return preacher is None or preacher.name != "Kris"
        return True