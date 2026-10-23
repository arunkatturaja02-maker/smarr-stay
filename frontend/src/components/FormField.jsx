import { useState } from 'react'

export function FormField({ id, label, error, hint, required = true, children }) {
  return (
    <div className={`field${error ? ' field--error' : ''}`}>
      <label htmlFor={id}>
        {label}
        {required ? (
          <span className="required-mark" aria-hidden="true">
            *
          </span>
        ) : null}
      </label>
      {children}
      {error ? (
        <p className="field-error" id={`${id}-error`} role="alert">
          {error}
        </p>
      ) : hint ? (
        <p className="field-hint" id={`${id}-hint`}>
          {hint}
        </p>
      ) : null}
    </div>
  )
}

export function TextField({
  id,
  label,
  error,
  hint,
  required = true,
  type = 'text',
  ...inputProps
}) {
  const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined

  return (
    <FormField
      id={id}
      label={label}
      error={error}
      hint={hint}
      required={required}
    >
      <input
        className="text-input"
        id={id}
        type={type}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={describedBy}
        required={required}
        {...inputProps}
      />
    </FormField>
  )
}

export function PasswordField({
  id,
  label,
  error,
  hint,
  autoComplete = 'current-password',
  ...inputProps
}) {
  const [visible, setVisible] = useState(false)
  const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined

  return (
    <FormField id={id} label={label} error={error} hint={hint}>
      <div className="password-wrap">
        <input
          className="text-input text-input--password"
          id={id}
          type={visible ? 'text' : 'password'}
          autoComplete={autoComplete}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={describedBy}
          required
          {...inputProps}
        />
        <button
          className="password-toggle"
          type="button"
          onClick={() => setVisible((current) => !current)}
          aria-label={visible ? 'Hide password' : 'Show password'}
          aria-pressed={visible}
        >
          {visible ? 'Hide' : 'Show'}
        </button>
      </div>
    </FormField>
  )
}

export function PasswordRules({ password }) {
  const rules = [
    { label: 'At least 8 characters', met: password.length >= 8 },
    {
      label: 'One uppercase letter',
      met: /[A-Z]/.test(password),
    },
    {
      label: 'One lowercase letter',
      met: /[a-z]/.test(password),
    },
    { label: 'One number', met: /[0-9]/.test(password) },
  ]

  return (
    <ul className="password-rules" aria-label="Password requirements">
      {rules.map((rule) => (
        <li className={rule.met ? 'is-met' : ''} key={rule.label}>
          <span aria-hidden="true">{rule.met ? '✓' : '○'}</span>
          {rule.label}
        </li>
      ))}
    </ul>
  )
}
