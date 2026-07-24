"""
End-to-end smoke test for the EduGen API.

Prerequisites
-------------
1. Server running:      uv run uvicorn app.main:app --reload
2. Database seeded:     uv run python seed.py

Run
---
    python test_api.py
    python test_api.py --url http://127.0.0.1:8000

Uses only the Python standard library - nothing to install.
Exits with code 0 if every check passes, 1 otherwise.
"""

import argparse
import http.cookiejar
import json
import sys
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000"

ADMIN = ("admin@edugen.com", "Admin@12345")
INSTRUCTOR = ("instructor@edugen.com", "Instructor@12345")
STUDENT = ("student@edugen.com", "Student@12345")

PASSED, FAILED = [], []
ctx = {}  # shared ids between steps


# ----------------------------------------------------------------------------
# HTTP helper
# ----------------------------------------------------------------------------

_cookie_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_cookie_jar))


def call(method, path, body=None, token=None):
    """Return (status_code, parsed_body_or_text)."""
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with _opener.open(req, timeout=20) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return e.code, raw
    except urllib.error.URLError as e:
        print(f"\nCannot reach {url}: {e.reason}")
        print("Is the server running?  uv run uvicorn app.main:app --reload")
        sys.exit(1)


def check(label, method, path, expect, body=None, token=None, save=None):
    """Run a request and record pass/fail. `expect` is an int or tuple of ints."""
    status, resp = call(method, path, body, token)
    ok = status in (expect if isinstance(expect, tuple) else (expect,))
    if ok:
        PASSED.append(label)
        print(f"  PASS  {status}  {method:6} {path}")
        if save and isinstance(resp, dict) and "id" in resp:
            ctx[save] = resp["id"]
    else:
        detail = resp.get("detail") if isinstance(resp, dict) else resp
        FAILED.append((label, f"expected {expect}, got {status}: {detail}"))
        print(f"  FAIL  {status}  {method:6} {path}   (expected {expect}) {detail}")
    return resp


def login(creds):
    status, resp = call("POST", "/api/auth/login", {"email": creds[0], "password": creds[1]})
    if status != 200 or not isinstance(resp, dict):
        print(f"\nLogin failed for {creds[0]}: {status} {resp}")
        print("Did you run:  uv run python seed.py  ?")
        sys.exit(1)
    return resp["access_token"]


def section(title):
    print(f"\n--- {title} ---")


# ----------------------------------------------------------------------------
# Test phases
# ----------------------------------------------------------------------------

def phase_auth():
    section("Auth")
    rnd = uuid.uuid4().hex[:8]
    check("register", "POST", "/api/auth/register", (201, 200),
          {"username": f"tester{rnd}", "email": f"tester{rnd}@edugen.com",
           "password": "Tester@12345"})
    check("register duplicate email rejected", "POST", "/api/auth/register", 400,
          {"username": "dup", "email": "admin@edugen.com", "password": "Dup@123456"})
    check("login wrong password rejected", "POST", "/api/auth/login", 401,
          {"email": ADMIN[0], "password": "totally-wrong"})

    ctx["admin_token"] = login(ADMIN)
    ctx["instructor_token"] = login(INSTRUCTOR)
    ctx["student_token"] = login(STUDENT)
    print("  PASS  200  login as admin / instructor / student")
    PASSED.extend(["login admin", "login instructor", "login student"])

    me = check("GET /me", "GET", "/api/auth/me", 200, token=ctx["student_token"])
    if isinstance(me, dict):
        ctx["student_id"] = me.get("id")
    admin_me = call("GET", "/api/auth/me", token=ctx["admin_token"])[1]
    if isinstance(admin_me, dict):
        ctx["admin_id"] = admin_me.get("id")

    check("/me without token", "GET", "/api/auth/me", 401)
    check("refresh-token", "POST", "/api/auth/refresh-token", 200)
    check("forgot-password", "POST", "/api/auth/forgot-password", 200, {"email": STUDENT[0]})
    check("reset-password bad OTP", "POST", "/api/auth/reset-password", 400,
          {"email": STUDENT[0], "otp": "000000", "new_password": "Whatever@123"})
    check("logout", "POST", "/api/auth/logout", 200)


