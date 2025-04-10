# Third-Party Imports
import pytest

# Standard Library Imports
from datetime import date

# Local Imports
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role


def test_assign_event():
    # Arrange
    date_one = date(2024, 6, 30)
    role_one = Role.ACOUSTIC
    date_two = date(2024, 7, 14)
    role_two = Role.LYRICS
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, role_one, role_two],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)

    # Act
    person.assign_event(date=date_one, role=role_one)
    person.assign_event(date=date_two, role=role_two)

    # Assert
    assert len(person.assigned_dates) == 2
    assert date_one in person.assigned_dates
    assert date_two in person.assigned_dates
    assert person.last_assigned_dates[role_one] == date_one
    assert person.last_assigned_dates[role_two] == date_two


@pytest.mark.parametrize('p_dates', [None, []])
def test_get_next_preaching_date_with_no_dates(p_dates):
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=p_dates,
                    on_leave=False)
    
    # Act
    next_preaching_date = person.get_next_preaching_date(reference_date=reference_date)

    # Assert
    assert next_preaching_date is None

def test_get_next_preaching_date_with_past_dates_only():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)],
                    on_leave=False)
    
    # Act
    next_preaching_date = person.get_next_preaching_date(reference_date=reference_date)

    # Assert
    assert next_preaching_date is None

def test_get_next_preaching_date_when_same_date():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[date(2024, 6, 30), reference_date, date(2024, 7, 14)],
                    on_leave=False)
    
    # Act
    next_preaching_date = person.get_next_preaching_date(reference_date=reference_date)

    # Assert
    assert next_preaching_date == reference_date

def test_get_next_preaching_date_when_future_date():
    # Arrange
    reference_date = date(2024, 7, 7)
    next_date = date(2024, 7, 21)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[date(2024, 6, 30), next_date, date(2024, 8, 4)],
                    on_leave=False)
    
    # Act
    next_preaching_date = person.get_next_preaching_date(reference_date=reference_date)

    # Assert
    assert next_preaching_date == next_date

def test_was_not_assigned_too_recently_to_role():
    # Arrange
    last_assigned_date = date(2024, 6, 30)
    reference_date = date(2024, 7, 7)
    role = Role.ACOUSTIC
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, role, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=last_assigned_date, role=role)
    not_assigned_recently = person.was_not_assigned_too_recently_to_role(role=role, date=reference_date)

    # Assert
    assert not_assigned_recently == True

def test_was_not_assigned_too_recently_to_role_with_no_assignments():
    # Arrange
    reference_date = date(2024, 6, 30)
    role = Role.WORSHIPLEADER
    person = Person(name='TestName',
                    roles=[role, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    not_assigned_recently = person.was_not_assigned_too_recently_to_role(role=role, date=reference_date)

    # Assert
    assert not_assigned_recently == True

def test_was_not_assigned_too_recently_to_role_worship_leader_4_weeks_ago():
    # Arrange
    last_assigned_date = date(2025, 3, 8)
    reference_date = date(2025, 4, 5)
    role = Role.WORSHIPLEADER
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=last_assigned_date, role=role)
    not_assigned_recently = person.was_not_assigned_too_recently_to_role(role=role, date=reference_date)

    # Assert
    assert not_assigned_recently == False

def test_was_not_assigned_too_recently_to_role_worship_leader_over_4_weeks_ago():
    # Arrange
    last_assigned_date = date(2025, 3, 1)
    reference_date = date(2025, 4, 5)
    role = Role.WORSHIPLEADER
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=last_assigned_date, role=role)
    not_assigned_recently = person.was_not_assigned_too_recently_to_role(role=role, date=reference_date)

    # Assert
    assert not_assigned_recently == True

def test_was_not_assigned_too_recently_to_role_sunday_school_teacher_4_weeks_ago():
    # Arrange
    last_assigned_date = date(2024, 6, 30)
    reference_date = date(2024, 7, 28)
    role = Role.SUNDAYSCHOOLTEACHER
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=last_assigned_date, role=role)
    not_assigned_recently = person.was_not_assigned_too_recently_to_role(role=role, date=reference_date)

    # Assert
    assert not_assigned_recently == False

def test_was_not_assigned_too_recently_to_role_sunday_school_teacher_over_4_weeks_ago():
    # Arrange
    last_assigned_date = date(2024, 6, 30)
    reference_date = date(2024, 8, 4)
    role = Role.SUNDAYSCHOOLTEACHER
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=last_assigned_date, role=role)
    not_assigned_recently = person.was_not_assigned_too_recently_to_role(role=role, date=reference_date)

    # Assert
    assert not_assigned_recently == True

