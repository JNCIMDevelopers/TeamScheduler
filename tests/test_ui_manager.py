# Standard Library Imports
import pytest
from datetime import date
from unittest.mock import MagicMock, patch

# Third-Party Imports
import customtkinter

# Local Imports
from ui.ui_manager import UIManager
from ui.ui_schedule_handler import UIScheduleHandler


@pytest.fixture
def mock_data():
    mock_app = MagicMock()
    mock_schedule_handler = MagicMock(UIScheduleHandler)
    title = "Test Title"
    mock_ui_manager = UIManager(
        app=mock_app, schedule_handler=mock_schedule_handler, title=title
    )
    return mock_app, mock_schedule_handler, mock_ui_manager


@pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
@patch("os.path.abspath")
@patch("subprocess.call")
@patch("os.startfile")
def test_handle_open_schedule_file(
    mock_startfile, mock_subprocess, mock_abspath, platform
):
    with patch("sys.platform", platform):
        # Arrange
        mock_app = MagicMock(customtkinter.CTk)
        mock_schedule_handler = MagicMock(UIScheduleHandler)
        title = "Test Title"
        ui_manager = UIManager(
            app=mock_app, schedule_handler=mock_schedule_handler, title=title
        )

        mock_label = MagicMock(customtkinter.CTkLabel)
        filepath = "test_schedule.csv"
        mock_abspath.return_value = "/absolute/path/to/test_schedule.csv"

        # Act
        ui_manager.handle_open_schedule_file(None, mock_label, filepath)

        # Assert
        if platform == "win32":
            mock_startfile.assert_called_once_with(mock_abspath.return_value)
            mock_subprocess.assert_not_called()
        elif platform == "darwin":
            mock_subprocess.assert_called_once_with(["open", mock_abspath.return_value])
            mock_startfile.assert_not_called()
        else:
            mock_subprocess.assert_called_once_with(
                ["xdg-open", mock_abspath.return_value]
            )
            mock_startfile.assert_not_called()


@pytest.mark.parametrize(
    "start_date, end_date, is_start_date_within_range, is_end_date_within_range, is_preaching_schedule_within_range, expected_message",
    [
        (None, date(2025, 4, 6), True, True, True, "Missing Input!"),  # No start date
        (date(2025, 4, 6), None, True, True, True, "Missing Input!"),  # No end date
        (None, None, True, True, True, "Missing Input!"),  # No start or end date
        (
            date(2025, 4, 13),
            date(2025, 4, 6),
            True,
            True,
            True,
            "Invalid Input!",
        ),  # End Date < Start Date
        (
            date(2025, 4, 6),
            date(2025, 4, 13),
            False,
            False,
            False,
            "No preaching schedule available within specified dates!",
        ),  # Dates outside of range
        (
            date(2025, 4, 6),
            date(2025, 4, 13),
            True,
            False,
            False,
            None,
        ),  # Only start date within range
        (
            date(2025, 4, 6),
            date(2025, 4, 13),
            False,
            True,
            False,
            None,
        ),  # Only end date within range
        (
            date(2025, 4, 6),
            date(2025, 4, 13),
            False,
            False,
            True,
            None,
        ),  # Only preaching schedule within range
    ],
)
@patch("ui.ui_manager.customtkinter.CTk")
def test_handle_create_button_click_validation_error_messages(
    mock_ctk,
    mock_data,
    start_date,
    end_date,
    is_start_date_within_range,
    is_end_date_within_range,
    is_preaching_schedule_within_range,
    expected_message,
):
    # Arrange
    mock_app, mock_schedule_handler, mock_ui_manager = mock_data
    mock_app.start_date_entry.get_date.return_value = start_date
    mock_app.end_date_entry.get_date.return_value = end_date

    mock_schedule_handler.is_within_date_range.side_effect = [
        is_start_date_within_range,
        is_end_date_within_range,
    ]
    mock_schedule_handler.is_preaching_schedule_within_date_range.return_value = (
        is_preaching_schedule_within_range
    )

    mock_schedule_handler.adjust_dates_within_range.return_value = (
        start_date,
        end_date,
        False,
    )
    mock_schedule_handler.create_schedule.return_value = None

    mock_ui_manager.configure_output_links = MagicMock()

    # Act
    with patch.object(
        mock_ui_manager, "configure_validation_error_message"
    ) as mock_error_message:
        mock_ui_manager.handle_create_button_click()

        # Assert
        if expected_message is None:
            mock_error_message.assert_not_called()
        else:
            mock_error_message.assert_called_once_with(text=expected_message)


@pytest.mark.parametrize("is_adjusted", [True, False])
@patch("ui.ui_manager.customtkinter.CTk")
def test_handle_create_button_click_alert_message(mock_ctk, mock_data, is_adjusted):
    # Arrange
    mock_app, mock_schedule_handler, mock_ui_manager = mock_data

    start_date = date(2025, 4, 6)
    end_date = date(2025, 4, 13)
    mock_app.start_date_entry.get_date.return_value = start_date
    mock_app.end_date_entry.get_date.return_value = end_date

    mock_schedule_handler.adjust_dates_within_range.return_value = (
        start_date,
        end_date,
        is_adjusted,
    )
    mock_schedule_handler.create_schedule.return_value = None

    mock_ui_manager.configure_output_links = MagicMock()

    # Act
    with patch.object(mock_ui_manager, "configure_alert_message") as mock_alert_message:
        mock_ui_manager.handle_create_button_click()

        # Assert
        if is_adjusted:
            expected_message = f"Preaching schedule is only available from {str(start_date)} to {str(end_date)}."
            mock_alert_message.assert_called_once_with(message=expected_message)
        else:
            mock_alert_message.assert_not_called()


@pytest.mark.parametrize(
    "exception, expected_message",
    [
        (
            PermissionError("PermissionDenied"),
            "Please close any open\noutput files and try again.",
        ),
        (Exception("GeneralError"), "An unexpected error occurred."),
        (None, None),
    ],
)
@patch("ui.ui_manager.customtkinter.CTk")
def test_handle_create_button_click_exception(
    mock_ctk, mock_data, exception, expected_message
):
    # Arrange
    mock_app, mock_schedule_handler, mock_ui_manager = mock_data

    start_date = date(2025, 4, 6)
    end_date = date(2025, 4, 13)
    mock_app.start_date_entry.get_date.return_value = start_date
    mock_app.end_date_entry.get_date.return_value = end_date

    mock_schedule_handler.adjust_dates_within_range.return_value = (
        start_date,
        end_date,
        False,
    )
    mock_schedule_handler.create_schedule.side_effect = exception

    mock_ui_manager.configure_output_links = MagicMock()

    # Act
    with patch.object(mock_ui_manager, "configure_error_message") as mock_error_message:
        mock_ui_manager.handle_create_button_click()

        # Assert
        if exception is None:
            mock_error_message.assert_not_called()
        else:
            mock_error_message.assert_called_once_with(message=expected_message)
