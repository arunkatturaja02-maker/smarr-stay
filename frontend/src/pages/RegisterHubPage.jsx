import { Link } from 'react-router-dom'
import { REGISTRATION_ROLES } from '../auth/roles'
import AuthLayout from '../components/AuthLayout'

export default function RegisterHubPage() {
  return (
    <AuthLayout
      wide
      eyebrow="Staff onboarding"
      title="Create a staff account."
      description="Choose the registration form that matches your hotel role. Every new account is reviewed before access is granted."
    >
      <div className="register-options">
        {Object.values(REGISTRATION_ROLES).map((role, index) => (
          <Link className="role-option" to={role.path} key={role.role}>
            <span className="role-option-index" aria-hidden="true">
              {String(index + 1).padStart(2, '0')}
            </span>
            <span className="role-option-copy">
              <span className="role-option-label">{role.label}</span>
              <span className="role-option-description">{role.summary}</span>
              <span className="role-option-meta">
                {role.highlights.join(' · ')}
              </span>
            </span>
            <span className="role-option-arrow" aria-hidden="true">
              →
            </span>
          </Link>
        ))}
      </div>

      <div className="approval-callout">
        <strong>Approval is required</strong>
        <p>
          Registration does not grant dashboard access. An administrator must
          approve your account before you can sign in.
        </p>
      </div>

      <p className="auth-switch">
        Already have an approved account? <Link to="/login">Sign in</Link>
      </p>
    </AuthLayout>
  )
}
