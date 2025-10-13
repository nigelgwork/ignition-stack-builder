import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Auth.css'

function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const { register } = useAuth()
  const navigate = useNavigate()

  const validatePassword = (pwd) => {
    const errors = []

    if (pwd.length < 8) {
      errors.push('at least 8 characters')
    }
    if (!/[A-Z]/.test(pwd)) {
      errors.push('one uppercase letter')
    }
    if (!/[a-z]/.test(pwd)) {
      errors.push('one lowercase letter')
    }
    if (!/\d/.test(pwd)) {
      errors.push('one digit')
    }
    if (!/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(pwd)) {
      errors.push('one special character')
    }

    return errors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    // Validate password strength
    const passwordErrors = validatePassword(password)
    if (passwordErrors.length > 0) {
      setError(`Password must contain ${passwordErrors.join(', ')}`)
      return
    }

    setLoading(true)

    const result = await register(email, password, fullName)

    setLoading(false)

    if (result.success) {
      setSuccess(true)
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } else {
      setError(result.error)
    }
  }

  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <h1>Registration Successful!</h1>
          <div className="success-message">
            Your account has been created successfully. Redirecting to login...
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>Create Account</h1>
        <p className="auth-subtitle">Sign up for Ignition Stack Builder</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="fullName">Full Name (Optional)</label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="John Doe"
              autoComplete="name"
            />
          </div>

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
                placeholder="Enter password"
                required
                autoComplete="new-password"
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
            <div className="password-requirements">
              Password must contain:
              <ul>
                <li className={password.length >= 8 ? 'met' : ''}>At least 8 characters</li>
                <li className={/[A-Z]/.test(password) ? 'met' : ''}>One uppercase letter</li>
                <li className={/[a-z]/.test(password) ? 'met' : ''}>One lowercase letter</li>
                <li className={/\d/.test(password) ? 'met' : ''}>One digit</li>
                <li className={/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password) ? 'met' : ''}>
                  One special character
                </li>
              </ul>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <div className="password-input-wrapper">
              <input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                className="password-input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter password"
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex="-1"
              >
                {showConfirmPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Register
