# Third-Party Imports
import pytest

# Standard Library Imports
from datetime import date

# Local Imports
from schedule_builder.helpers.worship_leader_selector import WorshipLeaderSelector
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role


@pytest.fixture
def team():
    role = Role.WORSHIPLEADER
    return [
        Person(name="Test1", roles=[role], blockout_dates=[], preaching_dates=[], teaching_dates=[], on_leave=False),
        Person(name="Test2", roles=[role], blockout_dates=[], preaching_dates=[], teaching_dates=[], on_leave=False),
        Person(name="Test3", roles=[role], blockout_dates=[], preaching_dates=[], teaching_dates=[], on_leave=False),
    ]

@pytest.fixture
def rotation():
    return ["Test2", "Test3", "Test1"]

def test_get_next_worship_leader_order(team, rotation):
    # Arrange
    selector = WorshipLeaderSelector(rotation)

    # Act
    worship_leader = selector.get_next(eligible_persons=team)
    next_worship_leader = selector.get_next(eligible_persons=team)
    next_next_worship_leader = selector.get_next(eligible_persons=team)

    # Assert
    assert worship_leader == team[1]
    assert next_worship_leader == team[2]
    assert next_next_worship_leader == team[0]

def test_get_next_worship_leader_when_rotation_does_not_match_any_persons(team):
    # Arrange
    rotation = ["TestX", "TestY", "TestZ"]
    selector = WorshipLeaderSelector(rotation)

    # Act
    worship_leader = selector.get_next(eligible_persons=team)

    # Assert
    assert worship_leader == None

def test_get_next_worship_leader_when_team_is_empty():
    # Arrange
    team = []
    rotation = ["Test1", "Test2", "Test3"]
    selector = WorshipLeaderSelector(rotation)

    # Act
    worship_leader = selector.get_next(eligible_persons=team)

    # Assert
    assert worship_leader == None

def test_get_next_worship_leader_when_rotation_is_empty(team):
    # Arrange
    rotation = []
    selector = WorshipLeaderSelector(rotation)

    # Act
    worship_leader = selector.get_next(eligible_persons=team)

    # Assert
    assert worship_leader == None