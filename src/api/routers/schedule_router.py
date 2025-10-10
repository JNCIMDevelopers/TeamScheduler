"""
Schedule-related API endpoints.
"""

from datetime import date
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from ...application.models import (
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
    AssignmentUpdateRequest,
    AssignmentUpdateResponse,
    AvailableReplacementsResponse,
    EventResponse,
    ErrorResponse,
)
from ...core.entities.role import Role
from ...core.services.schedule_service import ScheduleService
from ..dependencies import get_schedule_service


router = APIRouter()


@router.post("/schedule/generate", response_model=ScheduleGenerateResponse)
async def generate_schedule(
    request: ScheduleGenerateRequest,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """
    Generate a schedule for the specified date range.

    Args:
        request: Schedule generation parameters
        schedule_service: Injected schedule service

    Returns:
        Generated schedule with events
    """
    try:
        events, _ = schedule_service.generate_schedule(
            start_date=request.start_date,
            end_date=request.end_date,
            save_events=request.save_events,
        )

        event_responses = []
        for event in events:
            preacher = event.get_assigned_preacher()
            event_response = EventResponse(
                id=event.id,
                date=event.date,
                assignments=event.assignments,
                preacher_id=event.preacher_id,
                preacher_name=preacher.name if preacher else None,
                preacher_graphics_support=preacher.graphics_support
                if preacher
                else None,
            )
            event_responses.append(event_response)

        return ScheduleGenerateResponse(
            events=event_responses,
            message=f"Successfully generated schedule for {len(events)} events",
            events_created=len(events),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Schedule generation failed", detail=str(e), status_code=500
            ).dict(),
        )


@router.get("/schedule/events", response_model=List[EventResponse])
async def get_events(
    start_date: date,
    end_date: date,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """
    Get events between the specified dates.

    Args:
        start_date: Start date for event query
        end_date: End date for event query
        schedule_service: Injected schedule service

    Returns:
        List of events in the date range
    """
    try:
        events = schedule_service.event_repo.get_events_between(start_date, end_date)

        event_responses = []
        for event in events:
            # Set up team and preachers for business logic
            team = schedule_service.person_repo.get_all()
            preachers = schedule_service.preacher_repo.get_all()
            event.set_team_and_preachers(team, preachers)

            preacher = event.get_assigned_preacher()
            event_response = EventResponse(
                id=event.id,
                date=event.date,
                assignments=event.assignments,
                preacher_id=event.preacher_id,
                preacher_name=preacher.name if preacher else None,
                preacher_graphics_support=preacher.graphics_support
                if preacher
                else None,
            )
            event_responses.append(event_response)

        return event_responses

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to retrieve events", detail=str(e), status_code=500
            ).dict(),
        )


@router.put(
    "/schedule/events/{event_id}/assignment", response_model=AssignmentUpdateResponse
)
async def update_assignment(
    event_id: UUID,
    request: AssignmentUpdateRequest,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """
    Update a role assignment for a specific event.

    Args:
        event_id: ID of the event to update
        request: Assignment update details
        schedule_service: Injected schedule service

    Returns:
        Update result with success status
    """
    try:
        success = schedule_service.update_assignment(
            event_id=str(event_id), role=request.role, person_name=request.person_name
        )

        if not success:
            return AssignmentUpdateResponse(
                success=False,
                message="Failed to update assignment - check event ID, person eligibility",
            )

        # Get updated event for response
        updated_event = schedule_service.event_repo.get_by_id(event_id)
        if updated_event:
            team = schedule_service.person_repo.get_all()
            preachers = schedule_service.preacher_repo.get_all()
            updated_event.set_team_and_preachers(team, preachers)

            preacher = updated_event.get_assigned_preacher()
            event_response = EventResponse(
                id=updated_event.id,
                date=updated_event.date,
                assignments=updated_event.assignments,
                preacher_id=updated_event.preacher_id,
                preacher_name=preacher.name if preacher else None,
                preacher_graphics_support=preacher.graphics_support
                if preacher
                else None,
            )
        else:
            event_response = None

        return AssignmentUpdateResponse(
            success=True,
            message="Assignment updated successfully",
            event=event_response,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Assignment update failed", detail=str(e), status_code=500
            ).dict(),
        )


@router.get(
    "/schedule/events/{event_id}/replacements/{role}",
    response_model=AvailableReplacementsResponse,
)
async def get_available_replacements(
    event_id: UUID,
    role: Role,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """
    Get available replacements for a role in an event.

    Args:
        event_id: ID of the event
        role: Role to find replacements for
        schedule_service: Injected schedule service

    Returns:
        List of available person names who can fill the role
    """
    try:
        available_persons = schedule_service.get_available_replacements(
            event_id=str(event_id), role=role
        )

        # Get event date for response
        event = schedule_service.event_repo.get_by_id(event_id)
        event_date = event.date if event else date.today()

        return AvailableReplacementsResponse(
            role=role, available_persons=available_persons, event_date=event_date
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to get replacements", detail=str(e), status_code=500
            ).dict(),
        )
