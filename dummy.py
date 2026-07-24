"""
Populate the EduGen database with a realistic dummy dataset.

Run from the project root (where app/ lives):

    uv run python dummy_data.py            # insert
    uv run python dummy_data.py --reset    # delete previous dummy rows, then insert
    uv run python dummy_data.py --summary  # just show what is in the DB

Creates:
    3  roles              12 users (1 admin, 3 instructors, 8 students)
    4  categories          6 courses          14 modules        45 lessons
    6  quizzes            20 questions        18 enrollments    18 payments
    18 quiz attempts      62 graded answers    6 reviews         6 certificates

Idempotent: re-running will not duplicate rows (matched on natural keys such
as email, course title, certificate number).
"""

import argparse
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.db.database import SessionLocal
import app.models  # noqa: F401  - registers every mapper
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.course import Course, CourseLevel
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.quiz_attempt import QuizAttempt, QuizAttemptStatus
from app.models.quiz_answer import QuizAnswer
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.certificate import Certificate
from app.models.course_review import CourseReview

random.seed(42)  # deterministic output
NOW = datetime.now(timezone.utc)


def ago(days: int) -> datetime:
    return NOW - timedelta(days=days)


# ---------------------------------------------------------------- content ---

ROLES = ["Admin", "Instructor", "Student"]

USERS = [
    # username,      email,                        password,           role
    ("admin",        "admin@edugen.com",          "Admin@12345",      "Admin"),
    ("rajesh",       "rajesh@edugen.com",         "Instructor@12345", "Instructor"),
    ("meena",        "meena@edugen.com",          "Instructor@12345", "Instructor"),
    ("instructor",   "instructor@edugen.com",     "Instructor@12345", "Instructor"),
    ("student",      "student@edugen.com",        "Student@12345",    "Student"),
    ("arjun",        "arjun@edugen.com",          "Student@12345",    "Student"),
    ("priya",        "priya@edugen.com",          "Student@12345",    "Student"),
    ("karthik",      "karthik@edugen.com",        "Student@12345",    "Student"),
    ("divya",        "divya@edugen.com",          "Student@12345",    "Student"),
    ("sanjay",       "sanjay@edugen.com",         "Student@12345",    "Student"),
    ("nisha",        "nisha@edugen.com",          "Student@12345",    "Student"),
    ("vikram",       "vikram@edugen.com",         "Student@12345",    "Student"),
]

CATEGORIES = ["Web Development", "Data Science", "Cloud & DevOps", "Mobile Development"]

# title, category, level, price, language, duration, description
COURSES = [
    ("FastAPI from Scratch", "Web Development", CourseLevel.BEGINNER, "1499.00",
     "English", "8 weeks",
     "Build production-ready REST APIs with FastAPI, SQLAlchemy and JWT authentication."),
    ("Advanced PostgreSQL", "Data Science", CourseLevel.ADVANCED, "2999.00",
     "English", "6 weeks",
     "Indexing strategies, query planning, partitioning and performance tuning."),
    ("React for Beginners", "Web Development", CourseLevel.BEGINNER, "999.00",
     "English", "5 weeks",
     "Components, hooks, state management and routing in modern React."),
    ("Machine Learning Foundations", "Data Science", CourseLevel.INTERMEDIATE, "3499.00",
     "English", "10 weeks",
     "Regression, classification, model evaluation and feature engineering."),
    ("Docker & Kubernetes in Practice", "Cloud & DevOps", CourseLevel.INTERMEDIATE, "2499.00",
     "English", "7 weeks",
     "Containerise applications and orchestrate them on a real cluster."),
    ("Flutter Mobile Apps", "Mobile Development", CourseLevel.BEGINNER, "1799.00",
     "Tamil", "6 weeks",
     "Build cross-platform Android and iOS apps from a single codebase."),
]

