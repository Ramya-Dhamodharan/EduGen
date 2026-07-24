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
    QuizAttemptFeedback,
)
from app.schemas.quiz_answer_schemas import QuizAnswerOut, QuizAnswerNestedCreate
from app.services.quiz_attempt_service import QuizAttemptService

router = APIRouter()


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


# ---- Student: look up their own in-progress attempt(s) without starting one ----
# Must be declared before /{attempt_id} so "in-progress" isn't parsed as a UUID.
@router.get("/in-progress", response_model=List[QuizAttemptOut])
def list_in_progress_attempts(
    quiz_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Attempts the current student can resume.

    Pass ?quiz_id=... to check a single quiz (0 or 1 results), or omit it to
    get every quiz the student left mid-attempt - e.g. for a "continue where
    you left off" section after logging back in.
    """
    return QuizAttemptService(db).list_in_progress_for_student(current_user.id, quiz_id)


# ---- Owner or staff: view one ----
@router.get("/{attempt_id}", response_model=QuizAttemptOut)
def get_attempt(attempt_id: uuid.UUID, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    a = QuizAttemptService(db).get(attempt_id)
    _ensure_owner_or_staff(current_user, a.student_id)
    return a


# ---- Student starts their own attempt (or resumes an unfinished one) ----
# Safe to call every time a student opens the quiz - if they already have an
# IN_PROGRESS attempt for this quiz it's returned unchanged instead of a new
# one being created, which is what makes closing the tab, refreshing, losing
# connection, or logging in again all resumable.
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


# ---- Staff: give instructor feedback on a submitted attempt ----
@router.patch("/{attempt_id}/feedback", response_model=QuizAttemptOut,
              dependencies=[Depends(require_staff)])
def give_attempt_feedback(attempt_id: uuid.UUID, payload: QuizAttemptFeedback,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    return QuizAttemptService(db).add_feedback(attempt_id, payload.feedback, current_user.id)


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

