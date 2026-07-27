from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class RoleCreate(RoleBase):
    """Fields required to create a role."""
    pass


class RoleUpdate(BaseModel):
    """All fields optional — supports partial updates via PUT/PATCH."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)


class RoleOut(RoleBase):
    """Shape returned to the client."""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # allows .from_orm(role_model_instance)
