import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import { downloadEncryptedConfig, importEncryptedConfig, validateConfigStructure } from './crypto'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [darkMode, setDarkMode] = useState(true) // Default to dark mode
  const [catalog, setCatalog] = useState({ applications: [], categories: [] })
  const [selectedInstances, setSelectedInstances] = useState([])
  const [instanceCounter, setInstanceCounter] = useState({})
  const [generatedConfig, setGeneratedConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [globalSettings, setGlobalSettings] = useState({
    timezone: 'Australia/Adelaide',
    restart_policy: 'unless-stopped',
    ntfy_enabled: false,
    ntfy_server: 'https://ntfy.sh',
    ntfy_topic: ''
  })
  const [passwordVisibility, setPasswordVisibility] = useState({})
  const [integrationSettings, setIntegrationSettings] = useState({
    reverse_proxy: {
      base_domain: 'localhost',
      enable_https: false,
      letsencrypt_email: ''
    },
    mqtt: {
      enable_tls: false,
      username: '',
      password: '',
      tls_port: 8883
    },
    oauth: {
      realm_name: 'iiot',
      auto_configure_services: true,
      realm_users: []
    },
    database: {
      auto_register: true
    },
    email: {
      from_address: 'noreply@iiot.local',
      auto_configure_services: true
    }
  })
  const [integrationResults, setIntegrationResults] = useState(null)
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [showLoadDialog, setShowLoadDialog] = useState(false)
  const [savePassword, setSavePassword] = useState('')
  const [loadPassword, setLoadPassword] = useState('')
  const [loadFile, setLoadFile] = useState(null)
  const [saveLoadError, setSaveLoadError] = useState('')
  const [saveLoadSuccess, setSaveLoadSuccess] = useState('')

  useEffect(() => {
    // Set dark mode by default
    const savedTheme = localStorage.getItem('theme') || 'dark'
    const isDark = savedTheme === 'dark'
    setDarkMode(isDark)
    if (isDark) {
      document.documentElement.setAttribute('data-theme', 'dark')
    }

    // Load catalog
    fetchCatalog()
  }, [])

  // Detect integrations whenever instances change
  useEffect(() => {
    if (selectedInstances.length > 0) {
      detectIntegrations()
    } else {
      setIntegrationResults(null)
    }
  }, [selectedInstances])

  const detectIntegrations = async () => {
    try {
      const response = await axios.post(`${API_URL}/detect-integrations`, {
        instances: selectedInstances,
        global_settings: globalSettings
      })
      setIntegrationResults(response.data)
    } catch (error) {
      console.error('Error detecting integrations:', error)
    }
  }

  const fetchCatalog = async () => {
    try {
      const response = await axios.get(`${API_URL}/catalog`)
      setCatalog(response.data)
    } catch (error) {
      console.error('Error fetching catalog:', error)
    } finally {
      setLoading(false)
    }
  }

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

  const isServiceDisabled = (appId) => {
    // Define mutual exclusivity groups
    const mutualExclusivityGroups = {
      reverse_proxy: ['traefik', 'nginx-proxy-manager']
    }

    for (const [groupName, services] of Object.entries(mutualExclusivityGroups)) {
      if (services.includes(appId)) {
        // Check if any other service from this group is already selected
        const conflictingService = selectedInstances.find(inst =>
          services.includes(inst.app_id) && inst.app_id !== appId
        )

        if (conflictingService) {
          return {
            disabled: true,
            reason: `Only one reverse proxy allowed. Remove ${conflictingService.app_id} first.`
          }
        }
      }
    }

    return { disabled: false, reason: '' }
  }

  const addInstance = (app) => {
    // Check if service is disabled
    const disabledStatus = isServiceDisabled(app.id)
    if (disabledStatus.disabled) {
      return // Silently prevent adding, UI shows it's disabled
    }

    const count = (instanceCounter[app.id] || 0) + 1

    // Default instance name logic:
    // - First instance: use service type name (e.g., "keycloak", "postgres", "ignition")
    // - Additional instances: append number (e.g., "ignition-2", "postgres-2")
    const instanceName = count === 1 ? app.id : `${app.id}-${count}`

    const newInstance = {
      app_id: app.id,
      instance_name: instanceName,
      config: {},
      instanceId: Date.now() + Math.random() // Unique ID for React keys
    }

    // Set default config values
    if (app.configurable_options) {
      Object.entries(app.configurable_options).forEach(([key, option]) => {
        newInstance.config[key] = option.default
      })
    }

    setSelectedInstances([...selectedInstances, newInstance])
    setInstanceCounter({ ...instanceCounter, [app.id]: count })
  }

  const removeInstance = (instanceId) => {
    const newInstances = selectedInstances.filter(inst => inst.instanceId !== instanceId)
    setSelectedInstances(newInstances)
  }

  const updateInstanceConfig = (instanceId, key, value) => {
    let newInstances = selectedInstances.map(inst => {
      if (inst.instanceId === instanceId) {
        return {
          ...inst,
          config: { ...inst.config, [key]: value }
        }
      }
      return inst
    })

    setSelectedInstances(newInstances)
  }

  const handleFileUpload = async (instanceId, files) => {
    if (!files || files.length === 0) return

    const uploadedModules = []

    for (const file of files) {
      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await axios.post(`${API_URL}/upload-module`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        uploadedModules.push(response.data)
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error)
        alert(`Failed to upload ${file.name}: ${error.response?.data?.detail || error.message}`)
      }
    }

    // Update instance config with uploaded modules
    const newInstances = selectedInstances.map(inst => {
      if (inst.instanceId === instanceId) {
        const existingModules = inst.config.uploaded_modules || []
        return {
          ...inst,
          config: {
            ...inst.config,
            uploaded_modules: [...existingModules, ...uploadedModules]
          }
        }
      }
      return inst
    })
    setSelectedInstances(newInstances)
  }

  // Save configuration to encrypted file
  const handleSaveConfig = async () => {
    if (!savePassword || savePassword.length < 8) {
      setSaveLoadError('Password must be at least 8 characters')
      return
    }

    setSaveLoadError('')
    setSaveLoadSuccess('')

    try {
      const config = {
        instances: selectedInstances,
        global_settings: globalSettings,
        integration_settings: integrationSettings
      }

      const timestamp = new Date().toISOString().split('T')[0]
      const filename = `stack-config-${timestamp}.iiotstack`

      await downloadEncryptedConfig(config, savePassword, filename)

      setSaveLoadSuccess(`Configuration saved to ${filename}`)
      setTimeout(() => {
        setShowSaveDialog(false)
        setSavePassword('')
        setSaveLoadSuccess('')
      }, 2000)
    } catch (error) {
      setSaveLoadError(`Failed to save: ${error.message}`)
    }
  }

  // Load configuration from encrypted file
  const handleLoadConfig = async () => {
    if (!loadFile) {
      setSaveLoadError('Please select a file')
      return
    }

    if (!loadPassword) {
      setSaveLoadError('Please enter password')
      return
    }

    setSaveLoadError('')
    setSaveLoadSuccess('')

    try {
      const config = await importEncryptedConfig(loadFile, loadPassword)

      // Validate structure
      validateConfigStructure(config)

      // Validate with backend
      const response = await axios.post(`${API_URL}/validate-config`, config)

      if (response.data.valid) {
        // Apply configuration
        setSelectedInstances(config.instances || [])
        setGlobalSettings(config.global_settings || globalSettings)
        setIntegrationSettings(config.integration_settings || integrationSettings)

        setSaveLoadSuccess('Configuration loaded successfully!')
        setTimeout(() => {
          setShowLoadDialog(false)
          setLoadPassword('')
          setLoadFile(null)
          setSaveLoadSuccess('')
        }, 2000)
      }
    } catch (error) {
      setSaveLoadError(`Failed to load: ${error.message}`)
    }
  }

  const removeUploadedModule = (instanceId, filename) => {
    const newInstances = selectedInstances.map(inst => {
      if (inst.instanceId === instanceId) {
        const modules = inst.config.uploaded_modules || []
        return {
          ...inst,
          config: {
            ...inst.config,
            uploaded_modules: modules.filter(m => m.filename !== filename)
          }
        }
      }
      return inst
    })
    setSelectedInstances(newInstances)
  }

  const toggleSingleApp = (app) => {
    const exists = selectedInstances.find(inst => inst.app_id === app.id)
    if (exists) {
      setSelectedInstances(selectedInstances.filter(inst => inst.app_id !== app.id))
    } else {
      addInstance(app)
    }
  }

  const isAppSelected = (appId) => {
    return selectedInstances.some(inst => inst.app_id === appId)
  }

  const getInstancesForApp = (appId) => {
    return selectedInstances.filter(inst => inst.app_id === appId)
  }

  // Helper to determine if a service should show integration settings
  const getIntegrationSettingsFor = (appId) => {
    if (!integrationResults || !integrationResults.integrations) return null

    const integrations = integrationResults.integrations

    // MQTT Broker settings (EMQX, Mosquitto)
    if (['emqx', 'mosquitto'].includes(appId) && integrations.mqtt_broker) {
      if (integrations.mqtt_broker.providers.some(p => p.service_id === appId)) {
        return {
          type: 'mqtt_broker',
          data: integrations.mqtt_broker
        }
      }
    }

    // Reverse Proxy settings (Traefik, NPM)
    if (['traefik', 'nginx-proxy-manager'].includes(appId) && integrations.reverse_proxy) {
      if (integrations.reverse_proxy.provider === appId) {
        return {
          type: 'reverse_proxy',
          data: integrations.reverse_proxy
        }
      }
    }

    // OAuth Provider settings (Keycloak, Authentik, Authelia)
    if (['keycloak', 'authentik', 'authelia'].includes(appId) && integrations.oauth_provider) {
      if (integrations.oauth_provider.providers.includes(appId)) {
        return {
          type: 'oauth_provider',
          data: integrations.oauth_provider
        }
      }
    }

    // Email Testing settings (MailHog)
    if (appId === 'mailhog' && integrations.email_testing) {
      if (integrations.email_testing.provider === appId) {
        return {
          type: 'email_testing',
          data: integrations.email_testing
        }
      }
    }

    return null
  }

  const generateStack = async () => {
    try {
      const response = await axios.post(`${API_URL}/generate`, {
        instances: selectedInstances,
        integrations: [],
        global_settings: globalSettings,
        integration_settings: integrationSettings
      })
      setGeneratedConfig(response.data)
    } catch (error) {
      console.error('Error generating stack:', error)
      alert('Error generating stack configuration')
    }
  }

  const downloadStack = async () => {
    try {
      const response = await axios.post(`${API_URL}/download`, {
        instances: selectedInstances,
        integrations: [],
        global_settings: globalSettings,
        integration_settings: integrationSettings
      }, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'iiot-stack.zip')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error downloading stack:', error)
      alert('Error downloading stack')
    }
  }

  const downloadLinuxInstaller = async () => {
    try {
      const response = await axios.get(`${API_URL}/download/docker-installer/linux`, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'install-docker-linux.sh')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error downloading Linux installer:', error)
      alert('Error downloading Linux installer')
    }
  }

  const downloadWindowsInstaller = async () => {
    try {
      const response = await axios.get(`${API_URL}/download/docker-installer/windows`, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'install-docker-windows.ps1')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error downloading Windows installer:', error)
      alert('Error downloading Windows installer')
    }
  }

  const downloadOfflineBundle = async () => {
    try {
      const response = await axios.post(`${API_URL}/generate-offline-bundle`, {
        instances: selectedInstances,
        integrations: [],
        global_settings: globalSettings,
        integration_settings: integrationSettings
      }, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'iiot-stack-offline-bundle.zip')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Error downloading offline bundle:', error)
      alert('Error downloading offline bundle')
    }
  }

  const getAppsByCategory = (category) => {
    return catalog.applications.filter(app => app.category === category && !app.managed_by_parent && !app.hidden)
  }

  const getAvailableDatabases = () => {
    return selectedInstances
      .filter(inst => ['postgres', 'mariadb', 'mssql'].includes(inst.app_id))
      .map(inst => ({
        value: inst.instance_name,
        label: `${catalog.applications.find(a => a.id === inst.app_id)?.name} (${inst.config.name || inst.instance_name})`,
        instance: inst
      }))
  }

  const getAvailableMqttBrokers = () => {
    return selectedInstances
      .filter(inst => ['emqx', 'mosquitto'].includes(inst.app_id))
      .map(inst => ({
        value: inst.instance_name,
        label: `${catalog.applications.find(a => a.id === inst.app_id)?.name}`,
        instance: inst
      }))
  }

  const renderConfigInput = (instance, key, option, app) => {
    const value = instance.config[key]

    // Check version constraint for version-specific fields
    if (option.version_constraint) {
      const selectedVersion = instance.config.version || app.default_version || 'latest'

      // Determine if this is 8.1 or 8.3
      let is83 = false
      if (selectedVersion === 'latest' || selectedVersion.startsWith('8.3') || selectedVersion.startsWith('8.4') || selectedVersion.startsWith('9')) {
        is83 = true
      }

      // Show the appropriate module set
      if (is83 && option.version_constraint !== '8.3') {
        return null
      } else if (!is83 && option.version_constraint !== '8.1') {
        return null
      }
    }

    switch (option.type) {
      case 'select':
        const options = option.options || app.available_versions || []
        return (
          <select
            value={value !== undefined ? value : option.default}
            onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.value)}
          >
            {options.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        )

      case 'multiselect':
        const selectedValues = value || option.default || []
        const availableOptions = option.options || []
        return (
          <div className="multiselect-container">
            {availableOptions.map(opt => {
              // Handle both string options and object options with value/label/description
              const optValue = typeof opt === 'object' ? opt.value : opt
              const optLabel = typeof opt === 'object' ? opt.label : opt
              const optDescription = typeof opt === 'object' ? opt.description : null

              return (
                <label
                  key={optValue}
                  className="multiselect-option"
                  title={optDescription || ''}
                >
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(optValue)}
                    onChange={(e) => {
                      const newValues = e.target.checked
                        ? [...selectedValues, optValue]
                        : selectedValues.filter(v => v !== optValue)
                      updateInstanceConfig(instance.instanceId, key, newValues)
                    }}
                  />
                  <span>{optLabel}</span>
                </label>
              )
            })}
          </div>
        )

      case 'textarea':
        // Special handling for 3rd party modules - use file upload instead
        if (key === 'third_party_modules') {
          const uploadedModules = instance.config.uploaded_modules || []
          return (
            <div className="file-upload-container">
              <input
                type="file"
                accept=".modl"
                multiple
                onChange={(e) => handleFileUpload(instance.instanceId, Array.from(e.target.files))}
                className="file-input"
              />
              <div className="uploaded-files-list">
                {uploadedModules.map((module, idx) => (
                  <div key={idx} className="uploaded-file-item">
                    <span className="file-name">{module.filename}</span>
                    <span className="file-size">({(module.size / 1024).toFixed(1)} KB)</span>
                    <button
                      className="remove-file-btn"
                      onClick={() => removeUploadedModule(instance.instanceId, module.filename)}
                      type="button"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
              <p className="upload-hint">Upload .modl files for 3rd party modules</p>
            </div>
          )
        }
        return (
          <textarea
            value={value !== undefined ? value : (option.default || '')}
            onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.value)}
            placeholder={option.placeholder || ''}
            rows={4}
          />
        )

      case 'checkbox':
        return (
          <input
            type="checkbox"
            checked={value !== undefined ? value : option.default}
            onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.checked)}
          />
        )

      case 'password':
        const passwordFieldKey = `${instance.instanceId}_${key}`
        const isPasswordVisible = passwordVisibility[passwordFieldKey] || false
        return (
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <input
              type={isPasswordVisible ? "text" : "password"}
              value={value !== undefined ? value : (option.default || '')}
              onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.value)}
              style={{ flex: 1, paddingRight: '35px' }}
            />
            <button
              type="button"
              onClick={() => setPasswordVisibility(prev => ({
                ...prev,
                [passwordFieldKey]: !prev[passwordFieldKey]
              }))}
              style={{
                position: 'absolute',
                right: '8px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '18px',
                padding: '4px',
                opacity: 0.6
              }}
              title={isPasswordVisible ? "Hide password" : "Show password"}
            >
              {isPasswordVisible ? '👁️' : '👁️‍🗨️'}
            </button>
          </div>
        )

      case 'number':
        return (
          <input
            type="number"
            value={value !== undefined ? value : (option.default || '')}
            onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.value)}
          />
        )

      case 'user_list':
        const users = value || option.default || []

        const addUser = () => {
          const newUser = {
            username: '',
            password: '',
            email: '',
            firstName: '',
            lastName: '',
            temporary: true
          }
          updateInstanceConfig(instance.instanceId, key, [...users, newUser])
        }

        const removeUser = (index) => {
          const newUsers = users.filter((_, i) => i !== index)
          updateInstanceConfig(instance.instanceId, key, newUsers)
        }

        const updateUser = (index, field, val) => {
          const newUsers = users.map((user, i) =>
            i === index ? { ...user, [field]: val } : user
          )
          updateInstanceConfig(instance.instanceId, key, newUsers)
        }

        const handleCSVImport = (e) => {
          const file = e.target.files[0]
          if (!file) return

          const reader = new FileReader()
          reader.onload = (event) => {
            const csv = event.target.result
            const lines = csv.split('\n').filter(line => line.trim())

            // Skip header row if it exists
            const hasHeader = lines[0].toLowerCase().includes('username')
            const dataLines = hasHeader ? lines.slice(1) : lines

            const importedUsers = dataLines.map(line => {
              const [username, password, email, firstName, lastName] = line.split(',').map(v => v.trim())
              return {
                username: username || '',
                password: password || '',
                email: email || '',
                firstName: firstName || '',
                lastName: lastName || '',
                temporary: true
              }
            }).filter(user => user.username && user.password)

            updateInstanceConfig(instance.instanceId, key, [...users, ...importedUsers])
          }
          reader.readAsText(file)
          e.target.value = '' // Reset input
        }

        return (
          <div className="user-list-container">
            <div className="user-list-header">
              <button
                type="button"
                className="add-user-btn"
                onClick={addUser}
              >
                + Add User
              </button>
              <div className="csv-import-wrapper">
                <label htmlFor={`csv-import-${instance.instanceId}`} className="csv-import-btn">
                  📄 Import CSV
                </label>
                <input
                  id={`csv-import-${instance.instanceId}`}
                  type="file"
                  accept=".csv"
                  onChange={handleCSVImport}
                  style={{ display: 'none' }}
                />
              </div>
            </div>

            {users.length > 0 && (
              <div className="user-list">
                {users.map((user, index) => (
                  <div key={index} className="user-item">
                    <div className="user-fields">
                      <input
                        type="text"
                        placeholder="Username *"
                        value={user.username}
                        onChange={(e) => updateUser(index, 'username', e.target.value)}
                        className="user-input user-username"
                      />
                      <input
                        type="password"
                        placeholder="Password *"
                        value={user.password}
                        onChange={(e) => updateUser(index, 'password', e.target.value)}
                        className="user-input user-password"
                      />
                      <input
                        type="email"
                        placeholder="Email"
                        value={user.email}
                        onChange={(e) => updateUser(index, 'email', e.target.value)}
                        className="user-input user-email"
                      />
                      <input
                        type="text"
                        placeholder="First Name"
                        value={user.firstName}
                        onChange={(e) => updateUser(index, 'firstName', e.target.value)}
                        className="user-input user-firstname"
                      />
                      <input
                        type="text"
                        placeholder="Last Name"
                        value={user.lastName}
                        onChange={(e) => updateUser(index, 'lastName', e.target.value)}
                        className="user-input user-lastname"
                      />
                      <label className="user-temp-checkbox">
                        <input
                          type="checkbox"
                          checked={user.temporary}
                          onChange={(e) => updateUser(index, 'temporary', e.target.checked)}
                        />
                        <span>Temp</span>
                      </label>
                    </div>
                    <button
                      type="button"
                      className="remove-user-btn"
                      onClick={() => removeUser(index)}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}

            <p className="csv-format-help">
              CSV format: username,password,email,firstName,lastName<br/>
              Required fields: username, password
            </p>
          </div>
        )

      default: // text
        return (
          <input
            type="text"
            value={value !== undefined ? value : (option.default || '')}
            onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.value)}
          />
        )
    }
  }

  if (loading) {
    return <div className="loading">Loading catalog...</div>
  }

  const getNodeType = (appId) => {
    if (appId === 'traefik' || appId === 'nginx-proxy-manager') return 'proxy'
    if (appId === 'ignition') return 'app'
    if (appId === 'postgres' || appId === 'mariadb' || appId === 'mssql' || appId === 'sqlite') return 'database'
    if (appId === 'pgadmin' || appId === 'phpmyadmin') return 'database'
    if (appId === 'keycloak' || appId === 'authentik' || appId === 'authelia') return 'auth'
    if (appId === 'nodered' || appId === 'n8n') return 'app'
    if (appId === 'emqx' || appId === 'mosquitto' || appId === 'rabbitmq') return 'app'
    if (appId === 'prometheus' || appId === 'grafana' || appId === 'loki' || appId === 'dozzle') return 'app'
    if (appId === 'portainer' || appId === 'whatupdocker') return 'app'
    if (appId === 'vault') return 'app'
    if (appId === 'guacamole') return 'app'
    return 'app'
  }

  const getServiceUrl = (instance, config) => {
    const appId = instance.app_id

    // Check if reverse proxy is configured with custom domain
    const hasReverseProxy = integrationResults?.integrations?.reverse_proxy
    const baseDomain = integrationSettings.reverse_proxy.base_domain
    const useHttps = integrationSettings.reverse_proxy.enable_https

    // If reverse proxy is active and this service is a target, use the proxy URL
    if (hasReverseProxy && baseDomain !== 'localhost') {
      const isTarget = hasReverseProxy.targets?.some(t => t.service_id === appId)
      if (isTarget && appId !== 'traefik' && appId !== 'nginx-proxy-manager') {
        const protocol = useHttps ? 'https' : 'http'
        // Use custom name from config, fallback to instance_name
        const containerName = instance.config.name || instance.instance_name
        return `${protocol}://${containerName}.${baseDomain}`
      }
    }

    // Default localhost URLs
    if (appId === 'ignition') {
      return `http://localhost:${config.http_port || 8088}`
    } else if (appId === 'postgres') {
      return `localhost:${config.port || 5432}`
    } else if (appId === 'mariadb') {
      return `localhost:${config.port || 3306}`
    } else if (appId === 'mssql') {
      return `localhost:${config.port || 1433}`
    } else if (appId === 'keycloak') {
      return `http://localhost:${config.port || 8180}`
    } else if (appId === 'traefik') {
      return `http://localhost:${config.dashboard_port || 8080}`
    } else if (appId === 'grafana') {
      return `http://localhost:${config.port || 3000}`
    } else if (appId === 'prometheus') {
      return `http://localhost:${config.port || 9090}`
    } else if (appId === 'loki') {
      return `http://localhost:${config.port || 3100}`
    } else if (appId === 'dozzle') {
      return `http://localhost:${config.port || 8888}`
    } else if (appId === 'nodered') {
      return `http://localhost:${config.port || 1880}`
    } else if (appId === 'n8n') {
      return `http://localhost:${config.port || 5678}`
    } else if (appId === 'emqx') {
      return `http://localhost:${config.dashboard_port || 18083}`
    } else if (appId === 'mosquitto') {
      return `mqtt://localhost:${config.mqtt_port || 1883}`
    } else if (appId === 'rabbitmq') {
      return `http://localhost:${config.management_port || 15672}`
    } else if (appId === 'portainer') {
      return `https://localhost:${config.https_port || 9443}`
    } else if (appId === 'whatupdocker') {
      return `http://localhost:${config.port || 3001}`
    } else if (appId === 'vault') {
      return `http://localhost:${config.port || 8200}`
    } else if (appId === 'guacamole') {
      return `http://localhost:${config.port || 8080}`
    } else if (appId === 'authentik') {
      return `http://localhost:${config.http_port || 9000}`
    } else if (appId === 'authelia') {
      return `http://localhost:${config.port || 9091}`
    } else if (appId === 'mailhog') {
      return `http://localhost:${config.http_port || 8025}`
    } else if (appId === 'pgadmin') {
      return `http://localhost:${config.port || 5050}`
    } else if (appId === 'phpmyadmin') {
      return `http://localhost:${config.port || 8080}`
    } else if (appId === 'nginx-proxy-manager') {
      return `http://localhost:${config.admin_port || 81}`
    }
    return 'N/A'
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>Ignition Stack Builder</h1>
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
      </header>

      <main className="main-content">
        <div className="layout">
          <div className="catalog-section">
            {/* Global Settings */}
            <div className="category global-settings">
              <h2>Global Settings</h2>
              <div className="config-grid">
                <div className="config-row">
                  <label>Timezone:</label>
                  <select
                    value={globalSettings.timezone}
                    onChange={(e) => setGlobalSettings({...globalSettings, timezone: e.target.value})}
                  >
                    <option value="Australia/Adelaide">Australia/Adelaide</option>
                    <option value="Australia/Sydney">Australia/Sydney</option>
                    <option value="Australia/Melbourne">Australia/Melbourne</option>
                    <option value="Australia/Brisbane">Australia/Brisbane</option>
                    <option value="Australia/Perth">Australia/Perth</option>
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">America/New_York</option>
                    <option value="America/Chicago">America/Chicago</option>
                    <option value="America/Los_Angeles">America/Los_Angeles</option>
                    <option value="Europe/London">Europe/London</option>
                    <option value="Europe/Paris">Europe/Paris</option>
                    <option value="Asia/Tokyo">Asia/Tokyo</option>
                    <option value="Asia/Singapore">Asia/Singapore</option>
                  </select>
                </div>
                <div className="config-row">
                  <label>Restart Policy:</label>
                  <select
                    value={globalSettings.restart_policy}
                    onChange={(e) => setGlobalSettings({...globalSettings, restart_policy: e.target.value})}
                  >
                    <option value="no">no</option>
                    <option value="always">always</option>
                    <option value="unless-stopped">unless-stopped</option>
                    <option value="on-failure">on-failure</option>
                  </select>
                </div>
                <div className="config-row">
                  <label>
                    <input
                      type="checkbox"
                      checked={globalSettings.ntfy_enabled || false}
                      onChange={(e) => setGlobalSettings({...globalSettings, ntfy_enabled: e.target.checked})}
                    />
                    {' '}Enable Ntfy Monitoring
                  </label>
                  <span className="field-hint">Monitor stack with ntfy notifications</span>
                </div>
                {globalSettings.ntfy_enabled && (
                  <>
                    <div className="config-row">
                      <label>Ntfy Server:</label>
                      <input
                        type="text"
                        value={globalSettings.ntfy_server || 'https://ntfy.sh'}
                        onChange={(e) => setGlobalSettings({...globalSettings, ntfy_server: e.target.value})}
                        placeholder="https://ntfy.sh"
                      />
                    </div>
                    <div className="config-row">
                      <label>Ntfy Topic:</label>
                      <input
                        type="text"
                        value={globalSettings.ntfy_topic || ''}
                        onChange={(e) => setGlobalSettings({...globalSettings, ntfy_topic: e.target.value})}
                        placeholder="my-stack-monitoring"
                      />
                      <span className="field-hint">Unique topic name for your stack</span>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Integration Status */}
            {integrationResults && (integrationResults.conflicts?.length > 0 || integrationResults.warnings?.length > 0 || integrationResults.recommendations?.length > 0) && (
              <div className="category integration-status">
                <h2>🔗 Integration Status</h2>

                {/* Conflicts (Errors) */}
                {integrationResults.conflicts && integrationResults.conflicts.length > 0 && (
                  <div className="integration-section error-section">
                    <h3>⚠️ Conflicts</h3>
                    {integrationResults.conflicts.map((conflict, idx) => (
                      <div key={idx} className="integration-message error-message">
                        <strong>{conflict.services.join(', ')}</strong>: {conflict.message}
                      </div>
                    ))}
                  </div>
                )}

                {/* Warnings */}
                {integrationResults.warnings && integrationResults.warnings.length > 0 && (
                  <div className="integration-section warning-section">
                    <h3>ℹ️ Warnings</h3>
                    {integrationResults.warnings.map((warning, idx) => (
                      <div key={idx} className="integration-message warning-message">
                        {warning.service && <strong>{warning.service}:</strong>} {warning.message}
                      </div>
                    ))}
                  </div>
                )}

                {/* Recommendations */}
                {integrationResults.recommendations && integrationResults.recommendations.length > 0 && (
                  <div className="integration-section info-section">
                    <h3>💡 Recommendations</h3>
                    {integrationResults.recommendations.map((rec, idx) => (
                      <div key={idx} className="integration-message info-message">
                        {rec.message}
                        {rec.suggest && rec.suggest.length > 0 && (
                          <div className="suggestion-services">
                            Consider adding: {rec.suggest.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Application Categories */}
            {catalog.categories.map(category => {
              const allApps = getAppsByCategory(category)
              const enabledApps = allApps.filter(app => app.enabled)
              const comingSoonApps = allApps.filter(app => !app.enabled)

              if (allApps.length === 0) return null

              return (
                <div key={category} className="category">
                  <h2>{category}</h2>
                  <div className="app-list">
                    {/* Enabled Apps */}
                    {enabledApps.map(app => {
                      const instances = getInstancesForApp(app.id)
                      const disabledStatus = isServiceDisabled(app.id)

                      return (
                        <div key={app.id} className="app-section">
                          <div className={`app-item ${disabledStatus.disabled ? 'disabled' : ''}`} title={disabledStatus.disabled ? disabledStatus.reason : ''}>
                            <div className="app-info">
                              <div className="app-name">{app.name}</div>
                              {app.description && (
                                <div className="app-description">{app.description}</div>
                              )}
                              {disabledStatus.disabled && (
                                <div className="disabled-reason">🔒 {disabledStatus.reason}</div>
                              )}
                            </div>
                            <div className="app-controls">
                              {app.supports_multiple ? (
                                <button
                                  className="add-instance-btn"
                                  onClick={() => addInstance(app)}
                                  disabled={disabledStatus.disabled}
                                >
                                  + Add Instance
                                </button>
                              ) : (
                                <div className="checkbox-wrapper">
                                  <input
                                    type="checkbox"
                                    checked={isAppSelected(app.id)}
                                    onChange={() => toggleSingleApp(app)}
                                    disabled={disabledStatus.disabled}
                                  />
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Inline Instance Configurations */}
                          {instances.map((instance) => {
                            // For Ignition, separate configs into left and right columns
                            const isIgnition = app.id === 'ignition'
                            const leftColumnKeys = ['name', 'version', 'http_port', 'https_port', 'admin_username', 'admin_password', 'edition', 'memory_max', 'memory_init', 'commissioning_allow_non_secure', 'quick_start']
                            const rightColumnKeys = ['modules_81', 'modules_83', 'modules', 'third_party_modules']

                            return (
                              <div key={instance.instanceId} className="instance-config inline-config">
                                <div className="instance-header">
                                  <h3>{app.name} - {instance.config.name || instance.instance_name}</h3>
                                  <button
                                    className="remove-instance-btn"
                                    onClick={() => removeInstance(instance.instanceId)}
                                  >
                                    Remove
                                  </button>
                                </div>

                                {isIgnition ? (
                                  <div className="config-two-columns">
                                    {/* Left Column - Basic Configuration */}
                                    <div className="config-column-left">
                                      <h4 className="column-heading">Basic Configuration</h4>
                                      {app.configurable_options && Object.entries(app.configurable_options)
                                        .filter(([key]) => leftColumnKeys.includes(key))
                                        .map(([key, option]) => {
                                          const input = renderConfigInput(instance, key, option, app)
                                          if (!input) return null // Skip if version constraint doesn't match
                                          return (
                                            <div key={key} className="config-row">
                                              <label title={option.description || ''}>{option.label}:</label>
                                              {input}
                                            </div>
                                          )
                                        })}
                                    </div>

                                    {/* Right Column - Modules */}
                                    <div className="config-column-right">
                                      <h4 className="column-heading">Module Configuration</h4>
                                      {app.configurable_options && Object.entries(app.configurable_options)
                                        .filter(([key]) => rightColumnKeys.includes(key))
                                        .map(([key, option]) => {
                                          const input = renderConfigInput(instance, key, option, app)
                                          if (!input) return null // Skip if version constraint doesn't match
                                          return (
                                            <div key={key} className="config-row-full">
                                              <label title={option.description || ''}>{option.label}:</label>
                                              {input}
                                            </div>
                                          )
                                        })}
                                    </div>
                                  </div>
                                ) : (
                                  <div className="config-grid">
                                    {app.configurable_options && Object.entries(app.configurable_options).map(([key, option]) => (
                                      <div key={key} className="config-row">
                                        <label title={option.description || ''}>{option.label}:</label>
                                        {renderConfigInput(instance, key, option, app)}
                                      </div>
                                    ))}

                                    {/* Integration Provider Settings */}
                                    {(() => {
                                      const integrationInfo = getIntegrationSettingsFor(app.id)
                                      if (!integrationInfo) return null

                                      return (
                                        <>
                                          <div className="section-header">
                                            <label>
                                              {integrationInfo.type === 'mqtt_broker' && '📡 MQTT Broker Settings'}
                                              {integrationInfo.type === 'reverse_proxy' && '🌐 Reverse Proxy Settings'}
                                              {integrationInfo.type === 'oauth_provider' && '🔐 OAuth/SSO Settings'}
                                              {integrationInfo.type === 'email_testing' && '📧 Email Testing Settings'}
                                            </label>
                                          </div>

                                          {/* MQTT Broker Settings */}
                                          {integrationInfo.type === 'mqtt_broker' && (
                                            <>
                                              <div className="config-row">
                                                <label>Enable TLS/MQTTS:</label>
                                                <input
                                                  type="checkbox"
                                                  checked={integrationSettings.mqtt.enable_tls}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    mqtt: {...integrationSettings.mqtt, enable_tls: e.target.checked}
                                                  })}
                                                />
                                              </div>
                                              {integrationSettings.mqtt.enable_tls && (
                                                <div className="config-row">
                                                  <label>TLS Port:</label>
                                                  <input
                                                    type="number"
                                                    value={integrationSettings.mqtt.tls_port}
                                                    onChange={(e) => setIntegrationSettings({
                                                      ...integrationSettings,
                                                      mqtt: {...integrationSettings.mqtt, tls_port: parseInt(e.target.value)}
                                                    })}
                                                  />
                                                </div>
                                              )}
                                              <div className="config-row">
                                                <label>Username (optional):</label>
                                                <input
                                                  type="text"
                                                  value={integrationSettings.mqtt.username}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    mqtt: {...integrationSettings.mqtt, username: e.target.value}
                                                  })}
                                                  placeholder="mqtt_user"
                                                />
                                              </div>
                                              <div className="config-row">
                                                <label>Password (optional):</label>
                                                <input
                                                  type="password"
                                                  value={integrationSettings.mqtt.password}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    mqtt: {...integrationSettings.mqtt, password: e.target.value}
                                                  })}
                                                  placeholder="Enter password"
                                                />
                                              </div>
                                              <div className="info-text">
                                                Will be configured for: {integrationInfo.data.clients.map(c => {
                                                  const inst = selectedInstances.find(i => i.instance_name === c.instance_name)
                                                  return inst?.config?.name || c.instance_name
                                                }).join(', ')}
                                              </div>
                                            </>
                                          )}

                                          {/* Reverse Proxy Settings */}
                                          {integrationInfo.type === 'reverse_proxy' && (
                                            <>
                                              <div className="config-row">
                                                <label>Base Domain:</label>
                                                <input
                                                  type="text"
                                                  value={integrationSettings.reverse_proxy.base_domain}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    reverse_proxy: {...integrationSettings.reverse_proxy, base_domain: e.target.value}
                                                  })}
                                                  placeholder="localhost"
                                                />
                                              </div>
                                              <div className="config-row">
                                                <label>Enable HTTPS/TLS:</label>
                                                <input
                                                  type="checkbox"
                                                  checked={integrationSettings.reverse_proxy.enable_https}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    reverse_proxy: {...integrationSettings.reverse_proxy, enable_https: e.target.checked}
                                                  })}
                                                />
                                              </div>
                                              {integrationSettings.reverse_proxy.enable_https && (
                                                <div className="config-row">
                                                  <label>Let's Encrypt Email:</label>
                                                  <input
                                                    type="email"
                                                    value={integrationSettings.reverse_proxy.letsencrypt_email}
                                                    onChange={(e) => setIntegrationSettings({
                                                      ...integrationSettings,
                                                      reverse_proxy: {...integrationSettings.reverse_proxy, letsencrypt_email: e.target.value}
                                                    })}
                                                    placeholder="admin@example.com"
                                                  />
                                                </div>
                                              )}
                                              <div className="info-text">
                                                Routing for: {integrationInfo.data.targets.map(t => t.default_subdomain).join(', ')}
                                              </div>
                                            </>
                                          )}

                                          {/* OAuth/SSO Settings */}
                                          {integrationInfo.type === 'oauth_provider' && (
                                            <>
                                              <div className="config-row">
                                                <label>Realm Name:</label>
                                                <input
                                                  type="text"
                                                  value={integrationSettings.oauth.realm_name}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    oauth: {...integrationSettings.oauth, realm_name: e.target.value}
                                                  })}
                                                  placeholder="iiot"
                                                />
                                              </div>
                                              <div className="config-row">
                                                <label>Auto-configure Services:</label>
                                                <input
                                                  type="checkbox"
                                                  checked={integrationSettings.oauth.auto_configure_services}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    oauth: {...integrationSettings.oauth, auto_configure_services: e.target.checked}
                                                  })}
                                                />
                                              </div>

                                              {/* Realm User Management */}
                                              <div className="user-list-container">
                                                <div className="user-list-header">
                                                  <button
                                                    type="button"
                                                    className="add-user-btn"
                                                    onClick={() => {
                                                      const newUser = {
                                                        username: '',
                                                        password: '',
                                                        email: '',
                                                        firstName: '',
                                                        lastName: '',
                                                        temporary: true
                                                      }
                                                      setIntegrationSettings({
                                                        ...integrationSettings,
                                                        oauth: {...integrationSettings.oauth, realm_users: [...integrationSettings.oauth.realm_users, newUser]}
                                                      })
                                                    }}
                                                  >
                                                    + Add User
                                                  </button>
                                                  <div className="csv-import-wrapper">
                                                    <label htmlFor="csv-import-oauth" className="csv-import-btn">
                                                      📄 Import CSV
                                                    </label>
                                                    <input
                                                      id="csv-import-oauth"
                                                      type="file"
                                                      accept=".csv"
                                                      onChange={(e) => {
                                                        const file = e.target.files[0]
                                                        if (!file) return

                                                        const reader = new FileReader()
                                                        reader.onload = (event) => {
                                                          const csv = event.target.result
                                                          const lines = csv.split('\n').filter(line => line.trim())

                                                          // Skip header row if it exists
                                                          const hasHeader = lines[0].toLowerCase().includes('username')
                                                          const dataLines = hasHeader ? lines.slice(1) : lines

                                                          const importedUsers = dataLines.map(line => {
                                                            const [username, password, email, firstName, lastName] = line.split(',').map(v => v.trim())
                                                            return {
                                                              username: username || '',
                                                              password: password || '',
                                                              email: email || '',
                                                              firstName: firstName || '',
                                                              lastName: lastName || '',
                                                              temporary: true
                                                            }
                                                          }).filter(user => user.username && user.password)

                                                          setIntegrationSettings({
                                                            ...integrationSettings,
                                                            oauth: {...integrationSettings.oauth, realm_users: [...integrationSettings.oauth.realm_users, ...importedUsers]}
                                                          })
                                                        }
                                                        reader.readAsText(file)
                                                        e.target.value = '' // Reset input
                                                      }}
                                                      style={{ display: 'none' }}
                                                    />
                                                  </div>
                                                </div>

                                                {integrationSettings.oauth.realm_users.length > 0 && (
                                                  <div className="user-list">
                                                    {integrationSettings.oauth.realm_users.map((user, index) => (
                                                      <div key={index} className="user-item">
                                                        <div className="user-fields">
                                                          <input
                                                            type="text"
                                                            placeholder="Username *"
                                                            value={user.username}
                                                            onChange={(e) => {
                                                              const newUsers = integrationSettings.oauth.realm_users.map((u, i) =>
                                                                i === index ? { ...u, username: e.target.value } : u
                                                              )
                                                              setIntegrationSettings({
                                                                ...integrationSettings,
                                                                oauth: {...integrationSettings.oauth, realm_users: newUsers}
                                                              })
                                                            }}
                                                            className="user-input"
                                                          />
                                                          <input
                                                            type="password"
                                                            placeholder="Password *"
                                                            value={user.password}
                                                            onChange={(e) => {
                                                              const newUsers = integrationSettings.oauth.realm_users.map((u, i) =>
                                                                i === index ? { ...u, password: e.target.value } : u
                                                              )
                                                              setIntegrationSettings({
                                                                ...integrationSettings,
                                                                oauth: {...integrationSettings.oauth, realm_users: newUsers}
                                                              })
                                                            }}
                                                            className="user-input"
                                                          />
                                                          <input
                                                            type="email"
                                                            placeholder="Email"
                                                            value={user.email}
                                                            onChange={(e) => {
                                                              const newUsers = integrationSettings.oauth.realm_users.map((u, i) =>
                                                                i === index ? { ...u, email: e.target.value } : u
                                                              )
                                                              setIntegrationSettings({
                                                                ...integrationSettings,
                                                                oauth: {...integrationSettings.oauth, realm_users: newUsers}
                                                              })
                                                            }}
                                                            className="user-input"
                                                          />
                                                          <input
                                                            type="text"
                                                            placeholder="First Name"
                                                            value={user.firstName}
                                                            onChange={(e) => {
                                                              const newUsers = integrationSettings.oauth.realm_users.map((u, i) =>
                                                                i === index ? { ...u, firstName: e.target.value } : u
                                                              )
                                                              setIntegrationSettings({
                                                                ...integrationSettings,
                                                                oauth: {...integrationSettings.oauth, realm_users: newUsers}
                                                              })
                                                            }}
                                                            className="user-input"
                                                          />
                                                          <input
                                                            type="text"
                                                            placeholder="Last Name"
                                                            value={user.lastName}
                                                            onChange={(e) => {
                                                              const newUsers = integrationSettings.oauth.realm_users.map((u, i) =>
                                                                i === index ? { ...u, lastName: e.target.value } : u
                                                              )
                                                              setIntegrationSettings({
                                                                ...integrationSettings,
                                                                oauth: {...integrationSettings.oauth, realm_users: newUsers}
                                                              })
                                                            }}
                                                            className="user-input"
                                                          />
                                                          <label className="user-temp-checkbox">
                                                            <input
                                                              type="checkbox"
                                                              checked={user.temporary}
                                                              onChange={(e) => {
                                                                const newUsers = integrationSettings.oauth.realm_users.map((u, i) =>
                                                                  i === index ? { ...u, temporary: e.target.checked } : u
                                                                )
                                                                setIntegrationSettings({
                                                                  ...integrationSettings,
                                                                  oauth: {...integrationSettings.oauth, realm_users: newUsers}
                                                                })
                                                              }}
                                                            />
                                                            <span>Temp</span>
                                                          </label>
                                                        </div>
                                                        <button
                                                          type="button"
                                                          className="remove-user-btn"
                                                          onClick={() => {
                                                            const newUsers = integrationSettings.oauth.realm_users.filter((_, i) => i !== index)
                                                            setIntegrationSettings({
                                                              ...integrationSettings,
                                                              oauth: {...integrationSettings.oauth, realm_users: newUsers}
                                                            })
                                                          }}
                                                        >
                                                          ✕
                                                        </button>
                                                      </div>
                                                    ))}
                                                  </div>
                                                )}

                                                <p className="csv-format-help">
                                                  CSV format: username,password,email,firstName,lastName<br/>
                                                  Required fields: username, password
                                                </p>
                                              </div>

                                              <div className="info-text">
                                                Will configure OAuth for: {integrationInfo.data.clients.map(c => {
                                                  const inst = selectedInstances.find(i => i.instance_name === c.instance_name)
                                                  return inst?.config?.name || c.service_id
                                                }).join(', ')}
                                              </div>
                                            </>
                                          )}

                                          {/* Email Testing Settings */}
                                          {integrationInfo.type === 'email_testing' && (
                                            <>
                                              <div className="config-row">
                                                <label>From Address:</label>
                                                <input
                                                  type="email"
                                                  value={integrationSettings.email.from_address}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    email: {...integrationSettings.email, from_address: e.target.value}
                                                  })}
                                                  placeholder="noreply@iiot.local"
                                                />
                                              </div>
                                              <div className="config-row">
                                                <label>Auto-configure Services:</label>
                                                <input
                                                  type="checkbox"
                                                  checked={integrationSettings.email.auto_configure_services}
                                                  onChange={(e) => setIntegrationSettings({
                                                    ...integrationSettings,
                                                    email: {...integrationSettings.email, auto_configure_services: e.target.checked}
                                                  })}
                                                />
                                              </div>
                                              <div className="info-text">
                                                Will be used by: {integrationInfo.data.clients.map(c => {
                                                  const inst = selectedInstances.find(i => i.instance_name === c.instance_name)
                                                  return inst?.config?.name || c.instance_name
                                                }).join(', ')}
                                              </div>
                                            </>
                                          )}
                                        </>
                                      )
                                    })()}

                                    {/* Dynamic Integration Options for Ignition */}
                                    {app.id === 'ignition' && getAvailableDatabases().length > 0 && (
                                      <>
                                        <div className="section-header" style={{ borderTop: '1px dashed var(--border-color)' }}>
                                          <label>Database Integration</label>
                                        </div>
                                        <div className="config-row">
                                          <label title="Automatically register database in Ignition">Auto-register Database:</label>
                                          <input
                                            type="checkbox"
                                            checked={instance.config.auto_register_db || false}
                                            onChange={(e) => updateInstanceConfig(instance.instanceId, 'auto_register_db', e.target.checked)}
                                          />
                                        </div>
                                        {instance.config.auto_register_db && (
                                          <div className="config-row">
                                            <label>Select Database:</label>
                                            <select
                                              value={instance.config.db_to_register || ''}
                                              onChange={(e) => updateInstanceConfig(instance.instanceId, 'db_to_register', e.target.value)}
                                            >
                                              <option value="">-- Select Database --</option>
                                              {getAvailableDatabases().map(db => (
                                                <option key={db.value} value={db.value}>{db.label}</option>
                                              ))}
                                            </select>
                                          </div>
                                        )}
                                      </>
                                    )}

                                    {/* Dynamic Integration Options for Node-RED */}
                                    {app.id === 'nodered' && getAvailableMqttBrokers().length > 0 && (
                                      <>
                                        <div className="config-row" style={{ gridColumn: '1 / -1', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px dashed var(--border-color)' }}>
                                          <label style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--accent-color)' }}>MQTT Integration</label>
                                        </div>
                                        <div className="config-row">
                                          <label title="Connect Node-RED to MQTT broker">Connect to MQTT:</label>
                                          <input
                                            type="checkbox"
                                            checked={instance.config.connect_mqtt || false}
                                            onChange={(e) => updateInstanceConfig(instance.instanceId, 'connect_mqtt', e.target.checked)}
                                          />
                                        </div>
                                        {instance.config.connect_mqtt && (
                                          <div className="config-row">
                                            <label>Select MQTT Broker:</label>
                                            <select
                                              value={instance.config.mqtt_broker || ''}
                                              onChange={(e) => updateInstanceConfig(instance.instanceId, 'mqtt_broker', e.target.value)}
                                            >
                                              <option value="">-- Select Broker --</option>
                                              {getAvailableMqttBrokers().map(broker => (
                                                <option key={broker.value} value={broker.value}>{broker.label}</option>
                                              ))}
                                            </select>
                                          </div>
                                        )}
                                      </>
                                    )}
                                  </div>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      )
                    })}

                    {/* Coming Soon Apps Section */}
                    {comingSoonApps.length > 0 && (
                      <div className="planned-section">
                        <h4>Coming Soon</h4>
                        {comingSoonApps.map(app => (
                          <div key={app.id} className="app-item planned disabled">
                            <div className="app-info">
                              <div className="app-name">{app.name}</div>
                              {app.description && (
                                <div className="app-description">{app.description}</div>
                              )}
                            </div>
                            <div className="app-controls">
                              <span className="coming-soon">{app.planned ? 'Planned' : 'Coming Soon'}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="preview-panel">
            <div className="preview-section">
              <h2>Preview</h2>

              <div className="selected-items">
                <h3>Selected Services ({selectedInstances.length})</h3>
                {selectedInstances.length === 0 ? (
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    No services selected yet
                  </p>
                ) : (
                  <ul>
                    {selectedInstances.map((inst) => {
                      const app = catalog.applications.find(a => a.id === inst.app_id)
                      return (
                        <li key={inst.instanceId}>
                          {app?.name} ({inst.config.name || inst.instance_name})
                          {inst.config.version && ` - ${inst.config.version}`}
                        </li>
                      )
                    })}
                  </ul>
                )}
              </div>

              {generatedConfig && (
                <div className="preview-code">
                  <h4 style={{ marginBottom: '0.5rem' }}>docker-compose.yml</h4>
                  <pre>{generatedConfig.docker_compose}</pre>
                </div>
              )}

              <div className="action-buttons">
                <button
                  className="generate-btn"
                  onClick={generateStack}
                  disabled={selectedInstances.length === 0}
                >
                  Generate Preview
                </button>
                <button
                  className="download-btn"
                  onClick={downloadStack}
                  disabled={selectedInstances.length === 0}
                >
                  📦 Download Stack (.zip)
                </button>
                <button
                  className="download-btn"
                  onClick={downloadOfflineBundle}
                  disabled={selectedInstances.length === 0}
                  title="Download offline/airgapped bundle with image pull scripts"
                >
                  🔌 Offline Bundle
                </button>
                <button
                  className="save-config-btn"
                  onClick={() => setShowSaveDialog(true)}
                  disabled={selectedInstances.length === 0}
                  title="Save configuration as encrypted file"
                >
                  💾 Save Config
                </button>
                <button
                  className="load-config-btn"
                  onClick={() => setShowLoadDialog(true)}
                  title="Load configuration from encrypted file"
                >
                  📂 Load Config
                </button>
              </div>

              <div className="action-buttons" style={{ marginTop: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                <h4 style={{ width: '100%', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>🐳 Docker Installers</h4>
                <button
                  className="utility-btn"
                  onClick={downloadLinuxInstaller}
                  title="Download Docker & Docker Compose installer for Linux (Ubuntu, Debian, CentOS, etc.)"
                >
                  🐧 Linux Installer
                </button>
                <button
                  className="utility-btn"
                  onClick={downloadWindowsInstaller}
                  title="Download Docker Desktop installer script for Windows 10/11"
                >
                  🪟 Windows Installer
                </button>
              </div>
            </div>

            {/* Save Config Dialog */}
            {showSaveDialog && (
              <div className="modal-overlay" onClick={() => setShowSaveDialog(false)}>
                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  <h2>Save Configuration</h2>
                  <p>Your configuration will be encrypted with a password and saved as a .iiotstack file.</p>

                  <div className="form-group">
                    <label>Password (min 8 characters):</label>
                    <input
                      type="password"
                      value={savePassword}
                      onChange={(e) => setSavePassword(e.target.value)}
                      placeholder="Enter password"
                      minLength={8}
                    />
                  </div>

                  {saveLoadError && <div className="error-message">{saveLoadError}</div>}
                  {saveLoadSuccess && <div className="success-message">{saveLoadSuccess}</div>}

                  <div className="modal-actions">
                    <button onClick={handleSaveConfig} disabled={!savePassword}>
                      Save
                    </button>
                    <button onClick={() => {
                      setShowSaveDialog(false)
                      setSavePassword('')
                      setSaveLoadError('')
                      setSaveLoadSuccess('')
                    }}>
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Load Config Dialog */}
            {showLoadDialog && (
              <div className="modal-overlay" onClick={() => setShowLoadDialog(false)}>
                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  <h2>Load Configuration</h2>
                  <p>Select an encrypted .iiotstack file and enter its password.</p>

                  <div className="form-group">
                    <label>Configuration File:</label>
                    <input
                      type="file"
                      accept=".iiotstack"
                      onChange={(e) => setLoadFile(e.target.files[0])}
                    />
                  </div>

                  <div className="form-group">
                    <label>Password:</label>
                    <input
                      type="password"
                      value={loadPassword}
                      onChange={(e) => setLoadPassword(e.target.value)}
                      placeholder="Enter password"
                    />
                  </div>

                  {saveLoadError && <div className="error-message">{saveLoadError}</div>}
                  {saveLoadSuccess && <div className="success-message">{saveLoadSuccess}</div>}

                  <div className="modal-actions">
                    <button onClick={handleLoadConfig} disabled={!loadFile || !loadPassword}>
                      Load
                    </button>
                    <button onClick={() => {
                      setShowLoadDialog(false)
                      setLoadPassword('')
                      setLoadFile(null)
                      setSaveLoadError('')
                      setSaveLoadSuccess('')
                    }}>
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Service Overview */}
            {selectedInstances.length > 0 && (
              <div className="network-diagram">
                <h2>Service Overview</h2>
                <div className="service-grid">
                  {selectedInstances.map(inst => {
                    const app = catalog.applications.find(a => a.id === inst.app_id)
                    const nodeType = getNodeType(inst.app_id)
                    return (
                      <div key={inst.instanceId} className={`service-card ${nodeType}`}>
                        <div className="node-title">{app?.name}</div>
                        <div className="node-details">{inst.config.name || inst.instance_name}</div>
                        <div className="node-url">{getServiceUrl(inst, inst.config)}</div>
                      </div>
                    )
                  })}
                </div>

                {/* Legend */}
                <div className="network-legend">
                  <div className="legend-item">
                    <div className="legend-color proxy"></div>
                    <span>Reverse Proxy</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color app"></div>
                    <span>Application</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color database"></div>
                    <span>Database</span>
                  </div>
                  <div className="legend-item">
                    <div className="legend-color auth"></div>
                    <span>Authentication</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
