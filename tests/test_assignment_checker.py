# Third-Party Imports
import pytest

# Standard Library Imports
from datetime import date

# Local Imports
from schedule_builder.util.assignment_checker import (
    has_exceeded_consecutive_assignments,
)


@pytest.mark.parametrize(
    "assigned_dates, preaching_dates, reference_date, limit, expected",
    [
        (
            [date(2025, 4, 13), date(2025, 4, 20)],
            [],
            date(2025, 4, 27),
            2,
            True,
        ),  # Assigned dates reach limit
        (
            [],
            [date(2025, 4, 13), date(2025, 4, 20)],
            date(2025, 4, 27),
            2,
            True,
        ),  # Preaching dates reach limit
        (
            [date(2025, 4, 20)],
            [date(2025, 4, 27)],
            date(2025, 4, 27),
            2,
            True,
        ),  # Total dates reach limit
        (
            [date(2025, 3, 30)],
            [date(2025, 4, 6)],
            date(2025, 4, 27),
            2,
            False,
        ),  # Dates outside of time window
        (
            [date(2025, 4, 13)],
            [],
            date(2025, 4, 27),
            2,
            False,
        ),  # Assigned dates did not reach limit
        (
            [],
            [date(2025, 4, 13)],
            date(2025, 4, 27),
            2,
            False,
        ),  # Preaching dates did not reach limit
        (
            [date(2025, 4, 20), date(2025, 4, 27)],
            [],
            date(2025, 4, 13),
            2,
            False,
        ),  # Future dates only
        ([], [], date(2025, 4, 27), 1, False),  # No dates
    ],
)
def test_has_exceeded_consecutive_assignments(
    assigned_dates, preaching_dates, reference_date, limit, expected
):
    # Act
    has_exceeded = has_exceeded_consecutive_assignments(
        assigned_dates=assigned_dates,
        preaching_dates=preaching_dates,
        reference_date=reference_date,
        limit=limit,
    )

    # Assert
    assert has_exceeded == expected


@pytest.mark.parametrize(
    "assigned_dates, preaching_dates, reference_date, limit",
    [
        ([date(2025, 4, 20)], [], None, 2),  # None reference date
        ([date(2025, 4, 20)], [], date(2025, 4, 27), 0),  # Limit is zero
        ([date(2025, 4, 20)], [], date(2025, 4, 27), -1),  # Limit is negative number
    ],
)
def test_has_exceeded_consecutive_assignments_with_invalid_arguments(
    assigned_dates, preaching_dates, reference_date, limit
):
    # Act and Assert
    with pytest.raises(ValueError):
        has_exceeded_consecutive_assignments(
            assigned_dates=assigned_dates,
            preaching_dates=preaching_dates,
            reference_date=reference_date,
            limit=limit,
        )
