# Third-Party Imports
import pytest

# Standard Library Imports
from datetime import date

# Local Imports
from schedule_builder.builders.schedule import Schedule
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from schedule_builder.models.role import Role


def test_build_schedule():
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
    schedule = Schedule(team=team_input, event_dates=event_dates)

    # Act
    events, team_output = schedule.build()

    # Assert
    assert len(events) == 2
    assert team_output == team_input


@pytest.mark.parametrize("team_data", [None, []])
def test_build_schedule_with_no_team(team_data):
    # Arrange
    event_dates = [date(2024, 6, 30), date(2024, 7, 7)]
    schedule = Schedule(team=team_data, event_dates=event_dates)

    # Act
    events, team = schedule.build()

    # Assert
    assert events == []
    assert team == []


def test_get_eligible_person_when_eligible():
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
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person == person1


@pytest.mark.parametrize("team", [None, []])
def test_get_eligible_person_with_no_team(team):
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    event_dates = [reference_date]
    event = Event(date=reference_date, team=team)
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_with_no_valid_role():
    # Arrange
    role = Role.SUNDAYSCHOOLTEACHER
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
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_persons = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_persons is None


def test_get_eligible_person_when_on_leave():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=True,
    )

    team = [person]
    event = Event(date=reference_date, team=team)
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_with_blockout():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[reference_date],
        preaching_dates=[],
        on_leave=False,
    )

    team = [person]
    event = Event(date=reference_date, team=team)
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_with_preaching():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[reference_date],
        on_leave=False,
    )

    team = [person]
    event = Event(date=reference_date, team=team)
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_with_3_consecutive_assigned_dates():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 21)
    assigned_dates = [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)]
    event_dates = [assigned_dates, reference_date]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    for assigned_date in assigned_dates:
        person.assign_event(event_date=assigned_date, role=Role.ACOUSTIC)

    team = [person]
    event = Event(date=reference_date, team=team)
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_with_2_consecutive_same_role_assignments():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 14)
    assigned_dates = [date(2024, 6, 30), date(2024, 7, 7)]
    event_dates = [assigned_dates, reference_date]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    team = [person]
    event1_date = date(2024, 6, 30)
    event1 = Event(date=event1_date, team=team)
    event1.assign_role(role=role, person=person)

    event2_date = date(2024, 7, 7)
    event2 = Event(date=event2_date, team=team)
    event2.assign_role(role=role, person=person)

    event3 = Event(date=reference_date, team=team)

    schedule = Schedule(team=team, event_dates=event_dates)
    schedule.events = [event1, event2]

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event3)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_when_worship_leader_within_4_weeks_ago():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 7, 28)
    assigned_date = date(2024, 6, 30)
    event_dates = [
        assigned_date,
        date(2024, 7, 7),
        date(2024, 7, 14),
        date(2024, 7, 21),
        reference_date,
    ]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    team = [person]
    event = Event(date=assigned_date, team=team)
    event.assign_role(role=role, person=person)

    schedule = Schedule(team=team, event_dates=event_dates)
    schedule.events = [event]

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_when_worship_leader_over_5_weeks_ago():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 8, 4)
    assigned_date = date(2024, 6, 23)
    event_dates = [
        assigned_date,
        date(2024, 6, 30),
        date(2024, 7, 7),
        date(2024, 7, 14),
        date(2024, 7, 21),
        date(2024, 7, 28),
        reference_date,
    ]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    team = [person]
    event = Event(date=assigned_date, team=team)
    event.assign_role(role=role, person=person)

    next_event = Event(date=reference_date, team=team)

    schedule = Schedule(team=team, event_dates=event_dates)
    schedule.events = [event]

    # Act
    eligible_person = schedule.get_eligible_person(
        role=role, team=team, event=next_event
    )

    # Assert
    assert eligible_person == person


def test_get_eligible_person_for_next_worship_leader_in_rotation():
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
    schedule = Schedule(team=team, event_dates=event_dates, rotation=rotation)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person == person3


def test_get_eligible_person_for_worship_leader_with_preaching_next_week():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 6, 30)
    preaching_date = date(2024, 7, 7)
    event_dates = [reference_date, preaching_date]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[preaching_date],
        on_leave=False,
    )
    team = [person]
    event = Event(date=reference_date, team=team)
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person is None


