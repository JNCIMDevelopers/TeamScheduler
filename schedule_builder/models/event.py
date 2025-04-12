# Standard Library Imports
from datetime import date
from typing import List, Tuple

# Local Imports
from ..models.person import Person
from ..models.preacher import Preacher
from ..models.role import Role


class Event:
    """
    A class to represent an event, its team, roles, and preachers.

    Attributes:
        date (date): The date of the event.
        team (List[Person]): The team assigned to the event.
        roles (List[Role]): A dictionary mapping each role to the assigned person's name.
        preachers (List[Preacher]): The preachers for the event.

    Methods:
        assign_role(role, person, date): Assigns a person to a role on the event date.
        get_assigned_roles(): Returns a list of roles that have been assigned.
        get_unassigned_roles(): Returns a list of roles that have not been assigned.
        get_unassigned_names(): Returns a list of names of unassigned persons.
        get_person_by_name(name): Returns a person object by their name.
        get_person_status_on_date(person, date): Returns the status of a person on a given date.
        get_assigned_preacher_and_graphics_support(): Returns the assigned preacher and graphics support for the event date.
    """

    def __init__(self, date: date, team: List[Person] = [], preachers: List[Preacher] = []):
        """
        Initializes the Event with a date, team, and optionally preachers.

        Args:
            date (date): The date of the event.
            team (List[Person], optional): The team assigned to the event. Defaults to an empty list.
            preachers (List[Preacher], optional): The preachers for the event. Defaults to an empty list.
        """
        self.date: date = date
        self.team: List[Person] = team
        self.roles: List[Role] = {role: None for role in Role}
        self.preachers: List[Preacher] = preachers

    def assign_role(self, role: Role, person: Person) -> None:
        """
        Assigns a person to a role on the event date.

        Args:
            role (Role): The role to assign.
            person (Person): The person to assign to the role.
            date (date): The date of the event.

        Raises:
            ValueError: If the role is already assigned or not valid.
        """
        if role not in Role:
            raise ValueError(f"{role} is not a valid role.")

        if self.roles[role] is not None:
            raise ValueError(f"{role.name} already has a person assigned.")

        self.roles[role] = person.name
        person.assign_event(date=self.date, role=role)

    def get_assigned_roles(self) -> List[Role]:
        """
        Returns a list of roles that have been assigned.

        Returns:
            List[Role]: A list of assigned roles.
        """
        return [role for role in Role.get_schedule_order() if self.roles[role] is not None]

    def get_unassigned_roles(self) -> List[Role]:
        """
        Returns a list of roles that have not been assigned.

        Returns:
            List[Role]: A list of unassigned roles.
        """
        return [role for role in Role.get_schedule_order() if self.roles[role] is None]

    def get_unassigned_names(self) -> List[str]:
        """
        Returns a list of names of unassigned persons.

        Returns:
            List[str]: A list of unassigned person names.
        """
        assigned_names = {assigned_name for assigned_name in self.roles.values()}
        return [person.name for person in self.team if person.name not in assigned_names]

    def get_person_by_name(self, name: str) -> Person:
        """
        Returns a person object by their name.

        Args:
            name (str): The name of the person.

        Returns:
            Person: The person object, or None if not found.
        """
        return next((person for person in self.team if person.name == name), None)

    def get_person_status_on_date(self, person: Person, date: date) -> str:
        """
        Returns the status of a person on a given date.

        Args:
            person (Person): The person to check the status of.
            date (date): The date to check the status on.

        Returns:
            str: The status of the person on the given date.
        """
        if person.on_leave:
            return "ON-LEAVE"
        elif date in person.blockout_dates:
            return "BLOCKOUT"
        elif date in person.assigned_dates:
            return "ASSIGNED"
        elif date in person.preaching_dates:
            return "PREACHING"
        elif person.assigned_too_many_times_recently(reference_date=date):
            return "BREAK"
        elif Role.WORSHIPLEADER in person.roles and date in person.teaching_dates:
            return "TEACHING"
        else:
            return "UNASSIGNED"

    def get_assigned_preacher(self) -> Preacher:
        """
        Returns the assigned preacher for the event date.

        Returns:
            Preacher: The assigned preacher, or None if not assigned.
        """
        return next((preacher for preacher in self.preachers if self.date in preacher.dates), None)
    
    def is_assignable_if_needed(self, role: Role, person: Person) -> bool:
        """
        Checks if a person is assignable to a role. Used specifically for unassigned roles.
        
        Args:
            role (Role): The specific role to assign.
            person (Person): The person to check if assignable.

        Returns:
            bool: True if the person is assignable. False otherwise.
        """
        return (
            not person.on_leave 
            and role.value in person.roles
            and self.date not in person.blockout_dates
            and self.date not in person.preaching_dates
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the Event, including preachers, assigned roles, and unassigned roles and people.

        Returns:
            str: A string representation of the Event.
        """
        preacher = self.get_assigned_preacher()
        assigned_roles = self.get_assigned_roles()
        unassigned_roles = self.get_unassigned_roles()
        unassigned_names = self.get_unassigned_names()

        preacher_and_graphics_str = (f"PREACHER: {preacher.name}\nGRAPHICS: {preacher.graphics_support}")
        assigned_roles_str = "\n".join(f"{role.value}: {self.roles[role]}" for role in assigned_roles)
        unassigned_roles_str = "\n".join(
            f"{role.value} &rarr; Can be assigned to: {", ".join(
                [member.name for member in self.team if self.is_assignable_if_needed(role=role, person=member)]
            ) or "None"}"
            for role in unassigned_roles
        )
        unassigned_names_str = "\n".join(
            f"{name} ({self.get_person_status_on_date(person=self.get_person_by_name(name=name), date=self.date)})"
            for name in unassigned_names
        )

        return f"""Event on {self.date.strftime('%B-%d-%Y')}
        Preaching
        {preacher_and_graphics_str}
        Assigned Roles
        {assigned_roles_str}
        Unassigned Roles
        {unassigned_roles_str}
        Unassigned People
        {unassigned_names_str}"""
