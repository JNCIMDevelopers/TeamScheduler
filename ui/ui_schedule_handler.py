# Standard Library Imports
import copy
import logging
from datetime import date
from typing import List, Tuple, Type

# Local Imports
from config import SCHEDULE_CSV_FILE_PATH, SCHEDULE_DETAILS_HTML_FILE_PATH
from schedule_builder.builders.schedule import Schedule
from schedule_builder.eligibility.eligibility_checker import EligibilityChecker
from schedule_builder.helpers.file_exporter import FileExporter
from schedule_builder.helpers.worship_leader_selector import WorshipLeaderSelector
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from schedule_builder.util.date_generator import get_all_sundays


class UIScheduleHandler:
    """
    A class to handle the schedule-related logic for the user interface.
    """

    def __init__(
        self,
        team: List[Person],
        preachers: List[Preacher],
        worship_leader_selector: WorshipLeaderSelector,
        eligibility_checker: EligibilityChecker,
        file_exporter: FileExporter,
        schedule_class: Type[Schedule],
    ):
        """
        Initializes an instance of UIScheduleHandler.

        Args:
            team (List[Person]): List of team members to be scheduled.
            preachers (List[Preacher]): List of preachers available for the schedule.
            worship_leader_selector (WorshipLeaderSelector): Selector for worship leaders.
            eligibility_checker (EligibilityChecker): Eligibility checker for scheduling.
            file_exporter (FileExporter): An object to handle file export operations.
            schedule_class (Type[Schedule]): The class used to build the schedule.
        """
        self.logger = logging.getLogger(__name__)
        self.team = team
        self.preachers = preachers
        self.worship_leader_selector = worship_leader_selector
        self.eligibility_checker = eligibility_checker
        self.file_exporter = file_exporter
        self.schedule_class = schedule_class
        self.earliest_date, self.latest_date = self.calculate_preaching_date_range()
        self.logger.debug(f"Earliest Preaching Date: {str(self.earliest_date)}")
        self.logger.debug(f"Latest Preaching Date: {str(self.latest_date)}")

    def calculate_preaching_date_range(self) -> Tuple[date, date]:
        """
        Calculates the earliest and latest preaching dates from the preachers' schedules.

        Returns:
            Tuple[date, date]: A tuple containing the earliest and latest preaching dates.

        Raises:
            ValueError: If no preachers are available or no preaching dates are found.
        """
        if self.preachers is None or not self.preachers:
            raise ValueError("No preachers available to calculate date range.")

        all_dates = [
            preaching_date
            for preacher in self.preachers
            for preaching_date in preacher.dates
        ]

        if not all_dates:
            raise ValueError("No preaching dates available.")

        all_unique_dates = set(all_dates)

        earliest_date = min(all_unique_dates)
        latest_date = max(all_unique_dates)

        return (earliest_date, latest_date)

    def is_within_date_range(self, reference_date: date) -> bool:
        """
        Checks if a given date falls within the allowable preaching date range.

        Args:
            reference_date (date): The date to check.

        Returns:
            bool: True if the date is within the allowable range, False otherwise.
        """
        return self.earliest_date <= reference_date <= self.latest_date

    def is_preaching_schedule_within_date_range(
        self, start_date: date, end_date: date
    ) -> bool:
        """
        Checks if the preaching schedule falls within the specified date range.

        Args:
            start_date (date): The start date of the range.
            end_date (date): The end date of the range.

        Returns:
            bool: True if the preaching schedule is within the range, False otherwise.
        """
        return start_date <= self.earliest_date <= self.latest_date <= end_date

    def adjust_dates_within_range(
        self, start_date: date, end_date: date
    ) -> Tuple[date, date, bool]:
        """
        Adjusts the start and end dates to ensure they are within the available preaching date range.

        Args:
            start_date (date): The initial start date.
            end_date (date): The initial end date.

        Returns:
            Tuple[date, date, bool]: Adjusted start and end dates, and a flag indicating if any adjustments were made.
        """
        is_adjusted = False

        if start_date < self.earliest_date:
            start_date = self.earliest_date
            is_adjusted = True

        if end_date > self.latest_date:
            end_date = self.latest_date
            is_adjusted = True

        return (start_date, end_date, is_adjusted)

    def build_schedule(
        self, start_date: date, end_date: date
    ) -> Tuple[List[Event], List[Person]]:
        """
        Builds a schedule for the specified date range.

        Args:
            start_date (date): The start date of the schedule.
            end_date (date): The end date of the schedule.

        Returns:
            Tuple[List[Event], List[Person]]: A list of scheduled events and the updated team.
        """
        self.logger.info(f"Creating schedule from {str(start_date)} to {str(end_date)}")

        # Obtain Sunday dates within specified date range
        dates_to_assign = get_all_sundays(start_date=start_date, end_date=end_date)
        self.logger.debug(f"Sunday Dates:\n{str(dates_to_assign)}\n")

        # Deep copy team to prevent modifications from persisting between calls
        team_copy = copy.deepcopy(self.team)

        # Build Schedule
        events, updated_team = self.schedule_class(
            team=team_copy,
            event_dates=dates_to_assign,
            preachers=self.preachers,
            worship_leader_selector=self.worship_leader_selector,
            eligibility_checker=self.eligibility_checker,
        ).build()

        return events, updated_team

    def create_schedule(self, start_date: date, end_date: date) -> None:
        """
        Creates a schedule and exports it to both HTML and CSV formats.

        Args:
            start_date (date): The start date of the schedule.
            end_date (date): The end date of the schedule.
        """
        # Build Schedule
        events, updated_team = self.build_schedule(
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