def phase_roles():
    section("Roles (admin only)")
    t = ctx["admin_token"]
    check("list roles", "GET", "/api/roles", 200, token=t)
    r = check("create role", "POST", "/api/roles", (201, 200),
              {"name": f"TempRole{uuid.uuid4().hex[:6]}"}, token=t, save="temp_role_id")
    if "temp_role_id" in ctx:
        rid = ctx["temp_role_id"]
        check("get role", "GET", f"/api/roles/{rid}", 200, token=t)
        check("update role", "PUT", f"/api/roles/{rid}", 200,
              {"name": f"TempRole{uuid.uuid4().hex[:6]}"}, token=t)
        check("delete role", "DELETE", f"/api/roles/{rid}", (204, 200), token=t)


def phase_users():
    section("Users")
    a, s = ctx["admin_token"], ctx["student_token"]
    check("list users", "GET", "/api/users", 200, token=a)
    if ctx.get("student_id"):
        check("get own profile as student", "GET", f"/api/users/{ctx['student_id']}", 200, token=s)
        check("update own profile as student", "PUT", f"/api/users/{ctx['student_id']}", 200,
              {"username": "student"}, token=s)
    if ctx.get("admin_id"):
        check("student reading admin profile blocked", "GET",
              f"/api/users/{ctx['admin_id']}", 403, token=s)

    rnd = uuid.uuid4().hex[:8]
    u = check("admin creates user", "POST", "/api/users", (201, 200),
              {"username": f"made{rnd}", "email": f"made{rnd}@edugen.com",
               "password": "Made@123456", "role_id": 3}, token=a, save="made_user_id")
    if "made_user_id" in ctx:
        uid = ctx["made_user_id"]
        check("deactivate user", "PATCH", f"/api/users/{uid}/status", 200,
              {"is_active": False}, token=a)
        check("assign role", "PATCH", f"/api/users/{uid}/role", 200, {"role_id": 2}, token=a)
        check("delete user", "DELETE", f"/api/users/{uid}", (204, 200), token=a)


def phase_catalog():
    section("Catalog: category / course / module / lesson")
    i = ctx["instructor_token"]

    check("list categories", "GET", "/api/categories", 200, token=i)
    check("create category", "POST", "/api/categories", (201, 200),
          {"name": f"Cat{uuid.uuid4().hex[:6]}"}, token=i, save="category_id")
    cid = ctx.get("category_id")
    if cid:
        check("get category", "GET", f"/api/categories/{cid}", 200, token=i)
        check("update category", "PUT", f"/api/categories/{cid}", 200,
              {"name": f"Cat{uuid.uuid4().hex[:6]}"}, token=i)
        check("courses in category", "GET", f"/api/categories/{cid}/courses", 200, token=i)

        check("create course", "POST", "/api/courses", (201, 200), {
            "title": "FastAPI from Scratch",
            "description": "Build production REST APIs.",
            "language": "English", "duration": "8 weeks",
            "level": "Beginner", "price": 1499.00, "category_id": cid,
        }, token=i, save="course_id")

    crs = ctx.get("course_id")
    if crs:
        check("list courses", "GET", "/api/courses", 200, token=i)
        check("get course", "GET", f"/api/courses/{crs}", 200, token=i)
        check("search courses", "GET", "/api/courses/search?query=FastAPI", 200, token=i)
        check("update course", "PUT", f"/api/courses/{crs}", 200,
              {"description": "Updated description."}, token=i)
        check("course status", "PATCH", f"/api/courses/{crs}/status", 200,
              {"is_active": True}, token=i)
        check("course modules", "GET", f"/api/courses/{crs}/modules", 200, token=i)
        check("course reviews", "GET", f"/api/courses/{crs}/reviews", 200, token=i)
        check("course quizzes", "GET", f"/api/courses/{crs}/quizzes", 200, token=i)
        check("course enrollments (staff)", "GET", f"/api/courses/{crs}/enrollments", 200, token=i)

        check("create module", "POST", "/api/modules", (201, 200),
              {"title": "Getting Started", "description": "Setup.", "course_id": crs},
              token=i, save="module_id")
        # This endpoint takes the full ModuleCreate schema, so course_id is
        # required in the body even though it is also in the path.
        check("create module (nested)", "POST", f"/api/courses/{crs}/modules", (201, 200),
              {"title": "Nested Module", "description": "Created under a course.",
               "course_id": crs},
              token=i, save="nested_module_id")

    mod = ctx.get("module_id")
    if mod:
        check("list modules", "GET", "/api/modules", 200, token=i)
        check("get module", "GET", f"/api/modules/{mod}", 200, token=i)
        check("update module", "PUT", f"/api/modules/{mod}", 200,
              {"description": "Updated."}, token=i)
        check("module lessons", "GET", f"/api/modules/{mod}/lessons", 200, token=i)

        check("create lesson", "POST", "/api/lessons", (201, 200),
              {"title": "Installing uv", "description": "Toolchain.",
               "video_url": "https://videos.com/1.mp4", "module_id": mod},
              token=i, save="lesson_id")
        # Takes the full LessonCreate schema, so module_id is required too.
        check("create lesson (nested)", "POST", f"/api/modules/{mod}/lessons", (201, 200),
              {"title": "Nested Lesson", "description": "Created under a module.",
               "video_url": "https://videos.com/2.mp4", "module_id": mod},
              token=i, save="nested_lesson_id")

    les = ctx.get("lesson_id")
    if les:
        check("list lessons", "GET", "/api/lessons", 200, token=i)
        check("get lesson", "GET", f"/api/lessons/{les}", 200, token=i)
        check("update lesson", "PUT", f"/api/lessons/{les}", 200,
              {"description": "Updated."}, token=i)


