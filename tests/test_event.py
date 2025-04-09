# Third-Party Imports
import pytest

# Standard Library Imports
from datetime import date

# Local Imports
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from schedule_builder.models.role import Role


def test_assign_role():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    event = Event(date=reference_date, team=[person])

    # Act
    event.assign_role(role=role, person=person)
    assigned_name = event.roles[role]
    last_assigned_date = person.last_assigned_dates[role]

    # Assert
    assert assigned_name == person.name
    assert reference_date in person.assigned_dates
    assert last_assigned_date == reference_date

def test_assign_role_when_role_already_assigned():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person1 = Person(name='TestName',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    person2 = Person(name='TestName2',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    
    event = Event(date=reference_date, team=[person1, person2])

    # Act
    event.assign_role(role=role, person=person1)

    # Assert
    with pytest.raises(ValueError):
        event.assign_role(role=role, person=person2)

def test_assign_role_when_role_is_invalid():
    # Arrange
    role = "InvalidRole"
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    event = Event(date=reference_date, team=[person])

    # Assert
    with pytest.raises(ValueError):
        event.assign_role(role=role, person=person)

def test_get_assigned_roles():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    event = Event(date=reference_date, team=[person])

    # Act
    event.assign_role(role=role, person=person)
    assigned_roles = event.get_assigned_roles()

    # Assert
    assert len(assigned_roles) == 1
    assert role in assigned_roles

def test_get_unassigned_roles():
    # Arrange
    unassigned_role = Role.SUNDAYSCHOOLTEACHER
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    event = Event(date=reference_date, team=[person])
    for role in Role:
        if role != unassigned_role:
            event.roles[role] = "Test Person"

    # Act
    unassigned_roles = event.get_unassigned_roles()

    # Assert
    assert len(unassigned_roles) == 1
    assert unassigned_role in unassigned_roles

def test_get_unassigned_names():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person1 = Person(name='AssignedName',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    person2 = Person(name='UnassignedName',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    
    event = Event(date=reference_date, team=[person1, person2])

    # Act
    event.assign_role(role=role, person=person1)
    unassigned_names = event.get_unassigned_names()

    # Assert
    assert len(unassigned_names) == 1
    assert person2.name in unassigned_names

def test_get_person_by_name():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person1 = Person(name='TestOne',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    person2 = Person(name='TestTwo',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    
    event = Event(date=reference_date, team=[person1, person2])

    # Act
    person = event.get_person_by_name(name=person2.name)

    # Assert
    assert person == person2

def test_get_person_by_name_with_invalid_name():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person1 = Person(name='TestOne',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    person2 = Person(name='TestTwo',
                     roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                     blockout_dates=[],
                     preaching_dates=[],
                     on_leave=False)
    
    event = Event(date=reference_date, team=[person1, person2])

    # Act
    person = event.get_person_by_name(name="UnknownName")

    # Assert
    assert person == None

def test_get_person_status_on_date_when_on_leave():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='AssignedName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[reference_date],
                    preaching_dates=[reference_date],
                    on_leave=True)
    
    person.assigned_dates = [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)]
    event = Event(date=reference_date, team=[person])

    # Act
    status = event.get_person_status_on_date(person=person, date=reference_date)

    # Assert
    assert status == "ON-LEAVE"

def test_get_person_status_on_date_when_blockout():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='AssignedName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[reference_date],
                    preaching_dates=[reference_date],
                    on_leave=False)
    
    person.assigned_dates = [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)]
    event = Event(date=reference_date, team=[person])

    # Act
    status = event.get_person_status_on_date(person=person, date=reference_date)

    # Assert
    assert status == "BLOCKOUT"

def test_get_person_status_on_date_when_assigned():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='AssignedName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[reference_date],
                    on_leave=False)
    
    person.assigned_dates = [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14), reference_date]
    event = Event(date=reference_date, team=[person])

    # Act
    status = event.get_person_status_on_date(person=person, date=reference_date)

    # Assert
    assert status == "ASSIGNED"

def test_get_person_status_on_date_when_preaching():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='AssignedName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[reference_date],
                    on_leave=False)
    
    person.assigned_dates = [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)]
    event = Event(date=reference_date, team=[person])

    # Act
    status = event.get_person_status_on_date(person=person, date=reference_date)

    # Assert
    assert status == "PREACHING"

