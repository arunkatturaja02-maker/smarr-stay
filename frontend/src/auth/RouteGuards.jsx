import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { getRoleHome } from './roles'
import { useAuth } from './useAuth'

export function FullPageLoader({ label = 'Loading StaySmart…' }) {
  return (
    <div className="app-loading" role="status" aria-live="polite">
      <span className="spinner spinner--large" aria-hidden="true" />
      <p>{label}</p>
    </div>
  )
}

/** Requires a valid authenticated session. */
export function ProtectedRoute() {
  const { user, status } = useAuth()
  const location = useLocation()

  if (status === 'loading') {
    return <FullPageLoader label="Checking your session…" />
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return <Outlet />
}

/** Requires one of the supplied roles in addition to authentication. */
export function RoleRoute({ allowedRoles }) {
  const { user, status } = useAuth()
  const location = useLocation()

  if (status === 'loading') {
    return <FullPageLoader label="Checking your permissions…" />
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (!allowedRoles.includes(user.role)) {
    return (
      <Navigate
        to="/unauthorized"
        replace
        state={{ attemptedPath: location.pathname }}
      />
    )
  }

  return <Outlet />
}

/** Login and registration pages should redirect signed-in users home. */
export function PublicOnlyRoute() {
  const { user, status } = useAuth()

  if (status === 'loading') {
    return <FullPageLoader />
  }

  if (user) {
    return <Navigate to={getRoleHome(user.role)} replace />
  }

  return <Outlet />
}

export function RootRedirect() {
  const { user, status } = useAuth()

  if (status === 'loading') {
    return <FullPageLoader />
  }

  return <Navigate to={user ? getRoleHome(user.role) : '/login'} replace />
}
