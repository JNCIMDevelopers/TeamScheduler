# Standard Library Imports
import logging
from typing import List

# Third-Party Imports
import customtkinter

# Local Imports
from schedule_builder.helpers.file_exporter import FileExporter
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from ui.ui_manager import UIManager
from ui.ui_schedule_handler import UIScheduleHandler


class App(customtkinter.CTk):
    """
    A GUI application for scheduling team members and preachers.

    Provides functionality for generating schedules, managing team assignments,
    and exporting files.

    Attributes:
        file_exporter (FileExporter): Handles file export operations.
        ui_schedule_handler (UIScheduleHandler): Manages scheduling logic.
        ui_manager (UIManager): Manages the user interface and interactions.
    """

    def __init__(
        self, team: List[Person], preachers: List[Preacher], rotation: List[str]
    ):
        """
        Initializes the application with a team of members, preachers, and a worship leader rotation.

        Args:
            team (List[Person]): A list of team members who can be assigned to roles in the schedule.
            preachers (List[Preacher]): A list of preachers who can be scheduled for preaching duties.
            rotation (List[str]): A list of worship leader names in priority order for scheduling.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Setup dependencies
        self.file_exporter = FileExporter()
        self.ui_schedule_handler = UIScheduleHandler(
            team=team,
            preachers=preachers,
            rotation=rotation,
            file_exporter=self.file_exporter,
        )
        self.ui_manager = UIManager(
            app=self,
            schedule_handler=self.ui_schedule_handler,
            title="Schedule Builder",
        )

        # Setup UI
        self.ui_manager.setup()
