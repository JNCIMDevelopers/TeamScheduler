from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from uuid import UUID

from ..entities.person import Person
from ..entities.event import Event, Preacher
from ..entities.role import Role


class PersonRepository(ABC):
    """Repository interface for Person entity operations."""

    @abstractmethod
    def get_all(self) -> List[Person]:
        """Get all persons."""
        pass

    @abstractmethod
    def get_by_id(self, person_id: UUID) -> Optional[Person]:
        """Get person by ID."""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Person]:
        """Get person by name."""
        pass

    @abstractmethod
    def save(self, person: Person) -> Person:
        """Save person and return the saved entity."""
        pass

    @abstractmethod
    def delete(self, person_id: UUID) -> bool:
        """Delete person by ID. Returns True if deleted."""
        pass


class EventRepository(ABC):
    """Repository interface for Event entity operations."""

    @abstractmethod
    def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID."""
        pass

    @abstractmethod
    def get_by_date(self, event_date: date) -> Optional[Event]:
        """Get event by date."""
        pass

    @abstractmethod
    def get_events_between(self, start_date: date, end_date: date) -> List[Event]:
        """Get events between start and end dates (inclusive)."""
        pass

    @abstractmethod
    def save(self, event: Event) -> Event:
        """Save event and return the saved entity."""
        pass

    @abstractmethod
    def save_many(self, events: List[Event]) -> List[Event]:
        """Save multiple events."""
        pass

    @abstractmethod
    def delete(self, event_id: UUID) -> bool:
        """Delete event by ID. Returns True if deleted."""
        pass


class PreacherRepository(ABC):
    """Repository interface for Preacher entity operations."""

    @abstractmethod
    def get_all(self) -> List[Preacher]:
        """Get all preachers."""
        pass

    @abstractmethod
    def get_by_id(self, preacher_id: UUID) -> Optional[Preacher]:
        """Get preacher by ID."""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Preacher]:
        """Get preacher by name."""
        pass

    @abstractmethod
    def get_preacher_for_date(self, event_date: date) -> Optional[Preacher]:
        """Get preacher assigned to a specific date."""
        pass

    @abstractmethod
    def save(self, preacher: Preacher) -> Preacher:
        """Save preacher and return the saved entity."""
        pass

    @abstractmethod
    def delete(self, preacher_id: UUID) -> bool:
        """Delete preacher by ID. Returns True if deleted."""
        pass


class EligibilityRule(ABC):
    """Abstract interface for eligibility rules."""

    @abstractmethod
    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        """
        Check if a person is eligible for a role in an event.

        Args:
            person: The person being evaluated
            role: The role to be assigned
            event: The event context

        Returns:
            True if the person is eligible, False otherwise
        """
        pass

    @abstractmethod
    def get_reason(self) -> str:
        """Get human-readable description of this rule."""
        pass


class WorshipLeaderSelector(ABC):
    """Abstract interface for worship leader selection strategy."""

    @abstractmethod
    def select_worship_leader(
        self, eligible_persons: List[Person], event: Event
    ) -> Optional[Person]:
        """
        Select the next worship leader from eligible persons.

        Args:
            eligible_persons: List of persons eligible for worship leader role
            event: The event context

        Returns:
            Selected person or None if no selection can be made
        """
        pass

    @abstractmethod
    def get_next_in_rotation(self) -> Optional[str]:
        """Get the next person name in the rotation."""
        pass
