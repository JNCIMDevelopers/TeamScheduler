# Standard Library Imports
import copy
from datetime import date
import logging
import random
from typing import List, Optional, Tuple

# Local Imports
from ..eligibility.eligibility_checker import EligibilityChecker
from ..eligibility.rules import (
    RoleCapabilityRule,
    OnLeaveRule,
    BlockoutDateRule,
    PreachingDateRule,
    RoleTimeWindowRule,
    ConsecutiveAssignmentLimitRule,
    ConsecutiveRoleAssignmentLimitRule,
    WorshipLeaderTeachingRule,
    WorshipLeaderPreachingConflictRule,
    LuluEmceeRule,
    GeeWorshipLeaderRule,
)
from ..helpers.worship_leader_selector import WorshipLeaderSelector
from ..models.event import Event
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.role import Role


class Schedule:
    """
    A class to create and manage a schedule of events, assigning team members to various roles.

    Attributes:
        team (List[Person]): List of team members available for assignment.
        event_dates (List[date]): List of dates for the events.
        events (List[Event]): List of created events.
        preachers (List[Preacher]): List of available preachers.
        rotation (List[str]): List of order of worship leaders.
        default_role_assignment_limit (int): Default limit for role assignments.
    """

    def __init__(
        self,
        team: List[Person],
        event_dates: List[date],
        preachers: List[Preacher] = [],
        rotation: List[str] = [],
    ):
        """
        Initializes the Schedule with a team, event dates, and optionally a list of preachers.

        Args:
            team (List[Person]): List of team members available for assignment.
            event_dates (List[date]): List of dates for the events.
            preachers (List[Preacher], optional): List of available preachers. Defaults to [].
        """
        self.team: List[Person] = team
        self.event_dates: List[date] = event_dates
        self.events: List[Event] = []
        self.preachers: List[Preacher] = preachers
        self.worship_leader_selector = WorshipLeaderSelector(rotation=rotation)

        # Initialize the EligibilityChecker with all rules
        # The order of rules determine the sequence they are evaluated
        self.eligibility_checker = EligibilityChecker(
            rules=[
                RoleCapabilityRule(),
                LuluEmceeRule(),
                GeeWorshipLeaderRule(),
                OnLeaveRule(),
                BlockoutDateRule(),
                PreachingDateRule(),
                RoleTimeWindowRule(),
                ConsecutiveAssignmentLimitRule(),
                ConsecutiveRoleAssignmentLimitRule(assignment_limit=2),
                WorshipLeaderTeachingRule(),
                WorshipLeaderPreachingConflictRule(),
            ]
        )

    def build(self) -> Tuple[List[Event], List[Person]]:
        """
        Builds the schedule by creating events on each date and assigning team members to roles.

        Returns:
            Tuple[List[Event], List[Person]]: A tuple containing the list of events and the team.
        """
        if self.team is None or not self.team:
            logging.warning("No team available for schedule.")
            return ([], [])

        # Create event on each date
        for event_date in self.event_dates:
            logging.debug(f"Schedule Event Date: {str(event_date)}.")

            # Create a shallow copy of persons to maintain original team list for other events
            team_copy = copy.copy(self.team)

            # Initialize event
            event = Event(date=event_date, team=self.team, preachers=self.preachers)
            preacher = event.get_assigned_preacher()

            for role in Role:
                # Get eligible person
                eligible_person = self.get_eligible_person(
                    role=role, team=team_copy, date=event_date, preacher=preacher
                )

                if eligible_person:
                    # Assign role to person
                    event.assign_role(role=role, person=eligible_person)
                    logging.info(
                        f"{eligible_person.name} assigned as {role} on {str(event_date)}."
                    )

                    # Remove person from shallow copy of team to avoid assigning twice in the same event
                    team_copy.remove(eligible_person)

            # Add event once all persons and/or roles have been assigned
            self.events.append(event)

        return (self.events, self.team)

    def get_eligible_person(
        self,
        role: Role,
        team: List[Person],
        date: date,
        preacher: Optional[Preacher] = None,
    ) -> Optional[Person]:
        """
        Finds and returns an eligible person for a given role on a specific date.

        Args:
            role (Role): The role to be assigned.
            team (List[Person]): List of team members available for assignment.
            date (date): The date of the event.
            preacher (Preacher, optional): The assigned preacher. Defaults to None.

        Returns:
            Person: The eligible person for the role, or None if no eligible person is found.
        """
        if team is None or not team:
            logging.warning("No team available for getting eligible person.")
            return None

        # Get eligible persons from the team using the EligibilityChecker
        eligible_persons = [
            person
            for person in team
            if self.eligibility_checker.is_eligible(person, role, date, preacher)
        ]

        # Return random eligible team member
        if eligible_persons:
            logging.info(
                f"Eligible Persons for {role} on {date}: {[p.name for p in eligible_persons]}"
            )

            # If the role is WORSHIPLEADER, get the next worship leader from the rotation
            if role == Role.WORSHIPLEADER:
                next_worship_leader = self.worship_leader_selector.get_next(
                    eligible_persons=eligible_persons
                )
                if next_worship_leader:
                    return next_worship_leader

            return random.choice(eligible_persons)

        logging.warning(f"No eligible person for {role} on {date}.")
        return None
