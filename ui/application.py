# Standard Library Imports
import logging

# Third-Party Imports
import customtkinter

# Local Imports
from ui.ui_manager import UIManager
from ui.ui_schedule_handler import UIScheduleHandler


class App(customtkinter.CTk):
    """
    The main GUI application for building and managing a team schedule.
    """

    def __init__(
        self,
        schedule_handler: UIScheduleHandler,
        ui_manager: UIManager,
    ):
        """
        Initializes an instance of the App class.

        Args:
            schedule_handler (UIScheduleHandler): The scheduling logic and data handler.
            ui_manager (UIManager): The user interface manager that sets up and controls UI behavior.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.schedule_handler = schedule_handler
        self.ui_manager = ui_manager
        self.ui_manager.app = self

    def start(self):
        """
        Starts the application by setting up the UI and entering the main event loop.
        """
        self.ui_manager.setup()
        self.mainloop()
