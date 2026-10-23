import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { getRoleHome } from '../auth/roles'
import AuthLayout from '../components/AuthLayout'

export default function PendingApprovalPage() {
  const { user } = useAuth()
  const location = useLocation()
  const state = location.state || {}
  const reference = state.email || state.employeeId

  return (
    <AuthLayout
      eyebrow="Approval required"
      title="Your account is awaiting approval."
      description="Your registration was received successfully. A hotel administrator must approve the account before it can access any dashboard or protected data."
    >
      <div className="pending-banner">
        <span className="pending-icon" aria-hidden="true">
          ◷
        </span>
        <div>
          <strong>Status: Pending administrator review</strong>
          <p>
            {state.reason === 'login'
              ? 'Your credentials were accepted, but this account is not approved yet.'
              : 'No dashboard access is available until approval is complete.'}
          </p>
        </div>
      </div>

      {reference || state.roleLabel ? (
        <dl className="pending-details">
          {state.roleLabel ? (
            <div>
              <dt>Requested role</dt>
              <dd>{state.roleLabel}</dd>
            </div>
          ) : null}
          {state.employeeId ? (
            <div>
              <dt>Employee ID</dt>
              <dd>{state.employeeId}</dd>
            </div>
          ) : null}
          {reference ? (
            <div>
              <dt>Account reference</dt>
              <dd>{reference}</dd>
            </div>
          ) : null}
        </dl>
      ) : null}

      <ol className="approval-steps">
        <li>
          <span aria-hidden="true">1</span>
          <div>
            <strong>Administrator review</strong>
            <p>
              An authorised staff administrator reviews and approves the new
              account through a controlled, server-side process.
            </p>
          </div>
        </li>
        <li>
          <span aria-hidden="true">2</span>
          <div>
            <strong>Sign in after approval</strong>
            <p>
              Once approved, return to the sign-in page using your email or
              employee ID.
            </p>
          </div>
        </li>
        <li>
          <span aria-hidden="true">3</span>
          <div>
            <strong>Open your role dashboard</strong>
            <p>
              StaySmart will take you to the dashboard that matches your staff
              role.
            </p>
          </div>
        </li>
      </ol>

      {user ? (
        <div className="form-alert form-alert--info" role="status">
          You are already signed in.{' '}
          <Link to={getRoleHome(user.role)}>Go to your dashboard</Link>.
        </div>
      ) : null}

      <p className="auth-switch">
        {user ? (
          <Link to={getRoleHome(user.role)}>Return to your dashboard</Link>
        ) : (
          <Link to="/login">Back to sign in</Link>
        )}
      </p>
    </AuthLayout>
  )
}
