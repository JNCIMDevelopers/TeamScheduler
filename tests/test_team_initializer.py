import json
import pytest
from unittest.mock import patch, mock_open
from schedule_builder.builders.team_initializer import TeamInitializer
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from schedule_builder.models.role import Role

# Sample test data
TEAM_DATA = [
    {
        "name": "TestPerson",
        "roles": ["WORSHIPLEADER", "EMCEE"],
        "blockout_dates": ["2025-04-20"],
        "preaching_dates": ["2025-04-27"],
        "teaching_dates": ["2025-05-04"],
        "on_leave": False,
    }
]

PREACHING_DATA = [
    {
        "name": "TestPreacher",
        "graphics": "TestGraphics",
        "dates": ["2025-04-20", "2025-05-01"],
    }
]

ROTATION_DATA = ["TestPerson", "TestPreacher"]


@pytest.fixture
def team_initializer():
    """Fixture to initialize the TeamInitializer."""
    return TeamInitializer()


@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(TEAM_DATA))
@patch("schedule_builder.builders.file_builder.resource_path", return_value="mock_path")
def test_initialize_persons(mock_resource_path, mock_file, team_initializer):
    # Act
    persons = team_initializer.initialize_persons()

    # Assert
    assert len(persons) == 1
    assert isinstance(persons[0], Person)
    assert persons[0].name == TEAM_DATA[0]["name"]
    assert len(persons[0].roles) == len(TEAM_DATA[0]["roles"])
    assert Role.WORSHIPLEADER in persons[0].roles
    assert Role.EMCEE in persons[0].roles
    assert persons[0].blockout_dates[0].isoformat() == TEAM_DATA[0]["blockout_dates"][0]
    assert (
        persons[0].preaching_dates[0].isoformat() == TEAM_DATA[0]["preaching_dates"][0]
    )
    assert persons[0].teaching_dates[0].isoformat() == TEAM_DATA[0]["teaching_dates"][0]
    assert persons[0].on_leave == TEAM_DATA[0]["on_leave"]


@pytest.mark.parametrize(
    "missing_field, data",
    [
        (
            "name",
            [
                {
                    "roles": ["WORSHIPLEADER", "EMCEE"],
                    "blockout_dates": ["2025-04-20"],
                    "preaching_dates": ["2025-04-27"],
                    "teaching_dates": ["2025-05-04"],
                    "on_leave": False,
                }
            ],
        ),
        (
            "name",
            [
                {
                    "invalid_field": "TestPerson",
                    "roles": ["WORSHIPLEADER", "EMCEE"],
                    "blockout_datess": ["2025-04-20"],
                    "preaching_dates": ["2025-04-27"],
                    "teaching_dates": ["2025-05-04"],
                    "on_leave": False,
                }
            ],
        ),
        (
            "roles",
            [
                {
                    "name": "TestPerson",
                    "blockout_dates": ["2025-04-20"],
                    "preaching_dates": ["2025-04-27"],
                    "teaching_dates": ["2025-05-04"],
                    "on_leave": False,
                }
            ],
        ),
        (
            "roles",
            [
                {
                    "name": "TestPerson",
                    "invalid_field": ["WORSHIPLEADER", "EMCEE"],
                    "blockout_datess": ["2025-04-20"],
                    "preaching_dates": ["2025-04-27"],
                    "teaching_dates": ["2025-05-04"],
                    "on_leave": False,
                }
            ],
        ),
    ],
)
def test_initialize_persons_with_missing_fields(missing_field, data, team_initializer):
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        with patch(
            "schedule_builder.builders.file_builder.resource_path",
            return_value="mock_path",
        ):
            with pytest.raises(KeyError, match=missing_field):
                team_initializer.initialize_persons()


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=json.dumps([{"name": "TestPerson", "roles": ["INVALID ROLE"]}]),
)
@patch("schedule_builder.builders.file_builder.resource_path", return_value="mock_path")
def test_initialize_persons_with_invalid_role(
    mock_resource_path, mock_file, team_initializer
):
    with pytest.raises(AttributeError):
        team_initializer.initialize_persons()


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=json.dumps(
        [
            {
                "name": "TestPerson",
                "roles": ["WORSHIPLEADER"],
                "blockout_dates": ["INVALID-DATE"],
            }
        ]
    ),
)
@patch("schedule_builder.builders.file_builder.resource_path", return_value="mock_path")
def test_initialize_persons_with_invalid_date(
    mock_resource_path, mock_file, team_initializer
):
    with pytest.raises(ValueError):
        team_initializer.initialize_persons()