# course title -> [(module title, description, [lesson titles])]
STRUCTURE = {
    "FastAPI from Scratch": [
        ("Getting Started", "Environment setup and your first endpoint.",
         ["Installing Python and uv", "Project layout", "Your first route", "Interactive docs"]),
        ("Data & Validation", "Pydantic models and request validation.",
         ["Pydantic basics", "Request bodies", "Response models", "Custom validators"]),
        ("Database & Auth", "SQLAlchemy models and JWT security.",
         ["SQLAlchemy setup", "Repositories and services", "Password hashing", "JWT tokens"]),
    ],
    "Advanced PostgreSQL": [
        ("Query Performance", "Reading and improving query plans.",
         ["EXPLAIN ANALYZE", "Index types", "Composite indexes"]),
        ("Scaling Data", "Handling large tables.",
         ["Table partitioning", "Vacuum and bloat", "Connection pooling"]),
    ],
    "React for Beginners": [
        ("React Basics", "Components and JSX.",
         ["What is JSX", "Props and state", "Event handling"]),
        ("Hooks", "Modern function components.",
         ["useState", "useEffect", "Custom hooks"]),
        ("Routing", "Multi-page apps.",
         ["React Router setup", "Nested routes"]),
    ],
    "Machine Learning Foundations": [
        ("Supervised Learning", "Learning from labelled data.",
         ["Linear regression", "Logistic regression", "Decision trees"]),
        ("Model Evaluation", "Knowing if the model is any good.",
         ["Train/test split", "Cross validation", "Confusion matrix", "ROC and AUC"]),
    ],
    "Docker & Kubernetes in Practice": [
        ("Containers", "Packaging applications.",
         ["Images and layers", "Writing a Dockerfile", "Docker Compose"]),
        ("Kubernetes", "Running containers at scale.",
         ["Pods and deployments", "Services and ingress", "ConfigMaps and secrets"]),
    ],
    "Flutter Mobile Apps": [
        ("Dart & Widgets", "Language and UI basics.",
         ["Dart essentials", "Stateless widgets", "Stateful widgets"]),
        ("Building an App", "From screens to store.",
         ["Navigation", "Calling an API", "Publishing"]),
    ],
}

# course title -> (quiz title, pass_marks, [(question, a, b, c, d, correct, marks)])
QUIZZES = {
    "FastAPI from Scratch": ("Module 1 Check", 10, [
        ("Which command starts the FastAPI development server?",
         "python serve.py", "uvicorn app.main:app --reload", "fastapi start", "flask run", "B", 5),
        ("Which HTTP status code means Created?", "200", "204", "201", "400", "C", 5),
        ("What does Pydantic primarily provide?",
         "Database migrations", "Data validation", "Template rendering", "Task queues", "B", 5),
        ("Which decorator defines a POST route?",
         "@app.post", "@app.write", "@app.create", "@app.send", "A", 5),
    ]),
    "Advanced PostgreSQL": ("Indexing Quiz", 8, [
        ("Which command shows a query execution plan?",
         "DESCRIBE", "EXPLAIN", "SHOW PLAN", "ANALYSE", "B", 5),
        ("Which index type suits equality lookups best?",
         "GIN", "GiST", "B-tree", "BRIN", "C", 5),
        ("What does VACUUM reclaim?",
         "Dead tuples", "Indexes", "Sequences", "Locks", "A", 5),
    ]),
    "React for Beginners": ("Hooks Quiz", 6, [
        ("Which hook stores local component state?",
         "useEffect", "useState", "useMemo", "useRef", "B", 5),
        ("When does useEffect run by default?",
         "Before render", "After every render", "Only once ever", "Never", "B", 5),
        ("What must a custom hook name start with?",
         "hook", "use", "with", "on", "B", 5),
    ]),
    "Machine Learning Foundations": ("Evaluation Quiz", 8, [
        ("What does a confusion matrix summarise?",
         "Feature importance", "Prediction counts by class", "Learning rate", "Data drift", "B", 5),
        ("Which metric balances precision and recall?",
         "Accuracy", "F1 score", "MSE", "R squared", "B", 5),
        ("Why split data into train and test sets?",
         "Speed", "To measure generalisation", "To reduce size", "To clean data", "B", 5),
        ("What does overfitting mean?",
         "Model too simple", "Model memorises training data", "Too little data", "Bad labels", "B", 5),
    ]),
    "Docker & Kubernetes in Practice": ("Containers Quiz", 6, [
        ("Which file defines a container image build?",
         "Dockerfile", "compose.yml", "image.cfg", "build.json", "A", 5),
        ("What is the smallest deployable unit in Kubernetes?",
         "Container", "Pod", "Node", "Service", "B", 5),
        ("Which object exposes pods on a stable address?",
         "Ingress", "Service", "ConfigMap", "Job", "B", 5),
    ]),
    "Flutter Mobile Apps": ("Widgets Quiz", 6, [
        ("Which language does Flutter use?",
         "Kotlin", "Swift", "Dart", "Java", "C", 5),
        ("Which widget type holds mutable state?",
         "StatelessWidget", "StatefulWidget", "InheritedWidget", "Container", "B", 5),
        ("What rebuilds the UI after state changes?",
         "reload()", "setState()", "refresh()", "update()", "B", 5),
    ]),
}