def phase_quiz():
    section("Quizzes / questions")
    i = ctx["instructor_token"]
    crs, les = ctx.get("course_id"), ctx.get("lesson_id")
    if not crs:
        return
    check("create quiz", "POST", "/api/quizzes", (201, 200), {
        "title": "Module 1 Check", "description": "Quick check.",
        "course_id": crs, "lesson_id": les,
        "total_marks": 10, "pass_marks": 6, "duration": 15,
    }, token=i, save="quiz_id")

    q = ctx.get("quiz_id")
    if not q:
        return
    check("list quizzes", "GET", "/api/quizzes", 200, token=i)
    check("get quiz", "GET", f"/api/quizzes/{q}", 200, token=i)
    check("update quiz", "PUT", f"/api/quizzes/{q}", 200, {"pass_marks": 5}, token=i)
    check("quiz questions", "GET", f"/api/quizzes/{q}/questions", 200, token=i)

    q1 = check("create question 1", "POST", "/api/quiz-questions", (201, 200), {
        "quiz_id": q, "question": "Which command runs the dev server?",
        "option_a": "python serve.py", "option_b": "uvicorn app.main:app --reload",
        "option_c": "fastapi run", "option_d": "flask run",
        "correct_option": "B", "marks": 5,
    }, token=i, save="question1_id")

    check("create question 2 (nested)", "POST", f"/api/quizzes/{q}/questions", (201, 200), {
        "question": "Which status code means Created?",
        "option_a": "200", "option_b": "204", "option_c": "201", "option_d": "400",
        "correct_option": "C", "marks": 5,
    }, token=i, save="question2_id")

    check("list questions", "GET", "/api/quiz-questions", 200, token=i)
    if ctx.get("question1_id"):
        qid = ctx["question1_id"]
        check("get question", "GET", f"/api/quiz-questions/{qid}", 200, token=i)
        check("update question", "PUT", f"/api/quiz-questions/{qid}", 200,
              {"marks": 5}, token=i)


