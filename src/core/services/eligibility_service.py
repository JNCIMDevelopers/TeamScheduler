from typing import List, Optional
import logging
import random

from ..entities.person import Person
from ..entities.event import Event
from ..entities.role import Role
from ..interfaces.repositories import EligibilityRule, WorshipLeaderSelector


class EligibilityService:
    """
    Service for checking person eligibility for roles based on business rules.

    This service encapsulates all the complex eligibility logic from the original system.
    """

    def __init__(self, rules: List[EligibilityRule]):
        self.rules = rules
        self.logger = logging.getLogger(__name__)

    def is_eligible(self, person: Person, role: Role, event: Event) -> bool:
        """
        Check if a person is eligible for a role in an event.

        Args:
            person: The person being evaluated
            role: The role to be assigned
            event: The event context

        Returns:
            True if person passes all eligibility rules, False otherwise
        """
        for rule in self.rules:
            try:
                result = rule.is_eligible(person, role, event)
                self.logger.debug(
                    f"Role: {role.value}, Date: {event.date}, "
                    f"Person: {person.name}, Rule: {rule.__class__.__name__}, "
                    f"Result: {result}"
                )
                if not result:
                    return False
            except Exception as e:
                self.logger.error(
                    f"Error evaluating rule {rule.__class__.__name__}: {e}"
                )
                return False

        return True

    def get_eligible_persons(
        self, role: Role, event: Event, candidates: List[Person]
    ) -> List[Person]:
        """
        Get all persons eligible for a role in an event.

        Args:
            role: The role to check eligibility for
            event: The event context
            candidates: List of candidate persons to check

        Returns:
            List of eligible persons
        """
        eligible = []
        for person in candidates:
            if self.is_eligible(person, role, event):
                eligible.append(person)

        return eligible

    def add_rule(self, rule: EligibilityRule) -> None:
        """Add a new eligibility rule."""
        self.rules.append(rule)

    def remove_rule(self, rule_class: type) -> None:
        """Remove eligibility rules of a specific type."""
        self.rules = [rule for rule in self.rules if not isinstance(rule, rule_class)]


class PersonSelectionService:
    """
    Service for selecting persons for roles based on business logic.

    Handles worship leader rotation and general person selection strategies.
    """

    def __init__(self, worship_leader_selector: Optional[WorshipLeaderSelector] = None):
        self.worship_leader_selector = worship_leader_selector
        self.logger = logging.getLogger(__name__)

    def select_person_for_role(
        self, role: Role, eligible_persons: List[Person], event: Event
    ) -> Optional[Person]:
        """
        Select a person for a role from eligible candidates.

        Args:
            role: The role to assign
            eligible_persons: List of eligible persons
            event: The event context

        Returns:
            Selected person or None if no selection possible
        """
        if not eligible_persons:
            self.logger.warning(f"No eligible persons for {role.value} on {event.date}")
            return None

        self.logger.info(
            f"Eligible persons for {role.value} on {event.date}: {[p.name for p in eligible_persons]}"
        )

        # Special handling for worship leader role
        if role == Role.WORSHIP_LEADER and self.worship_leader_selector:
            selected = self.worship_leader_selector.select_worship_leader(
                eligible_persons, event
            )
            if selected:
                return selected

        # Default random selection for other roles
        return random.choice(eligible_persons)

    def set_worship_leader_selector(self, selector: WorshipLeaderSelector) -> None:
        """Set the worship leader selection strategy."""
        self.worship_leader_selector = selector
