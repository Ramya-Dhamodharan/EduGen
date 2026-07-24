# EduGen Frontend — Course Ledger

React + TypeScript + Vite + Tailwind + TanStack Query/Router.

Design direction: a "course ledger" — index-card course tiles, a rubber-stamp
level badge, dashed tear-rule dividers, monospace metadata. Deep forest-ink
(#1F3A34) on warm parchment (#F6F1E4), with an amber (#E8A33D) action accent.

## Setup

```bash
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if backend isn't on :8000
npm run dev
```

Open http://localhost:5173 — you'll land on /login since the catalog and
course routes require an authenticated session (matches the backend's
`require_user` dependency on courses/modules/lessons).

## Pages built

- `/login`, `/register` — auth forms
- `/` — course catalog: search, category + level filters, hero
- `/courses/:courseId` — course detail, modules/lessons accordion, enroll button
- `/my-courses` — student's enrollments with status + mark-complete

## Not yet built (backend supports these, UI doesn't yet)

- Admin/Instructor course/module/lesson management (create/edit/delete)
- Quizzes, quiz attempts
- Certificates, payments, course reviews
- Forgot/reset password flow

## Notes on the backend contract

- `EnrollmentOut` has a `status` string (`ACTIVE` / `COMPLETED`), not a
  numeric progress field — the UI reflects that rather than a progress bar.
- `POST /auth/register` never takes `role_id` — new accounts always default
  to the "Student" role server-side.
- Course/module/lesson **reads** require login (`require_user`); **writes**
  require staff (`require_staff` = Admin or Instructor). This UI is
  student-facing only, so it never calls the write endpoints.