def phase_student():
    section("Student flow: enroll / attempt / answer / pay / review")
    s = ctx["student_token"]
    crs = ctx.get("course_id")
    if not crs:
        return

    check("enroll", "POST", "/api/enrollments", (201, 200),
          {"course_id": crs}, token=s, save="enrollment_id")
    check("duplicate enroll rejected", "POST", "/api/enrollments", 400,
          {"course_id": crs}, token=s)

    en = ctx.get("enrollment_id")
    if en:
        check("get enrollment (owner)", "GET", f"/api/enrollments/{en}", 200, token=s)
        check("update progress", "PATCH", f"/api/enrollments/{en}/progress", 200,
              {"status": "ACTIVE"}, token=s)
        check("mark complete", "PATCH", f"/api/enrollments/{en}/complete", 200, token=s)
        check("update enrollment (staff)", "PUT", f"/api/enrollments/{en}", 200,
              {"status": "ACTIVE"}, token=ctx["instructor_token"])

    q = ctx.get("quiz_id")
    if q:
        check("start attempt", "POST", "/api/quiz-attempts", (201, 200),
              {"quiz_id": q}, token=s, save="attempt_id")

    at = ctx.get("attempt_id")
    if at:
        check("get attempt (owner)", "GET", f"/api/quiz-attempts/{at}", 200, token=s)
        if ctx.get("question1_id"):
            r = check("submit correct answer", "POST", f"/api/quiz-attempts/{at}/answers",
                      (201, 200), {"question_id": ctx["question1_id"], "selected_option": "B"},
                      token=s, save="answer_id")
            if isinstance(r, dict):
                if r.get("is_correct") is True:
                    PASSED.append("grading: correct answer marked correct")
                    print("  PASS  grading: is_correct=True, marks=%s" % r.get("marks_obtained"))
                else:
                    FAILED.append(("grading correct answer", f"is_correct={r.get('is_correct')}"))
                    print("  FAIL  grading: expected is_correct=True, got", r.get("is_correct"))
        if ctx.get("question2_id"):
            r = check("submit wrong answer", "POST", f"/api/quiz-attempts/{at}/answers",
                      (201, 200), {"question_id": ctx["question2_id"], "selected_option": "A"},
                      token=s)
            if isinstance(r, dict):
                if r.get("is_correct") is False:
                    PASSED.append("grading: wrong answer marked wrong")
                    print("  PASS  grading: is_correct=False, marks=%s" % r.get("marks_obtained"))
                else:
                    FAILED.append(("grading wrong answer", f"is_correct={r.get('is_correct')}"))
                    print("  FAIL  grading: expected is_correct=False")

        if ctx.get("question1_id"):
            # Same (attempt, question) as the nested submit above -> must be
            # rejected cleanly by the unique constraint guard.
            check("duplicate answer rejected", "POST", "/api/quiz-answers", 400,
                  {"attempt_id": at, "question_id": ctx["question1_id"],
                   "selected_option": "B"}, token=s)
            # Fresh attempt so the direct endpoint gets a real success case.
            second = call("POST", "/api/quiz-attempts", {"quiz_id": q}, s)[1]
            if isinstance(second, dict) and second.get("id"):
                check("submit answer (direct endpoint)", "POST", "/api/quiz-answers",
                      (201, 200),
                      {"attempt_id": second["id"], "question_id": ctx["question1_id"],
                       "selected_option": "B"}, token=s)
        check("update attempt (owner)", "PUT", f"/api/quiz-attempts/{at}", 200,
              {"status": "IN_PROGRESS"}, token=s)
        check("attempt answers", "GET", f"/api/quiz-attempts/{at}/answers", 200, token=s)
        r = check("submit attempt", "PATCH", f"/api/quiz-attempts/{at}/submit", 200, token=s)
        if isinstance(r, dict):
            score = r.get("score")
            if str(score).startswith("5"):
                PASSED.append("scoring: total = 5")
                print(f"  PASS  scoring: score={score} (5 correct + 0 wrong)")
            else:
                FAILED.append(("scoring", f"expected 5, got {score}"))
                print(f"  FAIL  scoring: expected 5, got {score}")
        check("double submit rejected", "PATCH", f"/api/quiz-attempts/{at}/submit", 400, token=s)

    if ctx.get("answer_id"):
        aid = ctx["answer_id"]
        check("get answer (owner)", "GET", f"/api/quiz-answers/{aid}", 200, token=s)
        check("update answer", "PUT", f"/api/quiz-answers/{aid}", 200,
              {"selected_option": "B"}, token=s)

    check("list all answers (staff)", "GET", "/api/quiz-answers", 200,
          token=ctx["instructor_token"])

    # payments
    p = check("initiate payment", "POST", "/api/payments", (201, 200), {
        "course_id": crs, "amount": 1499.00, "payment_method": "UPI",
        "currency": "INR", "payment_gateway": "razorpay",
    }, token=s, save="payment_id")
    txn = p.get("transaction_id") if isinstance(p, dict) else None

    pid = ctx.get("payment_id")
    if pid:
        check("get payment (owner)", "GET", f"/api/payments/{pid}", 200, token=s)
        check("payment status (no auth)", "PATCH", f"/api/payments/{pid}/status", 200,
              {"payment_status": "SUCCESS", "transaction_id": txn,
               "receipt_url": "https://receipts.com/1.pdf"})
        check("get receipt", "GET", f"/api/payments/{pid}/receipt", 200, token=s)
    if txn:
        check("webhook (no auth)", "POST", "/api/payments/webhook", 200,
              {"transaction_id": txn, "payment_status": "SUCCESS",
               "receipt_url": "https://receipts.com/1.pdf"})

    # review
    check("create review", "POST", "/api/course-reviews", (201, 200),
          {"course_id": crs, "rating": 5, "review": "Excellent course."},
          token=s, save="review_id")
    check("duplicate review rejected", "POST", "/api/course-reviews", 400,
          {"course_id": crs, "rating": 4, "review": "Again."}, token=s)
    check("invalid rating rejected", "POST", "/api/course-reviews", 422,
          {"course_id": crs, "rating": 9, "review": "Bad rating."}, token=s)

    rv = ctx.get("review_id")
    if rv:
        check("list reviews", "GET", "/api/course-reviews", 200, token=s)
        check("get review", "GET", f"/api/course-reviews/{rv}", 200, token=s)
        check("update own review", "PUT", f"/api/course-reviews/{rv}", 200,
              {"rating": 4}, token=s)


