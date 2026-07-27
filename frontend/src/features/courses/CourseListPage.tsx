import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { coursesApi } from '@/api/courses'
import { categoriesApi } from '@/api/categories'
import CourseCard from '@/components/ui/CourseCard'
import Loader from '@/components/ui/Loader'
import ErrorNote from '@/components/ui/ErrorNote'
import { useDebounce } from '@/hooks/useDebounce'

export default function CourseListPage() {
  const [query, setQuery] = useState('')
  const [level, setLevel] = useState('')
  const [category, setCategory] = useState('')
  const debouncedQuery = useDebounce(query, 300)

  const { data: categories } = useQuery({ queryKey: ['categories'], queryFn: categoriesApi.list })

  const { data: courses, isLoading, isError } = useQuery({
    queryKey: ['courses', 'search', debouncedQuery, level, category],
    queryFn: () =>
      coursesApi.search({
        query: debouncedQuery || undefined,
        level: level || undefined,
        category: category || undefined,
      }),
  })

  return (
    <div>
      {/* Hero */}
      <section className="mb-10 border-b-2 border-ledger pb-8">
        <p className="font-mono text-xs uppercase tracking-widest text-amber mb-2">Vol. 01 — Course Ledger</p>
        <h1 className="font-display text-4xl font-bold leading-tight mb-3 max-w-2xl">
          Every course you've started, finished, or haven't opened yet.
        </h1>
        <p className="text-ledger/70 max-w-xl">
          Browse the catalog, log your progress, and keep the record straight —
          one entry per course, one line per lesson.
        </p>
      </section>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6 font-mono text-xs">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search title…"
          className="border-b-2 border-ledger/20 bg-transparent px-1 py-1.5 focus:outline-none focus:border-amber flex-1 min-w-[160px]"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="border-2 border-ledger/20 rounded-sm px-2 py-1.5 bg-paper"
        >
          <option value="">All categories</option>
          {categories?.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="border-2 border-ledger/20 rounded-sm px-2 py-1.5 bg-paper"
        >
          <option value="">All levels</option>
          <option value="Beginner">Beginner</option>
          <option value="Intermediate">Intermediate</option>
          <option value="Advanced">Advanced</option>
        </select>
      </div>

      {isLoading && <Loader label="Pulling the ledger…" />}
      {isError && <ErrorNote message="Couldn't load courses." />}

      {courses && courses.length === 0 && (
        <div className="border-2 border-dashed border-ledger/20 rounded-sm p-10 text-center font-mono text-sm text-ledger/50">
          No entries match. Try clearing a filter.
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {courses?.map((course) => (
          <CourseCard key={course.id} course={course} />
        ))}
      </div>
    </div>
  )
}
