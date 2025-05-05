from datetime import date, timedelta
from typing import List


def has_exceeded_consecutive_assignments(
    assigned_dates: List[date],
    preaching_dates: List[date],
    reference_date: date,
    limit: int,
) -> bool:
    """
    Determines whether a person has met or exceeded the maximum number of assignments
    (serving or preaching) within the past `limit` weeks up to and including `reference_date`.

    Args:
        assigned_dates (Sequence[date]): Dates the person was assigned to serve.
        preaching_dates (Sequence[date]): Dates the person was scheduled to preach.
        reference_date (date): The date of the event being evaluated.
        limit (int): Maximum allowed number of assignments within the time window.

    Returns:
        bool: True if the number of assignments/preaching dates in the window
              is greater than or equal to `limit`, False otherwise.

    Raises:
        ValueError: If `reference_date` is None or `limit` is not a positive integer.
    """
    if not reference_date:
        raise ValueError("Invalid reference date.")

    if limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    window_start = reference_date - timedelta(weeks=limit)
    all_dates = assigned_dates + preaching_dates

    dates_within_window = [d for d in all_dates if window_start <= d <= reference_date]
    return len(dates_within_window) >= limit