@pytest.mark.parametrize(
    "role, is_eligible", [(Role.WORSHIPLEADER, False), (Role.ACOUSTIC, True)]
)
def test_get_eligible_person_for_worship_leader_with_teaching_on_same_date(
    role, is_eligible
):
    # Arrange
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    person = Person(
        name="TestName1",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[reference_date],
        on_leave=False,
    )
    team = [person]
    event = Event(date=reference_date, team=team)
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person == (person if is_eligible else None)


@pytest.mark.parametrize(
    "preacher_name, is_eligible", [("Edmund", True), ("TestPreacher", False)]
)
def test_get_eligible_person_for_special_condition_1(preacher_name, is_eligible):
    # Arrange
    role = Role.EMCEE
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    person = Person(
        name="Lulu",
        roles=[role],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )
    preacher = Preacher(
        name=preacher_name, graphics_support="Test", dates=[reference_date]
    )

    team = [person]
    preachers = [preacher]
    event = Event(date=reference_date, team=team, preachers=preachers)
    schedule = Schedule(team=team, event_dates=event_dates, preachers=preachers)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert

    assert eligible_person == (person if is_eligible else None)


@pytest.mark.parametrize(
    "role, preacher_name, is_eligible",
    [
        (Role.WORSHIPLEADER, "Kris", False),  # Expected Role and Preacher
        (Role.WORSHIPLEADER, "TestPreacher", True),  # Unexpected Preacher
        (Role.BACKUP, "Kris", True),  # Unexpected Role
    ],
)
def test_get_eligible_person_for_special_condition_2(role, preacher_name, is_eligible):
    # Arrange
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    person = Person(
        name="Gee",
        roles=[role],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )
    preacher = Preacher(
        name=preacher_name, graphics_support="Test", dates=[reference_date]
    )

    team = [person]
    preachers = [preacher]
    event = Event(date=reference_date, team=team, preachers=preachers)
    schedule = Schedule(team=team, event_dates=event_dates, preachers=preachers)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person == (person if is_eligible else None)


@pytest.mark.parametrize(
    "person_name, is_eligible",
    [
        ("Kris", True),  # Expected Acoustic Person
        ("TestName", False),  # Unexpected Acoustic Person
    ],
)
def test_get_eligible_person_for_special_condition_3(person_name, is_eligible):
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    person1 = Person(
        name="TestName1",
        roles=[Role.ACOUSTIC],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )
    person2 = Person(
        name=person_name,
        roles=[Role.ACOUSTIC],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )
    person3 = Person(
        name="TestName3",
        roles=[Role.ACOUSTIC],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )
    preacher = Preacher(
        name="TestPreacher", graphics_support="Test", dates=[reference_date]
    )
    worship_leader = Person(
        name="Gee",
        roles=[Role.WORSHIPLEADER],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )

    team = [person1, person2, person3, worship_leader]
    preachers = [preacher]
    event = Event(date=reference_date, team=team, preachers=preachers)
    event.roles[Role.WORSHIPLEADER] = worship_leader.name
    schedule = Schedule(team=team, event_dates=event_dates, preachers=preachers)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, event=event)

    # Assert
    assert eligible_person == (person2 if is_eligible else None)


@pytest.mark.parametrize(
    "person_to_assign_name, assigned_person_name, is_eligible",
    [
        ("Jeff", "Mariel", False),
        ("Mariel", "Jeff", False),
        ("Jeff", "TestName", True),
        ("Mariel", "TestName", True),
        ("TestName", "Jeff", True),
    ],
)
def test_get_eligible_person_for_special_condition_4(
    person_to_assign_name, assigned_person_name, is_eligible
):
    # Arrange
    event_date = date(2025, 4, 6)
    role_to_assign = Role.ACOUSTIC
    person_to_assign = Person(
        name=person_to_assign_name,
        roles=[role_to_assign],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )
    assigned_role = Role.LYRICS
    assigned_person = Person(
        name=assigned_person_name,
        roles=[assigned_role],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )
    team = [person_to_assign, assigned_person]
    preacher = Preacher(
        name="TestPreacher", graphics_support="Test", dates=[event_date]
    )
    preachers = [preacher]
    event = Event(
        date=event_date,
        team=team,
        preachers=preachers,
    )
    event.assign_role(role=assigned_role, person=assigned_person)
    schedule = Schedule(team=team, event_dates=[event_date], preachers=preachers)

    # Act
    eligible_person = schedule.get_eligible_person(
        role=role_to_assign, team=team, event=event
    )

    # Assert
    expected_person = person_to_assign if is_eligible else None
    assert eligible_person == expected_person
