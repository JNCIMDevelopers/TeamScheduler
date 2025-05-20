# Standard Library Imports
import pytest
from datetime import date
from unittest.mock import patch, MagicMock, ANY

# Local Imports
from schedule_builder.builders.schedule import Schedule
from schedule_builder.eligibility.eligibility_checker import EligibilityChecker
from schedule_builder.helpers.worship_leader_selector import WorshipLeaderSelector
from schedule_builder.models.event import Event
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from schedule_builder.models.role import Role
from ui.ui_schedule_handler import UIScheduleHandler


@pytest.fixture
def mock_schedule_handler_data():
    mock_team = [Person(name="TestPerson", roles=[Role.WORSHIPLEADER])]
    mock_preachers = [
        Preacher(
            name="TestPreacher",
            graphics_support="TestSupport",
            dates=[date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)],
        )
    ]
    mock_rotation = ["TestPerson"]
    mock_file_exporter = MagicMock()
    return mock_team, mock_preachers, mock_rotation, mock_file_exporter


@pytest.fixture
def mock_schedule_handler(mock_schedule_handler_data):
    mock_team, mock_preachers, mock_rotation, mock_file_exporter = (
        mock_schedule_handler_data
    )
    return UIScheduleHandler(
        team=mock_team,
        preachers=mock_preachers,
        worship_leader_selector=WorshipLeaderSelector(rotation=mock_rotation),
        eligibility_checker=EligibilityChecker(rules=[]),
        file_exporter=mock_file_exporter,
        schedule_class=Schedule,
    )


def test_schedule_handler_initialization(mock_schedule_handler_data):
    # Arrange
    mock_team, mock_preachers, mock_rotation, mock_file_exporter = (
        mock_schedule_handler_data
    )
    worship_leader_selector = WorshipLeaderSelector(rotation=mock_rotation)
    eligibility_checker = EligibilityChecker(rules=[])
    schedule_class = Schedule

    # Act
    schedule_handler = UIScheduleHandler(
        team=mock_team,
        preachers=mock_preachers,
        worship_leader_selector=worship_leader_selector,
        eligibility_checker=eligibility_checker,
        file_exporter=mock_file_exporter,
        schedule_class=schedule_class,
    )

    # Assert
    assert schedule_handler.team == mock_team
    assert schedule_handler.preachers == mock_preachers
    assert schedule_handler.worship_leader_selector == worship_leader_selector
    assert schedule_handler.eligibility_checker == eligibility_checker
    assert schedule_handler.file_exporter == mock_file_exporter
    assert schedule_handler.schedule_class == schedule_class
    assert schedule_handler.earliest_date == date(2025, 4, 6)
    assert schedule_handler.latest_date == date(2025, 4, 20)


@pytest.mark.parametrize(
    "preacher_data",
    [
        None,  # No preacher data
        [],  # Empty preacher data
        [
            Preacher(
                name="TestPreacher",
                graphics_support="TestSupport",
                dates=[],
            )
        ],  # Preacher with no dates
    ],
)
def test_schedule_handler_initialization_with_invalid_preacher_data(
    mock_schedule_handler_data, preacher_data
):
    # Arrange
    mock_team, mock_preachers, mock_rotation, mock_file_exporter = (
        mock_schedule_handler_data
    )
    mock_preachers = preacher_data

    # Act and Assert
    with pytest.raises(ValueError):
        UIScheduleHandler(
            team=mock_team,
            preachers=mock_preachers,
            worship_leader_selector=WorshipLeaderSelector(rotation=mock_rotation),
            eligibility_checker=EligibilityChecker(rules=[]),
            file_exporter=mock_file_exporter,
            schedule_class=Schedule,
        )


@pytest.mark.parametrize(
    "preaching_dates, expected_earliest_date, expected_latest_date",
    [
        (
            [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)],
            date(2025, 4, 6),
            date(2025, 4, 20),
        ),
        ([date(2025, 4, 6)], date(2025, 4, 6), date(2025, 4, 6)),  # Single date
        (
            [date(2025, 4, 6), date(2025, 4, 6), date(2025, 4, 13)],
            date(2025, 4, 6),
            date(2025, 4, 13),
        ),  # Duplicate dates
    ],
)
def test_calculate_preaching_date_range(
    mock_schedule_handler_data,
    preaching_dates,
    expected_earliest_date,
    expected_latest_date,
):
    # Arrange
    mock_team, mock_preachers, mock_rotation, mock_file_exporter = (
        mock_schedule_handler_data
    )
    mock_preachers = [
        Preacher(
            name="TestPreacher",
            graphics_support="TestSupport",
            dates=preaching_dates,
        )
    ]
    schedule_handler = UIScheduleHandler(
        team=mock_team,
        preachers=mock_preachers,
        worship_leader_selector=WorshipLeaderSelector(rotation=mock_rotation),
        eligibility_checker=EligibilityChecker(rules=[]),
        file_exporter=mock_file_exporter,
        schedule_class=Schedule,
    )

    # Act
    earliest_date, latest_date = schedule_handler.calculate_preaching_date_range()

    # Assert
    assert earliest_date == expected_earliest_date
    assert latest_date == expected_latest_date


