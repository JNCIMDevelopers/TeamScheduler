from datetime import date, timedelta
from typing import List


def has_exceeded_consecutive_assignments(
    assigned_dates: List[date],
    preaching_dates: List[date],
    reference_date: date,
    limit: int,
) -> bool:
    """
    Checks if a person has reached or exceeded the allowed number of consecutive assignments within a specified time window ending on the given reference date.

    Args:
        assigned_dates (List[date]): List of dates the person was assigned to serve.
        preaching_dates (List[date]): List of dates the person was scheduled to preach.
        reference_date (date): The current event date to evaluate against.
        limit (int): Maximum number of allowed consecutive assignments (default is 3).

    Returns:
        bool: True if the number of assignments/preaching dates within the time window
              is greater than or equal to the limit, False otherwise.
    """
    all_dates = assigned_dates + preaching_dates
    window_start = reference_date - timedelta(weeks=limit)

    relevant_dates = [d for d in all_dates if window_start <= d <= reference_date]
    return len(relevant_dates) >= limit
