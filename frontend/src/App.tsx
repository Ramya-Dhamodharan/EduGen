import { Outlet } from '@tanstack/react-router'
import Navbar from '@/components/layout/Navbar'

export default function App() {
  return (
    <div className="min-h-screen bg-parchment bg-grain">
      <Navbar />
      <main className="max-w-5xl mx-auto px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
