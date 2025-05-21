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
    person = Person(
        name="TestName",
        roles=[Role.WORSHIPLEADER, role_one, role_two],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    # Act
    person.assign_event(event_date=date_one, role=role_one)
    person.assign_event(event_date=date_two, role=role_two)

    # Assert
    assert len(person.assigned_dates) == 2
    assert date_one in person.assigned_dates
    assert date_two in person.assigned_dates
    assert person.last_assigned_dates[role_one] == date_one
    assert person.last_assigned_dates[role_two] == date_two
    assert date_one in person.role_assigned_dates[role_one]
    assert date_two in person.role_assigned_dates[role_two]


def test_unassign_event():
    # Arrange
    date_one = date(2024, 6, 30)
    role_one = Role.ACOUSTIC
    date_two = date(2024, 7, 14)
    role_two = Role.LYRICS
    person = Person(
        name="TestName",
        roles=[Role.WORSHIPLEADER, role_one, role_two],
        blockout_dates=[],
        preaching_dates=[],
        on_leave=False,
    )

    person.assign_event(event_date=date_one, role=role_one)
    person.assign_event(event_date=date_two, role=role_two)

    # Act
    person.unassign_event(event_date=date_one, role=role_one)

    # Assert
    assert len(person.assigned_dates) == 1
    assert date_one not in person.assigned_dates
    assert date_two in person.assigned_dates
    assert person.last_assigned_dates[role_one] is None
    assert person.last_assigned_dates[role_two] == date_two
    assert date_one not in person.role_assigned_dates[role_one]
    assert date_two in person.role_assigned_dates[role_two]


@pytest.mark.parametrize(
    "reference_date, preaching_dates, expected",
    [
        (date(2024, 7, 7), [], None),  # No dates
        (
            date(2024, 7, 7),
            [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)],
            date(2024, 7, 7),
        ),  # Same Date
        (
            date(2024, 7, 21),
            [date(2024, 6, 30), date(2024, 7, 7), date(2024, 7, 14)],
            None,
        ),  # Past Dates Only
        (
            date(2024, 7, 7),
            [date(2024, 6, 30), date(2024, 7, 21), date(2024, 8, 4)],
            date(2024, 7, 21),
        ),  # Future Date
    ],
)
def test_get_next_preaching_date(reference_date, preaching_dates, expected):
    # Arrange
    person = Person(
        name="TestName",
        roles=[Role.WORSHIPLEADER, Role.ACOUSTIC, Role.LYRICS],
        blockout_dates=[],
        preaching_dates=preaching_dates,
        on_leave=False,
    )

    # Act
    next_preaching_date = person.get_next_preaching_date(reference_date=reference_date)

    # Assert
    assert next_preaching_date == expected
