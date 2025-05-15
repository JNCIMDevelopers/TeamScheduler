from unittest.mock import MagicMock, patch
from schedule_builder.builders.schedule import Schedule
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from app_factory import create_app


@patch("app_factory.FileExporter")
@patch("app_factory.UIScheduleHandler")
@patch("app_factory.UIManager")
@patch("app_factory.App")
@patch("customtkinter.CTk.__init__", return_value=None)
def test_create_app_wires_dependencies_correctly(
    mock_ctk,
    mock_app_class,
    mock_ui_manager_class,
    mock_schedule_handler_class,
    mock_file_exporter_class,
):
    # Arrange
    team = [MagicMock(spec=Person)]
    preachers = [MagicMock(spec=Preacher)]
    worship_leader_selector = MagicMock()
    eligibility_checker = MagicMock()
    title = "Test"

    mock_file_exporter = MagicMock()
    mock_file_exporter_class.return_value = mock_file_exporter

    mock_schedule_handler = MagicMock()
    mock_schedule_handler_class.return_value = mock_schedule_handler

    mock_ui_manager = MagicMock()
    mock_ui_manager_class.return_value = mock_ui_manager

    mock_app_instance = MagicMock()
    mock_app_class.return_value = mock_app_instance

    # Act
    app = create_app(
        title=title,
        team=team,
        preachers=preachers,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
    )

    # Assert
    mock_file_exporter_class.assert_called_once()
    mock_schedule_handler_class.assert_called_once_with(
        team=team,
        preachers=preachers,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
        file_exporter=mock_file_exporter,
        schedule_class=Schedule,
    )
    mock_ui_manager_class.assert_called_once_with(
        app=None,
        schedule_handler=mock_schedule_handler,
        title=title,
    )
    mock_app_class.assert_called_once_with(
        schedule_handler=mock_schedule_handler,
        ui_manager=mock_ui_manager,
    )

    assert mock_ui_manager.app == mock_app_instance
    assert app == mock_app_instance
