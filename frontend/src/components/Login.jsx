import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Auth.css'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [version, setVersion] = useState(null)

  const { login, verifyMfa, mfaRequired } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    // Load version info
    fetch('/version.json')
      .then(res => res.json())
      .then(data => setVersion(data))
      .catch(err => console.log('Could not load version:', err))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(email, password)

    setLoading(false)

    if (result.success && !result.requiresMfa) {
      navigate('/dashboard')
    } else if (!result.success) {
      setError(result.error)
    }
    // If requiresMfa is true, the form will show MFA input
  }

  const handleMfaSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await verifyMfa(mfaCode)

    setLoading(false)

    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error)
      setMfaCode('')
    }
  }

  if (mfaRequired) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <h1>Two-Factor Authentication</h1>
          <p className="auth-subtitle">Enter your 6-digit code from your authenticator app</p>

          <form onSubmit={handleMfaSubmit}>
            <div className="form-group">
              <label htmlFor="mfaCode">Authentication Code</label>
              <input
                id="mfaCode"
                type="text"
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                maxLength={6}
                pattern="\d{6}"
                required
                autoFocus
                autoComplete="one-time-code"
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" disabled={loading || mfaCode.length !== 6}>
              {loading ? 'Verifying...' : 'Verify'}
            </button>
          </form>

          <div className="auth-footer">
            <p>Lost access to your authenticator? Contact support.</p>
            {version && (
              <p className="version-info">
                {version.fullVersion} • {version.commitDate}
              </p>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>Sign In</h1>
        <p className="auth-subtitle">Sign in to access your Ignition Stack Builder</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-wrapper">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                className="password-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex="-1"
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account? <Link to="/register">Sign up</Link>
          </p>
          {version && (
            <p className="version-info">
              {version.fullVersion} • {version.commitDate}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Login