@pytest.mark.parametrize(
    "preacher_data",
    [
        None,  # No preacher data
        [],  # Empty preacher data
        [
            Preacher(
                name="TestPreacher",
                graphics_support="TestSupport",
                dates=[],
            )
        ],  # Preacher with no dates
    ],
)
def test_calculate_preaching_date_range_with_invalid_preacher_data(
    mock_schedule_handler_data, preacher_data
):
    # Arrange
    mock_team, mock_preachers, mock_rotation, mock_file_exporter = (
        mock_schedule_handler_data
    )
    schedule_handler = UIScheduleHandler(
        team=mock_team,
        preachers=mock_preachers,
        worship_leader_selector=WorshipLeaderSelector(rotation=mock_rotation),
        eligibility_checker=EligibilityChecker(rules=[]),
        file_exporter=mock_file_exporter,
        schedule_class=Schedule,
    )
    schedule_handler.preachers = preacher_data

    # Act and Assert
    with pytest.raises(ValueError):
        schedule_handler.calculate_preaching_date_range()


@pytest.mark.parametrize(
    "reference_date, expected_result",
    [
        (date(2025, 4, 6), True),  # Lower boundary
        (date(2025, 4, 27), True),  # Upper boundary
        (date(2025, 3, 30), False),  # Below range
        (date(2025, 5, 4), False),  # Above range
    ],
)
def test_is_within_date_range(mock_schedule_handler, reference_date, expected_result):
    # Arrange
    mock_schedule_handler.earliest_date = date(2025, 4, 6)
    mock_schedule_handler.latest_date = date(2025, 4, 27)

    # Act
    is_within_range = mock_schedule_handler.is_within_date_range(
        reference_date=reference_date
    )

    # Assert
    assert is_within_range == expected_result


@pytest.mark.parametrize(
    "start_date, end_date, expected_result",
    [
        (
            date(2025, 3, 30),
            date(2025, 5, 4),
            True,
        ),  # Within range
        (
            date(2025, 4, 6),
            date(2025, 4, 27),
            True,
        ),  # Exactly at the range limits
        (
            date(2025, 4, 13),
            date(2025, 5, 4),
            False,
        ),  # Lower bound is outside the range
        (
            date(2025, 3, 30),
            date(2025, 4, 20),
            False,
        ),  # Upper bound is outside the range
        (
            date(2025, 4, 13),
            date(2025, 4, 20),
            False,
        ),  # Outside range
    ],
)
def test_is_preaching_schedule_within_date_range(
    mock_schedule_handler, start_date, end_date, expected_result
):
    # Arrange
    mock_schedule_handler.earliest_date = date(2025, 4, 6)
    mock_schedule_handler.latest_date = date(2025, 4, 27)

    # Act
    is_within_range = mock_schedule_handler.is_preaching_schedule_within_date_range(
        start_date=start_date, end_date=end_date
    )

    # Assert
    assert is_within_range == expected_result


@pytest.mark.parametrize(
    "start_date_input, end_date_input, expected_start_date, expected_end_date, expected_is_adjusted",
    [
        (
            date(2025, 4, 13),
            date(2025, 4, 20),
            date(2025, 4, 13),
            date(2025, 4, 20),
            False,
        ),  # Within range, no adjustment needed
        (
            date(2025, 4, 6),
            date(2025, 4, 27),
            date(2025, 4, 6),
            date(2025, 4, 27),
            False,
        ),  # Exactly at the range limits, no adjustment needed
        (
            date(2025, 3, 30),
            date(2025, 4, 20),
            date(2025, 4, 6),
            date(2025, 4, 20),
            True,
        ),  # Adjust start date
        (
            date(2025, 4, 6),
            date(2025, 5, 4),
            date(2025, 4, 6),
            date(2025, 4, 27),
            True,
        ),  # Adjust end date
        (
            date(2025, 3, 30),
            date(2025, 5, 4),
            date(2025, 4, 6),
            date(2025, 4, 27),
            True,
        ),  # Adjust both dates
    ],
)
def test_adjust_dates_within_range(
    mock_schedule_handler,
    start_date_input,
    end_date_input,
    expected_start_date,
    expected_end_date,
    expected_is_adjusted,
):
    # Arrange
    mock_schedule_handler.earliest_date = date(2025, 4, 6)
    mock_schedule_handler.latest_date = date(2025, 4, 27)

    # Act
    actual_start_date, actual_end_date, actual_is_adjusted = (
        mock_schedule_handler.adjust_dates_within_range(
            start_date=start_date_input, end_date=end_date_input
        )
    )

    # Assert
    assert actual_start_date == expected_start_date
    assert actual_end_date == expected_end_date
    assert actual_is_adjusted == expected_is_adjusted


