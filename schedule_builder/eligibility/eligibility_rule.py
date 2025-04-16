# Standard Library Imports
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

# Local Imports
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.role import Role


class EligibilityRule(ABC):
    """
    Abstract base class for eligibility rules.
    Each rule must implement the `is_eligible` method.
    """

    @abstractmethod
    def is_eligible(
        self, person: Person, role: Role, event_date: date, preacher: Optional[Preacher] = None
    ) -> bool:
        """
        Determines if a person is eligible for a role on a specific date.

        Args:
            person (Person): The person being evaluated.
            role (Role): The role being assigned.
            event_date (date): The date of the event.
            preacher (Preacher, optional): The assigned preacher. Defaults to None.

        Returns:
            bool: True if the person is eligible, False otherwise.
        """
        pass