@patch("builtins.open", new_callable=mock_open, read_data=json.dumps([]))
@patch("schedule_builder.builders.file_builder.resource_path", return_value="mock_path")
def test_initialize_persons_when_empty(mock_resource_path, mock_file, team_initializer):
    # Act
    persons = team_initializer.initialize_persons()

    # Assert
    assert persons == []


@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(PREACHING_DATA))
@patch("schedule_builder.builders.file_builder.resource_path", return_value="mock_path")
def test_initialize_preachers(mock_resource_path, mock_file, team_initializer):
    # Act
    preachers = team_initializer.initialize_preachers()

    # Assert
    assert len(preachers) == 1
    assert isinstance(preachers[0], Preacher)
    assert preachers[0].name == PREACHING_DATA[0]["name"]
    assert preachers[0].graphics_support == PREACHING_DATA[0]["graphics"]
    assert len(preachers[0].dates) == len(PREACHING_DATA[0]["dates"])
    assert preachers[0].dates[0].isoformat() == PREACHING_DATA[0]["dates"][0]


@pytest.mark.parametrize(
    "missing_field, data",
    [
        (
            "name",
            [
                {
                    "graphics": "TestGraphics",
                    "dates": ["2025-04-20", "2025-05-01"],
                }
            ],
        ),
        (
            "name",
            [
                {
                    "invalid_field": "TestPreacher",
                    "graphics": "TestGraphics",
                    "dates": ["2025-04-20", "2025-05-01"],
                }
            ],
        ),
        (
            "graphics",
            [
                {
                    "name": "TestPreacher",
                    "dates": ["2025-04-20", "2025-05-01"],
                }
            ],
        ),
        (
            "graphics",
            [
                {
                    "name": "TestPreacher",
                    "invalid_field": "TestGraphics",
                    "dates": ["2025-04-20", "2025-05-01"],
                }
            ],
        ),
    ],
)
def test_initialize_preachers_with_missing_fields(
    missing_field, data, team_initializer
):
    with patch("builtins.open", mock_open(read_data=json.dumps(data))):
        with patch(
            "schedule_builder.builders.file_builder.resource_path",
            return_value="mock_path",
        ):
            with pytest.raises(KeyError, match=missing_field):
                team_initializer.initialize_preachers()


@patch("builtins.open", new_callable=mock_open, read_data=json.dumps([]))
@patch("schedule_builder.builders.file_builder.resource_path", return_value="mock_path")
def test_initialize_preachers_when_empty(
    mock_resource_path, mock_file, team_initializer
):
    # Act
    preachers = team_initializer.initialize_preachers()

    # Assert
    assert preachers == []


@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(ROTATION_DATA))
@patch("schedule_builder.builders.file_builder.resource_path", return_value="mock_path")
def test_initialize_rotation(mock_resource_path, mock_file, team_initializer):
    # Act
    rotation = team_initializer.initialize_rotation()

    # Assert
    assert len(rotation) == 2
    assert rotation == ROTATION_DATA


@patch("builtins.open", new_callable=mock_open, read_data=json.dumps([]))
@patch("schedule_builder.builders.file_builder.resource_path", return_value="mock_path")
def test_initialize_rotation_when_empty(
    mock_resource_path, mock_file, team_initializer
):
    # Act
    rotation = team_initializer.initialize_rotation()

    # Assert
    assert rotation == []


@patch(
    "schedule_builder.builders.team_initializer.TeamInitializer.initialize_persons",
    return_value=[
        Person(
            name="TestPerson",
            roles=[],
            blockout_dates=[],
            preaching_dates=[],
            teaching_dates=[],
            on_leave=False,
        )
    ],
)
@patch(
    "schedule_builder.builders.team_initializer.TeamInitializer.initialize_preachers",
    return_value=[
        Preacher(name="TestPreacher", graphics_support="TestGraphics", dates=[])
    ],
)
@patch(
    "schedule_builder.builders.team_initializer.TeamInitializer.initialize_rotation",
    return_value=["TestPerson", "TestPerson2"],
)
def test_initialize_team(mock_rotation, mock_preachers, mock_persons, team_initializer):
    # Act
    persons, preachers, rotation = team_initializer.initialize_team()

    # Assert
    assert len(persons) == 1
    assert len(preachers) == 1
    assert len(rotation) == 2
