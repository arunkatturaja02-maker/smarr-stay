import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'
import api from '../api/client'
import { AuthContext } from './context'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [status, setStatus] = useState('loading')
  const [sessionExpired, setSessionExpired] = useState(false)

  // Authentication state is restored from the HttpOnly cookie. No JWT is
  // stored in localStorage or sessionStorage.
  useEffect(() => {
    let cancelled = false

    api
      .get('/api/auth/me')
      .then(({ data }) => {
        if (!cancelled) {
          setUser(data)
          setStatus('ready')
        }
      })
      .catch(() => {
        if (!cancelled) {
          setUser(null)
          setStatus('ready')
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    const handleExpired = () => {
      setUser(null)
      setStatus('ready')
      setSessionExpired(true)
    }

    window.addEventListener('staysmart:session-expired', handleExpired)
    return () =>
      window.removeEventListener('staysmart:session-expired', handleExpired)
  }, [])

  const login = useCallback(async (identifier, password) => {
    const { data } = await api.post('/api/auth/login', { identifier, password })
    setUser(data.user)
    setStatus('ready')
    setSessionExpired(false)
    return data.user
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.post('/api/auth/logout')
    } catch {
      // Local state is cleared even if the network request fails.
    } finally {
      setUser(null)
      setStatus('ready')
      setSessionExpired(false)
    }
  }, [])

  const clearSessionExpired = useCallback(() => {
    setSessionExpired(false)
  }, [])

  const value = useMemo(
    () => ({
      user,
      status,
      sessionExpired,
      login,
      logout,
      clearSessionExpired,
    }),
    [user, status, sessionExpired, login, logout, clearSessionExpired],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
