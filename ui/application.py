# Standard Library Imports
import logging
from datetime import date
from typing import List

# Third-Party Imports
import customtkinter

# Local Imports
from paths import SCHEDULE_CSV_FILE_PATH, SCHEDULE_DETAILS_HTML_FILE_PATH
from schedule_builder.helpers.file_exporter import FileExporter
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from ui.ui_event_handler import UIEventHandler
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
        self.file_exporter = FileExporter()
        self.ui_schedule_handler = UIScheduleHandler(
            team=team, preachers=preachers, rotation=rotation
        )
        self.ui_event_handler = UIEventHandler(
            app=self, schedule_handler=self.ui_schedule_handler
        )
        self.ui_manager = UIManager(
            app=self,
            schedule_handler=self.ui_schedule_handler,
            event_handler=self.ui_event_handler,
            title="Schedule Builder",
        )
        self.ui_manager.setup()

    def create_schedule(self, start_date: date, end_date: date) -> None:
        """
        Creates a schedule for the specified date range.

        This method generates a schedule, exports the details to an HTML file, and exports it to a CSV file.

        Args:
            start_date (date): The start date of the schedule.
            end_date (date): The end date of the schedule.
        """
        # Build Schedule
        events, updated_team = self.ui_schedule_handler.build_schedule(
            start_date=start_date, end_date=end_date
        )

        # Generate HTML document
        self.file_exporter.export_html(
            filepath=SCHEDULE_DETAILS_HTML_FILE_PATH,
            start_date=start_date,
            end_date=end_date,
            events=events,
            team=updated_team,
        )

        # Generate CSV document
        self.file_exporter.export_csv(
            filepath=SCHEDULE_CSV_FILE_PATH,
            events=events,
        )
