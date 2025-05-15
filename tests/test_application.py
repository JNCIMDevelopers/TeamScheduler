# Local Imports
from unittest.mock import MagicMock, patch
from ui.application import App


@patch("customtkinter.CTk.__init__", return_value=None)
def test_app_initialization_sets_dependencies(mock_ctk):
    # Arrange
    mock_ui_manager = MagicMock()

    # Act
    app = App(mock_ui_manager)

    # Assert
    assert app.ui_manager is mock_ui_manager


@patch("ui.application.App.mainloop", return_value=None)
@patch("ui.application.UIManager.setup", return_value=None)
@patch("customtkinter.CTk.__init__", return_value=None)
def test_app_start_calls_setup_and_mainloop(mock_ctk, mock_setup, mock_mainloop):
    # Arrange
    mock_ui_manager = MagicMock()
    app = App(mock_ui_manager)

    # Act
    app.start()

    # Assert
    mock_ui_manager.setup.assert_called_once()
    mock_mainloop.assert_called_once()
