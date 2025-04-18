from enum import StrEnum
from typing import List


class Role(StrEnum):
    """
    Enumeration representing different roles that can be assigned in an event.

    Attributes:
        WORSHIPLEADER (str): Worship leader role.
        EMCEE (str): Emcee role.
        ACOUSTIC (str): Acoustic guitar role.
        KEYS (str): Keys role.
        DRUMS (str): Drums role.
        BASS (str): Bass role.
        AUDIO (str): Audio role.
        LIVE (str): Livestream role.
        LYRICS (str): Lyrics projection role.
        SUNDAYSCHOOLTEACHER (str): Sunday school teacher role.
        BACKUP (str): Backup singer role.

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
            list: A list of Role enum members in their default schedule order.
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
