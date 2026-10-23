/**
 * Convert FastAPI/axios errors into one predictable shape for forms.
 * Returns { message, code, fields } without logging sensitive request data.
 */
export function getApiError(error) {
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return {
        message: 'The server took too long to respond. Please try again.',
        code: 'timeout',
        fields: {},
      }
    }
    return {
      message:
        'Could not reach the StaySmart server. Check that the backend is running and try again.',
      code: 'network_error',
      fields: {},
    }
  }

  const { status, data } = error.response
  const detail = data?.detail

  if (Array.isArray(detail)) {
    const fields = {}
    const messages = []

    detail.forEach((item) => {
      const fieldParts = Array.isArray(item.loc)
        ? item.loc.filter((part) => part !== 'body' && part !== 'query')
        : []
      const field = fieldParts.length ? String(fieldParts.at(-1)) : ''
      const message = String(item.msg || 'Invalid value.').replace(
        /^Value error, /i,
        '',
      )
      messages.push(message)
      if (field && !fields[field]) {
        fields[field] = message
      }
    })

    return {
      message: messages[0] || 'Please check the form and try again.',
      code: 'validation_error',
      fields,
    }
  }

  if (detail && typeof detail === 'object') {
    return {
      message: detail.message || 'The request could not be completed.',
      code: detail.code || `http_${status}`,
      fields: detail.field ? { [detail.field]: detail.message } : {},
    }
  }

  if (typeof detail === 'string') {
    return {
      message: detail,
      code: `http_${status}`,
      fields: {},
    }
  }

  if (status >= 500) {
    return {
      message: 'The server encountered a problem. Please try again shortly.',
      code: `http_${status}`,
      fields: {},
    }
  }

  return {
    message: 'The request could not be completed. Please try again.',
    code: `http_${status}`,
    fields: {},
  }
}
