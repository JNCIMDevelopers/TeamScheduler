"""
Tests for eligibility rules and eligibility service.
"""

from datetime import date

from src.core.entities.person import Person
from src.core.entities.event import Event, Preacher
from src.core.entities.role import Role
from src.core.services.eligibility_service import EligibilityService
from src.core.services.eligibility_rules import (
    RoleCapabilityRule,
    AvailabilityRule,
    ConsecutiveAssignmentLimitRule,
    RoleTimeWindowRule,
    WorshipLeaderTeachingConflictRule,
    PreachingConflictRule,
    LuluEmceeRule,
    GeeWorshipLeaderRule,
    JeffMarielConflictRule,
    MarkDrumsDateRule,
    AubreyDaveRule,
)


class TestEligibilityRules:
    """Test individual eligibility rules."""

    def test_role_capability_rule(self):
        """Test role capability checking rule."""
        rule = RoleCapabilityRule()
        person = Person(name="Test", roles=[Role.DRUMS, Role.BASS])
        event = Event(date=date(2024, 6, 15))

        # Person can perform drums
        assert rule.is_eligible(person, Role.DRUMS, event)

        # Person cannot perform worship leader
        assert not rule.is_eligible(person, Role.WORSHIP_LEADER, event)

    def test_availability_rule(self):
        """Test availability checking rule."""
        rule = AvailabilityRule()
        person = Person(
            name="Test",
            roles=[Role.DRUMS],
            blockout_dates=[date(2024, 12, 25)],
            preaching_dates=[date(2024, 1, 7)],
            on_leave=False,
        )
        event_available = Event(date=date(2024, 6, 15))
        event_blocked = Event(date=date(2024, 12, 25))
        event_preaching = Event(date=date(2024, 1, 7))

        # Available on normal date
        assert rule.is_eligible(person, Role.DRUMS, event_available)

        # Not available on blocked date
        assert not rule.is_eligible(person, Role.DRUMS, event_blocked)

        # Not available on preaching date
        assert not rule.is_eligible(person, Role.DRUMS, event_preaching)

        # Not available when on leave
        person.on_leave = True
        assert not rule.is_eligible(person, Role.DRUMS, event_available)

    def test_consecutive_assignment_limit_rule(self):
        """Test consecutive assignment limit rule."""
        rule = ConsecutiveAssignmentLimitRule(max_consecutive_weeks=2)
        person = Person(name="Test", roles=[Role.DRUMS])

        # Assign person to previous weeks
        person.assigned_dates = [
            date(2024, 6, 1),  # 2 weeks ago
            date(2024, 6, 8),  # 1 week ago
        ]

        # Should not be eligible (would be 3rd consecutive)
        event = Event(date=date(2024, 6, 15))
        assert not rule.is_eligible(person, Role.DRUMS, event)

        # Should be eligible if there's a gap
        person.assigned_dates = [
            date(2024, 5, 25),  # 3 weeks ago
            date(2024, 6, 8),  # 1 week ago (gap of 1 week)
        ]
        assert rule.is_eligible(person, Role.DRUMS, event)

    def test_role_time_window_rule(self):
        """Test minimum time between same role assignments."""
        time_windows = {Role.WORSHIP_LEADER: 4}  # 4 weeks minimum
        rule = RoleTimeWindowRule(time_windows)
        person = Person(name="Test", roles=[Role.WORSHIP_LEADER])

        # Set last assignment date
        last_assignment = date(2024, 6, 1)
        person.last_assigned_dates[Role.WORSHIP_LEADER] = last_assignment

        # Too soon (only 2 weeks later)
        event_too_soon = Event(date=date(2024, 6, 15))
        assert not rule.is_eligible(person, Role.WORSHIP_LEADER, event_too_soon)

        # Enough time (4+ weeks later)
        event_ok = Event(date=date(2024, 6, 29))
        assert rule.is_eligible(person, Role.WORSHIP_LEADER, event_ok)

        # Role not in time windows (should always be eligible)
        assert rule.is_eligible(person, Role.DRUMS, event_too_soon)

    def test_worship_leader_teaching_conflict_rule(self):
        """Test worship leader cannot be assigned when teaching."""
        rule = WorshipLeaderTeachingConflictRule()
        person = Person(
            name="Test", roles=[Role.WORSHIP_LEADER], teaching_dates=[date(2024, 6, 15)]
        )

        event = Event(date=date(2024, 6, 15))

        # Cannot be worship leader when teaching
        assert not rule.is_eligible(person, Role.WORSHIP_LEADER, event)

        # Can be assigned to other roles when teaching
        assert rule.is_eligible(person, Role.DRUMS, event)

        # Can be worship leader on non-teaching date
        event_other = Event(date=date(2024, 6, 22))
        assert rule.is_eligible(person, Role.WORSHIP_LEADER, event_other)

    def test_preaching_conflict_rule(self):
        """Test person cannot be assigned when preaching."""
        rule = PreachingConflictRule()
        person = Person(
            name="Test", roles=[Role.DRUMS], preaching_dates=[date(2024, 6, 15)]
        )

        event = Event(date=date(2024, 6, 15))

        # Cannot be assigned when preaching
        assert not rule.is_eligible(person, Role.DRUMS, event)

        # Can be assigned on non-preaching date
        event_other = Event(date=date(2024, 6, 22))
        assert rule.is_eligible(person, Role.DRUMS, event_other)


