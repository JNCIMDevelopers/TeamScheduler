# Standard Library Imports
import copy
from datetime import date, timedelta
import logging
import random
from typing import Tuple, List

# Local Imports
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.event import Event
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

        self.default_role_assignment_limit = 2

        self.worship_leader_name_rotation = rotation
        self.worship_leader_index = 0

    def build(self) -> Tuple[List[Event], List[Person]]:
        """
        Builds the schedule by creating events on each date and assigning team members to roles.

        Returns:
            Tuple[List[Event], List[Person]]: A tuple containing the list of events and the team.
        """
        # Create event on each date
        for event_date in self.event_dates:
            logging.debug(f"Schedule Event Date: {str(event_date)}")

            # Create a shallow copy of persons to maintain original team list for other events
            team_copy = copy.copy(self.team)
            if team_copy is None:
                logging.warning("Team is empty for schedule.")
                return []

            # Initialize event
            event = Event(date=event_date, team=self.team, preachers=self.preachers)
            preacher, _ = event.get_assigned_preacher_and_graphics_support()

            for role in Role:
                # Get eligible person
                eligible_person = self.get_eligible_person(role=role, team=team_copy, date=event_date, preacher_name=preacher)

                if eligible_person:
                    # Assign role to person
                    event.assign_role(role=role, person=eligible_person)

                    # Remove person from shallow copy of team to avoid assigning twice in the same event
                    team_copy.remove(eligible_person)

            # Add event once all persons and/or roles have been assigned
            self.events.append(event)

        return (self.events, self.team)

    def get_eligible_person(self, role: Role, team: List[Person], date: date, preacher_name: str = None) -> Person:
        """
        Finds and returns an eligible person for a given role on a specific date.

        Args:
            role (Role): The role to be assigned.
            team (List[Person]): List of team members available for assignment.
            date (date): The date of the event.
            preacher_name (str, optional): Name of the preacher. Defaults to None.

        Returns:
            Person: The eligible person for the role, or None if no eligible person is found.
        """
        if not team:
            logging.warning("Team is empty when getting eligible person.")
            return None

        # Get eligible persons from the team
        eligible_persons = []
        for person in team:
            # If person is not capable of role, skip person
            if role not in person.roles:
                logging.debug(f"{person.name} is not capable of {role}")
                continue

            # Special condition: Assign Lulu for Emcee only when Pastor Edmund is preaching
            if (person.name == "Lulu"
                and role == Role.EMCEE
                and (not preacher_name or (preacher_name and preacher_name != "Edmund"))):
                logging.debug(f"Skipped {person.name} for {role} due to assigned preacher {preacher_name}")
                continue

            # Special condition: Do not assign Gee for worship leading when Kris is preaching
            if (person.name == "Gee"
                and role == Role.WORSHIPLEADER
                and preacher_name == "Kris"):
                logging.debug(f"Skipped {person.name} for {role} due to assigned preacher {preacher_name}")
                continue

            # Eligiblity Criteria
            isOnLeave = person.on_leave
            isBlockedout = date in person.blockout_dates
            isPreaching = date in person.preaching_dates
            isAssignedTooManyTimesRecently = person.assigned_too_many_times_recently(reference_date=date)
            wasNotAssignedRoleTooRecently = person.was_not_assigned_too_recently_to_role(role=role, date=date)
            wasAssignedRoleConsecutivelyTooManyTimes = self.was_assigned_role_consecutively_too_many_times(name=person.name, role=role, date=date)

            # Eligiblity Criteria for Worship Leader Role
            isWorshipLeaderRole = role == Role.WORSHIPLEADER
            isTeaching = date in person.teaching_dates if isWorshipLeaderRole else False
            isUnavailableToWorshipLeadDueToPreaching = person.is_unavailable_due_to_preaching(reference_date=date) if isWorshipLeaderRole else False

            logging.debug(f"""Person: {person.name}
                          Role: {str(role)}
                          isOnLeave: {isOnLeave}
                          isBlockedout: {isBlockedout}
                          isPreaching: {isPreaching}
                          isAssignedTooManyTimesRecently: {isAssignedTooManyTimesRecently}
                          wasNotAssignedRoleTooRecently: {wasNotAssignedRoleTooRecently}
                          wasAssignedRoleConsecutivelyTooManyTimes: {wasAssignedRoleConsecutivelyTooManyTimes}
                          isWorshipLeaderRole: {isWorshipLeaderRole}
                          isTeaching: {isTeaching}
                          isUnavailableToWorshipLeadDueToPreaching: {isUnavailableToWorshipLeadDueToPreaching}""")

            if (not isOnLeave
                and not isBlockedout
                and not isPreaching
                and not isAssignedTooManyTimesRecently
                and wasNotAssignedRoleTooRecently
                and not wasAssignedRoleConsecutivelyTooManyTimes
                and (not isWorshipLeaderRole 
                     or (not isTeaching and not isUnavailableToWorshipLeadDueToPreaching)
                )):
                eligible_persons.append(person)

        # Return random eligible team member
        if eligible_persons:
            logging.info(f"Eligible Persons for {role} on {date}: {[p.name for p in eligible_persons]}")

            if (role == Role.WORSHIPLEADER):
                next_worship_leader = self.get_next_worship_leader(eligible_persons=eligible_persons)
                if next_worship_leader:
                    return next_worship_leader

            return random.choice(eligible_persons)

        logging.warning(f"No eligible person for {role} on {date}")

        return None

    def was_assigned_role_consecutively_too_many_times(self, name: str, role: Role, date: date) -> bool:
        """
        Checks if a person was assigned a specific role too many times consecutively within a limit.

        Args:
            name (str): Name of the person.
            role (Role): The role to check.
            date (date): The reference date.

        Returns:
            bool: True if the person was assigned the role too many times consecutively, False otherwise.
        """
        past_assigned_names = [
            event.roles[role]
            for event in self.events
            if date - event.date <= timedelta(weeks=self.default_role_assignment_limit)
        ]
        return past_assigned_names.count(name) >= self.default_role_assignment_limit
    
    def get_next_worship_leader(self, eligible_persons: List[Person]) -> Person:
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
        if not eligible_persons or not self.worship_leader_name_rotation:
            return None

        # Start checking from the current index
        next_index = self.worship_leader_index
        
        # Iterate through the list to find the next eligible worship leader
        for _ in range(len(self.worship_leader_name_rotation)):
            worship_leader_name = self.worship_leader_name_rotation[next_index]
            worship_leader = next((p for p in eligible_persons if p.name == worship_leader_name), None)
            
            if worship_leader:
                # Update the index only if a valid worship leader is found
                self.worship_leader_index = (next_index + 1) % len(self.worship_leader_name_rotation)
                return worship_leader

            # Move to the next index in the rotation
            next_index = (next_index + 1) % len(self.worship_leader_name_rotation)

        # If no eligible worship leader is found, return None
        return None