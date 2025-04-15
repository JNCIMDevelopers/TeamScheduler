# Standard Library Imports
import pytest
from datetime import date
from unittest.mock import MagicMock

# Local Imports
from schedule_builder.eligibility.eligibility_checker import EligibilityChecker
from schedule_builder.eligibility.eligibility_rule import EligibilityRule
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role
from schedule_builder.models.preacher import Preacher


# Fixtures for reusable setup
@pytest.fixture
def person():
    return Person(
        name="TestName",
        roles=[Role.WORSHIPLEADER, Role.EMCEE],
        blockout_dates=[],
        preaching_dates=[],
        teaching_dates=[],
        on_leave=False,
    )


@pytest.fixture
def event_date():
    return date(2025, 4, 6)


@pytest.fixture
def preacher():
    return Preacher(
        name="TestPreacher", graphics_support="Test", dates=[date(2025, 4, 6)]
    )


def test_is_eligible_with_no_rules(person, event_date):
    # Arrange
    checker = EligibilityChecker(rules=[])

    # Act
    is_eligible = checker.is_eligible(person, Role.WORSHIPLEADER, event_date)

    # Assert
    assert is_eligible


def test_is_eligible_with_single_passing_rule(person, event_date):
    # Arrange
    mock_rule = MagicMock(spec=EligibilityRule)
    mock_rule.is_eligible.return_value = True
    checker = EligibilityChecker(rules=[mock_rule])

    # Act
    is_eligible = checker.is_eligible(person, Role.WORSHIPLEADER, event_date)

    # Assert
    assert is_eligible
    mock_rule.is_eligible.assert_called_once()


def test_is_eligible_with_single_failing_rule(person, event_date):
    # Arrange
    mock_rule = MagicMock(spec=EligibilityRule)
    mock_rule.is_eligible.return_value = False
    checker = EligibilityChecker(rules=[mock_rule])

    # Act
    is_eligible = checker.is_eligible(person, Role.WORSHIPLEADER, event_date)

    # Assert
    assert not is_eligible
    mock_rule.is_eligible.assert_called_once()


def test_is_eligible_with_multiple_passing_rules(person, event_date):
    # Arrange
    mock_rule1 = MagicMock(spec=EligibilityRule)
    mock_rule2 = MagicMock(spec=EligibilityRule)
    mock_rule1.is_eligible.return_value = True
    mock_rule2.is_eligible.return_value = True
    checker = EligibilityChecker(rules=[mock_rule1, mock_rule2])

    # Act
    is_eligible = checker.is_eligible(person, Role.WORSHIPLEADER, event_date)

    # Assert
    assert is_eligible
    mock_rule1.is_eligible.assert_called_once()
    mock_rule2.is_eligible.assert_called_once()


def test_if_returns_early_when_rule_fails(person, event_date):
    # Arrange
    mock_rule1 = MagicMock(spec=EligibilityRule)
    mock_rule2 = MagicMock(spec=EligibilityRule)
    mock_rule3 = MagicMock(spec=EligibilityRule)
    mock_rule1.is_eligible.return_value = True
    mock_rule2.is_eligible.return_value = False
    mock_rule3.is_eligible.return_value = True
    checker = EligibilityChecker(rules=[mock_rule1, mock_rule2, mock_rule3])

    # Act
    is_eligible = checker.is_eligible(person, Role.WORSHIPLEADER, event_date)

    # Assert
    assert not is_eligible
    mock_rule1.is_eligible.assert_called_once()
    mock_rule2.is_eligible.assert_called_once()
    mock_rule3.is_eligible.assert_not_called()
