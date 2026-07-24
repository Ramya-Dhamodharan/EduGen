import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.quiz import Quiz
from app.models.quiz_answer import QuizAnswer
from app.models.quiz_attempt import QuizAttempt, QuizAttemptStatus, SubmissionStatus
from app.repositories.quiz_attempt_repo import QuizAttemptRepository


class QuizAttemptService:
    def __init__(self, db: Session):
        self.db = db
        self.attempt_repo = QuizAttemptRepository(db)

    def _get(self, attempt_id: uuid.UUID) -> QuizAttempt:
        attempt = self.attempt_repo.get_by_id(attempt_id)

        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attempt {attempt_id} not found",
            )

        return attempt

    def list_all(self) -> List[QuizAttempt]:
        return self.attempt_repo.get_all()

    def get(self, attempt_id: uuid.UUID) -> QuizAttempt:
        return self._get(attempt_id)

    def list_for_student(
        self,
        student_id: uuid.UUID,
    ) -> List[QuizAttempt]:
        return self.attempt_repo.get_by_student_id(student_id)

    def list_answers(
        self,
        attempt_id: uuid.UUID,
    ) -> List[QuizAnswer]:
        self._get(attempt_id)
        return self.attempt_repo.get_answers(attempt_id)

    def list_in_progress_for_student(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID | None = None,
    ) -> List[QuizAttempt]:
        return self.attempt_repo.get_in_progress_for_student(student_id, quiz_id)

    def start(
        self,
        student_id: uuid.UUID,
        quiz_id: uuid.UUID,
    ) -> QuizAttempt:
        """Start a quiz, or transparently resume an unfinished one.

        A student is only ever in one of two states for a given quiz:
        no attempt yet, or an IN_PROGRESS attempt they can continue. If an
        IN_PROGRESS attempt already exists we return it as-is (no new row,
        no reset of previously saved answers) so that calling this again
        after a browser refresh, a dropped connection, or a fresh login
        always lands the student back where they left off. Once an attempt
        is COMPLETED it is never returned here, so a new call starts a
        brand new attempt instead of resuming a submitted one.
        """

        quiz = (
            self.db.query(Quiz)
            .filter(Quiz.id == quiz_id)
            .first()
        )

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quiz {quiz_id} does not exist",
            )

        existing = self.attempt_repo.get_in_progress_for_quiz(
            student_id,
            quiz_id,
        )

        if existing:
            return existing

        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            status=QuizAttemptStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
            created_by=student_id,
        )

        return self.attempt_repo.create(attempt)

    def update(
        self,
        attempt_id: uuid.UUID,
        status_value: str | None,
    ) -> QuizAttempt:

        attempt = self._get(attempt_id)

        if status_value:
            attempt.status = QuizAttemptStatus(status_value)

        return self.attempt_repo.update(attempt)

    def _resolve_deadline(self, quiz: Quiz, student_id: uuid.UUID) -> datetime | None:
        """The submission deadline for this student on this quiz, if any.

        deadline = student's enrollment date (in the quiz's course) +
        quiz.duration_days. Returns None if the quiz has no duration_days
        configured, or if the student has no enrollment record for the
        quiz's course (in which case timeliness can't be determined).
        """
        if not quiz.duration_days:
            return None

        enrollment = (
            self.db.query(Enrollment)
            .filter(
                Enrollment.student_id == student_id,
                Enrollment.course_id == quiz.course_id,
            )
            .first()
        )

        if not enrollment:
            return None

        return enrollment.enrolled_at + timedelta(days=quiz.duration_days)

    def submit(
        self,
        attempt_id: uuid.UUID,
    ) -> QuizAttempt:

        attempt = self._get(attempt_id)

        if attempt.status == QuizAttemptStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attempt already submitted",
            )

        answers = self.attempt_repo.get_answers(attempt_id)

        total = Decimal("0")

        for answer in answers:
            if answer.marks_obtained is not None:
                total += answer.marks_obtained

        quiz = (
            self.db.query(Quiz)
            .filter(Quiz.id == attempt.quiz_id)
            .first()
        )

        completed_at = datetime.now(timezone.utc)

        attempt.score = total
        attempt.status = QuizAttemptStatus.COMPLETED
        attempt.completed_at = completed_at

        if quiz is not None:
            deadline = self._resolve_deadline(quiz, attempt.student_id)

            if deadline is not None:
                attempt.submission_status = (
                    SubmissionStatus.ON_TIME
                    if completed_at <= deadline
                    else SubmissionStatus.DELAYED
                )

        return self.attempt_repo.update(attempt)

    def add_feedback(
        self,
        attempt_id: uuid.UUID,
        feedback: str,
        instructor_id: uuid.UUID,
    ) -> QuizAttempt:
        """Instructor feedback for a student's quiz attempt/submission."""

        attempt = self._get(attempt_id)

        if attempt.status != QuizAttemptStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback can only be given on a submitted attempt",
            )

        attempt.feedback = feedback
        attempt.feedback_by = instructor_id
        attempt.feedback_at = datetime.now(timezone.utc)

        return self.attempt_repo.update(attempt)