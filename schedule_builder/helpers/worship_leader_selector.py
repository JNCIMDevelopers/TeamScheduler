# Standard Library Imports
import logging
from typing import List, Optional

# Local Imports
from ..models.person import Person


class WorshipLeaderSelector:
    """
    A class to select a worship leader.
    """

    def __init__(self, rotation: List[str] = None, index: int = 0):
        """
        Initializes the WorshipLeaderSelector with a rotation of worship leaders and an index.
        """
        self.rotation = rotation if rotation else []
        self.index = index  # Default to the first worship leader in the rotation

    def get_next(self, eligible_persons: List[Person]) -> Optional[Person]:
        """
        Finds and returns the next eligible worship leader from the rotation list.

        The method iterates through the list of worship leaders in a round-robin fashion,
        starting from the current index. It returns the first eligible worship leader found
        in the `eligible_persons` list. The index is updated only if a valid worship leader
        is returned, ensuring the next call starts from the correct position in the rotation.

        Args:
            eligible_persons (List[Person]): A list of persons who are eligible for the role of worship leader.

        Returns:
            Person: The next eligible worship leader based on the rotation, or None if no eligible person is found.
        """
        if not eligible_persons or not self.rotation:
            return None

        # Start checking from the current index
        next_index = self.index

        # Iterate through the list to find the next eligible worship leader
        for _ in range(len(self.rotation)):
            worship_leader_name = self.rotation[next_index]
            worship_leader = next(
                (p for p in eligible_persons if p.name == worship_leader_name), None
            )

            if worship_leader:
                # Update the index only if a valid worship leader is found
                self.index = (next_index + 1) % len(self.rotation)

                logging.info(f"Next worship leader selected: {worship_leader.name}")
                return worship_leader

            # Move to the next index in the rotation
            next_index = (next_index + 1) % len(self.rotation)

        logging.warning("No eligible worship leader found in the rotation.")
        return None
