# Standard Library Imports
from datetime import date
from typing import List, Optional
import logging

# Local Imports
from .eligibility_rule import EligibilityRule
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.role import Role


class EligibilityChecker:
    """
    Checks if a person is eligible for a specific role based on a set of predefined rules.

    The EligibilityChecker evaluates a list of eligibility rules to determine whether a person
    can be assigned to a role for a specific event, considering various factors like the person's
    availability, role capabilities, and any restrictions.

    Attributes:
        rules (List[EligibilityRule]): A list of eligibility rules to be evaluated.
    """

    def __init__(self, rules: List[EligibilityRule]):
        """Initializes the EligibilityChecker with a list of eligibility rules."""
        self.rules = rules

    def is_eligible(
        self,
        person: Person,
        role: Role,
        event_date: date,
        preacher: Optional[Preacher] = None,
    ) -> bool:
        """
        Evaluates all rules to determine if a person is eligible for a given role on a specific event date.

        Args:
            person (Person): The person being evaluated for eligibility.
            role (Role): The role being assigned.
            event_date (date): The date of the event.
            preacher (Preacher, optional): The assigned preacher for the event, if applicable.

        Returns:
            bool: True if the person passes all eligibility rules, False otherwise.
        """
        for rule in self.rules:
            result = rule.is_eligible(person, role, event_date, preacher)
            logging.debug(
                f"Role: {role}, Date: {event_date}, "
                f"Person: {person.name}, Rule: {rule.__class__.__name__}, "
                f"Preacher: {preacher.name if preacher else 'None'}, Result: {result}"
            )
            if not result:
                return False
        return True
