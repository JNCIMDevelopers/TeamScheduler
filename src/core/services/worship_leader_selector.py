"""
Worship leader selection service implementing rotation logic.
"""

from typing import List, Optional

from ..entities.person import Person
from ..entities.event import Event
from ..interfaces.repositories import WorshipLeaderSelector


class RotationWorshipLeaderSelector(WorshipLeaderSelector):
    """
    Worship leader selector that uses a rotation system.

    This maintains a rotation of worship leaders and selects the next
    person in line from those who are eligible.
    """

    def __init__(self, rotation_order: List[str]):
        """
        Initialize the selector with a rotation order.

        Args:
            rotation_order: List of person names in rotation order
        """
        self.rotation_order = rotation_order
        self.current_index = 0

    def select_worship_leader(
        self, eligible_persons: List[Person], event: Event
    ) -> Optional[Person]:
        """
        Select the next worship leader from eligible persons based on rotation.

        Args:
            eligible_persons: List of persons eligible for worship leader role
            event: The event context

        Returns:
            Selected person or None if no one in rotation is eligible
        """
        if not eligible_persons or not self.rotation_order:
            return None

        eligible_names = {person.name for person in eligible_persons}

        # Find the next person in rotation who is also eligible
        attempts = 0
        while attempts < len(self.rotation_order):
            next_name = self.rotation_order[self.current_index]

            if next_name in eligible_names:
                # Found next person in rotation who is eligible
                selected_person = next(
                    p for p in eligible_persons if p.name == next_name
                )
                self._advance_rotation()
                return selected_person

            # Move to next person in rotation
            self._advance_rotation()
            attempts += 1

        # No one in rotation is eligible, return None
        return None

    def get_next_in_rotation(self) -> Optional[str]:
        """Get the next person name in the rotation without advancing."""
        if not self.rotation_order:
            return None
        return self.rotation_order[self.current_index]

    def set_rotation_order(self, rotation_order: List[str]) -> None:
        """Update the rotation order."""
        self.rotation_order = rotation_order
        self.current_index = 0

    def reset_rotation(self) -> None:
        """Reset rotation to the beginning."""
        self.current_index = 0

    def _advance_rotation(self) -> None:
        """Move to the next person in rotation."""
        if self.rotation_order:
            self.current_index = (self.current_index + 1) % len(self.rotation_order)


class RandomWorshipLeaderSelector(WorshipLeaderSelector):
    """
    Worship leader selector that randomly selects from eligible persons.

    This is a fallback selector when no rotation is specified.
    """

    def select_worship_leader(
        self, eligible_persons: List[Person], event: Event
    ) -> Optional[Person]:
        """
        Randomly select a worship leader from eligible persons.

        Args:
            eligible_persons: List of persons eligible for worship leader role
            event: The event context

        Returns:
            Randomly selected person or None if no one is eligible
        """
        if not eligible_persons:
            return None

        import random

        return random.choice(eligible_persons)

    def get_next_in_rotation(self) -> Optional[str]:
        """Random selector has no rotation."""
        return None
