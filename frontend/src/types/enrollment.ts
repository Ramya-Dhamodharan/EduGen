// Matches EnrollmentOut exactly — note: no numeric "progress" field in this
// backend, only a status string (e.g. "ACTIVE" / "COMPLETED") + timestamps.
export interface Enrollment {
  id: string
  student_id: string
  course_id: string
  status: string
  enrolled_at?: string
  started_at?: string
  completed_at?: string
}
