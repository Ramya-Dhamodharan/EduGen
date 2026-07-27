import { useQuery, useQueries, useMutation, useQueryClient } from '@tanstack/react-query'
import { enrollmentsApi } from '@/api/enrollments'
import { coursesApi } from '@/api/courses'
import { useAuth } from '@/context/AuthContext'
import Loader from '@/components/ui/Loader'
import ErrorNote from '@/components/ui/ErrorNote'

const STATUS_STYLES: Record<string, string> = {
  ACTIVE: 'border-amber text-amber',
  COMPLETED: 'border-ledger text-ledger bg-ledger/5',
}

export default function MyCoursesPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()

  const { data: enrollments, isLoading, isError } = useQuery({
    queryKey: ['enrollments', 'me'],
    queryFn: () => enrollmentsApi.getForStudent(user!.id),
    enabled: !!user,
  })

  const courseQueries = useQueries({
    queries: (enrollments || []).map((e) => ({
      queryKey: ['courses', e.course_id],
      queryFn: () => coursesApi.getById(e.course_id),
      enabled: !!enrollments,
    })),
  })

  const completeMutation = useMutation({
    mutationFn: (enrollmentId: string) => enrollmentsApi.markComplete(enrollmentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['enrollments', 'me'] }),
  })

  if (isLoading) return <Loader label="Pulling your ledger…" />
  if (isError) return <ErrorNote message="Couldn't load your enrollments." />

  return (
    <div>
      <div className="mb-8 pb-6 border-b-2 border-ledger">
        <p className="font-mono text-xs uppercase tracking-widest text-amber mb-2">Personal Ledger</p>
        <h1 className="font-display text-3xl font-bold">My Courses</h1>
      </div>

      {enrollments?.length === 0 && (
        <div className="border-2 border-dashed border-ledger/20 rounded-sm p-10 text-center font-mono text-sm text-ledger/50">
          No entries yet. Head to the catalog and enroll in something.
        </div>
      )}

      <div className="space-y-3">
        {enrollments?.map((enrollment, i) => {
          const course = courseQueries[i]?.data
          const statusClass = STATUS_STYLES[enrollment.status] || 'border-ledger text-ledger'

          return (
            <div
              key={enrollment.id}
              className="flex items-center justify-between gap-4 bg-paper border border-ledger/15 rounded-sm px-5 py-4"
            >
              <div>
                <p className="font-display font-semibold">{course?.title || 'Loading…'}</p>
                <p className="font-mono text-xs text-ledger/50 mt-0.5">
                  Enrolled {enrollment.enrolled_at ? new Date(enrollment.enrolled_at).toLocaleDateString() : '—'}
                </p>
              </div>

              <div className="flex items-center gap-3">
                <span className={`font-mono text-[10px] uppercase tracking-widest border-2 rounded-sm px-2 py-1 ${statusClass}`}>
                  {enrollment.status}
                </span>
                {enrollment.status !== 'COMPLETED' && (
                  <button
                    onClick={() => completeMutation.mutate(enrollment.id)}
                    disabled={completeMutation.isPending}
                    className="font-mono text-xs text-amber hover:underline disabled:opacity-50"
                  >
                    Mark complete
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
