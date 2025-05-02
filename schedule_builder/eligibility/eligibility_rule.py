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
    Abstract base class for defining eligibility rules.

    This class serves as a blueprint for all eligibility rules. Each subclass must implement
    the `is_eligible` method to evaluate whether a person qualifies for a specific role
    based on defined criteria.

    Methods:
        is_eligible: Determines if a person is eligible for a role on a specific event date.
    """

    @abstractmethod
    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
        worship_leader: Optional[Person] = None,
    ) -> bool:
        """
        Abstract method to check if a person is eligible for a role.

        Args:
            person (Person): The person being evaluated for eligibility.
            role (Role): The role to be assigned.
            event_date (date): The date of the event.
            preacher (Preacher, optional): The preacher assigned to the event, if applicable.
            worship_leader (Person, optional): The worship leader assigned to the event, if applicable.

        Returns:
            bool: True if the person is eligible, False otherwise.
        """
        pass
