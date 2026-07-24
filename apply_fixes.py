"""
Apply the six outstanding fixes to this project, in place.

    python apply_fixes.py            # patch
    python apply_fixes.py --check    # report only, change nothing

Safe to re-run: every patch detects whether it is already applied.
Run from the project root (the folder containing app/).
"""

import argparse
import pathlib
import sys

CHECK_ONLY = False
results = []


def read(path):
    p = pathlib.Path(path)
    if not p.exists():
        return None, None
    raw = p.read_bytes().decode("utf-8")
    return p, raw.replace("\r\n", "\n")


def write(p, text, crlf=True):
    if CHECK_ONLY:
        return
    p.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def patch(path, name, old, new, already):
    """Replace `old` with `new`. `already` is a marker meaning it's done."""
    p, s = read(path)
    if s is None:
        results.append((name, "SKIP", f"{path} not found"))
        return
    if already in s:
        results.append((name, "OK", "already applied"))
        return
    if old not in s:
        results.append((name, "MANUAL", f"anchor not found in {path} - see notes"))
        return
    write(p, s.replace(old, new, 1))
    results.append((name, "PATCHED", path))


# ---------------------------------------------------------------- 1 & 2 -----
# Registration 500s: DEFAULT_ROLE is "student" but the row is "Student",
# and get_by_name does an exact match.



# -------------------------------------------------------------------- 3 -----
# Student updating their own profile nulls role_id / is_active.
# Assigning None marks the field as *set*, so exclude_unset still writes NULL.


# -------------------------------------------------------------------- 4 -----
# DELETE course / category 500 because child FKs get SET NULL instead of
# cascading. Module/Quiz/QuizAttempt already do this correctly.

def add_cascade(path, parent, children):
    p, s = read(path)
    if s is None:
        results.append((f"cascade {path}", "SKIP", "file not found"))
        return
    added, present = [], []
    for attr, cls in children:
        anchor = (f'    {attr}: Mapped[list["{cls}"]] = relationship(\n'
                  f'        "{cls}",\n'
                  f'        back_populates="{parent}",\n'
                  f'    )')
        anchor_no_cls = (f'    {attr}: Mapped[list["{cls}"]] = relationship(\n'
                         f'        back_populates="{parent}",\n'
                         f'    )')
        done = (f'    {attr}: Mapped[list["{cls}"]] = relationship(\n'
                f'        "{cls}",\n'
                f'        back_populates="{parent}",\n'
                f'        cascade="all, delete-orphan",\n'
                f'    )')
        done_no_cls = (f'    {attr}: Mapped[list["{cls}"]] = relationship(\n'
                       f'        back_populates="{parent}",\n'
                       f'        cascade="all, delete-orphan",\n'
                       f'    )')
        if done in s or done_no_cls in s:
            present.append(attr)
        elif anchor in s:
            s = s.replace(anchor, done, 1); added.append(attr)
        elif anchor_no_cls in s:
            s = s.replace(anchor_no_cls, done_no_cls, 1); added.append(attr)
    if added:
        write(p, s)
        results.append((f"4. cascade {pathlib.Path(path).stem}", "PATCHED", ", ".join(added)))
    elif present:
        results.append((f"4. cascade {pathlib.Path(path).stem}", "OK", "already applied"))
    else:
        results.append((f"4. cascade {pathlib.Path(path).stem}", "MANUAL",
                        "relationship block not recognised"))



# -------------------------------------------------------------------- 5 -----
# Any unique / FK violation surfaces as a 500. One handler turns every
# IntegrityError into a clean 400 - this covers the duplicate quiz answer
# regardless of which layer raises it.

def add_integrity_handler():
    p, s = read("app/main.py")
    if s is None:
        results.append(("5. IntegrityError handler", "SKIP", "app/main.py not found"))
        return
    if "IntegrityError" in s:
        results.append(("5. IntegrityError handler", "OK", "already applied"))
        return

    anchor = "# --- Routers ---"
    if anchor not in s:
        results.append(("5. IntegrityError handler", "MANUAL", "no '# --- Routers ---' marker"))
        return

    block = '''# --- Database integrity errors -> 400 instead of 500 ---
# Unique and foreign-key violations are client mistakes (duplicate answer,
# duplicate enrolment, deleting a row still referenced elsewhere), so they
# should not surface as Internal Server Error.
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    detail = "This action conflicts with existing data."
    orig = str(getattr(exc, "orig", "")) or ""
    if "uq_quiz_answers_attempt_question" in orig:
        detail = ("This question has already been answered for this attempt. "
                  "Use PUT /api/quiz-answers/{id} to change the answer.")
    elif "duplicate key" in orig.lower() or "unique" in orig.lower():
        detail = "A record with these values already exists."
    elif "not-null" in orig.lower() or "null value" in orig.lower():
        detail = ("This record is still referenced by others and cannot be "
                  "removed or changed.")
    return JSONResponse(status_code=400, content={"detail": detail})


''' + anchor

    write(p, s.replace(anchor, block, 1))
    results.append(("5. IntegrityError handler", "PATCHED", "app/main.py"))



