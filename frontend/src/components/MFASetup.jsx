import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import './MFASetup.css'

const API_URL = import.meta.env.VITE_API_URL || '/api'

function MFASetup() {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [step, setStep] = useState('initial') // initial, setup, verify, disable
  const [qrCode, setQrCode] = useState('')
  const [secret, setSecret] = useState('')
  const [backupCodes, setBackupCodes] = useState([])
  const [verificationCode, setVerificationCode] = useState('')
  const [disableCode, setDisableCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const startMFASetup = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await axios.post(`${API_URL}/auth/mfa/setup`)
      setQrCode(response.data.qr_code)
      setSecret(response.data.secret)
      setBackupCodes(response.data.backup_codes)
      setStep('setup')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to setup MFA')
    } finally {
      setLoading(false)
    }
  }

  const enableMFA = async () => {
    setLoading(true)
    setError('')

    try {
      await axios.post(`${API_URL}/auth/mfa/enable`, {
        code: verificationCode
      })
      setSuccess('MFA enabled successfully!')
      setTimeout(() => {
        navigate('/dashboard')
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid verification code')
      setVerificationCode('')
    } finally {
      setLoading(false)
    }
  }

  const disableMFA = async () => {
    setLoading(true)
    setError('')

    try {
      await axios.post(`${API_URL}/auth/mfa/disable`, {
        code: disableCode
      })
      setSuccess('MFA disabled successfully!')
      setTimeout(() => {
        navigate('/dashboard')
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid MFA code')
      setDisableCode('')
    } finally {
      setLoading(false)
    }
  }

  const downloadBackupCodes = () => {
    const text = backupCodes.join('\n')
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'mfa-backup-codes.txt'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  if (success) {
    return (
      <div className="page-container">
        <div className="mfa-box">
          <div className="success-message">{success}</div>
        </div>
      </div>
    )
  }

  if (user?.mfa_enabled && step === 'initial') {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>Multi-Factor Authentication</h1>
        </div>

        <div className="mfa-box">
          <div className="mfa-status enabled">
            <span className="status-icon">✓</span>
            <div>
              <h3>MFA is Enabled</h3>
              <p>Your account is protected with two-factor authentication.</p>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            className="danger-btn"
            onClick={() => setStep('disable')}
          >
            Disable MFA
          </button>
        </div>
      </div>
    )
  }

  if (step === 'disable') {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>Disable MFA</h1>
        </div>

        <div className="mfa-box">
          <p>Enter your current MFA code to disable two-factor authentication.</p>

          <div className="form-group">
            <label>Authentication Code</label>
            <input
              type="text"
              value={disableCode}
              onChange={(e) => setDisableCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="000000"
              maxLength={6}
              autoFocus
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="button-group">
            <button
              className="danger-btn"
              onClick={disableMFA}
              disabled={loading || disableCode.length !== 6}
            >
              {loading ? 'Disabling...' : 'Disable MFA'}
            </button>
            <button className="secondary-btn" onClick={() => setStep('initial')}>
              Cancel
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (step === 'setup') {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1>Enable MFA</h1>
        </div>

        <div className="mfa-box">
          <h2>Step 1: Scan QR Code</h2>
          <p>Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)</p>

          <div className="qr-code-container">
            <img src={qrCode} alt="MFA QR Code" />
          </div>

          <div className="secret-manual">
            <p>Or enter this code manually:</p>
            <code>{secret}</code>
          </div>

          <h2>Step 2: Save Backup Codes</h2>
          <p className="warning-text">
            Save these backup codes in a secure place. You can use them to access your account if you
            lose your authenticator device.
          </p>

          <div className="backup-codes">
            {backupCodes.map((code, idx) => (
              <code key={idx}>{code}</code>
            ))}
          </div>

          <button className="download-btn" onClick={downloadBackupCodes}>
            Download Backup Codes
          </button>

          <h2>Step 3: Verify</h2>
          <p>Enter the 6-digit code from your authenticator app to verify setup.</p>

          <div className="form-group">
            <label>Verification Code</label>
            <input
              type="text"
              value={verificationCode}
              onChange={(e) =>
                setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))
              }
              placeholder="000000"
              maxLength={6}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            className="primary-btn"
            onClick={enableMFA}
            disabled={loading || verificationCode.length !== 6}
          >
            {loading ? 'Verifying...' : 'Enable MFA'}
          </button>
        </div>
      </div>
    )
  }

  // Initial state - MFA not enabled
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Multi-Factor Authentication</h1>
      </div>

      <div className="mfa-box">
        <div className="mfa-status disabled">
          <span className="status-icon">⚠</span>
          <div>
            <h3>MFA is Disabled</h3>
            <p>
              Add an extra layer of security to your account by enabling two-factor
              authentication.
            </p>
          </div>
        </div>

        <div className="mfa-benefits">
          <h3>Why enable MFA?</h3>
          <ul>
            <li>Protect your account from unauthorized access</li>
            <li>Secure your sensitive stack configurations</li>
            <li>Meet security compliance requirements</li>
          </ul>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button className="primary-btn" onClick={startMFASetup} disabled={loading}>
          {loading ? 'Setting up...' : 'Enable MFA'}
        </button>
      </div>
    </div>
  )
}

export default MFASetup
