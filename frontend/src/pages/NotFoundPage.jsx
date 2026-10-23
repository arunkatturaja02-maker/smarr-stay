import { Link } from 'react-router-dom'
import Brand from '../components/Brand'

export default function NotFoundPage() {
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
          404
        </div>
        <p className="eyebrow">Page not found</p>
        <h1>We could not find that page.</h1>
        <p className="status-description">
          The address may be incorrect, or the page may belong to a module that
          has not been built yet.
        </p>

        <div className="status-actions">
          <Link className="btn btn--primary" to="/">
            Return to StaySmart
          </Link>
          <Link className="btn btn--secondary" to="/login">
            Sign in
          </Link>
        </div>
      </main>
    </div>
  )
}
