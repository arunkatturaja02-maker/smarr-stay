import axios from 'axios'

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/$/, '')

const api = axios.create({
  baseURL: API_BASE_URL,
  // Required so the browser sends/receives the HttpOnly authentication cookie.
  withCredentials: true,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const requestUrl = error.config?.url || ''
    const isAuthRequest =
      requestUrl.includes('/api/auth/login') ||
      requestUrl.includes('/api/auth/me') ||
      requestUrl.includes('/api/auth/logout')

    // Future protected API calls get a consistent "session expired" flow.
    // Login and the initial /me check handle their own 401 responses.
    if (status === 401 && !isAuthRequest) {
      window.dispatchEvent(new Event('staysmart:session-expired'))
    }

    return Promise.reject(error)
  },
)

export default api