@pytest.mark.parametrize(
    "event_date, expected_result",
    [
        (date(2025, 5, 11), True),  # Date found
        (date(2025, 5, 25), False),  # Date not found
    ],
)
def test_get_event_by_date(mock_schedule_handler, event_date, expected_result):
    # Arrange
    event1 = Event(date=date(2025, 5, 11))
    event2 = Event(date=date(2025, 5, 18))
    events = [event1, event2]
    event_date_str = event_date.strftime("%Y-%m-%d")

    # Act
    actual_event = mock_schedule_handler.get_event_by_date(
        events=events, event_date_str=event_date_str
    )

    # Assert
    assert actual_event is (event1 if expected_result else None)


def test_get_available_replacements_for_event(mock_schedule_handler):
    # Arrange
    event = MagicMock()
    role = MagicMock()
    person1 = MagicMock()
    person1.name = "TestPerson1"
    person2 = MagicMock()
    person2.name = "TestPerson2"
    person3 = MagicMock()
    person3.name = "TestPerson3"
    event.team = [person1, person2, person3]
    event.is_assignable_if_needed.side_effect = (
        lambda role, person: person is person1 or person is person3
    )

    # Act
    available_names = mock_schedule_handler.get_available_replacements_for_event(
        event, role
    )

    # Assert
    assert available_names == [person1.name, person3.name]


@patch("ui.ui_schedule_handler.get_all_sundays")
@patch("ui.ui_schedule_handler.Schedule")
def test_build_schedule(
    mock_schedule_class, mock_get_all_sundays, mock_schedule_handler_data
):
    # Arrange
    mock_start_date = date(2025, 4, 6)
    mock_end_date = date(2025, 4, 20)
    mock_sundays = [date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)]
    mock_events = ["Event1", "Event2", "Event3"]
    mock_updated_team = ["UpdatedPerson1", "UpdatedPerson2"]
    mock_get_all_sundays.return_value = mock_sundays
    mock_schedule_instance = MagicMock()
    mock_schedule_instance.build.return_value = (mock_events, mock_updated_team)
    mock_schedule_class.return_value = mock_schedule_instance

    mock_team, mock_preachers, mock_rotation, mock_file_exporter = (
        mock_schedule_handler_data
    )
    mock_schedule_handler = UIScheduleHandler(
        team=mock_team,
        preachers=mock_preachers,
        worship_leader_selector=WorshipLeaderSelector(rotation=mock_rotation),
        eligibility_checker=EligibilityChecker(rules=[]),
        file_exporter=mock_file_exporter,
        schedule_class=mock_schedule_class,
    )

    # Act
    events, updated_team = mock_schedule_handler.build_schedule(
        start_date=mock_start_date, end_date=mock_end_date
    )

    # Assert
    assert events == mock_events
    assert updated_team == mock_updated_team
    mock_get_all_sundays.assert_called_once_with(
        start_date=mock_start_date, end_date=mock_end_date
    )
    mock_schedule_class.assert_called_once_with(
        team=ANY,  # Ignore memory address due to deepcopy in application code
        preachers=mock_schedule_handler.preachers,
        worship_leader_selector=mock_schedule_handler.worship_leader_selector,
        eligibility_checker=mock_schedule_handler.eligibility_checker,
        event_dates=mock_sundays,
    )
    mock_schedule_instance.build.assert_called_once()


def test_build_schedule_with_real_schedule(mock_schedule_handler_data):
    # Arrange
    mock_team, mock_preachers, mock_rotation, mock_file_exporter = (
        mock_schedule_handler_data
    )
    schedule_handler = UIScheduleHandler(
        team=mock_team,
        preachers=mock_preachers,
        worship_leader_selector=WorshipLeaderSelector(rotation=mock_rotation),
        eligibility_checker=EligibilityChecker(rules=[]),
        file_exporter=mock_file_exporter,
        schedule_class=Schedule,
    )

    start_date = date(2025, 4, 6)
    end_date = date(2025, 4, 20)

    # Act
    events, updated_team = schedule_handler.build_schedule(
        start_date=start_date, end_date=end_date
    )

    # Assert
    assert isinstance(events, list)
    assert isinstance(updated_team, list)
