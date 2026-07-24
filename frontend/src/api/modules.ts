import { apiClient } from './client'

export const modulesApi = {
  getLessons: (moduleId: string) => apiClient.get(`/modules/${moduleId}/lessons`).then((r) => r.data),
}
