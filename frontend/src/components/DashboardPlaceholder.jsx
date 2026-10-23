import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { ROLE_DETAILS } from '../auth/roles'
import Brand from './Brand'

export default function DashboardPlaceholder({ cards, note }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const role = ROLE_DETAILS[user.role]
  const firstName = user.full_name.split(/\s+/)[0]
  const initials = user.full_name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()

  const handleLogout = async () => {
    try {
      await logout()
    } finally {
      navigate('/login', { replace: true })
    }
  }

  return (
    <div className="dashboard-shell">
      <header className="dashboard-topbar">
        <Brand />
        <div className="dashboard-topbar-actions">
          <span className={`role-badge role-badge--${user.role.toLowerCase()}`}>
            {role?.label || user.role}
          </span>
          <div className="user-chip" title={`${user.full_name} · ${user.employee_id}`}>
            <span className="avatar" aria-hidden="true">
              {initials}
            </span>
            <span className="user-chip-copy">
              <strong>{user.full_name}</strong>
              <small>{user.employee_id}</small>
            </span>
          </div>
          <button className="btn btn--ghost btn--small" type="button" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="dashboard-main" id="main-content">
        <section className="dashboard-hero">
          <div>
            <p className="eyebrow">Module 1 · Authenticated workspace</p>
            <h1 className="dashboard-title">Welcome, {firstName}.</h1>
            <p className="dashboard-subtitle">
              You are signed in as a{' '}
              <strong>{role?.label || user.role}</strong>. Your role-specific
              tools will appear in later modules.
            </p>
          </div>

          <div className="session-card">
            <div className="session-status">
              <span className="status-dot" aria-hidden="true" />
              Authentication active
            </div>
            <dl className="session-details">
              <div>
                <dt>Employee ID</dt>
                <dd>{user.employee_id}</dd>
              </div>
              <div>
                <dt>Email</dt>
                <dd>{user.email}</dd>
              </div>
            </dl>
          </div>
        </section>

        <section aria-labelledby="workspace-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Your workspace</p>
              <h2 id="workspace-heading">Planned for the next modules</h2>
            </div>
            <span className="coming-pill">Module 1 placeholder</span>
          </div>

          <div className="placeholder-grid">
            {cards.map((card, index) => (
              <article className="placeholder-card" key={card.title}>
                <div className="placeholder-card-top">
                  <span className="card-index" aria-hidden="true">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <span className="soon-pill">Coming soon</span>
                </div>
                <h3>{card.title}</h3>
                <p>{card.description}</p>
              </article>
            ))}
          </div>
        </section>

        <aside className="dashboard-notice">
          <span className="dashboard-notice-icon" aria-hidden="true">
            i
          </span>
          <p>
            {note ||
              'This dashboard is intentionally a placeholder. Module 1 only implements secure registration, login, and role-based access control.'}
          </p>
        </aside>
      </main>
    </div>
  )
}
