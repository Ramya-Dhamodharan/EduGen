import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_instructor, require_non_admin
from app.db.database import get_db
from app.schemas.course_schemas import (
    CourseCreate,
    CourseOut,
    CourseStatusUpdate,
    CourseUpdate,
)
from app.schemas.module_schemas import ModuleCreate, ModuleOut
from app.services.course_service import CourseService
from app.services.module_service import ModuleService

# Reads are open to Instructor/Student (catalog browsing). Writes are
# Instructor-only per-endpoint below.
router = APIRouter(dependencies=[Depends(require_non_admin)])


@router.get("/search", response_model=List[CourseOut])
async def search_courses(
    query: Optional[str] = None,
    category: Optional[uuid.UUID] = None,
    level: Optional[str] = None,
    language: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await CourseService(db).search_courses(
        query,
        category,
        level,
        language,
    )


@router.get("", response_model=List[CourseOut])
async def list_courses(
    db: AsyncSession = Depends(get_db),
):
    return await CourseService(db).list_courses()


@router.get("/{course_id}", response_model=CourseOut)
async def get_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await CourseService(db).get_course(course_id)


@router.post(
    "",
    response_model=CourseOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_instructor)],
)
async def create_course(
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
):
    return await CourseService(db).create_course(payload)


@router.put(
    "/{course_id}",
    response_model=CourseOut,
    dependencies=[Depends(require_instructor)],
)
async def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await CourseService(db).update_course(
        course_id,
        payload,
    )


@router.patch(
    "/{course_id}/status",
    response_model=CourseOut,
    dependencies=[Depends(require_instructor)],
)
async def update_course_status(
    course_id: uuid.UUID,
    payload: CourseStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await CourseService(db).update_course_status(
        course_id,
        payload,
    )


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_instructor)],
)
async def delete_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await CourseService(db).delete_course(course_id)


@router.get("/{course_id}/modules", response_model=List[ModuleOut])
async def list_modules_in_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await CourseService(db).get_modules(course_id)


@router.post(
    "/{course_id}/modules",
    response_model=ModuleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_instructor)],
)
async def create_module_under_course(
    course_id: uuid.UUID,
    payload: ModuleCreate,
    db: AsyncSession = Depends(get_db),
):
    return await ModuleService(db).create_module_under_course(
        course_id,
        payload.title,
        payload.description,
    )


@router.get("/{course_id}/reviews")
async def list_reviews_for_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    reviews = await CourseService(db).get_reviews(course_id)

    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "rating": r.rating,
            "review": r.review,
        }
        for r in reviews
    ]


@router.get("/{course_id}/quizzes")
async def list_quizzes_for_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    quizzes = await CourseService(db).get_quizzes(course_id)

    return [
        {
            "id": q.id,
            "title": q.title,
            "total_marks": q.total_marks,
            "pass_marks": q.pass_marks,
        }
        for q in quizzes
    ]


@router.get(
    "/{course_id}/enrollments",
    dependencies=[Depends(require_instructor)],
)
async def list_enrollments_for_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    enrollments = await CourseService(db).get_enrollments(course_id)

    return [
        {
            "id": e.id,
            "student_id": e.student_id,
            "status": e.status,
        }
        for e in enrollments
    ]