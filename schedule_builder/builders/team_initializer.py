# Standard Library Imports
import json
import logging
import os
import traceback
from datetime import date
from typing import List

# Local Imports
from paths import TEAM_DATA_FILE_PATH, PREACHING_DATA_FILE_PATH, ROTATION_DATA_FILE_PATH
from schedule_builder.builders.file_builder import resource_path
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from schedule_builder.models.role import Role


class TeamInitializer:
    """
    A class to initialize team members and preachers.

    Methods:
        parse_date(date_str): Parses a string in YYYY-MM-DD format into a date object.
        initialize_persons(): Initializes and returns a list of Person objects.
        initialize_preachers(): Initializes and returns a list of Preacher objects.
        initialize_rotation" Initializes and returns a list of names.
        initialize_team(): Initializes and returns both persons and preachers.
    """

    def __init__(self):
        """Initializes the TeamInitializer with a logger."""
        self.logger = logging.getLogger(__name__)

    def parse_date(self, date_str: str) -> date:
        """
        Parses a string in YYYY-MM-DD format into a date object.

        Args:
            date_str (str): The date string to parse.

        Returns:
            date: The parsed date object.
        """
        year, month, day = map(int, date_str.split("-"))
        return date(year, month, day)

    def initialize_persons(self) -> List[Person]:
        """
        Initializes and returns a list of Person objects.

        Returns:
            List[Person]: A list of initialized Person objects.
        """
        with open(resource_path(TEAM_DATA_FILE_PATH), "r") as f:
            persons_data = json.load(f)

        persons = []
        for person_data in persons_data:
            blockout_dates = [
                self.parse_date(d) for d in person_data.get("blockout_dates", [])
            ]
            preaching_dates = [
                self.parse_date(d) for d in person_data.get("preaching_dates", [])
            ]
            teaching_dates = [
                self.parse_date(d) for d in person_data.get("teaching_dates", [])
            ]
            roles = [getattr(Role, role) for role in person_data["roles"]]

            person = Person(
                name=person_data["name"],
                roles=roles,
                blockout_dates=blockout_dates,
                preaching_dates=preaching_dates,
                teaching_dates=teaching_dates,
                on_leave=person_data.get("on_leave", False),
            )
            persons.append(person)

        self.logger.debug(f"Team Data:\n{[str(p) for p in persons]}\n")

        return persons

    def initialize_preachers(self) -> List[Preacher]:
        """
        Initializes and returns a list of Preacher objects.

        Returns:
            List[Preacher]: A list of initialized Preacher objects.
        """
        with open(resource_path(PREACHING_DATA_FILE_PATH), "r") as f:
            preaching_data = json.load(f)

        preachers = []
        for data in preaching_data:
            preaching_dates = [self.parse_date(d) for d in data.get("dates", [])]
            preacher = Preacher(
                name=data["name"],
                graphics_support=data["graphics"],
                dates=preaching_dates,
            )
            preachers.append(preacher)

        self.logger.debug(f"Preacher Data:\n{[str(p) for p in preachers]}\n")

        return preachers

    def initialize_rotation(self) -> List[str]:
        """
        Initializes and returns a list of names.

        Returns:
            List[str]: A list of names.
        """
        with open(resource_path(ROTATION_DATA_FILE_PATH), "r") as f:
            names = json.load(f)

        self.logger.debug(f"Rotation Data:\n{[str(name) for name in names]}\n")

        return names

    def initialize_team(self):
        """
        Initializes and returns person, preachers, and rotation.

        Returns:
            tuple: A tuple containing a list of Person objects, Preacher objects and rotation names.
        """
        return (
            self.initialize_persons(),
            self.initialize_preachers(),
            self.initialize_rotation(),
        )
