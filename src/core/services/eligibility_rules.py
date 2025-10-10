"""
Eligibility rules implementing the business logic from the original system.

These rules determine whether a person can be assigned to a specific role
based on various constraints and business requirements.
"""

from datetime import date, timedelta
from typing import List

from ..entities.person import Person
from ..entities.event import Event
from ..entities.role import Role
from ..interfaces.repositories import EligibilityRule


class RoleCapabilityRule(EligibilityRule):
    """Rule to check if a person can perform the requested role."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        return person.can_perform_role(role)

    def get_reason(self) -> str:
        return "Person must have the capability to perform the role"


class AvailabilityRule(EligibilityRule):
    """Rule to check if a person is available on the event date."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        return person.is_available_on_date(event.date)

    def get_reason(self) -> str:
        return "Person must be available (not on leave, not blocked out, not preaching)"


class ConsecutiveAssignmentLimitRule(EligibilityRule):
    """Rule to prevent too many consecutive assignments."""

    def __init__(self, max_consecutive_weeks: int = 3):
        self.max_consecutive_weeks = max_consecutive_weeks

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        # Check if person has too many consecutive assignments leading up to this date
        consecutive_count = 0
        check_date = event.date

        for week in range(self.max_consecutive_weeks):
            check_date = check_date - timedelta(weeks=1)
            if check_date in person.assigned_dates:
                consecutive_count += 1
            else:
                break

        return consecutive_count < self.max_consecutive_weeks

    def get_reason(self) -> str:
        return f"Person cannot have more than {self.max_consecutive_weeks} consecutive assignments"


class RoleTimeWindowRule(EligibilityRule):
    """Rule to enforce minimum time between same role assignments."""

    def __init__(self, time_windows: dict[Role, int]):
        """
        Args:
            time_windows: Dictionary mapping roles to minimum weeks between assignments
        """
        self.time_windows = time_windows

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if role not in self.time_windows:
            return True

        min_weeks = self.time_windows[role]
        last_assignment = person.get_last_assignment_for_role(role)

        if last_assignment is None:
            return True

        days_since_last = (event.date - last_assignment).days
        return days_since_last >= (min_weeks * 7)

    def get_reason(self) -> str:
        return "Minimum time window between same role assignments must be respected"


class WorshipLeaderTeachingConflictRule(EligibilityRule):
    """Rule to prevent worship leader from being assigned when they're teaching."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if role == Role.WORSHIP_LEADER:
            return event.date not in person.teaching_dates
        return True

    def get_reason(self) -> str:
        return "Worship leader cannot be assigned when teaching"


class PreachingConflictRule(EligibilityRule):
    """Rule to prevent assignment when person is preaching."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        return event.date not in person.preaching_dates

    def get_reason(self) -> str:
        return "Person cannot be assigned when preaching"


# Special business rules for specific people (from the original system)


class LuluEmceeRule(EligibilityRule):
    """Special Rule: Assign Lulu for EMCEE role only when Pastor Edmund is preaching."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if person.name == "Lulu" and role == Role.EMCEE:
            preacher = event.get_assigned_preacher()
            return preacher is not None and preacher.name == "Edmund"
        return True

    def get_reason(self) -> str:
        return "Lulu can only be assigned as EMCEE when Pastor Edmund is preaching"


class GeeWorshipLeaderRule(EligibilityRule):
    """Special Rule: Prevent Gee from being worship leader when Kris is preaching."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if person.name == "Gee" and role == Role.WORSHIP_LEADER:
            preacher = event.get_assigned_preacher()
            return preacher is None or preacher.name != "Kris"
        return True

    def get_reason(self) -> str:
        return "Gee cannot be worship leader when Kris is preaching"


class KrisAcousticRule(EligibilityRule):
    """Special Rule: Assign Kris to ACOUSTIC when Gee is worship leader."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if role == Role.ACOUSTIC:
            worship_leader_name = event.assignments.get(Role.WORSHIP_LEADER)
            if worship_leader_name == "Gee":
                return person.name == "Kris"
        return True

    def get_reason(self) -> str:
        return "When Gee is worship leader, only Kris can be assigned to acoustic"


class JeffMarielConflictRule(EligibilityRule):
    """Special Rule: Do not assign both Jeff and Mariel during the same event."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if person.name not in ["Jeff", "Mariel"]:
            return True

        other_person = "Mariel" if person.name == "Jeff" else "Jeff"
        assigned_names = event.get_assigned_person_names()
        return other_person not in assigned_names

    def get_reason(self) -> str:
        return "Jeff and Mariel cannot both be assigned to the same event"


class MarkDrumsDateRule(EligibilityRule):
    """Special Rule: Do not assign Mark to drums until September 2025."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if role == Role.DRUMS and person.name == "Mark":
            return event.date >= date(2025, 9, 1)
        return True

    def get_reason(self) -> str:
        return "Mark cannot be assigned to drums until September 2025"


class AubreyDaveRule(EligibilityRule):
    """Special Rule: Prevent Aubrey from being assigned when Dave is not assigned."""

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        if person.name == "Aubrey":
            assigned_names = event.get_assigned_person_names()
            return "Dave" in assigned_names
        return True

    def get_reason(self) -> str:
        return "Aubrey can only be assigned when Dave is also assigned"


def get_default_eligibility_rules() -> List[EligibilityRule]:
    """
    Get the default set of eligibility rules for the system.

    Returns:
        List of eligibility rules to be used by the EligibilityService
    """
    # Default time windows (in weeks) for various roles
    time_windows = {
        Role.WORSHIP_LEADER: 4,
        Role.SUNDAY_SCHOOL_TEACHER: 6,
        Role.EMCEE: 3,
    }

    return [
        RoleCapabilityRule(),
        AvailabilityRule(),
        ConsecutiveAssignmentLimitRule(max_consecutive_weeks=3),
        RoleTimeWindowRule(time_windows),
        WorshipLeaderTeachingConflictRule(),
        PreachingConflictRule(),
        # Special business rules
        LuluEmceeRule(),
        GeeWorshipLeaderRule(),
        KrisAcousticRule(),
        JeffMarielConflictRule(),
        MarkDrumsDateRule(),
        AubreyDaveRule(),
    ]
