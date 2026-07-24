import { apiClient } from './client'
import type { Course } from '@/types/course'

export const coursesApi = {
  list: () => apiClient.get<Course[]>('/courses').then((r) => r.data),
  getById: (id: string) => apiClient.get<Course>(`/courses/${id}`).then((r) => r.data),
  search: (params: { query?: string; category?: string; level?: string; language?: string }) =>
    apiClient.get<Course[]>('/courses/search', { params }).then((r) => r.data),
  getModules: (id: string) => apiClient.get(`/courses/${id}/modules`).then((r) => r.data),
}
