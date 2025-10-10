from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict
from uuid import uuid4, UUID

from .role import Role


@dataclass
class Person:
    """
    Core entity representing a team member with their roles and availability.

    This is a pure domain entity with no external dependencies.
    """

    # Core attributes
    id: Optional[UUID] = field(default_factory=uuid4)
    name: str = ""
    roles: List[Role] = field(default_factory=list)

    # Availability constraints
    blockout_dates: List[date] = field(default_factory=list)
    preaching_dates: List[date] = field(default_factory=list)
    teaching_dates: List[date] = field(default_factory=list)
    on_leave: bool = False

    # Assignment tracking (computed fields)
    assigned_dates: List[date] = field(default_factory=list, init=False)
    last_assigned_dates: Dict[Role, Optional[date]] = field(
        default_factory=dict, init=False
    )
    role_assigned_dates: Dict[Role, List[date]] = field(
        default_factory=dict, init=False
    )

    def __post_init__(self):
        """Initialize tracking dictionaries based on person's roles."""
        if not self.last_assigned_dates:
            self.last_assigned_dates = {role: None for role in self.roles}
        if not self.role_assigned_dates:
            self.role_assigned_dates = {role: [] for role in self.roles}

    def can_perform_role(self, role: Role) -> bool:
        """Check if person has the capability to perform the given role."""
        return role in self.roles

    def is_available_on_date(self, event_date: date) -> bool:
        """Check if person is available on the given date."""
        return (
            not self.on_leave
            and event_date not in self.blockout_dates
            and event_date not in self.preaching_dates
        )

    def assign_to_event(self, event_date: date, role: Role) -> None:
        """Record assignment to an event for tracking purposes."""
        if event_date not in self.assigned_dates:
            self.assigned_dates.append(event_date)

        self.last_assigned_dates[role] = event_date

        if role not in self.role_assigned_dates:
            self.role_assigned_dates[role] = []
        self.role_assigned_dates[role].append(event_date)

    def unassign_from_event(self, event_date: date, role: Role) -> None:
        """Remove assignment from an event."""
        if event_date in self.assigned_dates:
            self.assigned_dates.remove(event_date)

        if (
            role in self.role_assigned_dates
            and event_date in self.role_assigned_dates[role]
        ):
            self.role_assigned_dates[role].remove(event_date)

        # Update last assigned date for this role
        remaining_dates = self.role_assigned_dates.get(role, [])
        self.last_assigned_dates[role] = (
            max(remaining_dates) if remaining_dates else None
        )

    def get_next_preaching_date(self, reference_date: date) -> Optional[date]:
        """Get the next preaching date on or after the reference date."""
        future_dates = [d for d in self.preaching_dates if d >= reference_date]
        return min(future_dates) if future_dates else None

    def get_last_assignment_for_role(self, role: Role) -> Optional[date]:
        """Get the last date this person was assigned to the given role."""
        return self.last_assigned_dates.get(role)

    def get_assignment_count_for_role(self, role: Role) -> int:
        """Get total number of times assigned to the given role."""
        return len(self.role_assigned_dates.get(role, []))
