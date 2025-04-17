# Standard Library Imports
import pytest
from datetime import date

# Local Imports
from schedule_builder.models.person import Person
from schedule_builder.models.preacher import Preacher
from ui.application import App


@pytest.fixture
def mock_app_data():
    mock_team = [Person(name="TestPerson", roles=[])]
    mock_preachers = [
        Preacher(
            name="TestPreacher",
            graphics_support="TestSupport",
            dates=[date(2025, 4, 6), date(2025, 4, 13), date(2025, 4, 20)],
        )
    ]
    mock_rotation = ["TestPerson"]
    return mock_team, mock_preachers, mock_rotation


def test_app_initialization(mock_app_data):
    # Assert
    mock_team, mock_preachers, mock_rotation = mock_app_data

    # Act
    app = App(team=mock_team, preachers=mock_preachers, rotation=mock_rotation)

    # Assert
    assert app.team == mock_team
    assert app.preachers == mock_preachers
    assert app.rotation == mock_rotation
    assert app.earliest_date == date(2025, 4, 6)
    assert app.latest_date == date(2025, 4, 20)
