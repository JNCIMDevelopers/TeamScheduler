# Standard Library Imports
import pytest
from datetime import date
from unittest.mock import patch

# Local Imports
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from ui.application import App


@pytest.fixture
def mock_app_data():
    mock_team = [Person(name="TestPerson", roles=[])]
    mock_preachers = [
        Preacher(
            name="TestPreacher",
            graphics_support="TestSupport",
            dates=[date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)],
        )
    ]
    mock_rotation = ["TestPerson"]
    return mock_team, mock_preachers, mock_rotation


@patch.object(App, "setup_ui", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_app_initialization(mock_ctk_init, mock_setup_ui, mock_app_data):
    # Arrange
    mock_team, mock_preachers, mock_rotation = mock_app_data

    # Act
    app = App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)

    # Assert
    assert app.team == mock_team
    assert app.preachers == mock_preachers
    assert app.rotation == mock_rotation
    assert app.earliest_date == date(2025, 4, 6)
    assert app.latest_date == date(2025, 4, 20)
    mock_setup_ui.assert_called_once()


@pytest.mark.parametrize(
    "preaching_dates, expected_earliest_date, expected_latest_date",
    [
        (
            [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)],
            date(2025, 4, 6),
            date(2025, 4, 20),
        ),
        ([date(2025, 4, 6)], date(2025, 4, 6), date(2025, 4, 6)),  # Single date
        (
            [date(2025, 4, 6), date(2025, 4, 6), date(2025, 4, 13)],
            date(2025, 4, 6),
            date(2025, 4, 13),
        ),  # Duplicate dates
    ],
)
@patch.object(App, "setup_ui", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_calculate_preaching_date_range(
    mock_ctk_init,
    mock_setup_ui,
    mock_app_data,
    preaching_dates,
    expected_earliest_date,
    expected_latest_date,
):
    # Arrange
    mock_team, mock_preachers, mock_rotation = mock_app_data
    mock_preachers = [
        Preacher(
            name="TestPreacher",
            graphics_support="TestSupport",
            dates=preaching_dates,
        )
    ]
    app = App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)

    # Act
    earliest_date, latest_date = app.calculate_preaching_date_range()

    # Assert
    assert earliest_date == expected_earliest_date
    assert latest_date == expected_latest_date


@pytest.mark.parametrize(
    "reference_date, expected_result",
    [
        (
            date(2025, 4, 6),
            True,
        ),  # Lower boundary
        (
            date(2025, 4, 27),
            True,
        ),  # Upper boundary
        (
            date(2025, 3, 30),
            False,
        ),  # Lower bound is outside the range
        (
            date(2025, 5, 4),
            False,
        ),  # Upper bound is outside the range
    ],
)
@patch.object(App, "setup_ui", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_is_within_date_range(
    mock_ctk_init, mock_setup_ui, mock_app_data, reference_date, expected_result
):
    # Arrange
    mock_team, mock_preachers, mock_rotation = mock_app_data
    app = App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)
    app.earliest_date = date(2025, 4, 6)
    app.latest_date = date(2025, 4, 27)

    # Act
    is_within_range = app.is_within_date_range(reference_date=reference_date)

    # Assert
    assert is_within_range == expected_result


@pytest.mark.parametrize(
    "start_date, end_date, expected_result",
    [
        (
            date(2025, 3, 30),
            date(2025, 5, 4),
            True,
        ),  # Within range
        (
            date(2025, 4, 6),
            date(2025, 4, 27),
            True,
        ),  # Exactly at the range limits
        (
            date(2025, 4, 13),
            date(2025, 5, 4),
            False,
        ),  # Lower bound is outside the range
        (
            date(2025, 3, 30),
            date(2025, 4, 20),
            False,
        ),  # Upper bound is outside the range
        (
            date(2025, 4, 13),
            date(2025, 4, 20),
            False,
        ),  # Outside range, adjusted to earliest and latest dates
    ],
)
@patch.object(App, "setup_ui", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_is_preaching_schedule_within_date_range(
    mock_ctk_init, mock_setup_ui, mock_app_data, start_date, end_date, expected_result
):
    # Arrange
    mock_team, mock_preachers, mock_rotation = mock_app_data
    app = App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)
    app.earliest_date = date(2025, 4, 6)
    app.latest_date = date(2025, 4, 27)

    # Act
    is_within_range = app.is_preaching_schedule_within_date_range(
        start_date=start_date, end_date=end_date
    )

    # Assert
    assert is_within_range == expected_result


@pytest.mark.parametrize(
    "start_date_input, end_date_input, expected_start_date, expected_end_date, expected_is_adjusted",
    [
        (
            date(2025, 4, 13),
            date(2025, 4, 20),
            date(2025, 4, 13),
            date(2025, 4, 20),
            False,
        ),  # Within range, no adjustment needed
        (
            date(2025, 4, 6),
            date(2025, 4, 27),
            date(2025, 4, 6),
            date(2025, 4, 27),
            False,
        ),  # Exactly at the range limits, no adjustment needed
        (
            date(2025, 3, 30),
            date(2025, 4, 20),
            date(2025, 4, 6),
            date(2025, 4, 20),
            True,
        ),  # Minimum date before range, adjusted to earliest date
        (
            date(2025, 4, 6),
            date(2025, 5, 4),
            date(2025, 4, 6),
            date(2025, 4, 27),
            True,
        ),  # Maximum date after range, adjusted to latest date
        (
            date(2025, 3, 30),
            date(2025, 5, 4),
            date(2025, 4, 6),
            date(2025, 4, 27),
            True,
        ),  # Outside range, adjusted to earliest and latest dates
    ],
)
@patch.object(App, "setup_ui", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_adjust_dates_within_range(
    mock_ctk_init,
    mock_setup_ui,
    mock_app_data,
    start_date_input,
    end_date_input,
    expected_start_date,
    expected_end_date,
    expected_is_adjusted,
):
    # Arrange
    mock_team, mock_preachers, mock_rotation = mock_app_data
    app = App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)
    app.earliest_date = date(2025, 4, 6)
    app.latest_date = date(2025, 4, 27)

    # Act
    actual_start_date, actual_end_date, actual_is_adjusted = (
        app.adjust_dates_within_range(
            start_date=start_date_input, end_date=end_date_input
        )
    )

    # Assert
    assert actual_start_date == expected_start_date
    assert actual_end_date == expected_end_date
    assert actual_is_adjusted == expected_is_adjusted
