# Standard Library Imports
from typing import List
import logging

# Local Imports
from .eligibility_rule import EligibilityRule
from ..models.event import Event
from ..models.person import Person
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

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        """
        Evaluates all rules to determine if a person is eligible for a given role on a specific event date.

        Args:
            person (Person): The person being evaluated for eligibility.
            role (Role): The role being assigned.
            event (Event): The event object.

        Returns:
            bool: True if the person passes all eligibility rules, False otherwise.
        """
        for rule in self.rules:
            result = rule.is_eligible(person, role, event)
            logging.debug(
                f"Role: {role}, Date: {event.date}, "
                f"Person: {person.name}, Rule: {rule.__class__.__name__}, "
                f"Result: {result}"
            )
            if not result:
                return False
        return True