class TestSpecialBusinessRules:
    """Test special business rules for specific people."""

    def test_lulu_emcee_rule(self):
        """Test Lulu can only be EMCEE when Pastor Edmund is preaching."""
        rule = LuluEmceeRule()
        lulu = Person(name="Lulu", roles=[Role.EMCEE])
        edmund = Preacher(name="Edmund", graphics_support="Team A")
        kris = Preacher(name="Kris", graphics_support="Team B")

        # Event with Edmund preaching
        event_edmund = Event(date=date(2024, 6, 15))
        event_edmund.set_team_and_preachers([lulu], [edmund])
        event_edmund.preacher_id = edmund.id

        # Event with Kris preaching
        event_kris = Event(date=date(2024, 6, 22))
        event_kris.set_team_and_preachers([lulu], [kris])
        event_kris.preacher_id = kris.id

        # Lulu can be EMCEE when Edmund preaches
        assert rule.is_eligible(lulu, Role.EMCEE, event_edmund)

        # Lulu cannot be EMCEE when Kris preaches
        assert not rule.is_eligible(lulu, Role.EMCEE, event_kris)

        # Rule doesn't apply to other people
        other_person = Person(name="Other", roles=[Role.EMCEE])
        assert rule.is_eligible(other_person, Role.EMCEE, event_kris)

    def test_gee_worship_leader_rule(self):
        """Test Gee cannot be worship leader when Kris is preaching."""
        rule = GeeWorshipLeaderRule()
        gee = Person(name="Gee", roles=[Role.WORSHIP_LEADER])
        kris_preacher = Preacher(name="Kris", graphics_support="Team B")
        edmund_preacher = Preacher(name="Edmund", graphics_support="Team A")

        # Event with Kris preaching
        event_kris = Event(date=date(2024, 6, 15))
        event_kris.set_team_and_preachers([gee], [kris_preacher])
        event_kris.preacher_id = kris_preacher.id

        # Event with Edmund preaching
        event_edmund = Event(date=date(2024, 6, 22))
        event_edmund.set_team_and_preachers([gee], [edmund_preacher])
        event_edmund.preacher_id = edmund_preacher.id

        # Gee cannot be worship leader when Kris preaches
        assert not rule.is_eligible(gee, Role.WORSHIP_LEADER, event_kris)

        # Gee can be worship leader when Edmund preaches
        assert rule.is_eligible(gee, Role.WORSHIP_LEADER, event_edmund)

    def test_jeff_mariel_conflict_rule(self):
        """Test Jeff and Mariel cannot both be assigned to same event."""
        rule = JeffMarielConflictRule()
        jeff = Person(name="Jeff", roles=[Role.BASS])
        mariel = Person(name="Mariel", roles=[Role.LYRICS])
        other = Person(name="Other", roles=[Role.DRUMS])

        event = Event(date=date(2024, 6, 15))
        event.set_team_and_preachers([jeff, mariel, other], [])

        # Initially both can be assigned
        assert rule.is_eligible(jeff, Role.BASS, event)
        assert rule.is_eligible(mariel, Role.LYRICS, event)

        # After Jeff is assigned, Mariel cannot be
        event.assign_person_to_role(Role.BASS, jeff)
        assert not rule.is_eligible(mariel, Role.LYRICS, event)

        # Rule doesn't apply to other people
        assert rule.is_eligible(other, Role.DRUMS, event)

    def test_mark_drums_date_rule(self):
        """Test Mark cannot be assigned to drums until September 2025."""
        rule = MarkDrumsDateRule()
        mark = Person(name="Mark", roles=[Role.DRUMS])

        # Before September 2025
        event_before = Event(date=date(2025, 8, 15))
        assert not rule.is_eligible(mark, Role.DRUMS, event_before)

        # September 2025 and after
        event_after = Event(date=date(2025, 9, 1))
        assert rule.is_eligible(mark, Role.DRUMS, event_after)

        # Rule doesn't apply to other roles
        assert rule.is_eligible(mark, Role.LIVE, event_before)

        # Rule doesn't apply to other people
        other = Person(name="Other", roles=[Role.DRUMS])
        assert rule.is_eligible(other, Role.DRUMS, event_before)

    def test_aubrey_dave_rule(self):
        """Test Aubrey can only be assigned when Dave is also assigned."""
        rule = AubreyDaveRule()
        aubrey = Person(name="Aubrey", roles=[Role.SUNDAY_SCHOOL_TEACHER])
        dave = Person(name="Dave", roles=[Role.LIVE])
        other = Person(name="Other", roles=[Role.DRUMS])

        event = Event(date=date(2024, 6, 15))
        event.set_team_and_preachers([aubrey, dave, other], [])

        # Initially Aubrey cannot be assigned (Dave not assigned)
        assert not rule.is_eligible(aubrey, Role.SUNDAY_SCHOOL_TEACHER, event)

        # After Dave is assigned, Aubrey can be assigned
        event.assign_person_to_role(Role.LIVE, dave)
        assert rule.is_eligible(aubrey, Role.SUNDAY_SCHOOL_TEACHER, event)

        # Rule doesn't apply to other people
        assert rule.is_eligible(other, Role.DRUMS, event)


