import { useRef, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { getApiError } from '../api/errors'
import api from '../api/client'
import { REGISTRATION_ROLES } from '../auth/roles'
import AuthLayout from '../components/AuthLayout'
import {
  PasswordField,
  PasswordRules,
  TextField,
} from '../components/FormField'

const EMPLOYEE_ID_PATTERN = /^[A-Za-z0-9_-]{3,40}$/
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const PHONE_PATTERN = /^\+?[0-9\s().-]{6,29}$/

const EMPTY_FORM = {
  full_name: '',
  employee_id: '',
  email: '',
  phone_number: '',
  password: '',
  confirm_password: '',
}

function validateForm(form) {
  const errors = {}

  if (form.full_name.trim().length < 2) {
    errors.full_name = 'Enter your full name.'
  }
  if (!EMPLOYEE_ID_PATTERN.test(form.employee_id.trim())) {
    errors.employee_id =
      'Use 3-40 letters, numbers, hyphens, or underscores.'
  }
  if (!EMAIL_PATTERN.test(form.email.trim())) {
    errors.email = 'Enter a valid email address.'
  }

  const phone = form.phone_number.trim()
  const phoneDigits = (phone.match(/\d/g) || []).length
  if (!PHONE_PATTERN.test(phone) || phoneDigits < 7 || phoneDigits > 20) {
    errors.phone_number = 'Enter a valid phone number with 7-20 digits.'
  }

  if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters.'
  } else if (!/[A-Z]/.test(form.password)) {
    errors.password = 'Password must include an uppercase letter.'
  } else if (!/[a-z]/.test(form.password)) {
    errors.password = 'Password must include a lowercase letter.'
  } else if (!/[0-9]/.test(form.password)) {
    errors.password = 'Password must include a number.'
  }

  if (!form.confirm_password) {
    errors.confirm_password = 'Confirm your password.'
  } else if (form.password !== form.confirm_password) {
    errors.confirm_password = 'Passwords do not match.'
  }

  return errors
}

export default function RegisterPage({ registrationKey }) {
  const config = REGISTRATION_ROLES[registrationKey]
  const navigate = useNavigate()

  const [form, setForm] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  const [serverError, setServerError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const submitLock = useRef(false)

  if (!config) {
    return <Navigate to="/register" replace />
  }

  const updateField = (field) => (event) => {
    const value = event.target.value
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (submitLock.current) return

    setServerError('')
    const nextErrors = validateForm(form)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    setSubmitting(true)
    submitLock.current = true
    try {
      await api.post(config.endpoint, {
        full_name: form.full_name.trim(),
        employee_id: form.employee_id.trim(),
        email: form.email.trim(),
        phone_number: form.phone_number.trim(),
        password: form.password,
        confirm_password: form.confirm_password,
      })

      navigate('/pending-approval', {
        replace: true,
        state: {
          email: form.email.trim(),
          employeeId: form.employee_id.trim().toUpperCase(),
          roleLabel: config.label,
          fromRegistration: true,
        },
      })
    } catch (error) {
      const apiError = getApiError(error)
      setServerError(apiError.message)
      setErrors(apiError.fields || {})
    } finally {
      submitLock.current = false
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout
      wide
      eyebrow={config.eyebrow}
      title={`${config.label} registration.`}
      description={config.summary}
    >
      <div className="approval-callout approval-callout--compact">
        <strong>Approval required before sign-in</strong>
        <p>
          Your details are submitted for administrator review. Do not share your
          password with anyone.
        </p>
      </div>

      {serverError ? (
        <div className="form-alert form-alert--error" role="alert">
          {serverError}
        </div>
      ) : null}

      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <fieldset className="form-section">
          <legend>Personal details</legend>

          <div className="form-grid">
            <div className="field--full">
              <TextField
                id="register-full-name"
                label="Full name"
                value={form.full_name}
                onChange={updateField('full_name')}
                autoComplete="name"
                maxLength={120}
                placeholder="e.g. Priya Sharma"
                error={errors.full_name}
              />
            </div>

            <TextField
              id="register-employee-id"
              label="Employee ID"
              value={form.employee_id}
              onChange={updateField('employee_id')}
              autoComplete="off"
              maxLength={40}
              placeholder="e.g. REC-1042"
              hint="Letters, numbers, hyphens, or underscores."
              error={errors.employee_id}
            />

            <TextField
              id="register-email"
              label="Email address"
              type="email"
              value={form.email}
              onChange={updateField('email')}
              autoComplete="email"
              maxLength={255}
              placeholder="you@hotel.com"
              error={errors.email}
            />

            <div className="field--full">
              <TextField
                id="register-phone"
                label="Phone number"
                type="tel"
                inputMode="tel"
                value={form.phone_number}
                onChange={updateField('phone_number')}
                autoComplete="tel"
                maxLength={30}
                placeholder="+91 98765 43210"
                hint="Include your country code if relevant."
                error={errors.phone_number}
              />
            </div>
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Account security</legend>

          <div className="form-grid">
            <PasswordField
              id="register-password"
              label="Password"
              value={form.password}
              onChange={updateField('password')}
              autoComplete="new-password"
              placeholder="Create a strong password"
              error={errors.password}
            />

            <PasswordField
              id="register-confirm-password"
              label="Confirm password"
              value={form.confirm_password}
              onChange={updateField('confirm_password')}
              autoComplete="new-password"
              placeholder="Re-enter your password"
              error={errors.confirm_password}
            />

            <div className="field--full">
              <PasswordRules password={form.password} />
            </div>
          </div>
        </fieldset>

        <button
          className="btn btn--primary btn--full"
          type="submit"
          disabled={submitting}
          aria-busy={submitting}
        >
          {submitting ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Submitting registration…
            </>
          ) : (
            'Submit registration for approval'
          )}
        </button>
      </form>

      <p className="auth-switch auth-switch--spread">
        <Link to="/register">Choose a different role</Link>
        <span aria-hidden="true">·</span>
        <Link to="/login">Back to sign in</Link>
      </p>
    </AuthLayout>
  )
}
