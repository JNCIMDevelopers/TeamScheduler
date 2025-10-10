"""
Dependency injection setup for FastAPI.

This module provides dependency factories for services and repositories.
"""

from functools import lru_cache
from typing import List

from ..core.services.schedule_service import ScheduleService
from ..core.services.eligibility_service import (
    EligibilityService,
    PersonSelectionService,
)
from ..core.services.eligibility_rules import get_default_eligibility_rules
from ..core.services.worship_leader_selector import RotationWorshipLeaderSelector
from ..core.interfaces.repositories import (
    PersonRepository,
    EventRepository,
    PreacherRepository,
)
from ..infrastructure.database.repositories import (
    InMemoryPersonRepository,
    InMemoryEventRepository,
    InMemoryPreacherRepository,
)


@lru_cache()
def get_person_repository() -> PersonRepository:
    """Get person repository instance."""
    return InMemoryPersonRepository()


@lru_cache()
def get_event_repository() -> EventRepository:
    """Get event repository instance."""
    return InMemoryEventRepository()


@lru_cache()
def get_preacher_repository() -> PreacherRepository:
    """Get preacher repository instance."""
    return InMemoryPreacherRepository()


@lru_cache()
def get_eligibility_service() -> EligibilityService:
    """Get eligibility service with default rules."""
    rules = get_default_eligibility_rules()
    return EligibilityService(rules)


@lru_cache()
def get_worship_leader_selector() -> RotationWorshipLeaderSelector:
    """Get worship leader selector with default rotation."""
    # TODO: Load rotation from configuration or database
    default_rotation = ["Gee", "John", "Sarah", "Michael"]
    return RotationWorshipLeaderSelector(default_rotation)


@lru_cache()
def get_person_selection_service() -> PersonSelectionService:
    """Get person selection service."""
    worship_leader_selector = get_worship_leader_selector()
    return PersonSelectionService(worship_leader_selector)


@lru_cache()
def get_schedule_service() -> ScheduleService:
    """Get fully configured schedule service."""
    person_repo = get_person_repository()
    event_repo = get_event_repository()
    preacher_repo = get_preacher_repository()
    eligibility_service = get_eligibility_service()
    selection_service = get_person_selection_service()

    return ScheduleService(
        person_repository=person_repo,
        event_repository=event_repo,
        preacher_repository=preacher_repo,
        eligibility_service=eligibility_service,
        selection_service=selection_service,
    )


# Configuration functions for updating services at runtime


def update_worship_leader_rotation(rotation: List[str]) -> None:
    """Update the worship leader rotation order."""
    selector = get_worship_leader_selector()
    selector.set_rotation_order(rotation)

    # Clear cache to force recreation with new selector
    get_person_selection_service.cache_clear()
    get_schedule_service.cache_clear()


def add_eligibility_rule(rule) -> None:
    """Add a new eligibility rule to the service."""
    eligibility_service = get_eligibility_service()
    eligibility_service.add_rule(rule)


def remove_eligibility_rule(rule_class: type) -> None:
    """Remove eligibility rules of a specific type."""
    eligibility_service = get_eligibility_service()
    eligibility_service.remove_rule(rule_class)
