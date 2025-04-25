from enum import StrEnum


class PersonStatus(StrEnum):
    """
    Enum representing the status of a person in the schedule.
    """

    ONLEAVE = "ON-LEAVE"
    BLOCKEDOUT = "BLOCKEDOUT"
    ASSIGNED = "ASSIGNED"
    PREACHING = "PREACHING"
    BREAK = "BREAK"
    TEACHING = "TEACHING"
    UNASSIGNED = "UNASSIGNED"
