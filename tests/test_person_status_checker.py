# Standard Library Imports
import pytest
from datetime import date

# Local Imports
from schedule_builder.helpers.person_status_checker import PersonStatusChecker
from schedule_builder.models.person import Person
from schedule_builder.models.person_status import PersonStatus
from schedule_builder.models.role import Role


@pytest.mark.parametrize(
    "roles, on_leave, blockout_dates, assigned_dates, preaching_dates, teaching_dates, expected_status",
    [
        ([Role.WORSHIPLEADER], True, [], [], [], [], PersonStatus.ONLEAVE),
        (
            [Role.WORSHIPLEADER],
            False,
            [date(2025, 4, 27)],
            [],
            [],
            [],
            PersonStatus.BLOCKEDOUT,
        ),
        (
            [Role.WORSHIPLEADER],
            False,
            [],
            [date(2025, 4, 27)],
            [],
            [],
            PersonStatus.ASSIGNED,
        ),
        (
            [Role.WORSHIPLEADER],
            False,
            [],
            [],
            [date(2025, 4, 27)],
            [],
            PersonStatus.PREACHING,
        ),
        (
            [Role.WORSHIPLEADER],
            False,
            [],
            [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)],
            [],
            [],
            PersonStatus.BREAK,
        ),
        (
            [Role.WORSHIPLEADER],
            False,
            [],
            [],
            [],
            [date(2025, 4, 27)],
            PersonStatus.TEACHING,
        ),
        (
            [Role.ACOUSTIC],
            False,
            [],
            [],
            [],
            [date(2025, 4, 27)],
            PersonStatus.UNASSIGNED,
        ),
        ([Role.WORSHIPLEADER], False, [], [], [], [], PersonStatus.UNASSIGNED),
    ],
)
def test_get_status(
    roles,
    on_leave,
    blockout_dates,
    assigned_dates,
    preaching_dates,
    teaching_dates,
    expected_status,
):
    # Arrange
    person = Person(
        name="TestName",
        roles=roles,
        blockout_dates=blockout_dates,
        preaching_dates=preaching_dates,
        on_leave=on_leave,
        teaching_dates=teaching_dates,
    )
    person.assigned_dates = assigned_dates
    check_date = date(2025, 4, 27)

    # Act
    status = PersonStatusChecker.get_status(person=person, check_date=check_date)

    # Assert
    assert status == expected_status


@pytest.mark.parametrize(
    "on_leave, blockout_dates, assigned_dates, preaching_dates, teaching_dates, expected_status",
    [
        (
            True,
            [date(2025, 4, 27)],
            [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20), date(2025, 4, 27)],
            [date(2025, 4, 27)],
            [date(2025, 4, 27)],
            PersonStatus.ONLEAVE,
        ),
        (
            False,
            [date(2025, 4, 27)],
            [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20), date(2025, 4, 27)],
            [date(2025, 4, 27)],
            [date(2025, 4, 27)],
            PersonStatus.BLOCKEDOUT,
        ),
        (
            False,
            [],
            [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20), date(2025, 4, 27)],
            [date(2025, 4, 27)],
            [date(2025, 4, 27)],
            PersonStatus.ASSIGNED,
        ),
        (
            False,
            [],
            [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)],
            [date(2025, 4, 27)],
            [date(2025, 4, 27)],
            PersonStatus.PREACHING,
        ),
        (
            False,
            [],
            [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)],
            [],
            [date(2025, 4, 27)],
            PersonStatus.BREAK,
        ),
        (False, [], [], [], [date(2025, 4, 27)], PersonStatus.TEACHING),
        (False, [], [], [], [], PersonStatus.UNASSIGNED),
    ],
)
def test_get_status_priority(
    on_leave,
    blockout_dates,
    assigned_dates,
    preaching_dates,
    teaching_dates,
    expected_status,
):
    # Arrange
    person = Person(
        name="TestName",
        roles=[Role.WORSHIPLEADER],
        blockout_dates=blockout_dates,
        preaching_dates=preaching_dates,
        on_leave=on_leave,
        teaching_dates=teaching_dates,
    )
    person.assigned_dates = assigned_dates
    check_date = date(2025, 4, 27)

    # Act
    status = PersonStatusChecker.get_status(person=person, check_date=check_date)

    # Assert
    assert status == expected_status
