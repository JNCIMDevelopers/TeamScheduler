"""
Tests for core domain entities in the new architecture.
"""

import pytest
from datetime import date

from src.core.entities.person import Person
from src.core.entities.event import Event, Preacher
from src.core.entities.role import Role


class TestPerson:
    """Test Person entity business logic."""

    def test_person_creation(self):
        """Test person can be created with proper attributes."""
        person = Person(
            name="John Doe",
            roles=[Role.WORSHIP_LEADER, Role.ACOUSTIC],
            blockout_dates=[date(2024, 12, 25)],
            preaching_dates=[date(2024, 1, 7)],
            on_leave=False,
        )

        assert person.name == "John Doe"
        assert Role.WORSHIP_LEADER in person.roles
        assert Role.ACOUSTIC in person.roles
        assert date(2024, 12, 25) in person.blockout_dates
        assert date(2024, 1, 7) in person.preaching_dates
        assert not person.on_leave

    def test_can_perform_role(self):
        """Test role capability checking."""
        person = Person(name="Test", roles=[Role.DRUMS, Role.BASS])

        assert person.can_perform_role(Role.DRUMS)
        assert person.can_perform_role(Role.BASS)
        assert not person.can_perform_role(Role.WORSHIP_LEADER)

    def test_availability_checking(self):
        """Test availability checking logic."""
        person = Person(
            name="Test",
            roles=[Role.DRUMS],
            blockout_dates=[date(2024, 12, 25)],
            preaching_dates=[date(2024, 1, 7)],
            on_leave=False,
        )

        # Available on normal date
        assert person.is_available_on_date(date(2024, 6, 15))

        # Not available on blockout date
        assert not person.is_available_on_date(date(2024, 12, 25))

        # Not available on preaching date
        assert not person.is_available_on_date(date(2024, 1, 7))

        # Not available when on leave
        person.on_leave = True
        assert not person.is_available_on_date(date(2024, 6, 15))

    def test_assignment_tracking(self):
        """Test event assignment tracking."""
        person = Person(name="Test", roles=[Role.DRUMS, Role.BASS])
        event_date = date(2024, 6, 15)

        # Assign to event
        person.assign_to_event(event_date, Role.DRUMS)

        assert event_date in person.assigned_dates
        assert person.last_assigned_dates[Role.DRUMS] == event_date
        assert event_date in person.role_assigned_dates[Role.DRUMS]

        # Unassign from event
        person.unassign_from_event(event_date, Role.DRUMS)

        assert event_date not in person.assigned_dates
        assert person.last_assigned_dates[Role.DRUMS] is None
        assert event_date not in person.role_assigned_dates[Role.DRUMS]

    def test_next_preaching_date(self):
        """Test finding next preaching date."""
        person = Person(
            name="Test",
            roles=[Role.WORSHIP_LEADER],
            preaching_dates=[date(2024, 1, 7), date(2024, 1, 21), date(2024, 2, 4)],
        )

        # Next date exists
        assert person.get_next_preaching_date(date(2024, 1, 15)) == date(2024, 1, 21)

        # No future dates
        assert person.get_next_preaching_date(date(2024, 3, 1)) is None

        # Same date
        assert person.get_next_preaching_date(date(2024, 1, 21)) == date(2024, 1, 21)


