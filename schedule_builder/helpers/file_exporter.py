# Standard Library Imports
import logging
from datetime import date
from typing import List

# Local Imports
from schedule_builder.builders.file_builder import (
    generate_team_schedule_html,
    create_html,
    get_schedule_data_for_csv,
    format_data_for_csv,
    create_csv,
)
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person


class FileExporter:
    """
    A utility class for exporting schedule data to HTML and CSV files.
    """

    def __init__(self):
        """
        Initializes the FileExporter with a logger.
        """
        self.logger = logging.getLogger(__name__)

    def export_html(
        self,
        filepath: str,
        start_date: date,
        end_date: date,
        events: List[Event],
        team: List[Person],
    ) -> None:
        """
        Exports the team schedule as an HTML file.

        Args:
            filepath (str): The path to save the HTML file.
            start_date (date): The start date of the schedule.
            end_date (date): The end date of the schedule.
            events (List[Event]): A list of scheduled events.
            team (List[Person]): A list of team members.
        """
        html_content = generate_team_schedule_html(start_date, end_date, events, team)
        self.logger.debug(f"HTML Data:\n{html_content}\n")

        create_html(content=html_content, filepath=filepath)

    def export_csv(self, filepath: str, events: List[Event]) -> None:
        """
        Exports the event schedule as a CSV file.

        Args:
            filepath (str): The path to save the CSV file.
            events (List[Event]): A list of scheduled events.
        """
        csv_data = get_schedule_data_for_csv(events=events)
        formatted_csv_data = format_data_for_csv(data=csv_data)
        self.logger.debug(f"CSV Data:\n{formatted_csv_data}\n")

        create_csv(data=formatted_csv_data, filepath=filepath)
