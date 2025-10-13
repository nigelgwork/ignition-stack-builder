import { useState, useEffect } from 'react'
import axios from 'axios'
import './Settings.css'

const API_URL = import.meta.env.VITE_API_URL || '/api'

function Settings() {
  const [settings, setSettings] = useState({
    theme: 'dark',
    timezone: 'UTC',
    notifications_enabled: true,
    preferences: {}
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API_URL}/settings/`)
      setSettings(response.data)
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load settings' })
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage({ type: '', text: '' })

    try {
      await axios.put(`${API_URL}/settings/`, settings)
      setMessage({ type: 'success', text: 'Settings saved successfully!' })

      // Apply theme change
      if (settings.theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark')
      } else {
        document.documentElement.removeAttribute('data-theme')
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save settings' })
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="page-container loading">Loading settings...</div>
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Settings</h1>
      </div>

      <div className="settings-content">
        <div className="settings-section">
          <h2>Appearance</h2>

          <div className="setting-item">
            <label>Theme</label>
            <select
              value={settings.theme}
              onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>
        </div>

        <div className="settings-section">
          <h2>Regional</h2>

          <div className="setting-item">
            <label>Timezone</label>
            <select
              value={settings.timezone}
              onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
            >
              <option value="UTC">UTC</option>
              <option value="America/New_York">America/New_York</option>
              <option value="America/Chicago">America/Chicago</option>
              <option value="America/Los_Angeles">America/Los_Angeles</option>
              <option value="Europe/London">Europe/London</option>
              <option value="Europe/Paris">Europe/Paris</option>
              <option value="Asia/Tokyo">Asia/Tokyo</option>
              <option value="Asia/Singapore">Asia/Singapore</option>
              <option value="Australia/Sydney">Australia/Sydney</option>
              <option value="Australia/Melbourne">Australia/Melbourne</option>
            </select>
          </div>
        </div>

        <div className="settings-section">
          <h2>Notifications</h2>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.notifications_enabled}
                onChange={(e) =>
                  setSettings({ ...settings, notifications_enabled: e.target.checked })
                }
              />
              Enable notifications
            </label>
          </div>
        </div>

        {message.text && (
          <div className={`message ${message.type}`}>{message.text}</div>
        )}

        <div className="settings-actions">
          <button className="save-btn" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Settings
