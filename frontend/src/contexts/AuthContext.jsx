import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [mfaRequired, setMfaRequired] = useState(false)
  const [tempToken, setTempToken] = useState(null)

  const API_URL = import.meta.env.VITE_API_URL || '/api'

  // Configure axios to include auth token in all requests
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/me`)
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch current user:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const register = async (email, password, fullName) => {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        password,
        full_name: fullName
      })
      return { success: true, user: response.data }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      }
    }
  }

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      })

      const { access_token, refresh_token, requires_mfa } = response.data

      if (requires_mfa) {
        setMfaRequired(true)
        setTempToken(access_token)
        return { success: true, requiresMfa: true }
      }

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      // Fetch user info
      await fetchCurrentUser()

      return { success: true, requiresMfa: false }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  const verifyMfa = async (code) => {
    try {
      const response = await axios.post(
        `${API_URL}/auth/mfa/verify`,
        { code },
        {
          headers: {
            Authorization: `Bearer ${tempToken}`
          }
        }
      )

      const { access_token, refresh_token } = response.data

      // Store tokens
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      // Clear MFA state
      setMfaRequired(false)
      setTempToken(null)

      // Fetch user info
      await fetchCurrentUser()

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'MFA verification failed'
      }
    }
  }

  const logout = async () => {
    try {
      await axios.post(`${API_URL}/auth/logout`)
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local state regardless of API call success
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      delete axios.defaults.headers.common['Authorization']
      setUser(null)
      setMfaRequired(false)
      setTempToken(null)
    }
  }

  const refreshAccessToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        logout()
        return false
      }

      const response = await axios.post(`${API_URL}/auth/refresh`, {
        refresh_token: refreshToken
      })

      const { access_token } = response.data
      localStorage.setItem('access_token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      logout()
      return false
    }
  }

  // Setup axios interceptor for token refresh on 401
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          const refreshed = await refreshAccessToken()

          if (refreshed) {
            return axios(originalRequest)
          }
        }

        return Promise.reject(error)
      }
    )

    return () => {
      axios.interceptors.response.eject(interceptor)
    }
  }, [])

  const value = {
    user,
    loading,
    mfaRequired,
    register,
    login,
    verifyMfa,
    logout,
    isAuthenticated: !!user
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
