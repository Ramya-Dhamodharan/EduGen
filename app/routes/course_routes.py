import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import require_staff, require_user
from app.schemas.course_schemas import CourseCreate, CourseUpdate, CourseStatusUpdate, CourseOut
from app.schemas.module_schemas import ModuleCreate, ModuleOut
from app.services.course_service import CourseService
from app.services.module_service import ModuleService

# Reads are open to any logged-in user (students browse the catalog).
# Writes are restricted to staff (Admin or Instructor) per-endpoint below.
router = APIRouter(dependencies=[Depends(require_user)])


@router.get("/search", response_model=List[CourseOut])
def search_courses(
    query: Optional[str] = None,
    category: Optional[uuid.UUID] = None,
    level: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return CourseService(db).search_courses(query, category, level, language)


@router.get("", response_model=List[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return CourseService(db).list_courses()


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    return CourseService(db).get_course(course_id)


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    return CourseService(db).create_course(payload)


@router.put("/{course_id}", response_model=CourseOut,
            dependencies=[Depends(require_staff)])
def update_course(course_id: uuid.UUID, payload: CourseUpdate, db: Session = Depends(get_db)):
    return CourseService(db).update_course(course_id, payload)


@router.patch("/{course_id}/status", response_model=CourseOut,
              dependencies=[Depends(require_staff)])
def update_course_status(course_id: uuid.UUID, payload: CourseStatusUpdate, db: Session = Depends(get_db)):
    return CourseService(db).update_course_status(course_id, payload)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_staff)])
def delete_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    CourseService(db).delete_course(course_id)


@router.get("/{course_id}/modules", response_model=List[ModuleOut])
def list_modules_in_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    return CourseService(db).get_modules(course_id)


@router.post("/{course_id}/modules", response_model=ModuleOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_staff)])
def create_module_under_course(course_id: uuid.UUID, payload: ModuleCreate, db: Session = Depends(get_db)):
    return ModuleService(db).create_module_under_course(course_id, payload.title, payload.description)


@router.get("/{course_id}/reviews")
def list_reviews_for_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    reviews = CourseService(db).get_reviews(course_id)
    return [{"id": r.id, "student_id": r.student_id, "rating": r.rating, "review": r.review} for r in reviews]


@router.get("/{course_id}/quizzes")
def list_quizzes_for_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    quizzes = CourseService(db).get_quizzes(course_id)
    return [{"id": q.id, "title": q.title, "total_marks": q.total_marks, "pass_marks": q.pass_marks} for q in quizzes]


@router.get("/{course_id}/enrollments", dependencies=[Depends(require_staff)])
def list_enrollments_for_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    enrollments = CourseService(db).get_enrollments(course_id)
    return [{"id": e.id, "student_id": e.student_id, "status": e.status, "progress": e.progress} for e in enrollments]

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.enrollment import get_course_enrollments
from app.schemas.enrollment import EnrollmentResponse

router = APIRouter(
    prefix="/api/v1/courses",
    tags=["Courses"]
)


@router.get(
    "/{course_id}/enrollments",
    response_model=list[EnrollmentResponse]
)
def course_enrollments(
    course_id: int,
    db: Session = Depends(get_db)
):
    return get_course_enrollments(
        db,
        course_id
    )
