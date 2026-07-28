import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_staff, require_user
from app.db.database import get_db
from app.schemas.category_schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
)
from app.schemas.course_schemas import CourseOut
from app.services.category_service import CategoryService

# Reads open to any logged-in user; writes restricted to staff (Admin/Instructor).
router = APIRouter(dependencies=[Depends(require_user)])


@router.get("", response_model=List[CategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    return await CategoryService(db).list_categories()


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await CategoryService(db).get_category(category_id)


@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_staff)],
)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    return await CategoryService(db).create_category(payload)


@router.put(
    "/{category_id}",
    response_model=CategoryOut,
    dependencies=[Depends(require_staff)],
)
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await CategoryService(db).update_category(
        category_id,
        payload,
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_staff)],
)
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await CategoryService(db).delete_category(category_id)


@router.get(
    "/{category_id}/courses",
    response_model=List[CourseOut],
)
async def list_courses_in_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await CategoryService(db).get_courses_in_category(
        category_id
    )