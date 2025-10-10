from datetime import date
from typing import List, Tuple, Optional
import logging
import copy

from ..entities.person import Person
from ..entities.event import Event
from ..entities.role import Role
from ..interfaces.repositories import (
    PersonRepository,
    EventRepository,
    PreacherRepository,
)
from .eligibility_service import EligibilityService, PersonSelectionService


class ScheduleService:
    """
    Core service for generating and managing team schedules.

    This service encapsulates the main business logic for schedule generation,
    separated from UI and database concerns.
    """

    def __init__(
        self,
        person_repository: PersonRepository,
        event_repository: EventRepository,
        preacher_repository: PreacherRepository,
        eligibility_service: EligibilityService,
        selection_service: PersonSelectionService,
    ):
        self.person_repo = person_repository
        self.event_repo = event_repository
        self.preacher_repo = preacher_repository
        self.eligibility_service = eligibility_service
        self.selection_service = selection_service
        self.logger = logging.getLogger(__name__)

    def generate_schedule(
        self, start_date: date, end_date: date, save_events: bool = True
    ) -> Tuple[List[Event], List[Person]]:
        """
        Generate a complete schedule for the specified date range.

        Args:
            start_date: Start date for schedule generation
            end_date: End date for schedule generation
            save_events: Whether to save the generated events to repository

        Returns:
            Tuple of (generated events, updated team with assignment tracking)
        """
        self.logger.info(f"Generating schedule from {start_date} to {end_date}")

        # Get all team members and preachers
        team = self.person_repo.get_all()
        preachers = self.preacher_repo.get_all()

        if not team:
            self.logger.warning("No team members available for scheduling")
            return [], []

        # Generate event dates (Sundays only)
        event_dates = self._get_sunday_dates(start_date, end_date)
        self.logger.debug(f"Event dates: {event_dates}")

        # Deep copy team to prevent modifications from persisting
        team_copy = copy.deepcopy(team)
        events = []

        for event_date in event_dates:
            self.logger.debug(f"Processing event date: {event_date}")

            # Create event
            event = Event(date=event_date)
            event.set_team_and_preachers(team_copy, preachers)

            # Assign preacher if available
            preacher = self.preacher_repo.get_preacher_for_date(event_date)
            if preacher:
                event.preacher_id = preacher.id

            # Assign roles in priority order
            self._assign_roles_for_event(event, team_copy)
            events.append(event)

        if save_events:
            saved_events = self.event_repo.save_many(events)
            return saved_events, team_copy

        return events, team_copy

    def update_assignment(
        self, event_id: str, role: Role, person_name: Optional[str]
    ) -> bool:
        """
        Update a role assignment for a specific event.

        Args:
            event_id: ID of the event to update
            role: Role to assign/unassign
            person_name: Name of person to assign, or None to unassign

        Returns:
            True if update was successful
        """
        try:
            from uuid import UUID

            event = self.event_repo.get_by_id(UUID(event_id))
            if not event:
                self.logger.error(f"Event not found: {event_id}")
                return False

            if person_name is None:
                # Unassign role
                event.unassign_role(role)
            else:
                # Assign role to person
                person = self.person_repo.get_by_name(person_name)
                if not person:
                    self.logger.error(f"Person not found: {person_name}")
                    return False

                # Check eligibility
                team = self.person_repo.get_all()
                preachers = self.preacher_repo.get_all()
                event.set_team_and_preachers(team, preachers)

                if not self.eligibility_service.is_eligible(person, role, event):
                    self.logger.warning(
                        f"Person {person_name} is not eligible for {role.value}"
                    )
                    return False

                event.assign_person_to_role(role, person)

            # Save updated event
            self.event_repo.save(event)
            return True

        except Exception as e:
            self.logger.error(f"Error updating assignment: {e}")
            return False

    def get_available_replacements(self, event_id: str, role: Role) -> List[str]:
        """
        Get list of persons who can replace the current assignment for a role.

        Args:
            event_id: ID of the event
            role: Role to find replacements for

        Returns:
            List of person names who are eligible for the role
        """
        try:
            from uuid import UUID

            event = self.event_repo.get_by_id(UUID(event_id))
            if not event:
                return []

            team = self.person_repo.get_all()
            preachers = self.preacher_repo.get_all()
            event.set_team_and_preachers(team, preachers)

            eligible_persons = self.eligibility_service.get_eligible_persons(
                role, event, team
            )
            return [person.name for person in eligible_persons]

        except Exception as e:
            self.logger.error(f"Error getting replacements: {e}")
            return []

    def _assign_roles_for_event(self, event: Event, team: List[Person]) -> None:
        """
        Assign all roles for a single event.

        Args:
            event: Event to assign roles for
            team: Available team members
        """
        # Create a shallow copy for role assignment to avoid modifying the original team
        available_team = team.copy()

        for role in Role.get_assignment_order():
            self.logger.debug(f"Assigning role: {role.value}")

            eligible_persons = self.eligibility_service.get_eligible_persons(
                role, event, available_team
            )

            selected_person = self.selection_service.select_person_for_role(
                role, eligible_persons, event
            )

            if selected_person:
                event.assign_person_to_role(role, selected_person)
                # Remove from available team to prevent double assignment
                available_team.remove(selected_person)
                self.logger.info(
                    f"Assigned {selected_person.name} to {role.value} on {event.date}"
                )
            else:
                self.logger.warning(f"Could not assign {role.value} on {event.date}")

    def _get_sunday_dates(self, start_date: date, end_date: date) -> List[date]:
        """
        Get all Sunday dates between start_date and end_date (inclusive).

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of Sunday dates
        """
        from datetime import timedelta

        sundays = []
        current_date = start_date

        # Find first Sunday on or after start_date
        days_until_sunday = (6 - current_date.weekday()) % 7
        if days_until_sunday > 0:
            current_date = current_date + timedelta(days=days_until_sunday)

        # Collect all Sundays until end_date
        while current_date <= end_date:
            sundays.append(current_date)
            current_date += timedelta(days=7)

        return sundays