def test_get_person_status_on_date__when_on_break():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='AssignedName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    person.assigned_dates = [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)]
    event = Event(date=reference_date, team=[person])

    # Act
    status = event.get_person_status_on_date(person=person, date=reference_date)

    # Assert
    assert status == "BREAK"

def test_get_person_status_on_date_teaching_with_worship_leader_role():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='AssignedName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    teaching_dates=[reference_date],
                    on_leave=False)
    
    person.assigned_dates = [date(2024, 6, 30), date(2024, 7, 7)]
    event = Event(date=reference_date, team=[person])

    # Act
    status = event.get_person_status_on_date(person=person, date=reference_date)

    # Assert
    assert status == "TEACHING"

def test_get_person_status_on_date_teaching_without_worship_leader_role():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='AssignedName',
                    roles=[Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    teaching_dates=[reference_date],
                    on_leave=False)
    
    person.assigned_dates = [date(2024, 6, 30), date(2024, 7, 7)]
    event = Event(date=reference_date, team=[person])

    # Act
    status = event.get_person_status_on_date(person=person, date=reference_date)

    # Assert
    assert status == "UNASSIGNED"

def test_get_person_status_on_date_when_unassigned():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='AssignedName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    teaching_dates=[],
                    on_leave=False)
    
    person.assigned_dates = [date(2024, 6, 30), date(2024, 7, 7)]
    event = Event(date=reference_date, team=[person])

    # Act
    status = event.get_person_status_on_date(person=person, date=reference_date)

    # Assert
    assert status == "UNASSIGNED"

def test_get_assigned_preacher():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    preacher1 = Preacher(name='TestPreacher1',
                         graphics_support='TestGraphics1',
                         dates=[reference_date])
    preacher2 = Preacher(name='TestPreacher2',
                         graphics_support='TestGraphics2',
                         dates=[date(2024, 7, 14)])
    
    event = Event(date=reference_date, team=[person], preachers=[preacher1, preacher2])

    # Act
    preacher = event.get_assigned_preacher()

    # Assert
    assert preacher == preacher1

def test_get_assigned_preacher_when_no_preacher():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    preacher1 = Preacher(name='TestPreacher1',
                         graphics_support='TestGraphics1',
                         dates=[date(2024, 7, 14)])
    preacher2 = Preacher(name='TestPreacher2',
                         graphics_support='TestGraphics2',
                         dates=[date(2024, 7, 21)])
    
    event = Event(date=reference_date, team=[person], preachers=[preacher1, preacher2])

    # Act
    preacher = event.get_assigned_preacher()

    # Assert
    assert preacher == None

def test_is_assignable_if_needed():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    event = Event(date=reference_date, team=[person])

    # Act
    is_assignable = event.is_assignable_if_needed(role=role, person=person)

    # Assert
    assert is_assignable == True

def test_is_assignable_if_needed_when_on_leave():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=True)
    event = Event(date=reference_date, team=[person])

    # Act
    is_assignable = event.is_assignable_if_needed(role=role, person=person)

    # Assert
    assert is_assignable == False

def test_is_assignable_if_needed_when_not_capable_of_role():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.AUDIO],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    event = Event(date=reference_date, team=[person])

    # Act
    is_assignable = event.is_assignable_if_needed(role=role, person=person)

    # Assert
    assert is_assignable == False

def test_is_assignable_if_needed_when_blocked_out():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[reference_date],
                    preaching_dates=[],
                    on_leave=False)
    event = Event(date=reference_date, team=[person])

    # Act
    is_assignable = event.is_assignable_if_needed(role=role, person=person)

    # Assert
    assert is_assignable == False

def test_is_assignable_if_needed_when_preaching():
    # Arrange
    role = Role.ACOUSTIC
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[reference_date],
                    on_leave=False)
    event = Event(date=reference_date, team=[person])

    # Act
    is_assignable = event.is_assignable_if_needed(role=role, person=person)

    # Assert
    assert is_assignable == False