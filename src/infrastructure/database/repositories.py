"""
In-memory repository implementations for development and testing.

These repositories store data in memory and will lose data when the application restarts.
For production use, replace with database-backed implementations.
"""

from datetime import date
from typing import List, Optional, Dict
from uuid import UUID
import copy

from ...core.entities.person import Person
from ...core.entities.event import Event, Preacher
from ...core.interfaces.repositories import (
    PersonRepository,
    EventRepository,
    PreacherRepository,
)


class InMemoryPersonRepository(PersonRepository):
    """In-memory implementation of PersonRepository."""

    def __init__(self):
        self._persons: Dict[UUID, Person] = {}
        self._name_index: Dict[str, UUID] = {}
        self._init_sample_data()

    def get_all(self) -> List[Person]:
        """Get all persons."""
        return list(self._persons.values())

    def get_by_id(self, person_id: UUID) -> Optional[Person]:
        """Get person by ID."""
        return self._persons.get(person_id)

    def get_by_name(self, name: str) -> Optional[Person]:
        """Get person by name."""
        person_id = self._name_index.get(name)
        if person_id:
            return self._persons.get(person_id)
        return None

    def save(self, person: Person) -> Person:
        """Save person and return the saved entity."""
        if person.id is None:
            from uuid import uuid4

            person.id = uuid4()

        # Deep copy to avoid reference issues
        saved_person = copy.deepcopy(person)
        self._persons[saved_person.id] = saved_person
        self._name_index[saved_person.name] = saved_person.id

        return saved_person

    def delete(self, person_id: UUID) -> bool:
        """Delete person by ID. Returns True if deleted."""
        person = self._persons.get(person_id)
        if person:
            del self._persons[person_id]
            # Remove from name index
            for name, id_val in list(self._name_index.items()):
                if id_val == person_id:
                    del self._name_index[name]
                    break
            return True
        return False

    def _init_sample_data(self):
        """Initialize with sample data for development."""
        from ...core.entities.role import Role

        sample_persons = [
            Person(name="Gee", roles=[Role.WORSHIP_LEADER, Role.ACOUSTIC]),
            Person(name="John", roles=[Role.WORSHIP_LEADER, Role.KEYS]),
            Person(name="Sarah", roles=[Role.EMCEE, Role.LYRICS]),
            Person(name="Michael", roles=[Role.DRUMS, Role.AUDIO]),
            Person(name="Kris", roles=[Role.ACOUSTIC, Role.KEYS]),
            Person(name="Lulu", roles=[Role.EMCEE, Role.BACKUP]),
            Person(name="Jeff", roles=[Role.BASS, Role.AUDIO]),
            Person(name="Mariel", roles=[Role.LYRICS, Role.BACKUP]),
            Person(name="Mark", roles=[Role.DRUMS, Role.LIVE]),
            Person(name="Dave", roles=[Role.LIVE, Role.AUDIO]),
            Person(name="Aubrey", roles=[Role.SUNDAY_SCHOOL_TEACHER, Role.BACKUP]),
        ]

        for person in sample_persons:
            self.save(person)


class InMemoryEventRepository(EventRepository):
    """In-memory implementation of EventRepository."""

    def __init__(self):
        self._events: Dict[UUID, Event] = {}
        self._date_index: Dict[date, UUID] = {}

    def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID."""
        event = self._events.get(event_id)
        return copy.deepcopy(event) if event else None

    def get_by_date(self, event_date: date) -> Optional[Event]:
        """Get event by date."""
        event_id = self._date_index.get(event_date)
        if event_id:
            event = self._events.get(event_id)
            return copy.deepcopy(event) if event else None
        return None

    def get_events_between(self, start_date: date, end_date: date) -> List[Event]:
        """Get events between start and end dates (inclusive)."""
        events = []
        for event_date, event_id in self._date_index.items():
            if start_date <= event_date <= end_date:
                event = self._events.get(event_id)
                if event:
                    events.append(copy.deepcopy(event))

        # Sort by date
        events.sort(key=lambda e: e.date)
        return events

    def save(self, event: Event) -> Event:
        """Save event and return the saved entity."""
        if event.id is None:
            from uuid import uuid4

            event.id = uuid4()

        # Deep copy to avoid reference issues
        saved_event = copy.deepcopy(event)
        self._events[saved_event.id] = saved_event
        self._date_index[saved_event.date] = saved_event.id

        return saved_event

    def save_many(self, events: List[Event]) -> List[Event]:
        """Save multiple events."""
        saved_events = []
        for event in events:
            saved_event = self.save(event)
            saved_events.append(saved_event)
        return saved_events

    def delete(self, event_id: UUID) -> bool:
        """Delete event by ID. Returns True if deleted."""
        event = self._events.get(event_id)
        if event:
            del self._events[event_id]
            # Remove from date index
            for event_date, id_val in list(self._date_index.items()):
                if id_val == event_id:
                    del self._date_index[event_date]
                    break
            return True
        return False


class InMemoryPreacherRepository(PreacherRepository):
    """In-memory implementation of PreacherRepository."""

    def __init__(self):
        self._preachers: Dict[UUID, Preacher] = {}
        self._name_index: Dict[str, UUID] = {}
        self._init_sample_data()

    def get_all(self) -> List[Preacher]:
        """Get all preachers."""
        return list(self._preachers.values())

    def get_by_id(self, preacher_id: UUID) -> Optional[Preacher]:
        """Get preacher by ID."""
        return self._preachers.get(preacher_id)

    def get_by_name(self, name: str) -> Optional[Preacher]:
        """Get preacher by name."""
        preacher_id = self._name_index.get(name)
        if preacher_id:
            return self._preachers.get(preacher_id)
        return None

    def get_preacher_for_date(self, event_date: date) -> Optional[Preacher]:
        """Get preacher assigned to a specific date."""
        for preacher in self._preachers.values():
            if preacher.is_preaching_on_date(event_date):
                return preacher
        return None

    def save(self, preacher: Preacher) -> Preacher:
        """Save preacher and return the saved entity."""
        if preacher.id is None:
            from uuid import uuid4

            preacher.id = uuid4()

        # Deep copy to avoid reference issues
        saved_preacher = copy.deepcopy(preacher)
        self._preachers[saved_preacher.id] = saved_preacher
        self._name_index[saved_preacher.name] = saved_preacher.id

        return saved_preacher

    def delete(self, preacher_id: UUID) -> bool:
        """Delete preacher by ID. Returns True if deleted."""
        preacher = self._preachers.get(preacher_id)
        if preacher:
            del self._preachers[preacher_id]
            # Remove from name index
            for name, id_val in list(self._name_index.items()):
                if id_val == preacher_id:
                    del self._name_index[name]
                    break
            return True
        return False

    def _init_sample_data(self):
        """Initialize with sample data for development."""
        from datetime import timedelta

        sample_preachers = [
            Preacher(name="Edmund", graphics_support="Graphics Team A"),
            Preacher(name="Kris", graphics_support="Graphics Team B"),
            Preacher(name="Guest Speaker", graphics_support="Graphics Team A"),
        ]

        # Add some sample preaching dates (next few Sundays)
        today = date.today()
        next_sunday = today + timedelta(days=(6 - today.weekday()) % 7)

        sample_preachers[0].add_preaching_date(next_sunday)
        sample_preachers[1].add_preaching_date(next_sunday + timedelta(days=7))
        sample_preachers[2].add_preaching_date(next_sunday + timedelta(days=14))

        for preacher in sample_preachers:
            self.save(preacher)
