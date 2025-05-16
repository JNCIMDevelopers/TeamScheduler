# Standard Library Imports
import logging

# Third-Party Imports
import customtkinter

# Local Imports
from ui.ui_manager import UIManager


class App(customtkinter.CTk):
    """
    The main GUI application for building and managing a team schedule.
    """

    def __init__(self, ui_manager: UIManager):
        """
        Initializes an instance of the App class.

        Args:
            ui_manager (UIManager): The user interface manager that sets up and controls UI behavior.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.ui_manager = ui_manager

    def start(self):
        """
        Starts the application by setting up the UI and entering the main event loop.
        """
        self.ui_manager.setup()
        self.mainloop()