def test_was_not_assigned_too_recently_to_role_emcee_2_weeks_ago():
    # Arrange
    last_assigned_date = date(2025, 3, 23)
    reference_date = date(2025, 4, 6)
    role = Role.EMCEE
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=last_assigned_date, role=role)
    not_assigned_recently = person.was_not_assigned_too_recently_to_role(role=role, date=reference_date)

    # Assert
    assert not_assigned_recently == False

def test_was_not_assigned_too_recently_to_role_emcee_over_2_weeks_ago():
    # Arrange
    last_assigned_date = date(2025, 3, 16)
    reference_date = date(2025, 4, 6)
    role = Role.EMCEE
    person = Person(name='TestName',
                    roles=[role],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=last_assigned_date, role=role)
    not_assigned_recently = person.was_not_assigned_too_recently_to_role(role=role, date=reference_date)

    # Assert
    assert not_assigned_recently == True

@pytest.mark.parametrize('p_dates', [None, []])
def test_is_unavailable_due_to_preaching_with_no_dates(p_dates):
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=p_dates,
                    on_leave=False)
    
    # Act
    is_unavailable = person.is_unavailable_due_to_preaching(reference_date=reference_date)

    # Assert
    assert is_unavailable == False

def test_is_unavailable_due_to_preaching_with_past_dates_only():
    # Arrange
    reference_date = date(2024, 7, 21)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)],
                    on_leave=False)
    
    # Act
    is_unavailable = person.is_unavailable_due_to_preaching(reference_date=reference_date)

    # Assert
    assert is_unavailable is False

def test_is_unavailable_due_to_preaching_when_preaching_next_week():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[date(2024, 6, 30), date(2024, 7, 14)],
                    on_leave=False)
    
    # Act
    is_unavailable = person.is_unavailable_due_to_preaching(reference_date=reference_date)

    # Assert
    assert is_unavailable == True

def test_is_unavailable_due_to_preaching_when_same_date():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[reference_date],
                    on_leave=False)
    
    # Act
    is_unavailable = person.is_unavailable_due_to_preaching(reference_date=reference_date)

    # Assert
    assert is_unavailable == True

def test_is_unavailable_due_to_preaching_with_far_future_date():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[date(2024, 7, 21), date(2024, 8, 4)],
                    on_leave=False)
    
    # Act
    is_unavailable = person.is_unavailable_due_to_preaching(reference_date=reference_date)

    # Assert
    assert is_unavailable == False

def test_assigned_too_many_times_recently_with_no_dates():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    is_assigned_too_many_times = person.assigned_too_many_times_recently(reference_date=reference_date)

    # Assert
    assert is_assigned_too_many_times == False

def test_assigned_too_many_times_recently_with_2_consecutive_assigned_dates():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=date(2024, 6, 23), role=Role.WORSHIPLEADER)
    person.assign_event(date=date(2024, 6, 30), role=Role.ACOUSTIC)
    is_assigned_too_many_times = person.assigned_too_many_times_recently(reference_date=reference_date)

    # Assert
    assert is_assigned_too_many_times == False

def test_assigned_too_many_times_recently_with_2_total_consecutive_assigned_and_preaching_dates():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[date(2024, 6, 23)],
                    on_leave=False)
    
    # Act
    person.assign_event(date=date(2024, 6, 30), role=Role.ACOUSTIC)
    is_assigned_too_many_times = person.assigned_too_many_times_recently(reference_date=reference_date)

    # Assert
    assert is_assigned_too_many_times == False

def test_assigned_too_many_times_recently_with_3_assigned_dates():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[],
                    on_leave=False)
    
    # Act
    person.assign_event(date=date(2024, 6, 16), role=Role.WORSHIPLEADER)
    person.assign_event(date=date(2024, 6, 23), role=Role.ACOUSTIC)
    person.assign_event(date=date(2024, 6, 30), role=Role.LYRICS)
    is_assigned_too_many_times = person.assigned_too_many_times_recently(reference_date=reference_date)

    # Assert
    assert is_assigned_too_many_times == True

def test_assigned_too_many_times_recently_with_2_total_assigned_and_preaching_dates():
    # Arrange
    reference_date = date(2024, 7, 7)
    person = Person(name='TestName',
                    roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
                    blockout_dates=[],
                    preaching_dates=[date(2024, 6, 23)],
                    on_leave=False)
    
    # Act
    person.assign_event(date=date(2024, 6, 16), role=Role.ACOUSTIC)
    person.assign_event(date=date(2024, 6, 30), role=Role.LYRICS)
    is_assigned_too_many_times = person.assigned_too_many_times_recently(reference_date=reference_date)

    # Assert
    assert is_assigned_too_many_times == True