# ------------------------------------------------------------------ helpers --

def get_or_create(db, model, defaults=None, **filters):
    """Return (obj, created)."""
    obj = db.query(model).filter_by(**filters).first()
    if obj:
        return obj, False
    obj = model(**filters, **(defaults or {}))
    db.add(obj)
    db.flush()
    return obj, True


def reset(db):
    """Delete rows in FK-safe order."""
    for model in (QuizAnswer, QuizAttempt, QuizQuestion, Quiz, Certificate,
                  CourseReview, Payment, Enrollment, Lesson, Module, Course,
                  Category):
        n = db.query(model).delete()
        print(f"  deleted {n:4} {model.__name__}")
    emails = [u[1] for u in USERS]
    doomed = [u.id for u in db.query(User).filter(User.email.in_(emails)).all()]
    if doomed:
        # Roles survive the reset but carry created_by/updated_by FKs to users,
        # so clear those references before the users disappear.
        db.query(Role).filter(Role.created_by.in_(doomed)).update(
            {Role.created_by: None}, synchronize_session=False)
        db.query(Role).filter(Role.updated_by.in_(doomed)).update(
            {Role.updated_by: None}, synchronize_session=False)
    n = db.query(User).filter(User.email.in_(emails)).delete(synchronize_session=False)
    print(f"  deleted {n:4} User")
    db.commit()


def summary(db):
    print("\nCurrent database contents")
    print("-" * 34)
    for model in (Role, User, Category, Course, Module, Lesson, Quiz,
                  QuizQuestion, QuizAttempt, QuizAnswer, Enrollment,
                  Payment, Certificate, CourseReview):
        print(f"  {model.__name__:16} {db.query(model).count():5}")


# --------------------------------------------------------------------- main --

