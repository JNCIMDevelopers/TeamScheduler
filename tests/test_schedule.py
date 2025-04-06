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


def test_get_eligible_person_when_eligible():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person1 = Person(name='TestName1',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    person2 = Person(name='TestName2',
                     roles=[Role.BASS, Role.DRUMS, Role.LIVE],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    
    team = [person1, person2]
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person == person1

@pytest.mark.parametrize('team', [None, []])
def test_get_eligible_person_with_no_team(team):
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    event_dates = [reference_date]
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None


def test_get_eligible_person_with_no_valid_role():
    # Arrange
    role = Role.SUNDAYSCHOOLTEACHER
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person1 = Person(name='TestName1',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    person2 = Person(name='TestName2',
                     roles=[Role.BASS, Role.DRUMS, Role.LIVE],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    
    team = [person1, person2]
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_persons = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_persons is None

def test_get_eligible_person_when_on_leave():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=True)
    
    team = [person]
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None

def test_get_eligible_person_with_blockout():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[reference_date],
                    preaching_dates=[],
                    on_leave=False)
    
    team = [person]
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None

def test_get_eligible_person_with_preaching():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 7)
    event_dates = [date(2024, 6, 30), reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[reference_date],
                    on_leave=False)
    
    team = [person]
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None

def test_get_eligible_person_with_3_consecutive_assigned_dates():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 21)
    assigned_dates = [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)]
    event_dates = [assigned_dates, reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    for assigned_date in assigned_dates:
        person.assign_event(date=assigned_date, role=Role.ACOUSTIC)

    team = [person]
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None

def test_get_eligible_person_with_2_consecutive_same_role_assignments():
    # Arrange
    role = Role.LYRICS
    reference_date = date(2024, 7, 14)
    assigned_dates = [date(2024, 6, 30), date(2024, 7, 7)]
    event_dates = [assigned_dates, reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)

    team = [person]
    event1_date = date(2024, 6, 30)
    event1 = Event(date=event1_date, team=team)
    event1.assign_role(role=role, person=person)

    event2_date = date(2024, 7, 7)
    event2 = Event(date=event2_date, team=team)
    event2.assign_role(role=role, person=person)
    
    schedule = Schedule(team=team, event_dates=event_dates)
    schedule.events=[event1, event2]

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None

def test_get_eligible_person_when_worship_leader_within_4_weeks_ago():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 7, 28)
    assigned_date = date(2024, 6, 30)
    event_dates = [assigned_date, date(2024, 7, 7), date(2024, 7, 14), date(2024, 7, 21), reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    team = [person]
    event = Event(date=assigned_date, team=team)
    event.assign_role(role=role, person=person)

    schedule = Schedule(team=team, event_dates=event_dates)
    schedule.events = [event]

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None

def test_get_eligible_person_when_worship_leader_over_5_weeks_ago():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 8, 4)
    assigned_date = date(2024, 6, 23)
    event_dates = [assigned_date, date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14), date(2024, 7, 21), date(2024, 7, 28), reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    team = [person]
    event = Event(date=assigned_date, team=team)
    event.assign_role(role=role, person=person)

    schedule = Schedule(team=team, event_dates=event_dates)
    schedule.events = [event]

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person == person

def test_get_eligible_person_for_worship_leader_with_preaching_next_week():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 6, 30)
    preaching_date = date(2024, 7, 7)
    event_dates = [reference_date, preaching_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[preaching_date],
                    on_leave=False)
    team = [person]
    
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None

def test_get_eligible_person_for_worship_leader_with_teaching_on_same_date():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    teaching_dates=[reference_date],
                    on_leave=False)
    team = [person]
    
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person is None

def test_get_eligible_person_for_non_worship_leader_role_with_teaching_on_same_date():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    person = Person(name='TestName1',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    teaching_dates=[reference_date],
                    on_leave=False)
    team = [person]
    
    schedule = Schedule(team=team, event_dates=event_dates)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date)

    # Assert
    assert eligible_person == person

def test_get_eligible_person_for_worshipleader_when_special_condition_pastor_preaching():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    person1 = Person(name='NotGee',
                     roles=[role],
                     blockout_dates=[],
                     preaching_dates=[],
                     teaching_dates=[],
                     on_leave=False)
    person2 = Person(name='Gee',
                     roles=[role],
                     blockout_dates=[],
                     preaching_dates=[],
                     teaching_dates=[],
                     on_leave=False)
    preacher = Preacher(name='Kris',
                        graphics_support='Test',
                        dates=[reference_date])
    
    team = [person1, person2]
    preachers = [preacher]

    schedule = Schedule(team=team, event_dates=event_dates, preachers=preachers)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date, preacher_name=preacher.name)

    # Assert
    assert eligible_person == person1

def test_get_eligible_person_for_other_role_when_special_condition_pastor_preaching():
    # Arrange
    role = Role.BACKUP
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    special_person = Person(name='Gee',
                            roles=[Role.WORSHIPLEADER, role],
                            blockout_dates=[],
                            preaching_dates=[],
                            teaching_dates=[],
                            on_leave=False)
    preacher = Preacher(name='Kris',
                        graphics_support='Test',
                        dates=[reference_date])
    
    team = [special_person]
    preachers = [preacher]

    schedule = Schedule(team=team, event_dates=event_dates, preachers=preachers)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date, preacher_name=preacher.name)

    # Assert
    assert eligible_person == special_person

def test_get_eligible_person_for_worshipleader_when_special_condition_pastor_is_not_preaching():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]
    special_person = Person(name='Gee',
                            roles=[role],
                            blockout_dates=[],
                            preaching_dates=[],
                            teaching_dates=[],
                            on_leave=False)
    preacher = Preacher(name='TestPreacher',
                        graphics_support='Test',
                        dates=[reference_date])
    
    team = [special_person]
    preachers = [preacher]

    schedule = Schedule(team=team, event_dates=event_dates, preachers=preachers)

    # Act
    eligible_person = schedule.get_eligible_person(role=role, team=team, date=reference_date, preacher_name=preacher.name)

    # Assert
    assert eligible_person == special_person

def test_get_next_worship_leader():
    # Arrange
    role = Role.WORSHIPLEADER
    reference_date = date(2024, 6, 30)
    event_dates = [reference_date]

    person1 = Person(name='Test1',
                        roles=[role],
                        blockout_dates=[],
                        preaching_dates=[],
                        teaching_dates=[],
                        on_leave=False)
    person2 = Person(name='Test2',
                        roles=[role],
                        blockout_dates=[],
                        preaching_dates=[],
                        teaching_dates=[],
                        on_leave=False)
    person3 = Person(name='Test3',
                        roles=[role],
                        blockout_dates=[],
                        preaching_dates=[],
                        teaching_dates=[],
                        on_leave=False)
    preacher = Preacher(name='TestPreacher',
                        graphics_support='Test',
                        dates=[reference_date])
    
    team = [person1, person2, person3]
    preachers = [preacher]
    rotation = [person2.name, person3.name, person1.name]

    schedule = Schedule(team=team, event_dates=event_dates, preachers=preachers, rotation=rotation)

    # Act
    worship_leader = schedule.get_next_worship_leader(eligible_persons=team)
    next_worship_leader = schedule.get_next_worship_leader(eligible_persons=team)
    next_next_worship_leader = schedule.get_next_worship_leader(eligible_persons=team)

    # Assert
    assert worship_leader == person2
    assert next_worship_leader == person3
    assert next_next_worship_leader == person1