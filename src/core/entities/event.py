from dataclasses import dataclass, field
from datetime import date as DateType
from typing import List, Optional, Dict
from uuid import uuid4, UUID

from .person import Person
from .role import Role


@dataclass
class Preacher:
    """Core entity representing a preacher with their assigned dates and graphics support."""

    id: Optional[UUID] = field(default_factory=uuid4)
    name: str = ""
    graphics_support: str = ""
    dates: List[DateType] = field(default_factory=list)

    def is_preaching_on_date(self, event_date: DateType) -> bool:
        """Check if this preacher is assigned to preach on the given date."""
        return event_date in self.dates

    def add_preaching_date(self, event_date: DateType) -> None:
        """Add a preaching date to this preacher's schedule."""
        if event_date not in self.dates:
            self.dates.append(event_date)
            self.dates.sort()

    def remove_preaching_date(self, event_date: DateType) -> None:
        """Remove a preaching date from this preacher's schedule."""
        if event_date in self.dates:
            self.dates.remove(event_date)


@dataclass
class Event:
    """
    Core entity representing a church service event with role assignments.

    This is a pure domain entity focused on role assignment logic.
    """

    id: Optional[UUID] = field(default_factory=uuid4)
    date: DateType = field(default_factory=DateType.today)
    assignments: Dict[Role, Optional[str]] = field(default_factory=dict)
    preacher_id: Optional[UUID] = None

    # Non-persistent references for business logic
    _team: List[Person] = field(default_factory=list, init=False, repr=False)
    _preachers: List[Preacher] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Initialize assignments dictionary with all roles."""
        if not self.assignments:
            self.assignments = {role: None for role in Role}

    def set_team_and_preachers(
        self, team: List[Person], preachers: List[Preacher]
    ) -> None:
        """Set the team and preachers for business logic operations."""
        self._team = team
        self._preachers = preachers

    def assign_person_to_role(self, role: Role, person: Person) -> None:
        """Assign a person to a specific role for this event."""
        if self.assignments.get(role) is not None:
            raise ValueError(f"Role {role.value} is already assigned")

        self.assignments[role] = person.name
        person.assign_to_event(self.date, role)

    def unassign_role(self, role: Role) -> None:
        """Remove assignment from a role."""
        if role in self.assignments:
            person_name = self.assignments[role]
            if person_name:
                person = self.get_person_by_name(person_name)
                if person:
                    person.unassign_from_event(self.date, role)
            self.assignments[role] = None

    def get_person_by_name(self, name: str) -> Optional[Person]:
        """Find a person in the team by name."""
        return next((person for person in self._team if person.name == name), None)

    def get_assigned_preacher(self) -> Optional[Preacher]:
        """Get the preacher assigned to this event date."""
        if not self.preacher_id:
            # Fall back to finding by date if no explicit assignment
            return next(
                (
                    preacher
                    for preacher in self._preachers
                    if preacher.is_preaching_on_date(self.date)
                ),
                None,
            )
        return next(
            (
                preacher
                for preacher in self._preachers
                if preacher.id == self.preacher_id
            ),
            None,
        )

    def get_assigned_roles(self) -> List[Role]:
        """Get list of roles that have been assigned."""
        return [
            role
            for role, person_name in self.assignments.items()
            if person_name is not None
        ]

    def get_unassigned_roles(self) -> List[Role]:
        """Get list of roles that are still unassigned."""
        return [
            role
            for role, person_name in self.assignments.items()
            if person_name is None
        ]

    def get_assigned_person_names(self) -> List[str]:
        """Get list of person names who are assigned to this event."""
        return [name for name in self.assignments.values() if name is not None]

    def get_unassigned_person_names(self) -> List[str]:
        """Get list of person names who are not assigned to this event."""
        assigned_names = set(self.get_assigned_person_names())
        return [
            person.name for person in self._team if person.name not in assigned_names
        ]

    def is_person_assigned(self, person_name: str) -> bool:
        """Check if a person is assigned to any role in this event."""
        return person_name in self.get_assigned_person_names()

    def get_person_role(self, person_name: str) -> Optional[Role]:
        """Get the role assigned to a specific person."""
        for role, assigned_name in self.assignments.items():
            if assigned_name == person_name:
                return role
        return None

    def is_role_assigned(self, role: Role) -> bool:
        """Check if a specific role has been assigned."""
        return self.assignments.get(role) is not None