def build(db):
    counts = {}

    # ---- roles ----
    roles = {}
    for name in ROLES:
        role, _ = get_or_create(db, Role, name=name)
        roles[name] = role
    counts["roles"] = len(roles)

    # ---- users ----
    users = {}
    made_users = 0
    for username, email, password, role_name in USERS:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                username=username, email=email,
                password_hash=hash_password(password),
                role_id=roles[role_name].id, is_active=True,
            )
            db.add(user)
            db.flush()
            user.created_by = user.id
            made_users += 1
        users[email] = user
    db.flush()
    counts["users"] = made_users

    admin = users["admin@edugen.com"]
    instructors = [users[e] for e in
                   ("rajesh@edugen.com", "meena@edugen.com", "instructor@edugen.com")]
    students = [users[e] for e in
                ("student@edugen.com", "arjun@edugen.com", "priya@edugen.com",
                 "karthik@edugen.com", "divya@edugen.com", "sanjay@edugen.com",
                 "nisha@edugen.com", "vikram@edugen.com")]

    # ---- categories ----
    cats = {}
    for i, name in enumerate(CATEGORIES):
        cat, _ = get_or_create(
            db, Category, name=name,
            defaults={"is_active": True, "created_by": admin.id, "created_at": ago(120 - i)},
        )
        cats[name] = cat
    counts["categories"] = len(cats)

    # ---- courses ----
    courses = {}
    for i, (title, cat_name, level, price, lang, dur, desc) in enumerate(COURSES):
        owner = instructors[i % len(instructors)]
        course, _ = get_or_create(
            db, Course, title=title,
            defaults={
                "description": desc, "language": lang, "duration": dur,
                "level": level, "price": Decimal(price),
                "category_id": cats[cat_name].id, "is_active": True,
                "created_by": owner.id, "created_at": ago(100 - i * 5),
            },
        )
        courses[title] = course
    counts["courses"] = len(courses)

    # ---- modules + lessons ----
    n_mod = n_les = 0
    for course_title, mods in STRUCTURE.items():
        course = courses[course_title]
        owner_id = course.created_by
        for m_i, (m_title, m_desc, lessons) in enumerate(mods):
            module, created = get_or_create(
                db, Module, title=m_title, course_id=course.id,
                defaults={"description": m_desc, "is_active": True,
                          "created_by": owner_id, "created_at": ago(95 - m_i)},
            )
            n_mod += created
            for l_i, l_title in enumerate(lessons):
                _, c = get_or_create(
                    db, Lesson, title=l_title, module_id=module.id,
                    defaults={
                        "description": f"{l_title} - part of {m_title}.",
                        "video_url": f"https://videos.edugen.com/"
                                     f"{course_title.lower().replace(' ', '-')}/"
                                     f"{l_title.lower().replace(' ', '-')}.mp4",
                        "is_active": True, "created_by": owner_id,
                        "created_at": ago(94 - l_i),
                    },
                )
                n_les += c
    counts["modules"], counts["lessons"] = n_mod, n_les

    # ---- quizzes + questions ----
    quiz_by_course = {}
    n_q = n_qq = 0
    for course_title, (q_title, pass_marks, questions) in QUIZZES.items():
        course = courses[course_title]
        first_lesson = (
            db.query(Lesson)
            .join(Module, Lesson.module_id == Module.id)
            .filter(Module.course_id == course.id)
            .first()
        )
        total = sum(q[6] for q in questions)
        quiz, created = get_or_create(
            db, Quiz, title=q_title, course_id=course.id,
            defaults={
                "description": f"Assessment for {course_title}.",
                "lesson_id": first_lesson.id if first_lesson else None,
                "total_marks": total, "pass_marks": pass_marks, "duration": 15,
                "is_active": True, "created_by": course.created_by,
                "created_at": ago(80),
            },
        )
        n_q += created
        quiz_by_course[course_title] = quiz
        for text, a, b, c, d, correct, marks in questions:
            _, cq = get_or_create(
                db, QuizQuestion, question=text, quiz_id=quiz.id,
                defaults={"option_a": a, "option_b": b, "option_c": c, "option_d": d,
                          "correct_option": correct, "marks": marks,
                          "created_by": course.created_by, "created_at": ago(80)},
            )
            n_qq += cq
    counts["quizzes"], counts["questions"] = n_q, n_qq

    # ---- enrollments, payments, attempts, reviews, certificates ----
    n_en = n_pay = n_att = n_ans = n_rev = n_cert = 0
    course_list = list(courses.values())
    cert_seq = 1

    for s_i, student in enumerate(students):
        # each student takes 2-3 courses
        picked = random.sample(course_list, k=random.choice([2, 3]))
        for c_i, course in enumerate(picked):
            completed = (s_i + c_i) % 3 == 0
            enrolled_on = ago(70 - s_i * 3 - c_i)

            enrollment = (
                db.query(Enrollment)
                .filter(Enrollment.student_id == student.id,
                        Enrollment.course_id == course.id)
                .first()
            )
            if not enrollment:
                enrollment = Enrollment(
                    student_id=student.id, course_id=course.id,
                    status=EnrollmentStatus.COMPLETED if completed else EnrollmentStatus.ACTIVE,
                    enrolled_at=enrolled_on,
                    started_at=enrolled_on + timedelta(days=1),
                    completed_at=enrolled_on + timedelta(days=30) if completed else None,
                )
                db.add(enrollment)
                n_en += 1

            # payment
            existing_pay = (
                db.query(Payment)
                .filter(Payment.student_id == student.id, Payment.course_id == course.id)
                .first()
            )
            if not existing_pay:
                status = (PaymentStatus.SUCCESS if completed or c_i == 0
                          else random.choice([PaymentStatus.SUCCESS,
                                              PaymentStatus.PENDING,
                                              PaymentStatus.FAILED]))
                txn = f"TXN-{uuid.uuid4().hex[:12].upper()}"
                db.add(Payment(
                    student_id=student.id, course_id=course.id,
                    transaction_id=txn, amount=course.price or Decimal("0.00"),
                    currency="INR",
                    payment_method=random.choice(list(PaymentMethod)),
                    payment_gateway=random.choice(["razorpay", "stripe", "payu"]),
                    payment_status=status,
                    payment_date=enrolled_on if status == PaymentStatus.SUCCESS else None,
                    receipt_url=(f"https://receipts.edugen.com/{txn}.pdf"
                                 if status == PaymentStatus.SUCCESS else None),
                    created_by=student.id, created_at=enrolled_on,
                ))
                n_pay += 1

            # quiz attempt with graded answers
            quiz = quiz_by_course.get(course.title)
            if quiz:
                has_attempt = (
                    db.query(QuizAttempt)
                    .filter(QuizAttempt.student_id == student.id,
                            QuizAttempt.quiz_id == quiz.id)
                    .first()
                )
                if not has_attempt:
                    questions = (db.query(QuizQuestion)
                                 .filter(QuizQuestion.quiz_id == quiz.id).all())
                    attempt = QuizAttempt(
                        quiz_id=quiz.id, student_id=student.id,
                        status=QuizAttemptStatus.COMPLETED if completed
                        else QuizAttemptStatus.IN_PROGRESS,
                        started_at=enrolled_on + timedelta(days=5),
                        created_by=student.id,
                    )
                    db.add(attempt)
                    db.flush()
                    n_att += 1

                    score = Decimal("0")
                    for q in questions:
                        # completed students answer most questions right
                        right = random.random() < (0.85 if completed else 0.5)
                        chosen = q.correct_option if right else random.choice(
                            [o for o in ("A", "B", "C", "D") if o != q.correct_option]
                        )
                        marks = Decimal(str(q.marks)) if right else Decimal("0")
                        score += marks
                        db.add(QuizAnswer(
                            attempt_id=attempt.id, question_id=q.id,
                            selected_option=chosen, is_correct=right,
                            marks_obtained=marks, created_by=student.id,
                        ))
                        n_ans += 1

                    if completed:
                        attempt.score = score
                        attempt.completed_at = enrolled_on + timedelta(days=5, hours=1)

            # review (only for completed courses)
            if completed:
                has_review = (
                    db.query(CourseReview)
                    .filter(CourseReview.student_id == student.id,
                            CourseReview.course_id == course.id)
                    .first()
                )
                if not has_review:
                    rating = random.choice([3, 4, 4, 5, 5, 5])
                    texts = {
                        5: "Excellent course. Clear explanations and great hands-on examples.",
                        4: "Very good content, though a few sections could go deeper.",
                        3: "Useful material but the pacing felt uneven in places.",
                    }
                    db.add(CourseReview(
                        course_id=course.id, student_id=student.id,
                        rating=rating, review=texts[rating],
                        created_by=student.id,
                        created_at=enrolled_on + timedelta(days=32),
                    ))
                    n_rev += 1

                # certificate
                has_cert = (
                    db.query(Certificate)
                    .filter(Certificate.student_id == student.id,
                            Certificate.course_id == course.id)
                    .first()
                )
                if not has_cert:
                    number = f"EDU-2026-{cert_seq:04d}"
                    while db.query(Certificate).filter(
                            Certificate.certificate_number == number).first():
                        cert_seq += 1
                        number = f"EDU-2026-{cert_seq:04d}"
                    db.add(Certificate(
                        student_id=student.id, course_id=course.id,
                        certificate_number=number,
                        certificate_url=f"https://certs.edugen.com/{number}.pdf",
                        issued_at=enrolled_on + timedelta(days=31),
                    ))
                    cert_seq += 1
                    n_cert += 1

    counts.update({"enrollments": n_en, "payments": n_pay, "attempts": n_att,
                   "answers": n_ans, "reviews": n_rev, "certificates": n_cert})
    db.commit()
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true",
                    help="delete existing dummy rows before inserting")
    ap.add_argument("--summary", action="store_true",
                    help="only print current row counts")
    args = ap.parse_args()

    db = SessionLocal()
    try:
        if args.summary:
            summary(db)
            return 0

        if args.reset:
            print("Resetting dummy data...")
            reset(db)

        print("Inserting dummy data...")
        counts = build(db)

        print("\nInserted (new rows only)")
        print("-" * 34)
        for k, v in counts.items():
            print(f"  {k:16} {v:5}")
        summary(db)

        print("\nSample logins (all seeded users)")
        print("-" * 34)
        print("  Admin        admin@edugen.com        Admin@12345")
        print("  Instructor   rajesh@edugen.com       Instructor@12345")
        print("  Student      arjun@edugen.com        Student@12345")
        print("\nDone.")
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())