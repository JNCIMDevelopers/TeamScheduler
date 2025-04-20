# Standard Library Imports
import copy
import logging
from datetime import date
from typing import List, Tuple

# Local Imports
from schedule_builder.builders.schedule import Schedule
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person
from schedule_builder.util.date_generator import get_all_sundays


class UIScheduleHandler:
    """
    Handles schedule-related logic for the user interface.

    This class manages date validation, range adjustments, and schedule creation
    for the specified date range.
    """

    def __init__(self, team, preachers, rotation):
        """
        Initializes the schedule handler with team, preachers, and rotation data.

        Args:
            team: The list of team members.
            preachers: The list of preachers.
            rotation: The priority order of worship leaders.
        """
        self.logger = logging.getLogger(__name__)
        self.team = team
        self.preachers = preachers
        self.rotation = rotation
        self.earliest_date, self.latest_date = self.calculate_preaching_date_range()
        self.logger.debug(f"Earliest Preaching Date: {str(self.earliest_date)}")
        self.logger.debug(f"Latest Preaching Date: {str(self.latest_date)}")

    def calculate_preaching_date_range(self) -> Tuple[date, date]:
        """
        Calculates the earliest and latest preaching dates.

        Returns:
            Tuple[date, date]: A tuple containing the earliest and latest preaching dates.
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
        Checks if a given date falls within the permissible date range.

        Args:
            reference_date (date): The date to check.

        Returns:
            bool: True if the date is within range, False otherwise.
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
            bool: True if the schedule is within range, False otherwise.
        """
        return start_date <= self.earliest_date <= self.latest_date <= end_date

    def adjust_dates_within_range(
        self, start_date: date, end_date: date
    ) -> Tuple[date, date, bool]:
        """
        Adjusts the start and end dates to ensure they fall within the permissible range.

        Args:
            start_date (date): The initial start date.
            end_date (date): The initial end date.

        Returns:
            Tuple[date, date, bool]: Adjusted start and end dates, and a flag indicating
            whether adjustments were made.
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
        Creates a schedule for the specified date range.

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
        events, updated_team = Schedule(
            team=team_copy,
            preachers=self.preachers,
            rotation=self.rotation,
            event_dates=dates_to_assign,
        ).build()

        return events, updated_team
