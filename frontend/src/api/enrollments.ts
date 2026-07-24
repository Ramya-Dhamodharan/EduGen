import { apiClient } from './client'
import type { Enrollment } from '@/types/enrollment'

export const enrollmentsApi = {
  // student_id comes from the auth token server-side — body only needs course_id
  enroll: (courseId: string) =>
    apiClient.post<Enrollment>('/enrollments', { course_id: courseId }).then((r) => r.data),

  markComplete: (enrollmentId: string) =>
    apiClient.patch<Enrollment>(`/enrollments/${enrollmentId}/complete`).then((r) => r.data),

  getForStudent: (studentId: string) =>
    apiClient.get<Enrollment[]>(`/students/${studentId}/enrollments`).then((r) => r.data),
}
