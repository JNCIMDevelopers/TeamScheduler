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
    A GUI application for scheduling using customtkinter and tkcalendar.

    This class initializes and configures the user interface, allowing users to input
    a date range for scheduling. It handles the creation of schedules based on team
    and preacher data, validates date inputs, and provides options to view and manage
    the generated schedules.
    """

    def __init__(
        self, team: List[Person], preachers: List[Preacher], rotation: List[str]
    ):
        """
        Initializes the application with a list of team members, preachers, and a rotation.

        Args:
            team (List[Person]): A list of Person objects representing the team members.
            preachers (List[Preacher]): A list of Preacher objects representing the preachers.
            rotation (List[str]): A list of strings representing the priority order of worship leaders.
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
