<<<<<<< HEAD
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user, require_staff
from app.schemas.quiz_attempt_schemas import (
    QuizAttemptCreate,
    QuizAttemptUpdate,
    QuizAttemptOut,
)
from app.schemas.quiz_answer_schemas import QuizAnswerOut, QuizAnswerNestedCreate
from app.services.quiz_attempt_service import QuizAttemptService
=======
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptUpdate,
    QuizAttemptSubmit,
    QuizAttemptResponse,
)

from app.crud.quiz_attempt import (
    start_quiz_attempt,
    get_quiz_attempt_by_id,
    update_quiz_attempt,
    submit_quiz_attempt,
    delete_quiz_attempt,
    get_student_quiz_attempts,
    get_quiz_attempts,
)

>>>>>>> origin/dev

router = APIRouter()


<<<<<<< HEAD
def _is_staff(user: User) -> bool:
    return user.role.name.lower() in ("admin", "instructor")


def _ensure_owner_or_staff(user: User, owner_id: uuid.UUID) -> None:
    if _is_staff(user) or user.id == owner_id:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to access this resource")


# ---- Staff: list all attempts ----
@router.get("", response_model=List[QuizAttemptOut], dependencies=[Depends(require_staff)])
def list_attempts(db: Session = Depends(get_db)):
    return QuizAttemptService(db).list_all()


# ---- Owner or staff: view one ----
@router.get("/{attempt_id}", response_model=QuizAttemptOut)
def get_attempt(attempt_id: uuid.UUID, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    a = QuizAttemptService(db).get(attempt_id)
    _ensure_owner_or_staff(current_user, a.student_id)
    return a


# ---- Student starts their own attempt ----
@router.post("", response_model=QuizAttemptOut, status_code=status.HTTP_201_CREATED)
def start_attempt(payload: QuizAttemptCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return QuizAttemptService(db).start(current_user.id, payload.quiz_id)


# ---- Owner or staff: update ----
@router.put("/{attempt_id}", response_model=QuizAttemptOut)
def update_attempt(attempt_id: uuid.UUID, payload: QuizAttemptUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    a = QuizAttemptService(db).get(attempt_id)
    _ensure_owner_or_staff(current_user, a.student_id)
    return QuizAttemptService(db).update(attempt_id, payload.status)


# ---- Owner or staff: submit & score ----
@router.patch("/{attempt_id}/submit", response_model=QuizAttemptOut)
def submit_attempt(attempt_id: uuid.UUID, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    a = QuizAttemptService(db).get(attempt_id)
    _ensure_owner_or_staff(current_user, a.student_id)
    return QuizAttemptService(db).submit(attempt_id)


# ---- Owner or staff: list answers for an attempt ----
@router.get("/{attempt_id}/answers", response_model=List[QuizAnswerOut])
def list_attempt_answers(attempt_id: uuid.UUID, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    a = QuizAttemptService(db).get(attempt_id)
    _ensure_owner_or_staff(current_user, a.student_id)
    return QuizAttemptService(db).list_answers(attempt_id)


# ---- Nested: submit an answer under an attempt (owner or staff) ----
@router.post("/{attempt_id}/answers", response_model=QuizAnswerOut, status_code=status.HTTP_201_CREATED)
def submit_answer_under_attempt(
    attempt_id: uuid.UUID,
    payload: QuizAnswerNestedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.quiz_answer_service import QuizAnswerService
    a = QuizAttemptService(db).get(attempt_id)
    _ensure_owner_or_staff(current_user, a.student_id)
    return QuizAnswerService(db).submit(attempt_id, payload.question_id,
                                        payload.selected_option, current_user.id)

=======
# ==================================================
# 1. START QUIZ ATTEMPT
#
# POST /api/quiz-attempts/start
#
# Description:
# Start a new quiz attempt
# ==================================================

@router.post(
    "/start",
    response_model=QuizAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_attempt(
    attempt_data: QuizAttemptCreate,
    db: Session = Depends(get_db),
):

    return start_quiz_attempt(
        db=db,
        attempt_data=attempt_data,
    )


# ==================================================
# 2. GET QUIZ ATTEMPT BY ID
#
# GET /api/quiz-attempts/{attempt_id}
#
# Description:
# Get a quiz attempt by ID
# ==================================================

@router.get(
    "/{attempt_id}",
    response_model=QuizAttemptResponse,
)
def get_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db),
):

    return get_quiz_attempt_by_id(
        db=db,
        attempt_id=attempt_id,
    )


# ==================================================
# 3. UPDATE QUIZ ATTEMPT
#
# PUT /api/quiz-attempts/{attempt_id}
#
# Description:
# Update a quiz attempt
# ==================================================

@router.put(
    "/{attempt_id}",
    response_model=QuizAttemptResponse,
)
def update_attempt(
    attempt_id: UUID,
    attempt_data: QuizAttemptUpdate,
    db: Session = Depends(get_db),
):

    return update_quiz_attempt(
        db=db,
        attempt_id=attempt_id,
        attempt_data=attempt_data,
    )


# ==================================================
# 4. SUBMIT QUIZ ATTEMPT
#
# POST /api/quiz-attempts/{attempt_id}/submit
#
# Description:
# Submit and score a quiz attempt
# ==================================================

@router.post(
    "/{attempt_id}/submit",
    response_model=QuizAttemptResponse,
)
def submit_attempt(
    attempt_id: UUID,
    submit_data: QuizAttemptSubmit,
    db: Session = Depends(get_db),
):

    return submit_quiz_attempt(
        db=db,
        attempt_id=attempt_id,
        submit_data=submit_data,
    )


# ==================================================
# 5. DELETE QUIZ ATTEMPT
#
# DELETE /api/quiz-attempts/{attempt_id}
#
# Description:
# Delete a quiz attempt
# ==================================================

@router.delete(
    "/{attempt_id}",
)
def delete_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db),
):

    return delete_quiz_attempt(
        db=db,
        attempt_id=attempt_id,
    )


# ==================================================
# 6. GET QUIZ ATTEMPTS FOR STUDENT
#
# GET /api/users/{student_id}/quiz-attempts
#
# Description:
# List quiz attempts for a student
# ==================================================

@router.get(
    "/student/{student_id}",
    response_model=list[QuizAttemptResponse],
)
def get_student_attempts(
    student_id: UUID,
    db: Session = Depends(get_db),
):

    return get_student_quiz_attempts(
        db=db,
        student_id=student_id,
    )


# ==================================================
# 7. GET QUIZ ATTEMPTS
#
# GET /api/quizzes/{quiz_id}/attempts
#
# Description:
# List all attempts for a quiz
# ==================================================

@router.get(
    "/quiz/{quiz_id}",
    response_model=list[QuizAttemptResponse],
)
def get_attempts_for_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
):

    return get_quiz_attempts(
        db=db,
        quiz_id=quiz_id,
    )
>>>>>>> origin/dev
