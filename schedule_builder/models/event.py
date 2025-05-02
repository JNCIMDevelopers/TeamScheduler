# Standard Library Imports
# Alias datetime.date to DateType to avoid conflict with the Event.date attribute
from datetime import date as DateType
from typing import List, Optional

# Local Imports
from ..helpers.person_status_checker import PersonStatusChecker
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.role import Role


class Event:
    """
    A class representing an event with its date, team, roles, and preachers.
    """

    def __init__(
        self,
        date: DateType,
        team: Optional[List[Person]] = None,
        preachers: Optional[List[Preacher]] = None,
    ):
        """
        Initializes the event with a date, team, and optional preachers.

        Args:
            date (date): The date of the event.
            team (List[Person], optional): The team for the event.
            preachers (List[Preacher], optional): The preachers for the event.
        """
        self.date: DateType = date
        self.team: List[Person] = team if team else []
        self.preachers: List[Preacher] = preachers if preachers else []
        self.roles: dict[Role, Optional[str]] = {role: None for role in Role}

    def assign_role(self, role: Role, person: Person) -> None:
        """
        Assigns a person to a role for the event.

        Args:
            role (Role): The role to assign.
            person (Person): The person to assign to the role.

        Raises:
            ValueError: If the role is already assigned or invalid.
        """
        if role not in Role:
            raise ValueError(f"{role} is not a valid role.")

        if self.roles[role] is not None:
            raise ValueError(f"{role.name} already has a person assigned.")

        self.roles[role] = person.name
        person.assign_event(event_date=self.date, role=role)

    def get_assigned_roles(self) -> List[Role]:
        """
        Returns the list of roles that have been assigned.

        Returns:
            List[Role]: A list of assigned roles.
        """
        return [
            role for role in Role.get_schedule_order() if self.roles[role] is not None
        ]

    def get_unassigned_roles(self) -> List[Role]:
        """
        Returns the list of roles that are unassigned.

        Returns:
            List[Role]: A list of unassigned roles.
        """
        return [role for role in Role.get_schedule_order() if self.roles[role] is None]

    def get_unassigned_names(self) -> List[str]:
        """
        Returns the names of persons who are unassigned.

        Returns:
            List[str]: A list of unassigned names.
        """
        assigned_names = set(self.roles.values())
        return [
            person.name for person in self.team if person.name not in assigned_names
        ]

    def get_person_by_name(self, name: Optional[str]) -> Optional[Person]:
        """
        Returns a person object by their name.

        Args:
            name (str): The person's name.

        Returns:
            Person: The person object, or None if not found.
        """
        return next((person for person in self.team if person.name == name), None)

    def get_assigned_preacher(self) -> Optional[Preacher]:
        """
        Returns the preacher assigned to the event date.

        Returns:
            Preacher: The assigned preacher, or None if not assigned.
        """
        return next(
            (preacher for preacher in self.preachers if self.date in preacher.dates),
            None,
        )

    def is_assignable_if_needed(self, role: Role, person: Person) -> bool:
        """
        Checks if a person can be assigned to a role on the event date when no other persons are available.

        Args:
            role (Role): The role to check.
            person (Person): The person to check.

        Returns:
            bool: True if the person can be assigned, False otherwise.
        """
        return (
            not person.on_leave
            and role.value in person.roles
            and self.date not in person.blockout_dates
            and self.date not in person.preaching_dates
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the event, including preachers, assigned roles, and unassigned roles/people.

        Returns:
            str: The string representation of the event.
        """
        preacher = self.get_assigned_preacher()
        assigned_roles = self.get_assigned_roles()
        unassigned_roles = self.get_unassigned_roles()
        unassigned_names = self.get_unassigned_names()

        preacher_and_graphics_str = f"PREACHER: {preacher.name if preacher else ''}\nGRAPHICS: {preacher.graphics_support if preacher else ''}"
        assigned_roles_str = "\n".join(
            f"{role.value}: {self.roles[role]}" for role in assigned_roles
        )
        unassigned_roles_str = "\n".join(
            f"{role.value} &rarr; Can be assigned to: {
                ', '.join(
                    [
                        member.name
                        for member in self.team
                        if self.is_assignable_if_needed(role=role, person=member)
                    ]
                )
                or 'None'
            }"
            for role in unassigned_roles
        )
        unassigned_names_str = "\n".join(
            f"{name} ({PersonStatusChecker.get_status(person=person, check_date=self.date) if person else 'UNKNOWN'})"
            for name in unassigned_names
            if (person := self.get_person_by_name(name=name)) is not None
        )

        return f"""Event on {self.date.strftime("%B-%d-%Y")}
        Preaching
        {preacher_and_graphics_str}
        Assigned Roles
        {assigned_roles_str}
        Unassigned Roles
        {unassigned_roles_str}
        Unassigned People
        {unassigned_names_str}"""
