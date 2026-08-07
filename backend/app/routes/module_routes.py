import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_instructor, require_non_admin
from app.db.database import get_db
from app.schemas.lesson_schemas import LessonCreate, LessonOut
from app.schemas.module_schemas import (
    ModuleCreate,
    ModuleOut,
    ModuleUpdate,
)
from app.services.lesson_service import LessonService
from app.services.module_service import ModuleService

# Reads open to Instructor/Student; writes restricted to Instructor below.
router = APIRouter(dependencies=[Depends(require_non_admin)])


@router.get("", status_code=status.HTTP_200_OK, response_model=List[ModuleOut])
async def list_modules(
    db: AsyncSession = Depends(get_db),
):
    return await ModuleService(db).list_modules()


@router.get("/{module_id}", status_code=status.HTTP_200_OK, response_model=ModuleOut)
async def get_module(
    module_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await ModuleService(db).get_module(module_id)


@router.post(
    "",
    response_model=ModuleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_instructor)],
)
async def create_module(
    payload: ModuleCreate,
    db: AsyncSession = Depends(get_db),
):
    return await ModuleService(db).create_module(payload)


@router.put(
    "/{module_id}",
    status_code=status.HTTP_200_OK,
    response_model=ModuleOut,
    dependencies=[Depends(require_instructor)],
)
async def update_module(
    module_id: uuid.UUID,
    payload: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await ModuleService(db).update_module(
        module_id,
        payload,
    )


@router.delete(
    "/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_instructor)],
)
async def delete_module(
    module_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await ModuleService(db).delete_module(module_id)


@router.get(
    "/{module_id}/lessons",
    status_code=status.HTTP_200_OK,
    response_model=List[LessonOut],
)
async def list_lessons_in_module(
    module_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await ModuleService(db).get_lessons(module_id)


@router.post(
    "/{module_id}/lessons",
    response_model=LessonOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_instructor)],
)
async def create_lesson_under_module(
    module_id: uuid.UUID,
    payload: LessonCreate,
    db: AsyncSession = Depends(get_db),
):
    return await LessonService(db).create_lesson_under_module(
        module_id,
        payload.title,
        payload.description,
        payload.video_url,
    )
