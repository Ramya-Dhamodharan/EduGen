export interface Course {
  id: string
  title: string
  description?: string
  language?: string
  duration?: string
  level?: string
  price?: number
  category_id: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}
