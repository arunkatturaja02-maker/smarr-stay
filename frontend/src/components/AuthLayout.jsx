import Brand from './Brand'

const rolePreview = [
  {
    initial: 'R',
    label: 'Receptionists',
    detail: 'Arrivals, departures and room coordination',
  },
  {
    initial: 'M',
    label: 'Housekeeping managers',
    detail: 'Priorities, assignments and inspections',
  },
  {
    initial: 'S',
    label: 'Housekeeping staff',
    detail: 'Room readiness and service tasks',
  },
]

export default function AuthLayout({
  eyebrow,
  title,
  description,
  children,
  wide = false,
}) {
  return (
    <div className="auth-shell">
      <aside className="auth-aside">
        <div className="aside-orbit aside-orbit--one" aria-hidden="true" />
        <div className="aside-orbit aside-orbit--two" aria-hidden="true" />

        <div className="auth-aside-top">
          <Brand light />
        </div>

        <div className="auth-aside-content">
          <p className="aside-eyebrow">Smart hotel operations</p>
          <h2 className="aside-title">
            Every stay,
            <span> perfectly coordinated.</span>
          </h2>
          <p className="aside-copy">
            One secure workspace for room allocation and housekeeping service
            priorities — built for the people who keep the hotel moving.
          </p>

          <ul className="role-preview" aria-label="StaySmart staff roles">
            {rolePreview.map((role) => (
              <li className="role-preview-item" key={role.label}>
                <span className="role-preview-initial" aria-hidden="true">
                  {role.initial}
                </span>
                <span>
                  <strong>{role.label}</strong>
                  <small>{role.detail}</small>
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className="auth-aside-foot">
          <span className="secure-dot" aria-hidden="true" />
          <span>Module 1 · Secure staff access</span>
        </div>
      </aside>

      <main className="auth-main" id="main-content">
        <div className={`auth-card${wide ? ' auth-card--wide' : ''}`}>
          <header className="auth-card-header">
            {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
            <h1>{title}</h1>
            {description ? <p className="auth-description">{description}</p> : null}
          </header>

          {children}

          <div className="auth-security-note">
            <svg
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              aria-hidden="true"
            >
              <path d="M12 3l7 3v5c0 4.6-2.9 8.6-7 10-4.1-1.4-7-5.4-7-10V6l7-3z" />
              <path d="M9.5 12l1.7 1.7 3.5-3.7" />
            </svg>
            <span>
              Sessions use a secure HttpOnly cookie. JWTs are never stored in
              localStorage.
            </span>
          </div>
        </div>
      </main>
    </div>
  )
}
