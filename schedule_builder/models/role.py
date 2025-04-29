from enum import StrEnum
from typing import List


class Role(StrEnum):
    """
    Enum for event roles.

    Attributes:
        WORSHIPLEADER, EMCEE, ACOUSTIC, KEYS, DRUMS, BASS, AUDIO, LIVE, LYRICS, SUNDAYSCHOOLTEACHER, BACKUP

    Note: The roles are listed in descending order of priority.
    """

    WORSHIPLEADER = "WORSHIP LEADER"
    EMCEE = "EMCEE"
    ACOUSTIC = "ACOUSTIC GUITAR"
    KEYS = "KEYS"
    DRUMS = "DRUMS"
    BASS = "BASS"
    AUDIO = "AUDIO"
    LIVE = "LIVE"
    LYRICS = "LYRICS"
    SUNDAYSCHOOLTEACHER = "SUNDAY SCHOOL TEACHER"
    BACKUP = "BACKUP"

    @staticmethod
    def get_schedule_order() -> List["Role"]:
        """
        Returns the default schedule order for roles in an event.

        This is the order displayed in the schedule and is not the priority order.

        Returns:
            List[Role]: A list of Role enum members in their default schedule order.
        """
        return [
            Role.EMCEE,
            Role.WORSHIPLEADER,
            Role.ACOUSTIC,
            Role.KEYS,
            Role.DRUMS,
            Role.BASS,
            Role.AUDIO,
            Role.LIVE,
            Role.LYRICS,
            Role.BACKUP,
            Role.SUNDAYSCHOOLTEACHER,
        ]
