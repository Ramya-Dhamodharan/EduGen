from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class ModuleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    course_id: UUID


class ModuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ModuleOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    course_id: UUID
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True