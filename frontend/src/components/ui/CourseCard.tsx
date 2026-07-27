import { Link } from '@tanstack/react-router'
import type { Course } from '@/types/course'
import LevelStamp from './LevelStamp'

export default function CourseCard({ course }: { course: Course }) {
  return (
    <Link
      to="/courses/$courseId"
      params={{ courseId: course.id }}
      className="group relative block bg-paper border border-ledger/15 rounded-sm p-5 shadow-[2px_2px_0_0_rgba(31,58,52,0.08)] transition hover:-translate-y-0.5 hover:shadow-[3px_3px_0_0_rgba(31,58,52,0.15)]"
    >
      {/* punch-hole detail, reinforces the "index card" motif */}
      <div className="absolute -left-1.5 top-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-parchment border border-ledger/20" />

      <div className="flex items-start justify-between gap-3 mb-2">
        <h3 className="font-display text-lg font-semibold leading-snug text-ledger group-hover:underline decoration-amber decoration-2 underline-offset-4">
          {course.title}
        </h3>
        <LevelStamp level={course.level} />
      </div>

      {course.description && (
        <p className="text-sm text-ledger/70 line-clamp-2 mb-4">{course.description}</p>
      )}

      <div className="dash-rule mb-3" />

      <div className="flex items-center justify-between font-mono text-xs text-ledger/60">
        <span>{course.duration || '—'}</span>
        <span>{course.language || '—'}</span>
        <span>{course.price ? `$${course.price}` : 'Free'}</span>
      </div>
    </Link>
  )
}
