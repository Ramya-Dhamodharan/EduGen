from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.db.database import get_db
from app.schemas.role_schemas import (
    RoleCreate,
    RoleOut,
    RoleUpdate,
)
from app.services.role_service import RoleService

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", status_code=status.HTTP_200_OK, response_model=List[RoleOut])
async def list_roles(
    db: AsyncSession = Depends(get_db),
):
    return await RoleService(db).list_roles()


@router.get("/{role_id}", status_code=status.HTTP_200_OK, response_model=RoleOut)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await RoleService(db).get_role(role_id)


@router.post(
    "",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    return await RoleService(db).create_role(payload)


@router.put("/{role_id}", status_code=status.HTTP_200_OK, response_model=RoleOut)
async def update_role(
    role_id: int,
    payload: RoleUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await RoleService(db).update_role(
        role_id,
        payload,
    )


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
):
    await RoleService(db).delete_role(role_id)
