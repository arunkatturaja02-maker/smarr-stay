import { Link } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { getRoleHome, getRoleLabel } from '../auth/roles'
import Brand from '../components/Brand'

export default function UnauthorizedPage() {
  const { user } = useAuth()

  return (
    <div className="status-page">
      <header className="status-page-top">
        <Brand />
        <Link className="btn btn--ghost btn--small" to="/">
          Go home
        </Link>
      </header>

      <main className="status-card" id="main-content">
        <div className="status-code" aria-hidden="true">
          403
        </div>
        <span className="status-icon status-icon--lock" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            width="28"
            height="28"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.7"
          >
            <rect x="4" y="10" width="16" height="11" rx="2" />
            <path d="M8 10V7a4 4 0 018 0v3" />
            <path d="M12 14v3" />
          </svg>
        </span>
        <p className="eyebrow">Access denied</p>
        <h1>This workspace is not available to your role.</h1>
        <p className="status-description">
          {user
            ? `You are signed in as a ${getRoleLabel(user.role)}. Your role does not include permission for this page. The backend enforces the same restriction independently.`
            : 'You need an approved staff account to open this page. Sign in with the account that matches the workspace you need.'}
        </p>

        <div className="status-actions">
          {user ? (
            <Link className="btn btn--primary" to={getRoleHome(user.role)}>
              Go to my dashboard
            </Link>
          ) : (
            <Link className="btn btn--primary" to="/login">
              Sign in
            </Link>
          )}
          <Link className="btn btn--secondary" to="/">
            Return home
          </Link>
        </div>

        <p className="status-help">
          If you believe you should have access, contact your hotel
          administrator.
        </p>
      </main>
    </div>
  )
}
