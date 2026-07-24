import { createRootRoute, createRoute, createRouter, redirect } from '@tanstack/react-router'

import App from '@/App'
import LoginPage from '@/features/auth/LoginPage'
import RegisterPage from '@/features/auth/RegisterPage'
import CourseListPage from '@/features/courses/CourseListPage'
import CourseDetailPage from '@/features/courses/CourseDetailPage'
import MyCoursesPage from '@/features/enrollments/MyCoursesPage'

const rootRoute = createRootRoute({ component: App })

// Simple guard: every protected route checks for a stored access_token
// before loading. (Full validity is still checked server-side — this
// just avoids flashing protected UI to a logged-out visitor.)
function requireAuth() {
  if (!localStorage.getItem('access_token')) {
    throw redirect({ to: '/login' })
  }
}

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: LoginPage,
})

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/register',
  component: RegisterPage,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: requireAuth,
  component: CourseListPage,
})

const courseDetailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/courses/$courseId',
  beforeLoad: requireAuth,
  component: CourseDetailPage,
})

const myCoursesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/my-courses',
  beforeLoad: requireAuth,
  component: MyCoursesPage,
})

const routeTree = rootRoute.addChildren([
  loginRoute,
  registerRoute,
  indexRoute,
  courseDetailRoute,
  myCoursesRoute,
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