def phase_certificates():
    section("Certificates")
    i, s = ctx["instructor_token"], ctx["student_token"]
    crs, sid = ctx.get("course_id"), ctx.get("student_id")
    if not (crs and sid):
        return
    num = f"EDU-{uuid.uuid4().hex[:8].upper()}"
    check("issue certificate", "POST", "/api/certificates", (201, 200),
          {"student_id": sid, "course_id": crs, "certificate_number": num,
           "certificate_url": f"https://certs.com/{num}.pdf"},
          token=i, save="certificate_id")
    check("duplicate number rejected", "POST", "/api/certificates", 400,
          {"student_id": sid, "course_id": crs, "certificate_number": num}, token=i)

    check("verify certificate (public)", "GET", f"/api/certificates/verify/{num}", 200)
    r = call("GET", f"/api/certificates/verify/{num}")[1]
    if isinstance(r, dict) and r.get("valid") is True:
        PASSED.append("verify returns valid=true")
        print("  PASS  verify: valid=true")
    else:
        FAILED.append(("verify valid", str(r)))
        print("  FAIL  verify: expected valid=true")

    r = call("GET", "/api/certificates/verify/DOES-NOT-EXIST")[1]
    if isinstance(r, dict) and r.get("valid") is False:
        PASSED.append("verify unknown returns valid=false")
        print("  PASS  verify unknown: valid=false")
    else:
        FAILED.append(("verify unknown", str(r)))
        print("  FAIL  verify unknown: expected valid=false")

    check("list certificates (staff)", "GET", "/api/certificates", 200, token=i)
    if ctx.get("certificate_id"):
        cert = ctx["certificate_id"]
        check("get certificate (owner)", "GET", f"/api/certificates/{cert}", 200, token=s)


def phase_students_subresources():
    section("Per-student sub-resources")
    s, i = ctx["student_token"], ctx["instructor_token"]
    sid = ctx.get("student_id")
    if not sid:
        return
    for sub in ("enrollments", "quiz-attempts", "certificates", "payments"):
        check(f"own {sub}", "GET", f"/api/students/{sid}/{sub}", 200, token=s)
        check(f"staff views {sub}", "GET", f"/api/students/{sid}/{sub}", 200, token=i)


