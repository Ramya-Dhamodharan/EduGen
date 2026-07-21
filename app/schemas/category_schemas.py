from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class CategoryOut(BaseModel):
    id: UUID
    name: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True