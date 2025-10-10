"""
Tests for worship leader selection services.
"""

from datetime import date

from src.core.entities.person import Person
from src.core.entities.event import Event
from src.core.entities.role import Role
from src.core.services.worship_leader_selector import (
    RotationWorshipLeaderSelector,
    RandomWorshipLeaderSelector,
)


class TestRotationWorshipLeaderSelector:
    """Test rotation-based worship leader selection."""

    def test_rotation_creation(self):
        """Test creating selector with rotation order."""
        rotation = ["Alice", "Bob", "Charlie"]
        selector = RotationWorshipLeaderSelector(rotation)

        assert selector.rotation_order == rotation
        assert selector.current_index == 0
        assert selector.get_next_in_rotation() == "Alice"

    def test_basic_rotation_selection(self):
        """Test basic rotation through worship leaders."""
        rotation = ["Alice", "Bob", "Charlie"]
        selector = RotationWorshipLeaderSelector(rotation)

        # Create eligible persons
        alice = Person(name="Alice", roles=[Role.WORSHIP_LEADER])
        bob = Person(name="Bob", roles=[Role.WORSHIP_LEADER])
        charlie = Person(name="Charlie", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [alice, bob, charlie]

        event = Event(date=date(2024, 6, 15))

        # Should select Alice first (index 0)
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected.name == "Alice"
        assert selector.current_index == 1  # Advanced to next

        # Should select Bob next (index 1)
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected.name == "Bob"
        assert selector.current_index == 2  # Advanced to next

        # Should select Charlie next (index 2)
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected.name == "Charlie"
        assert selector.current_index == 0  # Wrapped around

    def test_rotation_with_ineligible_persons(self):
        """Test rotation skips ineligible persons."""
        rotation = ["Alice", "Bob", "Charlie"]
        selector = RotationWorshipLeaderSelector(rotation)

        # Only Alice and Charlie are eligible (Bob is missing)
        alice = Person(name="Alice", roles=[Role.WORSHIP_LEADER])
        charlie = Person(name="Charlie", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [alice, charlie]

        event = Event(date=date(2024, 6, 15))

        # Should select Alice first
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected.name == "Alice"

        # Should skip Bob (not eligible) and select Charlie
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected.name == "Charlie"

        # Should wrap around and select Alice again
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected.name == "Alice"

    def test_no_eligible_persons_in_rotation(self):
        """Test when no one in rotation is eligible."""
        rotation = ["Alice", "Bob", "Charlie"]
        selector = RotationWorshipLeaderSelector(rotation)

        # Eligible person not in rotation
        david = Person(name="David", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [david]

        event = Event(date=date(2024, 6, 15))

        # Should return None (no one in rotation is eligible)
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected is None

    def test_empty_rotation(self):
        """Test selector with empty rotation."""
        selector = RotationWorshipLeaderSelector([])

        alice = Person(name="Alice", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [alice]
        event = Event(date=date(2024, 6, 15))

        # Should return None (no rotation defined)
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected is None
        assert selector.get_next_in_rotation() is None

    def test_empty_eligible_persons(self):
        """Test selector with no eligible persons."""
        rotation = ["Alice", "Bob"]
        selector = RotationWorshipLeaderSelector(rotation)

        event = Event(date=date(2024, 6, 15))

        # Should return None (no eligible persons)
        selected = selector.select_worship_leader([], event)
        assert selected is None

    def test_set_rotation_order(self):
        """Test updating rotation order."""
        selector = RotationWorshipLeaderSelector(["Alice", "Bob"])

        # Update rotation
        new_rotation = ["Charlie", "David", "Eve"]
        selector.set_rotation_order(new_rotation)

        assert selector.rotation_order == new_rotation
        assert selector.current_index == 0  # Reset to beginning
        assert selector.get_next_in_rotation() == "Charlie"

    def test_reset_rotation(self):
        """Test resetting rotation to beginning."""
        rotation = ["Alice", "Bob", "Charlie"]
        selector = RotationWorshipLeaderSelector(rotation)

        # Advance rotation
        alice = Person(name="Alice", roles=[Role.WORSHIP_LEADER])
        bob = Person(name="Bob", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [alice, bob]
        event = Event(date=date(2024, 6, 15))

        selector.select_worship_leader(
            eligible_persons, event
        )  # Selects Alice, advances to index 1
        selector.select_worship_leader(
            eligible_persons, event
        )  # Selects Bob, advances to index 2

        assert selector.current_index == 2

        # Reset rotation
        selector.reset_rotation()
        assert selector.current_index == 0
        assert selector.get_next_in_rotation() == "Alice"

    def test_rotation_index_handling(self):
        """Test proper index handling in rotation."""
        rotation = ["Alice", "Bob"]
        selector = RotationWorshipLeaderSelector(rotation)

        alice = Person(name="Alice", roles=[Role.WORSHIP_LEADER])
        bob = Person(name="Bob", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [alice, bob]
        event = Event(date=date(2024, 6, 15))

        # Test multiple rotations
        expected_sequence = ["Alice", "Bob", "Alice", "Bob", "Alice"]

        for expected_name in expected_sequence:
            selected = selector.select_worship_leader(eligible_persons, event)
            assert selected.name == expected_name


class TestRandomWorshipLeaderSelector:
    """Test random worship leader selection."""

    def test_random_selection(self):
        """Test random selection from eligible persons."""
        selector = RandomWorshipLeaderSelector()

        alice = Person(name="Alice", roles=[Role.WORSHIP_LEADER])
        bob = Person(name="Bob", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [alice, bob]

        event = Event(date=date(2024, 6, 15))

        # Should select someone (can't test randomness deterministically)
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected is not None
        assert selected.name in ["Alice", "Bob"]

    def test_random_selection_single_person(self):
        """Test random selection with only one eligible person."""
        selector = RandomWorshipLeaderSelector()

        alice = Person(name="Alice", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [alice]

        event = Event(date=date(2024, 6, 15))

        # Should always select the only eligible person
        selected = selector.select_worship_leader(eligible_persons, event)
        assert selected.name == "Alice"

    def test_random_selection_empty_list(self):
        """Test random selection with no eligible persons."""
        selector = RandomWorshipLeaderSelector()

        event = Event(date=date(2024, 6, 15))

        # Should return None
        selected = selector.select_worship_leader([], event)
        assert selected is None

    def test_get_next_in_rotation(self):
        """Test that random selector has no rotation."""
        selector = RandomWorshipLeaderSelector()

        # Random selector should have no rotation concept
        assert selector.get_next_in_rotation() is None


class TestWorshipLeaderSelectionIntegration:
    """Integration tests for worship leader selection."""

    def test_selector_with_person_selection_service(self):
        """Test integration with PersonSelectionService."""
        from src.core.services.eligibility_service import PersonSelectionService

        rotation = ["Alice", "Bob", "Charlie"]
        worship_selector = RotationWorshipLeaderSelector(rotation)
        selection_service = PersonSelectionService(worship_selector)

        # Create eligible persons
        alice = Person(name="Alice", roles=[Role.WORSHIP_LEADER])
        bob = Person(name="Bob", roles=[Role.WORSHIP_LEADER])
        charlie = Person(name="Charlie", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [alice, bob, charlie]

        event = Event(date=date(2024, 6, 15))

        # Should use worship leader selector for WORSHIP_LEADER role
        selected = selection_service.select_person_for_role(
            Role.WORSHIP_LEADER, eligible_persons, event
        )
        assert selected.name == "Alice"  # First in rotation

        # Should use random selection for other roles
        drummer = Person(name="Drummer", roles=[Role.DRUMS])
        selected = selection_service.select_person_for_role(
            Role.DRUMS, [drummer], event
        )
        assert selected.name == "Drummer"

    def test_selector_update_in_service(self):
        """Test updating worship leader selector in service."""
        from src.core.services.eligibility_service import PersonSelectionService

        # Initial selector
        initial_selector = RotationWorshipLeaderSelector(["Alice"])
        service = PersonSelectionService(initial_selector)

        # Update to new selector
        new_selector = RotationWorshipLeaderSelector(["Bob", "Charlie"])
        service.set_worship_leader_selector(new_selector)

        # Should use new selector
        bob = Person(name="Bob", roles=[Role.WORSHIP_LEADER])
        charlie = Person(name="Charlie", roles=[Role.WORSHIP_LEADER])
        eligible_persons = [bob, charlie]
        event = Event(date=date(2024, 6, 15))

        selected = service.select_person_for_role(
            Role.WORSHIP_LEADER, eligible_persons, event
        )
        assert selected.name == "Bob"  # First in new rotation
