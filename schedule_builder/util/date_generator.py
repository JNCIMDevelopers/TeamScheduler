from datetime import datetime, date
from dateutil.rrule import rrule, DAILY, SU
from typing import List, Optional


def get_all_sundays(
    start_date: Optional[date] = None, end_date: Optional[date] = None
) -> List[date]:
    """
    Returns all Sundays between the specified start and end dates.

    If no `start_date` is provided, it defaults to today's date. If no `end_date` is provided, it also defaults to today's date.

    Args:
        start_date (Optional[date]): The starting date for the search (default is today).
        end_date (Optional[date]): The ending date for the search (default is today).

    Returns:
        List[date]: A list of Sundays between the specified dates.

    Examples:
        >>> get_all_sundays(date(2024, 1, 1), date(2024, 12, 31))
        [date(2024, 1, 7), date(2024, 1, 14), ..., date(2024, 12, 29)]
    """
    # Set start date and end date as current date by default
    start_date = start_date if start_date else datetime.today().date()
    end_date = end_date if end_date else datetime.today().date()

    # Get all sunday datetimes between specified dates
    sundays = list(
        rrule(DAILY, interval=1, byweekday=SU, dtstart=start_date, until=end_date)
    )

    # Extract only the date part from each datetime object
    sundays_dates = [dt.date() for dt in sundays]
    return sundays_dates
