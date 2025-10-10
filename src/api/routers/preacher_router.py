"""
Preacher-related API endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from ...application.models import (
    PreacherCreateRequest,
    PreacherUpdateRequest,
    PreacherResponse,
)
from ...core.services.schedule_service import ScheduleService
from ..dependencies import get_schedule_service


router = APIRouter()


@router.get("/preachers", response_model=List[PreacherResponse])
async def get_all_preachers(
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Get all preachers in the system."""
    try:
        preachers = schedule_service.preacher_repo.get_all()
        return [PreacherResponse.model_validate(preacher) for preacher in preachers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preachers/{preacher_id}", response_model=PreacherResponse)
async def get_preacher(
    preacher_id: UUID, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """Get a specific preacher by ID."""
    try:
        preacher = schedule_service.preacher_repo.get_by_id(preacher_id)
        if not preacher:
            raise HTTPException(status_code=404, detail="Preacher not found")
        return PreacherResponse.model_validate(preacher)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preachers", response_model=PreacherResponse)
async def create_preacher(
    request: PreacherCreateRequest,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Create a new preacher."""
    try:
        from ...core.entities.event import Preacher

        preacher = Preacher(
            name=request.name,
            graphics_support=request.graphics_support,
            dates=request.dates,
        )

        saved_preacher = schedule_service.preacher_repo.save(preacher)
        return PreacherResponse.model_validate(saved_preacher)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preachers/{preacher_id}", response_model=PreacherResponse)
async def update_preacher(
    preacher_id: UUID,
    request: PreacherUpdateRequest,
    schedule_service: ScheduleService = Depends(get_schedule_service),
):
    """Update an existing preacher."""
    try:
        preacher = schedule_service.preacher_repo.get_by_id(preacher_id)
        if not preacher:
            raise HTTPException(status_code=404, detail="Preacher not found")

        # Update fields if provided
        if request.name is not None:
            preacher.name = request.name
        if request.graphics_support is not None:
            preacher.graphics_support = request.graphics_support
        if request.dates is not None:
            preacher.dates = request.dates

        saved_preacher = schedule_service.preacher_repo.save(preacher)
        return PreacherResponse.model_validate(saved_preacher)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/preachers/{preacher_id}")
async def delete_preacher(
    preacher_id: UUID, schedule_service: ScheduleService = Depends(get_schedule_service)
):
    """Delete a preacher."""
    try:
        success = schedule_service.preacher_repo.delete(preacher_id)
        if not success:
            raise HTTPException(status_code=404, detail="Preacher not found")
        return {"message": "Preacher deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
