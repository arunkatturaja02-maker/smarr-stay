import { useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getApiError } from '../api/errors'
import { useAuth } from '../auth/useAuth'
import { getRoleHome } from '../auth/roles'
import AuthLayout from '../components/AuthLayout'
import { PasswordField, TextField } from '../components/FormField'

export default function LoginPage() {
  const { login, sessionExpired, clearSessionExpired } = useAuth()
  const navigate = useNavigate()

  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const submitLock = useRef(false)

  const updateIdentifier = (event) => {
    setIdentifier(event.target.value)
    setErrors((current) => ({ ...current, identifier: undefined }))
  }

  const updatePassword = (event) => {
    setPassword(event.target.value)
    setErrors((current) => ({ ...current, password: undefined }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (submitLock.current) return

    clearSessionExpired()
    setServerError('')

    const nextErrors = {}
    if (!identifier.trim()) {
      nextErrors.identifier = 'Enter your email address or employee ID.'
    }
    if (!password) {
      nextErrors.password = 'Enter your password.'
    }
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    setSubmitting(true)
    submitLock.current = true
    try {
      const user = await login(identifier.trim(), password)
      navigate(getRoleHome(user.role), { replace: true })
    } catch (error) {
      const apiError = getApiError(error)

      if (apiError.code === 'account_pending_approval') {
        navigate('/pending-approval', {
          replace: true,
          state: { email: identifier.trim(), reason: 'login' },
        })
        return
      }

      setServerError(apiError.message)
      setErrors(apiError.fields || {})
    } finally {
      submitLock.current = false
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout
      eyebrow="Staff sign in"
      title="Welcome back."
      description="Sign in with your staff account to continue to your role-specific workspace."
    >
      {sessionExpired ? (
        <div className="form-alert form-alert--info" role="status">
          Your session expired or was ended. Please sign in again.
        </div>
      ) : null}

      {serverError ? (
        <div className="form-alert form-alert--error" role="alert">
          {serverError}
        </div>
      ) : null}

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <TextField
          id="login-identifier"
          label="Email or employee ID"
          type="text"
          value={identifier}
          onChange={updateIdentifier}
          autoComplete="username"
          autoFocus
          placeholder="you@hotel.com or EMP-001"
          error={errors.identifier}
        />

        <PasswordField
          id="login-password"
          label="Password"
          value={password}
          onChange={updatePassword}
          autoComplete="current-password"
          placeholder="Enter your password"
          error={errors.password}
        />

        <button
          className="btn btn--primary btn--full"
          type="submit"
          disabled={submitting}
          aria-busy={submitting}
        >
          {submitting ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Signing in…
            </>
          ) : (
            'Sign in'
          )}
        </button>
      </form>

      <p className="auth-switch">
        New staff member? <Link to="/register">Create a staff account</Link>
      </p>

      <div className="guest-note">
        <strong>Guests</strong>
        <span>
          Guest check-in verification and service requests will be introduced in
          a later module.
        </span>
      </div>
    </AuthLayout>
  )
}
