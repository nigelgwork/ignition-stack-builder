import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import App from '../App'
import './Dashboard.css'

function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [darkMode, setDarkMode] = useState(true)

  useEffect(() => {
    // Set dark mode by default
    const savedTheme = localStorage.getItem('theme') || 'dark'
    const isDark = savedTheme === 'dark'
    setDarkMode(isDark)
    if (isDark) {
      document.documentElement.setAttribute('data-theme', 'dark')
    }
  }, [])

  const toggleDarkMode = () => {
    const newMode = !darkMode
    setDarkMode(newMode)
    if (newMode) {
      document.documentElement.setAttribute('data-theme', 'dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.removeAttribute('data-theme')
      localStorage.setItem('theme', 'light')
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="dashboard-wrapper">
      <nav className="dashboard-nav">
        <div className="nav-left">
          <h2>Ignition Stack Builder</h2>
          <span className="user-badge">Welcome, {user?.full_name || user?.email}</span>
        </div>

        <div className="nav-right">
          <div className="theme-toggle">
            <span className="theme-toggle-label">☀️</span>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={darkMode}
                onChange={toggleDarkMode}
              />
              <span className="toggle-slider round"></span>
            </label>
            <span className="theme-toggle-label">🌙</span>
          </div>

          <button className="nav-btn" onClick={() => navigate('/my-stacks')}>
            My Stacks
          </button>
          <button className="nav-btn" onClick={() => navigate('/settings')}>
            Settings
          </button>

          <div className="user-menu-container">
            <button
              className="user-menu-btn"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </button>

            {showUserMenu && (
              <div className="user-menu-dropdown">
                <div className="user-menu-header">
                  <div className="user-email">{user?.email}</div>
                  {user?.mfa_enabled && (
                    <span className="mfa-badge">MFA Enabled</span>
                  )}
                </div>
                <button onClick={() => navigate('/mfa-setup')}>
                  {user?.mfa_enabled ? 'Manage MFA' : 'Enable MFA'}
                </button>
                <button onClick={handleLogout} className="logout-btn">
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <App />
      </div>
    </div>
  )
}

export default Dashboard
