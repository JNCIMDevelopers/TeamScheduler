# Standard Library Imports
import os
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


def test_execute_edit_command(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_command = MagicMock()

    # Act
    mock_ui_manager._execute_edit_command(mock_command)

    # Assert
    assert mock_ui_manager.undo_stack == [mock_command]
    assert mock_ui_manager.redo_stack == []
    mock_command.execute.assert_called_once()
    mock_command.undo.assert_not_called()


def test_execute_edit_command_for_multiple_commands(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_command1 = MagicMock()
    mock_command2 = MagicMock()

    # Act
    mock_ui_manager._execute_edit_command(mock_command1)
    mock_ui_manager._execute_edit_command(mock_command2)

    # Assert
    assert mock_ui_manager.undo_stack == [mock_command1, mock_command2]
    assert mock_ui_manager.redo_stack == []
    mock_command1.execute.assert_called_once()
    mock_command1.undo.assert_not_called()
    mock_command2.execute.assert_called_once()
    mock_command2.undo.assert_not_called()


def test_undo_last_edit(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_sheet = MagicMock()
    mock_command = MagicMock()
    mock_ui_manager._execute_edit_command(mock_command)

    # Act
    mock_ui_manager._undo_last_edit(sheet=mock_sheet)

    # Assert
    assert mock_ui_manager.undo_stack == []
    assert mock_ui_manager.redo_stack == [mock_command]
    mock_command.execute.assert_called_once()
    mock_command.undo.assert_called_once()


def test_undo_last_edit_with_empty_undo_stack(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_sheet = MagicMock()

    # Act
    mock_ui_manager._undo_last_edit(sheet=mock_sheet)

    # Assert
    assert mock_ui_manager.undo_stack == []
    assert mock_ui_manager.redo_stack == []


def test_undo_last_edit_idempotency(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_sheet = MagicMock()
    mock_command = MagicMock()
    mock_ui_manager._execute_edit_command(mock_command)

    # Act
    mock_ui_manager._undo_last_edit(sheet=mock_sheet)
    mock_ui_manager._undo_last_edit(sheet=mock_sheet)

    # Assert
    assert mock_ui_manager.undo_stack == []
    assert mock_ui_manager.redo_stack == [mock_command]
    mock_command.execute.assert_called_once()
    mock_command.undo.assert_called_once()


def test_redo_last_edit(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_sheet = MagicMock()
    mock_command = MagicMock()
    mock_ui_manager._execute_edit_command(mock_command)
    mock_ui_manager._undo_last_edit(sheet=mock_sheet)

    # Act
    mock_ui_manager._redo_last_edit(sheet=mock_sheet)

    # Assert
    assert mock_ui_manager.undo_stack == [mock_command]
    assert mock_ui_manager.redo_stack == []
    assert mock_command.execute.call_count == 2
    mock_command.undo.asser_called_once()


def test_redo_last_edit_with_empty_redo_stack(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_sheet = MagicMock()

    # Act
    mock_ui_manager._redo_last_edit(sheet=mock_sheet)

    # Assert
    assert mock_ui_manager.undo_stack == []
    assert mock_ui_manager.redo_stack == []


def test_redo_last_edit_idempotency(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_sheet = MagicMock()
    mock_command = MagicMock()
    mock_ui_manager._execute_edit_command(mock_command)
    mock_ui_manager._undo_last_edit(sheet=mock_sheet)

    # Act
    mock_ui_manager._redo_last_edit(sheet=mock_sheet)
    mock_ui_manager._redo_last_edit(sheet=mock_sheet)

    # Assert
    assert mock_ui_manager.undo_stack == [mock_command]
    assert mock_ui_manager.redo_stack == []
    assert mock_command.execute.call_count == 2
    mock_command.undo.assert_called_once()


def test_multiple_command_undo_redo_operations(mock_data):
    # Arrange
    _, _, mock_ui_manager = mock_data
    mock_sheet = MagicMock()
    mock_command1 = MagicMock()
    mock_command2 = MagicMock()
    mock_command3 = MagicMock()
    mock_command4 = MagicMock()

    # Act
    mock_ui_manager._execute_edit_command(mock_command1)
    mock_ui_manager._execute_edit_command(mock_command2)
    mock_ui_manager._execute_edit_command(mock_command3)
    mock_ui_manager._undo_last_edit(sheet=mock_sheet)
    mock_ui_manager._undo_last_edit(sheet=mock_sheet)
    mock_ui_manager._redo_last_edit(sheet=mock_sheet)
    mock_ui_manager._execute_edit_command(mock_command4)

    # Assert
    assert mock_ui_manager.undo_stack == [mock_command1, mock_command2, mock_command4]
    assert mock_ui_manager.redo_stack == []
    mock_command1.execute.assert_called_once()
    mock_command1.undo.assert_not_called()
    assert mock_command2.execute.call_count == 2
    mock_command3.execute.assert_called_once()
    mock_command3.undo.assert_called_once()
    mock_command2.undo.assert_called_once()
    mock_command4.execute.assert_called_once()
    mock_command4.undo.assert_not_called()


@pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
@patch("os.path.abspath")
@patch("subprocess.call")
def test_handle_open_schedule_file(mock_subprocess, mock_abspath, platform):
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

        # Conditionally patch os.startfile for win32 platform
        if platform == "win32":
            if not hasattr(os, "startfile"):
                pytest.skip(
                    "Skipping test as the test is for Windows but running on a non-Windows system."
                )
            with patch("os.startfile") as mock_startfile:
                # Act
                ui_manager._handle_open_schedule_file(None, mock_label, filepath)

                # Assert
                mock_startfile.assert_called_once_with(mock_abspath.return_value)
                mock_subprocess.assert_not_called()
        elif platform == "darwin":
            # Act
            ui_manager._handle_open_schedule_file(None, mock_label, filepath)

            # Assert
            mock_subprocess.assert_called_once_with(["open", mock_abspath.return_value])
        else:
            # Act
            ui_manager._handle_open_schedule_file(None, mock_label, filepath)

            # Assert
            mock_subprocess.assert_called_once_with(
                ["xdg-open", mock_abspath.return_value]
            )


@pytest.mark.parametrize("expected_message", ["Invalid", None])
@patch("ui.ui_manager.customtkinter.CTk")
def test_handle_create_button_click_validation_error_messages(
    mock_ctk, mock_data, expected_message
):
    # Arrange
    mock_app, mock_schedule_handler, mock_ui_manager = mock_data
    start_date = date(2025, 4, 6)
    end_date = date(2025, 4, 13)
    mock_app.start_date_entry.get_date.return_value = start_date
    mock_app.end_date_entry.get_date.return_value = end_date

    mock_schedule_handler.validate_dates.return_value = expected_message
    mock_schedule_handler.adjust_dates_within_range.return_value = (
        start_date,
        end_date,
        False,
    )
    mock_schedule_handler.build_schedule.return_value = (None, None)

    mock_ui_manager.configure_output_links = MagicMock()

    # Act
    with patch.object(
        mock_ui_manager, "_configure_validation_error_message"
    ) as mock_error_message:
        mock_ui_manager.handle_create_button_click()

        # Assert
        if expected_message:
            mock_error_message.assert_called_once_with(text=expected_message)
        else:
            mock_error_message.assert_not_called()


@pytest.mark.parametrize("is_adjusted", [True, False])
@patch("ui.ui_manager.UIManager.show_schedule_popup")
@patch("ui.ui_manager.customtkinter.CTk")
def test_handle_create_button_click_alert_message(
    mock_ctk, mock_popup, mock_data, is_adjusted
):
    # Arrange
    mock_app, mock_schedule_handler, mock_ui_manager = mock_data

    start_date = date(2025, 4, 6)
    end_date = date(2025, 4, 13)
    mock_app.start_date_entry.get_date.return_value = start_date
    mock_app.end_date_entry.get_date.return_value = end_date
    mock_schedule_handler.validate_dates.return_value = None
    mock_schedule_handler.adjust_dates_within_range.return_value = (
        start_date,
        end_date,
        is_adjusted,
    )
    mock_schedule_handler.build_schedule.return_value = (None, None)

    mock_ui_manager.configure_output_links = MagicMock()

    # Act
    with patch.object(
        mock_ui_manager, "_configure_alert_message"
    ) as mock_alert_message:
        mock_ui_manager.handle_create_button_click()

        # Assert
        if is_adjusted:
            expected_message = f"Preaching schedule is only available from {str(start_date)} to {str(end_date)}."
            mock_alert_message.assert_called_once_with(message=expected_message)
        else:
            mock_alert_message.assert_not_called()

        mock_popup.assert_called_once()


@patch("ui.ui_manager.UIManager.show_schedule_popup")
@patch("ui.ui_manager.customtkinter.CTk")
def test_handle_create_button_click_exception(mock_ctk, mock_popup, mock_data):
    # Arrange
    mock_app, mock_schedule_handler, mock_ui_manager = mock_data

    start_date = date(2025, 4, 6)
    end_date = date(2025, 4, 13)
    mock_app.start_date_entry.get_date.return_value = start_date
    mock_app.end_date_entry.get_date.return_value = end_date
    mock_schedule_handler.validate_dates.return_value = None
    mock_schedule_handler.adjust_dates_within_range.return_value = (
        start_date,
        end_date,
        False,
    )
    mock_schedule_handler.build_schedule.side_effect = Exception("GeneralError")

    mock_ui_manager.configure_output_links = MagicMock()

    # Act
    with patch.object(
        mock_ui_manager, "_configure_error_message"
    ) as mock_error_message:
        mock_ui_manager.handle_create_button_click()

        # Assert
        mock_error_message.assert_called_once_with(
            message="An unexpected error occurred."
        )
        mock_popup.assert_not_called()
