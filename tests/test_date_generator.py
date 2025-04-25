# Standard Library Imports
from datetime import datetime, date

# Local Imports
from schedule_builder.util.date_generator import get_all_sundays


def test_get_all_sundays_with_sunday_inputs():
    # Arrange
    start_date = date(2025, 4, 6)
    end_date = date(2025, 4, 27)
    expected_sundays = [
        date(2025, 4, 6),
        date(2025, 4, 13),
        date(2025, 4, 20),
        date(2025, 4, 27),
    ]

    # Act
    sunday_dates = get_all_sundays(start_date=start_date, end_date=end_date)

    # Assert
    assert sunday_dates == expected_sundays


def test_get_all_sundays_with_non_sunday_inputs():
    # Arrange
    start_date = date(2025, 4, 5)
    end_date = date(2025, 4, 28)
    expected_sundays = [
        date(2025, 4, 6),
        date(2025, 4, 13),
        date(2025, 4, 20),
        date(2025, 4, 27),
    ]

    # Act
    sunday_dates = get_all_sundays(start_date=start_date, end_date=end_date)

    # Assert
    assert sunday_dates == expected_sundays


def test_get_all_sundays_with_start_date_after_end_date():
    # Arrange
    start_date = date(2025, 4, 27)
    end_date = date(2025, 4, 6)

    # Act
    sunday_dates = get_all_sundays(start_date=start_date, end_date=end_date)

    # Assert
    assert sunday_dates == []


def test_get_all_sundays_with_single_sunday_date():
    # Arrange
    single_date = date(2025, 4, 27)

    # Act
    sunday_dates = get_all_sundays(start_date=single_date, end_date=single_date)

    # Assert
    assert sunday_dates == [single_date]


def test_get_all_sundays_with_single_non_sunday_date():
    # Arrange
    single_date = date(2025, 4, 23)

    # Act
    sunday_dates = get_all_sundays(start_date=single_date, end_date=single_date)

    # Assert
    assert sunday_dates == []


def test_get_all_sundays_with_no_dates():
    # Arrange
    today_date = datetime.today().date()
    expected_sundays = [today_date] if today_date.weekday() == 6 else []

    # Act
    sunday_dates = get_all_sundays(start_date=None, end_date=None)

    # Assert
    assert sunday_dates == expected_sundays
