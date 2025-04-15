# Standard Library Imports
import pytest
from datetime import date, timedelta

# Local Imports
from schedule_builder.eligibility.rules import (
    RoleCapabilityRule,
    OnLeaveRule,
    BlockoutDateRule,
    PreachingDateRule,
    RoleTimeWindowRule,
    ConsecutiveAssignmentLimitRule,
    ConsecutiveRoleAssignmentLimitRule,
    WorshipLeaderTeachingRule,
    WorshipLeaderPreachingConflictRule,
    LuluEmceeRule,
    GeeWorshipLeaderRule,
)
from schedule_builder.models.person import Person
from schedule_builder.models.role import Role
from schedule_builder.models.preacher import Preacher

# Fixtures for reusable setup
@pytest.fixture
def person():
    return Person(
        name="TestName",
        roles=[Role.WORSHIPLEADER, Role.EMCEE, Role.SUNDAYSCHOOLTEACHER],
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
    return Preacher(name="Edmund", graphics_support="Test", dates=[date(2025, 4, 6)])

class TestRoleCapabilityRule:
    def test_person_with_role_is_eligible(self, person, event_date):
        # Arrange
        rule = RoleCapabilityRule()
        person.roles = [Role.WORSHIPLEADER]

        # Act
        is_eligible = rule.is_eligible(person, Role.WORSHIPLEADER, event_date)

        # Assert
        assert is_eligible

    def test_person_without_role_is_ineligible(self, person, event_date):
        # Arrange
        rule = RoleCapabilityRule()
        person.roles = [Role.EMCEE]

        # Act
        is_eligible = rule.is_eligible(person, Role.LYRICS, event_date)

        # Assert
        assert not is_eligible

class TestOnLeaveRule:
    def test_person_on_leave_is_ineligible(self, person, event_date):
        # Arrange
        rule = OnLeaveRule()
        person.on_leave = True
    
        # Act
        is_eligible = rule.is_eligible(person, Role.WORSHIPLEADER, event_date)

        # Assert
        assert not is_eligible

    def test_person_not_on_leave_is_eligible(self, person, event_date):
        # Arrange
        rule = OnLeaveRule()
        person.on_leave = False

        # Act
        is_eligible = rule.is_eligible(person, Role.WORSHIPLEADER, event_date)

        # Assert
        assert is_eligible

class TestBlockoutDateRule:
    @pytest.mark.parametrize(
        "blockout_dates, event_date, expected",
        [
            ([date(2025, 4, 6)], date(2025, 4, 6), False),  # Blockout date matches event date
            ([date(2025, 4, 13)], date(2025, 4, 6), True),  # Blockout date does not match
            ([], date(2025, 4, 6), True),  # No blockout dates
        ],
    )
    def test_blockout_date_rule(self, blockout_dates, event_date, expected, person):
        # Arrange
        rule = BlockoutDateRule()
        person.blockout_dates = blockout_dates

        # Act
        is_eligible = rule.is_eligible(person, Role.WORSHIPLEADER, event_date)

        # Assert
        assert is_eligible == expected

class TestPreachingDateRule:
    @pytest.mark.parametrize(
        "preaching_dates, event_date, expected",
        [
            ([date(2025, 4, 6)], date(2025, 4, 6), False),  # Preaching date matches event date
            ([date(2025, 4, 13)], date(2025, 4, 6), True),  # Preaching date does not match
            ([], date(2025, 4, 6), True),  # No preaching dates
        ],
    )
    def test_preaching_date_rule(self, preaching_dates, event_date, expected, person):
        # Arrange
        rule = PreachingDateRule()
        person.preaching_dates = preaching_dates
        
        # Act
        is_eligible = rule.is_eligible(person, Role.WORSHIPLEADER, event_date)

        # Assert
        assert is_eligible == expected

class TestRoleTimeWindowRule:
    @pytest.mark.parametrize(
        "role, last_assigned_date, event_date, expected",
        [
            (Role.WORSHIPLEADER, date(2025, 3, 9), date(2025, 4, 6), False),  # Within time window
            (Role.WORSHIPLEADER, date(2025, 3, 2), date(2025, 4, 6), True),  # Outside time window
            (Role.WORSHIPLEADER, None, date(2025, 4, 6), True),  # Not assigned recently
            (Role.SUNDAYSCHOOLTEACHER, date(2025, 3, 9), date(2025, 4, 6), False),  # Within time window
            (Role.SUNDAYSCHOOLTEACHER, date(2025, 3, 2), date(2025, 4, 6), True),  # Outside time window
            (Role.SUNDAYSCHOOLTEACHER, None, date(2025, 4, 6), True),  # Not assigned recently
            (Role.EMCEE, date(2025, 3, 23), date(2025, 4, 6), False),  # Within time window
            (Role.EMCEE, date(2025, 3, 16), date(2025, 4, 6), True),  # Outside time window
            (Role.EMCEE, None, date(2025, 4, 6), True),  # Not assigned recently
        ],
    )
    def test_role_time_window_rule(self, role, last_assigned_date, event_date, expected, person):
        # Arrange
        rule = RoleTimeWindowRule()
        person.roles = [role]
        person.last_assigned_dates[role] = last_assigned_date

        # Act
        is_eligible = rule.is_eligible(person, role, event_date)

        # Assert
        assert is_eligible == expected

class TestConsecutiveAssignmentLimitRule:
    def test_person_not_assigned_too_many_times_is_eligible(self, person, event_date):
        # Arrange
        rule = ConsecutiveAssignmentLimitRule()
        person.assigned_dates = [
            event_date - timedelta(weeks=1),
            event_date - timedelta(weeks=2)
        ]

        # Act
        is_eligible = rule.is_eligible(person, Role.ACOUSTIC, event_date)

        # Assert
        assert is_eligible

    def test_person_with_no_assignments_is_eligible(self, person, event_date):
        # Arrange
        rule = ConsecutiveAssignmentLimitRule()
        person.assigned_dates = []

        # Act
        is_eligible = rule.is_eligible(person, Role.ACOUSTIC, event_date)

        # Assert
        assert is_eligible

    def test_person_assigned_too_many_times_is_ineligible(self, person, event_date):
        # Arrange
        rule = ConsecutiveAssignmentLimitRule()
        person.assigned_dates = [
            event_date - timedelta(weeks=1),
            event_date - timedelta(weeks=2),
            event_date - timedelta(weeks=3),
        ]

        # Act
        is_eligible = rule.is_eligible(person, Role.ACOUSTIC, event_date)

        # Assert
        assert not is_eligible

class TestConsecutiveRoleAssignmentLimitRule:
    def test_person_within_role_assignment_limit_is_eligible(self, person, event_date):
        # Arrange
        rule = ConsecutiveRoleAssignmentLimitRule(assignment_limit=3)
        person.role_assigned_dates[Role.LYRICS] = [
            event_date - timedelta(weeks=1),
            event_date - timedelta(weeks=2),
        ]

        # Act
        is_eligible = rule.is_eligible(person, Role.LYRICS, event_date)

        # Assert
        assert is_eligible

    def test_person_exceeding_role_assignment_limit_is_ineligible(self, person, event_date):
        # Arrange
        rule = ConsecutiveRoleAssignmentLimitRule(assignment_limit=3)
        person.role_assigned_dates[Role.LYRICS] = [
            event_date - timedelta(weeks=1),
            event_date - timedelta(weeks=2),
            event_date - timedelta(weeks=3),
        ]

        # Act
        is_eligible = rule.is_eligible(person, Role.LYRICS, event_date)

        # Assert
        assert not is_eligible

class TestWorshipLeaderTeachingRule:
    @pytest.mark.parametrize(
        "role, teaching_dates, event_date, expected",
        [
            (Role.WORSHIPLEADER, [date(2025, 4, 6)], date(2025, 4, 6), False),  # Teaching date matches event date
            (Role.WORSHIPLEADER, [date(2025, 4, 13)], date(2025, 4, 6), True),  # Teaching date does not match
            (Role.WORSHIPLEADER, [], date(2025, 4, 6), True),  # No teaching dates
            (Role.KEYS, [date(2025, 4, 6)], date(2025, 4, 6), True),  # Non-Worship Leader role
        ],
    )
    def test_worship_leader_with_no_teaching_conflict(self, role, teaching_dates, event_date, expected, person):
        # Arrange
        rule = WorshipLeaderTeachingRule()
        person.roles = [role]
        person.teaching_dates = teaching_dates

        # Act
        is_eligible = rule.is_eligible(person, role, event_date)

        # Assert
        assert is_eligible == expected

class TestWorshipLeaderPreachingConflictRule:
    @pytest.mark.parametrize(
        "role, preaching_dates, event_date, expected",
        [
            (Role.WORSHIPLEADER, [date(2025, 4, 6)], date(2025, 4, 6), False),  # Preaching on same date
            (Role.WORSHIPLEADER, [date(2025, 4, 13)], date(2025, 4, 6), False),  # Preaching within time window
            (Role.WORSHIPLEADER, [date(2025, 3, 30)], date(2025, 4, 6), True),  # Preaching outside and before time window
            (Role.WORSHIPLEADER, [date(2025, 4, 20)], date(2025, 4, 6), True),  # Preaching outside and after time window
            (Role.WORSHIPLEADER, [], date(2025, 4, 6), True),  # No preaching dates
            (Role.KEYS, [date(2025, 4, 6)], date(2025, 4, 6), True),  # Non-Worship Leader role
        ],
    )
    def test_worship_leader_with_no_preaching_conflict(self, role, preaching_dates, event_date, expected, person):
        # Arrange
        rule = WorshipLeaderPreachingConflictRule()
        person.roles = [role]
        person.preaching_dates = preaching_dates

        # Act
        is_eligible = rule.is_eligible(person, role, event_date)

        # Assert
        assert is_eligible == expected

class TestLuluEmceeRule:
    @pytest.mark.parametrize(
        "person_name, preacher_name, expected",
        [
            ("Lulu", "Edmund", True),
            ("Lulu", "OtherPreacher", False),
            ("OtherEmcee", "Edmund", True)
        ],
    )
    def test_lulu_emcee_rule(self, person_name, preacher_name, expected):
        # Arrange
        rule = LuluEmceeRule()
        person.name = person_name
        person.role = [Role.EMCEE]
        event_date = date(2025, 4, 6)
        preacher = Preacher(name=preacher_name, graphics_support="Test", dates=[event_date])

        # Act
        is_eligible = rule.is_eligible(person, Role.EMCEE, event_date, preacher)

        # Assert
        assert is_eligible == expected

class TestGeeWorshipLeaderRule:
    @pytest.mark.parametrize(
        "role, person_name, preacher_name, expected",
        [
            (Role.WORSHIPLEADER, "Gee", "Kris", False),
            (Role.WORSHIPLEADER, "Gee", "TestPreacher", True),
            (Role.BACKUP, "Gee", "Kris", True),
            (Role.WORSHIPLEADER, "TestName", "Kris", True),
        ],
    )
    def test_gee_is_eligible_when_kris_is_preaching(self, role, person_name, preacher_name, expected):
        # Arrange
        rule = GeeWorshipLeaderRule()
        person.name = person_name
        person.roles = [role]
        event_date = date(2025, 4, 6)
        preacher = Preacher(name=preacher_name, graphics_support="Test", dates=[event_date])

        # Act
        is_eligible = rule.is_eligible(person, role, event_date, preacher)

        # Assert
        assert is_eligible == expected