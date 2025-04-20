# Standard Library Imports
import pytest
from datetime import date
from unittest.mock import patch, MagicMock, ANY

# Local Imports
from schedule_builder.helpers.file_exporter import FileExporter
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from ui.application import App
from ui.ui_schedule_handler import UIScheduleHandler
from ui.ui_event_handler import UIEventHandler
from ui.ui_manager import UIManager


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


@patch("ui.application.UIManager.setup", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_app_initialization(mock_ctk_init, mock_setup_ui, mock_app_data):
    # Arrange
    mock_team, mock_preachers, mock_rotation = mock_app_data

    # Act
    app = App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)

    # Assert
    mock_ctk_init.assert_called_once()
    assert isinstance(app.file_exporter, FileExporter)
    assert isinstance(app.ui_schedule_handler, UIScheduleHandler)
    assert isinstance(app.ui_event_handler, UIEventHandler)
    assert isinstance(app.ui_manager, UIManager)
    mock_setup_ui.assert_called_once()


@patch("ui.application.UIManager.setup", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_app_initialization_with_empty_inputs(mock_ctk_init, mock_setup_ui):
    # Arrange
    mock_team = []
    mock_preachers = []
    mock_rotation = []

    # Act and Assert
    with pytest.raises(ValueError):
        App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)

    mock_ctk_init.assert_called_once()
    mock_setup_ui.assert_not_called()


@patch("ui.application.UIManager.setup", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_build_schedule(mock_ctk_init, mock_setup_ui, mock_app_data):
    # Arrange
    mock_team, mock_preachers, mock_rotation = mock_app_data
    app = App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)

    mock_ui_schedule_handler = MagicMock()
    mock_ui_file_exporter = MagicMock()
    app.ui_schedule_handler = mock_ui_schedule_handler
    app.file_exporter = mock_ui_file_exporter

    mock_events = ["event1", "event2"]
    mock_team = ["team_member_1", "team_member_2"]
    mock_ui_schedule_handler.build_schedule.return_value = (mock_events, mock_team)

    start_date = date(2025, 4, 6)
    end_date = date(2025, 4, 20)

    # Act
    app.create_schedule(start_date=start_date, end_date=end_date)

    # Assert
    mock_ui_schedule_handler.build_schedule.assert_called_once_with(
        start_date=start_date, end_date=end_date
    )

    mock_ui_file_exporter.export_html.assert_called_once_with(
        filepath=ANY,
        start_date=start_date,
        end_date=end_date,
        events=mock_events,
        team=mock_team,
    )

    mock_ui_file_exporter.export_csv.assert_called_once_with(
        filepath=ANY, events=mock_events
    )
