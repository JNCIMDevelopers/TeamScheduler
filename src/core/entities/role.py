from enum import StrEnum
from typing import List


class Role(StrEnum):
    """
    Enum for event roles.

    The roles are listed in descending order of priority for assignment.
    """

    WORSHIP_LEADER = "WORSHIP LEADER"
    EMCEE = "EMCEE"
    ACOUSTIC = "ACOUSTIC GUITAR"
    KEYS = "KEYS"
    DRUMS = "DRUMS"
    BASS = "BASS"
    AUDIO = "AUDIO"
    LIVE = "LIVE"
    LYRICS = "LYRICS"
    SUNDAY_SCHOOL_TEACHER = "SUNDAY SCHOOL TEACHER"
    BACKUP = "BACKUP"

    @staticmethod
    def get_assignment_order() -> List["Role"]:
        """
        Returns the order in which roles should be assigned during scheduling.

        Returns:
            List[Role]: Roles in priority order for assignment.
        """
        return [
            Role.WORSHIP_LEADER,
            Role.EMCEE,
            Role.ACOUSTIC,
            Role.KEYS,
            Role.DRUMS,
            Role.BASS,
            Role.AUDIO,
            Role.LIVE,
            Role.LYRICS,
            Role.BACKUP,
            Role.SUNDAY_SCHOOL_TEACHER,
        ]

    @staticmethod
    def get_display_order() -> List["Role"]:
        """
        Returns the order for displaying roles in schedules and UI.

        Returns:
            List[Role]: Roles in display order.
        """
        return [
            Role.EMCEE,
            Role.WORSHIP_LEADER,
            Role.ACOUSTIC,
            Role.KEYS,
            Role.DRUMS,
            Role.BASS,
            Role.AUDIO,
            Role.LIVE,
            Role.LYRICS,
            Role.BACKUP,
            Role.SUNDAY_SCHOOL_TEACHER,
        ]