def phase_permissions():
    section("Permission boundaries")
    s, i = ctx["student_token"], ctx["instructor_token"]

    # student blocked from admin/staff endpoints
    check("student: list users blocked", "GET", "/api/users", 403, token=s)
    check("student: list roles blocked", "GET", "/api/roles", 403, token=s)
    check("student: create role blocked", "POST", "/api/roles", 403, {"name": "X"}, token=s)
    check("student: create category blocked", "POST", "/api/categories", 403,
          {"name": "X"}, token=s)
    check("student: create course blocked", "POST", "/api/courses", 403,
          {"title": "X", "category_id": ctx.get("category_id") or str(uuid.uuid4())}, token=s)
    check("student: list all enrollments blocked", "GET", "/api/enrollments", 403, token=s)
    check("student: list all attempts blocked", "GET", "/api/quiz-attempts", 403, token=s)
    check("student: list all payments blocked", "GET", "/api/payments", 403, token=s)
    check("student: list all certificates blocked", "GET", "/api/certificates", 403, token=s)
    if ctx.get("course_id"):
        check("student: course roster blocked", "GET",
              f"/api/courses/{ctx['course_id']}/enrollments", 403, token=s)

    # instructor blocked from admin-only
    check("instructor: list users blocked", "GET", "/api/users", 403, token=i)
    check("instructor: list roles blocked", "GET", "/api/roles", 403, token=i)

    # no token -> 401
    check("no token: users", "GET", "/api/users", 401)
    check("no token: courses", "GET", "/api/courses", 401)
    check("no token: categories", "GET", "/api/categories", 401)

    # student can read catalog
    check("student: read courses", "GET", "/api/courses", 200, token=s)
    check("student: read categories", "GET", "/api/categories", 200, token=s)
    check("student: read lessons", "GET", "/api/lessons", 200, token=s)


def phase_cleanup():
    section("Cleanup (delete created resources)")
    i, s = ctx["instructor_token"], ctx["student_token"]
    if ctx.get("review_id"):
        check("delete review", "DELETE", f"/api/course-reviews/{ctx['review_id']}",
              (204, 200), token=s)
    if ctx.get("certificate_id"):
        check("delete certificate", "DELETE", f"/api/certificates/{ctx['certificate_id']}",
              (204, 200), token=i)
    if ctx.get("enrollment_id"):
        check("delete enrollment", "DELETE", f"/api/enrollments/{ctx['enrollment_id']}",
              (204, 200), token=i)
    for key, path in (("question1_id", "quiz-questions"), ("question2_id", "quiz-questions")):
        if ctx.get(key):
            check(f"delete {key}", "DELETE", f"/api/{path}/{ctx[key]}", (204, 200), token=i)
    if ctx.get("quiz_id"):
        check("delete quiz", "DELETE", f"/api/quizzes/{ctx['quiz_id']}", (204, 200), token=i)
    if ctx.get("lesson_id"):
        check("delete lesson", "DELETE", f"/api/lessons/{ctx['lesson_id']}", (204, 200), token=i)
    if ctx.get("nested_lesson_id"):
        check("delete nested lesson", "DELETE",
              f"/api/lessons/{ctx['nested_lesson_id']}", (204, 200), token=i)
    if ctx.get("nested_module_id"):
        check("delete nested module", "DELETE",
              f"/api/modules/{ctx['nested_module_id']}", (204, 200), token=i)
    if ctx.get("module_id"):
        check("delete module", "DELETE", f"/api/modules/{ctx['module_id']}", (204, 200), token=i)
    if ctx.get("course_id"):
        check("delete course", "DELETE", f"/api/courses/{ctx['course_id']}", (204, 200), token=i)
    if ctx.get("category_id"):
        check("delete category", "DELETE", f"/api/categories/{ctx['category_id']}",
              (204, 200), token=i)


# ----------------------------------------------------------------------------

def main():
    global BASE
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=BASE)
    ap.add_argument("--no-cleanup", action="store_true",
                    help="keep created rows so you can inspect them")
    args = ap.parse_args()
    BASE = args.url.rstrip("/")

    print(f"Testing {BASE}")
    check("root", "GET", "/", (200, 404))

    phase_auth()
    phase_roles()
    phase_users()
    phase_catalog()
    phase_quiz()
    phase_student()
    phase_certificates()
    phase_students_subresources()
    phase_permissions()
    if not args.no_cleanup:
        phase_cleanup()

    total = len(PASSED) + len(FAILED)
    print("\n" + "=" * 62)
    print(f"  RESULT: {len(PASSED)}/{total} passed, {len(FAILED)} failed")
    print("=" * 62)
    if FAILED:
        print("\nFailures:")
        for label, why in FAILED:
            print(f"  - {label}: {why}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())