import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_instructor, require_non_admin
from app.db.database import get_db
from app.schemas.lesson_schemas import (
    LessonCreate,
    LessonUpdate,
    LessonOut,
)
from app.services.lesson_service import LessonService

# Reads open to Instructor/Student; writes restricted to Instructor below.
router = APIRouter(dependencies=[Depends(require_non_admin)])


@router.get("", status_code=status.HTTP_200_OK, response_model=List[LessonOut])
async def list_lessons(
    db: AsyncSession = Depends(get_db),
):
    return await LessonService(db).list_lessons()


@router.get("/{lesson_id}", status_code=status.HTTP_200_OK, response_model=LessonOut)
async def get_lesson(
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await LessonService(db).get_lesson(lesson_id)


@router.post(
    "",
    response_model=LessonOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_instructor)],
)
async def create_lesson(
    payload: LessonCreate,
    db: AsyncSession = Depends(get_db),
):
    return await LessonService(db).create_lesson(payload)


@router.put(
    "/{lesson_id}",
    status_code=status.HTTP_200_OK,
    response_model=LessonOut,
    dependencies=[Depends(require_instructor)],
)
async def update_lesson(
    lesson_id: uuid.UUID,
    payload: LessonUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await LessonService(db).update_lesson(
        lesson_id,
        payload,
    )


@router.delete(
    "/{lesson_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_instructor)],
)
async def delete_lesson(
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await LessonService(db).delete_lesson(lesson_id)
