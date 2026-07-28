import { useState } from 'react'
import { Link, useNavigate } from '@tanstack/react-router'
import { useAuth } from '@/context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await login({ email, password })
      navigate({ to: '/' })
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Invalid email or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <div className="text-center mb-6">
          <p className="font-mono text-xs uppercase tracking-widest text-ledger/50 mb-1">Ledger Entry</p>
          <h1 className="font-display text-2xl font-bold">Log in</h1>
        </div>

        <div className="bg-paper border border-ledger/15 rounded-sm p-6 shadow-[2px_2px_0_0_rgba(31,58,52,0.08)] space-y-4">
          {error && <p className="font-mono text-xs text-rust">{error}</p>}

          <div>
            <label className="block font-mono text-[10px] uppercase tracking-widest text-ledger/60 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border-b-2 border-ledger/20 bg-transparent py-2 text-sm focus:outline-none focus:border-amber"
            />
          </div>

          <div>
            <label className="block font-mono text-[10px] uppercase tracking-widest text-ledger/60 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border-b-2 border-ledger/20 bg-transparent py-2 text-sm focus:outline-none focus:border-amber"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-ledger text-parchment rounded-sm py-2.5 font-mono text-xs uppercase tracking-widest hover:bg-ledgerlight transition disabled:opacity-50"
          >
            {loading ? 'Logging in…' : 'Log in'}
          </button>
        </div>

        <p className="text-center text-sm text-ledger/60 mt-4">
          New here?{' '}
          <Link to="/register" className="text-amber font-medium hover:underline">
            Create an account
          </Link>
        </p>
      </form>
    </div>
  )
}
