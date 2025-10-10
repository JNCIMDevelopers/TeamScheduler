"""
Person-related API endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from ...application.models import (
    PersonCreateRequest,
    PersonUpdateRequest,
    PersonResponse,
)
from ...core.services.schedule_service import ScheduleService
from ..dependencies import get_schedule_service


router = APIRouter()


@router.get("/persons", response_model=List[PersonResponse])
async def get_all_persons(
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Get all persons in the system."""
    try:
        persons = schedule_service.person_repo.get_all()
        return [PersonResponse.model_validate(person) for person in persons]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/persons/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: UUID, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """Get a specific person by ID."""
    try:
        person = schedule_service.person_repo.get_by_id(person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return PersonResponse.model_validate(person)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/persons", response_model=PersonResponse)
async def create_person(
    request: PersonCreateRequest,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Create a new person."""
    try:
        from ...core.entities.person import Person

        person = Person(
            name=request.name,
            roles=request.roles,
            blockout_dates=request.blockout_dates,
            preaching_dates=request.preaching_dates,
            teaching_dates=request.teaching_dates,
            on_leave=request.on_leave,
        )

        saved_person = schedule_service.person_repo.save(person)
        return PersonResponse.model_validate(saved_person)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/persons/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: UUID,
    request: PersonUpdateRequest,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Update an existing person."""
    try:
        person = schedule_service.person_repo.get_by_id(person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        # Update fields if provided
        if request.name is not None:
            person.name = request.name
        if request.roles is not None:
            person.roles = request.roles
        if request.blockout_dates is not None:
            person.blockout_dates = request.blockout_dates
        if request.preaching_dates is not None:
            person.preaching_dates = request.preaching_dates
        if request.teaching_dates is not None:
            person.teaching_dates = request.teaching_dates
        if request.on_leave is not None:
            person.on_leave = request.on_leave

        saved_person = schedule_service.person_repo.save(person)
        return PersonResponse.model_validate(saved_person)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/persons/{person_id}")
async def delete_person(
    person_id: UUID, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """Delete a person."""
    try:
        success = schedule_service.person_repo.delete(person_id)
        if not success:
            raise HTTPException(status_code=404, detail="Person not found")
        return {"message": "Person deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