# -------------------------------------------------------------------- 6 -----
# Best-effort pre-check in the answer service (nicer message, avoids the
# aborted transaction). Optional - fix 5 already covers the 500.

def add_duplicate_precheck():
    p, s = read("app/services/quiz_answer_service.py")
    if s is None:
        results.append(("6. duplicate-answer pre-check", "SKIP", "file not found"))
        return
    if "already been answered" in s:
        results.append(("6. duplicate-answer pre-check", "OK", "already applied"))
        return

    anchor = ('                detail=f"Attempt {attempt_id} does not exist",\n'
              '            )\n')
    if anchor not in s:
        results.append(("6. duplicate-answer pre-check", "MANUAL",
                        "attempt-check block not found; fix 5 covers this anyway"))
        return

    new = anchor + '''
        # One answer per (attempt, question) - matches the DB constraint
        # uq_quiz_answers_attempt_question.
        existing = (
            self.db.query(QuizAnswer)
            .filter(
                QuizAnswer.attempt_id == attempt_id,
                QuizAnswer.question_id == question_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This question has already been answered for this attempt. "
                       "Use PUT /api/quiz-answers/{id} to change the answer.",
            )
'''
    if "QuizAnswer" not in s.split("class ")[0]:
        results.append(("6. duplicate-answer pre-check", "MANUAL",
                        "QuizAnswer not imported; fix 5 covers this anyway"))
        return
    write(p, s.replace(anchor, new, 1))
    results.append(("6. duplicate-answer pre-check", "PATCHED",
                    "app/services/quiz_answer_service.py"))




def run_all():
    patch(
        "app/services/auth_service.py",
        "1. DEFAULT_ROLE casing",
        'DEFAULT_ROLE = "student"',
        'DEFAULT_ROLE = "Student"',
        already='DEFAULT_ROLE = "Student"',
    )

    patch(
        "app/repositories/role_repo.py",
        "2. role lookup case-insensitive",
        "return self.db.query(Role).filter(Role.name == name).first()",
        "# Case-insensitive so \"student\" also matches a \"Student\" row.\n"
        "        return self.db.query(Role).filter(Role.name.ilike(name)).first()",
        already="Role.name.ilike(name)",
    )

    patch(
        "app/routes/user_routes.py",
        "3. profile update wipes role_id",
        "        payload.role_id = None\n        payload.is_active = None\n",
        "        # Drop these from the \"set\" fields entirely. Assigning None marks\n"
        "        # them as explicitly set, so model_dump(exclude_unset=True) would\n"
        "        # write NULL into two NOT NULL columns.\n"
        "        payload.__pydantic_fields_set__.discard(\"role_id\")\n"
        "        payload.__pydantic_fields_set__.discard(\"is_active\")\n",
        already="__pydantic_fields_set__.discard",
    )

    add_cascade("app/models/course.py", "course", [
        ("modules", "Module"), ("enrollments", "Enrollment"), ("quizzes", "Quiz"),
        ("reviews", "CourseReview"), ("certificates", "Certificate"), ("payments", "Payment"),
    ])

    add_cascade("app/models/category.py", "category", [("courses", "Course")])

    add_integrity_handler()

    add_duplicate_precheck()


# ----------------------------------------------------------------- report ---

def main():
    global CHECK_ONLY
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only")
    args = ap.parse_args()
    CHECK_ONLY = args.check

    run_all()

    width = max(len(n) for n, _, _ in results)
    print("\nFix status")
    print("-" * (width + 26))
    for name, status, note in results:
        print(f"  {name:<{width}}  {status:<8} {note}")

    manual = [r for r in results if r[1] in ("MANUAL", "SKIP")]
    patched = [r for r in results if r[1] == "PATCHED"]

    print()
    if patched:
        print(f"{len(patched)} fix(es) applied.")
    if manual:
        print(f"{len(manual)} need manual attention (see notes above).")

    print("\nNext steps:")
    print("  1. uv run python dummy_data.py --reset   # clears the old .test users")
    print("  2. restart uvicorn")
    print("  3. python test_api.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())