class TestEligibilityService:
    """Test the eligibility service that combines multiple rules."""

    def test_eligibility_service_with_multiple_rules(self):
        """Test eligibility service evaluates all rules."""
        rules = [
            RoleCapabilityRule(),
            AvailabilityRule(),
        ]
        service = EligibilityService(rules)

        person = Person(
            name="Test",
            roles=[Role.DRUMS],  # Can perform drums
            blockout_dates=[date(2024, 12, 25)],  # Blocked on Christmas
            on_leave=False,
        )

        event_available = Event(date=date(2024, 6, 15))
        event_blocked = Event(date=date(2024, 12, 25))

        # Passes both rules
        assert service.is_eligible(person, Role.DRUMS, event_available)

        # Fails availability rule
        assert not service.is_eligible(person, Role.DRUMS, event_blocked)

        # Fails capability rule
        assert not service.is_eligible(person, Role.WORSHIP_LEADER, event_available)

    def test_get_eligible_persons(self):
        """Test getting all eligible persons for a role."""
        rules = [RoleCapabilityRule(), AvailabilityRule()]
        service = EligibilityService(rules)

        person1 = Person(name="Drummer", roles=[Role.DRUMS], on_leave=False)
        person2 = Person(name="Bassist", roles=[Role.BASS], on_leave=False)
        person3 = Person(name="OnLeave", roles=[Role.DRUMS], on_leave=True)

        candidates = [person1, person2, person3]
        event = Event(date=date(2024, 6, 15))

        eligible = service.get_eligible_persons(Role.DRUMS, event, candidates)

        # Only person1 should be eligible for drums
        assert len(eligible) == 1
        assert eligible[0].name == "Drummer"

    def test_add_remove_rules(self):
        """Test adding and removing rules from service."""
        service = EligibilityService([RoleCapabilityRule()])
        person = Person(name="Test", roles=[Role.DRUMS], on_leave=True)
        event = Event(date=date(2024, 6, 15))

        # Initially only capability rule - person is eligible
        assert service.is_eligible(person, Role.DRUMS, event)

        # Add availability rule - person becomes ineligible (on leave)
        service.add_rule(AvailabilityRule())
        assert not service.is_eligible(person, Role.DRUMS, event)

        # Remove availability rule - person becomes eligible again
        service.remove_rule(AvailabilityRule)
        assert service.is_eligible(person, Role.DRUMS, event)
