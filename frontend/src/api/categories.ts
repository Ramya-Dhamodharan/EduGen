import { apiClient } from './client'
import type { Category } from '@/types/category'

export const categoriesApi = {
  list: () => apiClient.get<Category[]>('/categories').then((r) => r.data),
}
