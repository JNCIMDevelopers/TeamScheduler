# Third-Party Imports
import pytest

# Standard Library Imports
from datetime import date

# Local Imports
from schedule_builder.builders.schedule import Schedule
from schedule_builder.eligibility.eligibility_checker import EligibilityChecker
from schedule_builder.eligibility.rules import (
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
    KrisAcousticRule,
    JeffMarielAssignmentRule,
    MarkDrumsRule,
    AubreyAssignmentRule,
)
from schedule_builder.helpers.worship_leader_selector import WorshipLeaderSelector
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role


@pytest.fixture
def eligibility_checker():
    return EligibilityChecker(
        rules=[
            OnLeaveRule(),
            BlockoutDateRule(),
            PreachingDateRule(),
            RoleCapabilityRule(),
            WorshipLeaderTeachingRule(),
            ConsecutiveAssignmentLimitRule(),
            ConsecutiveRoleAssignmentLimitRule(assignment_limit=2),
            RoleTimeWindowRule(),
            WorshipLeaderPreachingConflictRule(),
            LuluEmceeRule(),
            GeeWorshipLeaderRule(),
            KrisAcousticRule(),
            JeffMarielAssignmentRule(),
            MarkDrumsRule(),
            AubreyAssignmentRule(),
        ]
    )


def test_build_schedule(eligibility_checker):
    # Arrange
    event_dates = [date(2024, 6, 30), date(2024, 7, 7)]
    person1 = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )
    person2 = Person(
        name="TestName2",
        roles=[Role.BASS, Role.DRUMS, Role.LIVE],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    team_input = [person1, person2]
    worship_leader_selector = WorshipLeaderSelector(rotation=[])
    schedule = Schedule(
        team=team_input,
        event_dates=event_dates,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )

    # Act
    events, team_output = schedule.build()

    # Assert
    assert len(events) == 2
    assert team_output == team_input


@pytest.mark.parametrize("team_data", [None, []])
def test_build_schedule_with_no_team(team_data, eligibility_checker):
    # Arrange
    event_dates = [date(2024, 6, 30), date(2024, 7, 7)]
    worship_leader_selector = WorshipLeaderSelector(rotation=[])
    schedule = Schedule(
        team=team_data,
        event_dates=event_dates,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )

    # Act
    events, team = schedule.build()

    # Assert
    assert events == []
    assert team == []


def test_get_eligible_person_when_eligible(eligibility_checker):
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person1 = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )
    person2 = Person(
        name="TestName2",
        roles=[Role.BASS, Role.DRUMS, Role.LIVE],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    team = [person1, person2]
    event = Event(date=reference_date, team=team)
    worship_leader_selector = WorshipLeaderSelector(rotation=[])
    schedule = Schedule(
        team=team,
        event_dates=event_dates,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person == person1


@pytest.mark.parametrize("team", [None, []])
def test_get_eligible_person_with_no_team(team, eligibility_checker):
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    event_dates = [reference_date]
    event = Event(date=reference_date, team=team)
    worship_leader_selector = WorshipLeaderSelector(rotation=[])
    schedule = Schedule(
        team=team,
        event_dates=event_dates,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_when_none_eligible(eligibility_checker):
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person1 = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )
    person2 = Person(
        name="TestName2",
        roles=[Role.BASS, Role.DRUMS, Role.LIVE],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    team = [person1, person2]
    event = Event(date=reference_date, team=team)
    worship_leader_selector = WorshipLeaderSelector(rotation=[])
    schedule = Schedule(
        team=team,
        event_dates=event_dates,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_for_next_worship_leader_in_rotation(eligibility_checker):
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 7, 7)
    event_dates = [reference_date, date(2024, 7, 14), date(2024, 7, 21)]
    person1 = Person(
        name="TestName1",
        roles=[role, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )
    person2 = Person(
        name="TestName2",
        roles=[role, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[reference_date],
        preaching_dates=[],
        on_leave=False,
    )
    person3 = Person(
        name="TestName3",
        roles=[role, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    team = [person1, person2, person3]
    rotation = [person2.name, person3.name, person1.name]
    event = Event(date=reference_date, team=team)
    worship_leader_selector = WorshipLeaderSelector(rotation=rotation)
    schedule = Schedule(
        team=team,
        event_dates=event_dates,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person == person3


def test_get_eligible_person_for_next_worship_leader_with_no_rotation(
    eligibility_checker,
):
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 7, 7)
    event_dates = [reference_date, date(2024, 7, 14), date(2024, 7, 21)]
    person1 = Person(
        name="TestName1",
        roles=[role, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )
    person2 = Person(
        name="TestName2",
        roles=[role, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[reference_date],
        preaching_dates=[],
        on_leave=False,
    )
    person3 = Person(
        name="TestName3",
        roles=[role, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    team = [person1, person2, person3]
    rotation = []
    event = Event(date=reference_date, team=team)
    worship_leader_selector = WorshipLeaderSelector(rotation=rotation)
    schedule = Schedule(
        team=team,
        event_dates=event_dates,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person in team
