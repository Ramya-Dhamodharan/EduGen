import { Link, useNavigate, useRouterState } from '@tanstack/react-router'
import { useAuth } from '@/context/AuthContext'

const TABS = [
  { to: '/', label: 'Catalog' },
  { to: '/my-courses', label: 'My Courses' },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const pathname = useRouterState({ select: (s) => s.location.pathname })

  const handleLogout = async () => {
    await logout()
    navigate({ to: '/login' })
  }

  return (
    <header className="bg-ledger text-parchment">
      <div className="max-w-5xl mx-auto px-6 pt-5 flex items-end justify-between">
        <Link to="/" className="font-display text-2xl font-bold tracking-tight pb-3">
          EduGen<span className="text-amber">.</span>
        </Link>

        <div className="flex items-end gap-1">
          {user &&
            TABS.map((tab) => {
              const active = pathname === tab.to
              return (
                <Link
                  key={tab.to}
                  to={tab.to}
                  className={`px-4 py-2 rounded-t-sm font-mono text-xs uppercase tracking-widest transition ${
                    active ? 'tab-active text-ledger' : 'text-parchment/70 hover:text-parchment'
                  }`}
                >
                  {tab.label}
                </Link>
              )
            })}

          <div className="ml-3 pb-3 flex items-center gap-3 text-sm">
            {user ? (
              <>
                <span className="text-parchment/70 font-mono text-xs">{user.username}</span>
                <button onClick={handleLogout} className="text-amber hover:underline font-medium">
                  Log out
                </button>
              </>
            ) : (
              <Link to="/login" className="text-amber hover:underline font-medium">
                Log in
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
