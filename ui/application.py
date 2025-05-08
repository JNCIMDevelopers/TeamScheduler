# Standard Library Imports
import logging

# Third-Party Imports
import customtkinter

# Local Imports
from schedule_builder.helpers.file_exporter import FileExporter
from ui.ui_manager import UIManager
from ui.ui_schedule_handler import UIScheduleHandler


class App(customtkinter.CTk):
    """
    The main GUI application for building and managing a team schedule.

    This class acts as the entry point for the graphical interface and coordinates the
    application's core components, such as scheduling logic, file export, and UI management.

    Attributes:
        file_exporter (FileExporter): Responsible for handling file export operations.
        schedule_handler (UIScheduleHandler): Encapsulates the scheduling logic and data.
        ui_manager (UIManager): Manages the layout and interaction of UI components.
    """

    def __init__(
        self,
        file_exporter: FileExporter,
        schedule_handler: UIScheduleHandler,
        ui_manager: UIManager,
    ):
        """
        Initializes the App with injected core components.

        Args:
            file_exporter (FileExporter): An instance responsible for exporting schedule data to files.
            schedule_handler (UIScheduleHandler): The scheduling logic and data handler.
            ui_manager (UIManager): The user interface manager that sets up and controls UI behavior.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.file_exporter = file_exporter
        self.schedule_handler = schedule_handler
        self.ui_manager = ui_manager
        self.ui_manager.app = self

    def start(self):
        """
        Starts the application by setting up the UI and entering the main event loop.
        """
        self.ui_manager.setup()
        self.mainloop()