class TestEvent:
    """Test Event entity business logic."""

    def test_event_creation(self):
        """Test event can be created with proper attributes."""
        event = Event(date=date(2024, 6, 15))

        assert event.date == date(2024, 6, 15)
        assert event.id is not None
        assert len(event.assignments) == len(Role)

        # All roles should be unassigned initially
        for role in Role:
            assert event.assignments[role] is None

    def test_role_assignment(self):
        """Test role assignment logic."""
        person = Person(name="Test Person", roles=[Role.DRUMS])
        event = Event(date=date(2024, 6, 15))
        event.set_team_and_preachers([person], [])

        # Assign role
        event.assign_person_to_role(Role.DRUMS, person)

        assert event.assignments[Role.DRUMS] == "Test Person"
        assert event.is_role_assigned(Role.DRUMS)
        assert event.is_person_assigned("Test Person")
        assert event.get_person_role("Test Person") == Role.DRUMS

    def test_role_assignment_errors(self):
        """Test role assignment error conditions."""
        person1 = Person(name="Person 1", roles=[Role.DRUMS])
        person2 = Person(name="Person 2", roles=[Role.DRUMS])
        event = Event(date=date(2024, 6, 15))
        event.set_team_and_preachers([person1, person2], [])

        # Assign role to person 1
        event.assign_person_to_role(Role.DRUMS, person1)

        # Should raise error when trying to assign same role to person 2
        with pytest.raises(ValueError, match="Role .* is already assigned"):
            event.assign_person_to_role(Role.DRUMS, person2)

    def test_role_unassignment(self):
        """Test role unassignment logic."""
        person = Person(name="Test Person", roles=[Role.DRUMS])
        event = Event(date=date(2024, 6, 15))
        event.set_team_and_preachers([person], [])

        # Assign then unassign role
        event.assign_person_to_role(Role.DRUMS, person)
        event.unassign_role(Role.DRUMS)

        assert event.assignments[Role.DRUMS] is None
        assert not event.is_role_assigned(Role.DRUMS)
        assert not event.is_person_assigned("Test Person")

    def test_assigned_roles_tracking(self):
        """Test tracking of assigned and unassigned roles."""
        person1 = Person(name="Person 1", roles=[Role.DRUMS])
        person2 = Person(name="Person 2", roles=[Role.BASS])
        event = Event(date=date(2024, 6, 15))
        event.set_team_and_preachers([person1, person2], [])

        # Initially all roles unassigned
        assert len(event.get_assigned_roles()) == 0
        assert len(event.get_unassigned_roles()) == len(Role)

        # Assign some roles
        event.assign_person_to_role(Role.DRUMS, person1)
        event.assign_person_to_role(Role.BASS, person2)

        assigned_roles = event.get_assigned_roles()
        unassigned_roles = event.get_unassigned_roles()

        assert Role.DRUMS in assigned_roles
        assert Role.BASS in assigned_roles
        assert Role.DRUMS not in unassigned_roles
        assert Role.BASS not in unassigned_roles
        assert len(assigned_roles) == 2
        assert len(unassigned_roles) == len(Role) - 2


class TestPreacher:
    """Test Preacher entity business logic."""

    def test_preacher_creation(self):
        """Test preacher can be created with proper attributes."""
        preacher = Preacher(
            name="Pastor Smith",
            graphics_support="Graphics Team A",
            dates=[date(2024, 1, 7), date(2024, 1, 14)],
        )

        assert preacher.name == "Pastor Smith"
        assert preacher.graphics_support == "Graphics Team A"
        assert date(2024, 1, 7) in preacher.dates
        assert date(2024, 1, 14) in preacher.dates

    def test_preaching_date_management(self):
        """Test adding and removing preaching dates."""
        preacher = Preacher(name="Pastor", graphics_support="Team A")

        # Add preaching date
        preacher.add_preaching_date(date(2024, 1, 7))
        assert preacher.is_preaching_on_date(date(2024, 1, 7))

        # Add duplicate date (should not duplicate)
        preacher.add_preaching_date(date(2024, 1, 7))
        assert preacher.dates.count(date(2024, 1, 7)) == 1

        # Remove preaching date
        preacher.remove_preaching_date(date(2024, 1, 7))
        assert not preacher.is_preaching_on_date(date(2024, 1, 7))


class TestRole:
    """Test Role enum functionality."""

    def test_role_enum_values(self):
        """Test role enum has expected values."""
        assert Role.WORSHIP_LEADER == "WORSHIP LEADER"
        assert Role.EMCEE == "EMCEE"
        assert Role.DRUMS == "DRUMS"
        assert Role.BASS == "BASS"

    def test_role_ordering(self):
        """Test role assignment and display orders."""
        assignment_order = Role.get_assignment_order()
        display_order = Role.get_display_order()

        # Should have all roles in both orders
        assert len(assignment_order) == len(Role)
        assert len(display_order) == len(Role)

        # Worship leader should be first in assignment order (highest priority)
        assert assignment_order[0] == Role.WORSHIP_LEADER

        # Emcee should be first in display order
        assert display_order[0] == Role.EMCEE
