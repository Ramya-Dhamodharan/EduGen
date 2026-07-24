import { apiClient } from './client'
import type { CurrentUser } from '@/types/user'

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type?: string
}

export const authApi = {
  login: (data: LoginPayload) => apiClient.post<TokenResponse>('/auth/login', data).then((r) => r.data),
  register: (data: RegisterPayload) => apiClient.post<CurrentUser>('/auth/register', data).then((r) => r.data),
  logout: () => apiClient.post('/auth/logout'),
  me: () => apiClient.get<CurrentUser>('/auth/me').then((r) => r.data),
}
