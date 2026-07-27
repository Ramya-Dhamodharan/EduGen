from datetime import datetime
from uuid import UUID
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    language: Optional[str] = None
    duration: Optional[str] = None
    level: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: UUID


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    language: Optional[str] = None
    duration: Optional[str] = None
    level: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[UUID] = None


class CourseStatusUpdate(BaseModel):
    is_active: bool


class CourseOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    language: Optional[str] = None
    duration: Optional[str] = None
    level: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: UUID
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True