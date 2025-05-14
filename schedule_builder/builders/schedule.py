# Standard Library Imports
import copy
from datetime import date
import logging
import random
from typing import List, Optional, Tuple

# Local Imports
from ..eligibility.eligibility_checker import EligibilityChecker
from ..helpers.worship_leader_selector import WorshipLeaderSelector
from ..models.event import Event
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.role import Role


class Schedule:
    """
    A class to build a schedule for team members based on their roles and availability.
    """

    def __init__(
        self,
        team: List[Person],
        event_dates: List[date],
        worship_leader_selector: WorshipLeaderSelector,
        eligibility_checker: EligibilityChecker,
        preachers: Optional[List[Preacher]] = None,
    ):
        """
        Initializes an instance of Schedule.


        Args:
            team (List[Person]): List of available team members.
            event_dates (List[date]): List of event dates.
            worship_leader_selector (WorshipLeaderSelector): Selector for worship leaders.
            eligibility_checker (EligibilityChecker): Eligibility checker for scheduling.
            preachers (Optional[List[Preacher]]): List of available preachers. Defaults to None.
        """
        self.team: List[Person] = team
        self.preachers: List[Preacher] = preachers if preachers else []
        self.event_dates: List[date] = event_dates
        self.events: List[Event] = []
        self.worship_leader_selector = worship_leader_selector
        self.eligibility_checker = eligibility_checker

    def build(self) -> Tuple[List[Event], List[Person]]:
        """
        Builds the event schedule, assigning roles to team members for each event date.

        Returns:
            Tuple[List[Event], List[Person]]: List of scheduled events and team members.
        """
        if not self.team:
            logging.warning("No team available for schedule.")
            return ([], [])

        for event_date in self.event_dates:
            logging.debug(f"Schedule Event Date: {str(event_date)}.")

            # Create a shallow copy of persons to maintain original team list for other events
            team_copy = copy.copy(self.team)
            event = Event(date=event_date, team=self.team, preachers=self.preachers)

            for role in Role:
                eligible_person = self.get_eligible_person(
                    role=role, team=team_copy, event=event
                )
                if eligible_person:
                    event.assign_role(role=role, person=eligible_person)
                    logging.info(
                        f"{eligible_person.name} assigned as {role} on {str(event_date)}."
                    )
                    team_copy.remove(eligible_person)

            self.events.append(event)

        return (self.events, self.team)

    def get_eligible_person(
        self, role: Role, team: List[Person], event: Event
    ) -> Optional[Person]:
        """
        Finds an eligible person from the team for a specific role on a given event date.

        Args:
            role (Role): The role to be assigned.
            team (List[Person]): List of available team members.
            event (Event): The event object.

        Returns:
            Person: The eligible person for the role, or None if no one is eligible.
        """
        if not team:
            logging.warning("No team available for getting eligible person.")
            return None

        # Filter team members based on eligibility criteria
        eligible_persons = [
            person
            for person in team
            if self.eligibility_checker.is_eligible(
                person=person, role=role, event=event
            )
        ]

        if not eligible_persons:
            logging.warning(f"No eligible person for {role} on {event.date}.")
            return None

        logging.info(
            f"Eligible Persons for {role} on {event.date}: {[p.name for p in eligible_persons]}"
        )

        # Get the next worship leader in the rotation for the WORSHIPLEADER role
        if role == Role.WORSHIPLEADER:
            next_worship_leader = self.worship_leader_selector.get_next(
                eligible_persons=eligible_persons
            )
            if next_worship_leader:
                return next_worship_leader

        return random.choice(eligible_persons)
