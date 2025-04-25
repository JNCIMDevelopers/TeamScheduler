# Standard Library Imports
import pytest
from datetime import date
from unittest.mock import patch

# Local Imports
from schedule_builder.helpers.file_exporter import FileExporter
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from ui.application import App
from ui.ui_schedule_handler import UIScheduleHandler
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
