"""
Application layer DTOs (Data Transfer Objects) and request/response models.

These models define the API contract and are separate from domain entities.
"""

from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from ..core.entities.role import Role


class PersonCreateRequest(BaseModel):
    """Request model for creating a new person."""

    name: str = Field(..., min_length=1, max_length=100)
    roles: List[Role] = Field(default_factory=list)
    blockout_dates: List[date] = Field(default_factory=list)
    preaching_dates: List[date] = Field(default_factory=list)
    teaching_dates: List[date] = Field(default_factory=list)
    on_leave: bool = False


class PersonUpdateRequest(BaseModel):
    """Request model for updating a person."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    roles: Optional[List[Role]] = None
    blockout_dates: Optional[List[date]] = None
    preaching_dates: Optional[List[date]] = None
    teaching_dates: Optional[List[date]] = None
    on_leave: Optional[bool] = None


class PersonResponse(BaseModel):
    """Response model for person data."""

    id: UUID
    name: str
    roles: List[Role]
    blockout_dates: List[date]
    preaching_dates: List[date]
    teaching_dates: List[date]
    on_leave: bool
    assigned_dates: List[date] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PreacherCreateRequest(BaseModel):
    """Request model for creating a new preacher."""

    name: str = Field(..., min_length=1, max_length=100)
    graphics_support: str = Field(default="", max_length=100)
    dates: List[date] = Field(default_factory=list)


class PreacherUpdateRequest(BaseModel):
    """Request model for updating a preacher."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    graphics_support: Optional[str] = Field(None, max_length=100)
    dates: Optional[List[date]] = None


class PreacherResponse(BaseModel):
    """Response model for preacher data."""

    id: UUID
    name: str
    graphics_support: str
    dates: List[date]

    model_config = ConfigDict(from_attributes=True)


class EventResponse(BaseModel):
    """Response model for event data."""

    id: UUID
    date: date
    assignments: Dict[Role, Optional[str]]
    preacher_id: Optional[UUID] = None
    preacher_name: Optional[str] = None
    preacher_graphics_support: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ScheduleGenerateRequest(BaseModel):
    """Request model for generating a schedule."""

    start_date: date
    end_date: date
    save_events: bool = True


class ScheduleGenerateResponse(BaseModel):
    """Response model for schedule generation."""

    events: List[EventResponse]
    message: str
    events_created: int


class AssignmentUpdateRequest(BaseModel):
    """Request model for updating a role assignment."""

    role: Role
    person_name: Optional[str] = None  # None to unassign


class AssignmentUpdateResponse(BaseModel):
    """Response model for assignment update."""

    success: bool
    message: str
    event: Optional[EventResponse] = None


class AvailableReplacementsResponse(BaseModel):
    """Response model for getting available replacements."""

    role: Role
    available_persons: List[str]
    event_date: date


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    detail: Optional[str] = None
    status_code: int
