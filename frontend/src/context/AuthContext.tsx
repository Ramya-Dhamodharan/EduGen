import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, type LoginPayload, type RegisterPayload } from '@/api/auth'
import type { CurrentUser } from '@/types/user'

interface AuthContextValue {
  user: CurrentUser | null
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setIsLoading(false)
      return
    }
    authApi.me().then(setUser).catch(() => localStorage.removeItem('access_token')).finally(() => setIsLoading(false))
  }, [])

  const login = async (payload: LoginPayload) => {
    const { access_token } = await authApi.login(payload)
    localStorage.setItem('access_token', access_token)
    setUser(await authApi.me())
  }

  const register = async (payload: RegisterPayload) => {
    await authApi.register(payload)
    await login({ email: payload.email, password: payload.password })
  }

  const logout = async () => {
    await authApi.logout().catch(() => {})
    localStorage.removeItem('access_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
