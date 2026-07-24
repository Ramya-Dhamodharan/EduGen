import { useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { coursesApi } from '@/api/courses'
import { modulesApi } from '@/api/modules'
import { enrollmentsApi } from '@/api/enrollments'
import { useAuth } from '@/context/AuthContext'
import LevelStamp from '@/components/ui/LevelStamp'
import Loader from '@/components/ui/Loader'
import ErrorNote from '@/components/ui/ErrorNote'
import type { CourseModule } from '@/types/module'
import type { Lesson } from '@/types/lesson'

function LessonRow({ lesson }: { lesson: Lesson }) {
  return (
    <li className="flex items-center gap-3 py-2 pl-4 border-l-2 border-ledger/10 text-sm">
      <span className="font-mono text-xs text-ledger/40">▸</span>
      <span>{lesson.title}</span>
    </li>
  )
}

function ModuleAccordionItem({ module, index }: { module: CourseModule; index: number }) {
  const [open, setOpen] = useState(false)

  const { data: lessons, isLoading } = useQuery({
    queryKey: ['modules', module.id, 'lessons'],
    queryFn: () => modulesApi.getLessons(module.id),
    enabled: open,
  })

  return (
    <div className="border border-ledger/15 rounded-sm bg-paper">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <span className="flex items-center gap-3">
          <span className="font-mono text-xs text-ledger/40">{String(index + 1).padStart(2, '0')}</span>
          <span className="font-medium">{module.title}</span>
        </span>
        <span className="font-mono text-xs text-ledger/40">{open ? '−' : '+'}</span>
      </button>

      {open && (
        <div className="px-4 pb-4">
          {isLoading && <p className="font-mono text-xs text-ledger/40 pl-4">Loading lessons…</p>}
          <ul>{lessons?.map((l: Lesson) => <LessonRow key={l.id} lesson={l} />)}</ul>
          {lessons?.length === 0 && (
            <p className="font-mono text-xs text-ledger/40 pl-4">No lessons yet.</p>
          )}
        </div>
      )}
    </div>
  )
}

export default function CourseDetailPage() {
  const { courseId } = useParams({ from: '/courses/$courseId' })
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const { data: course, isLoading, isError } = useQuery({
    queryKey: ['courses', courseId],
    queryFn: () => coursesApi.getById(courseId),
  })

  const { data: modules } = useQuery({
    queryKey: ['courses', courseId, 'modules'],
    queryFn: () => coursesApi.getModules(courseId),
  })

  const { data: myEnrollments } = useQuery({
    queryKey: ['enrollments', 'me'],
    queryFn: () => enrollmentsApi.getForStudent(user!.id),
    enabled: !!user,
  })

  const existingEnrollment = myEnrollments?.find((e) => e.course_id === courseId)

  const enrollMutation = useMutation({
    mutationFn: () => enrollmentsApi.enroll(courseId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['enrollments', 'me'] }),
  })

  if (isLoading) return <Loader label="Opening the ledger entry…" />
  if (isError || !course) return <ErrorNote message="Course not found." />

  return (
    <div>
      <div className="mb-6 pb-6 border-b-2 border-ledger">
        <div className="flex items-start justify-between gap-4 mb-3">
          <h1 className="font-display text-3xl font-bold leading-tight">{course.title}</h1>
          <LevelStamp level={course.level} />
        </div>
        {course.description && <p className="text-ledger/70 max-w-2xl mb-4">{course.description}</p>}

        <div className="flex items-center gap-4 font-mono text-xs text-ledger/60 mb-5">
          <span>{course.duration || '—'}</span>
          <span>·</span>
          <span>{course.language || '—'}</span>
          <span>·</span>
          <span>{course.price ? `$${course.price}` : 'Free'}</span>
        </div>

        {user &&
          (existingEnrollment ? (
            <span className="inline-block font-mono text-xs uppercase tracking-widest border-2 border-ledger px-3 py-1.5 rounded-sm">
              Status: {existingEnrollment.status}
            </span>
          ) : (
            <button
              onClick={() => enrollMutation.mutate()}
              disabled={enrollMutation.isPending}
              className="bg-amber text-ledger font-mono text-xs uppercase tracking-widest px-5 py-2.5 rounded-sm hover:brightness-95 transition disabled:opacity-50"
            >
              {enrollMutation.isPending ? 'Enrolling…' : 'Enroll in this course'}
            </button>
          ))}
      </div>

      <h2 className="font-display text-xl font-semibold mb-4">Modules</h2>
      <div className="space-y-3">
        {modules?.map((m: CourseModule, i: number) => (
          <ModuleAccordionItem key={m.id} module={m} index={i} />
        ))}
        {modules?.length === 0 && (
          <p className="font-mono text-sm text-ledger/50">No modules published yet.</p>
        )}
      </div>
    </div>
  )
}
