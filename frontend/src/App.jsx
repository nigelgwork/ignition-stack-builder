import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

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
    restart_policy: 'unless-stopped'
  })

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

  const addInstance = (app) => {
    const count = (instanceCounter[app.id] || 0) + 1
    const instanceName = `${app.id}-${count}`

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
    const newInstances = selectedInstances.map(inst => {
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

  const generateStack = async () => {
    try {
      const response = await axios.post(`${API_URL}/generate`, {
        instances: selectedInstances,
        integrations: [],
        global_settings: globalSettings
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
        global_settings: globalSettings
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

  const getAppsByCategory = (category) => {
    return catalog.applications.filter(app => app.category === category)
  }

  const renderConfigInput = (instance, key, option, app) => {
    const value = instance.config[key]

    switch (option.type) {
      case 'select':
        const options = option.options || app.available_versions || []
        return (
          <select
            value={value || option.default}
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
            {availableOptions.map(opt => (
              <label key={opt} className="multiselect-option">
                <input
                  type="checkbox"
                  checked={selectedValues.includes(opt)}
                  onChange={(e) => {
                    const newValues = e.target.checked
                      ? [...selectedValues, opt]
                      : selectedValues.filter(v => v !== opt)
                    updateInstanceConfig(instance.instanceId, key, newValues)
                  }}
                />
                <span>{opt}</span>
              </label>
            ))}
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
            value={value || option.default || ''}
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
        return (
          <input
            type="password"
            value={value || option.default}
            onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.value)}
          />
        )

      case 'number':
        return (
          <input
            type="number"
            value={value || option.default}
            onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.value)}
          />
        )

      default: // text
        return (
          <input
            type="text"
            value={value || option.default}
            onChange={(e) => updateInstanceConfig(instance.instanceId, key, e.target.value)}
          />
        )
    }
  }

  if (loading) {
    return <div className="loading">Loading catalog...</div>
  }

  const getNodeType = (appId) => {
    if (appId === 'traefik') return 'proxy'
    if (appId === 'ignition') return 'app'
    if (appId === 'postgres' || appId === 'mariadb' || appId === 'mssql' || appId === 'sqlite') return 'database'
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
              </div>
            </div>

            {/* Application Categories */}
            {catalog.categories.map(category => {
              const apps = getAppsByCategory(category)
              if (apps.length === 0) return null

              return (
                <div key={category} className="category">
                  <h2>{category}</h2>
                  <div className="app-list">
                    {apps.map(app => {
                      const instances = getInstancesForApp(app.id)

                      return (
                        <div key={app.id} className="app-section">
                          <div className={`app-item ${!app.enabled ? 'disabled' : ''}`}>
                            <div className="app-info">
                              <div className="app-name">{app.name}</div>
                              {app.description && (
                                <div className="app-description">{app.description}</div>
                              )}
                            </div>
                            <div className="app-controls">
                              {app.enabled ? (
                                app.supports_multiple ? (
                                  <button
                                    className="add-instance-btn"
                                    onClick={() => addInstance(app)}
                                  >
                                    + Add Instance
                                  </button>
                                ) : (
                                  <div className="checkbox-wrapper">
                                    <input
                                      type="checkbox"
                                      checked={isAppSelected(app.id)}
                                      onChange={() => toggleSingleApp(app)}
                                    />
                                  </div>
                                )
                              ) : (
                                <span className="coming-soon">Coming Soon</span>
                              )}
                            </div>
                          </div>

                          {/* Inline Instance Configurations */}
                          {instances.map((instance) => {
                            // For Ignition, separate configs into left and right columns
                            const isIgnition = app.id === 'ignition'
                            const leftColumnKeys = ['name', 'version', 'http_port', 'https_port', 'admin_username', 'admin_password', 'edition', 'memory_max', 'memory_init', 'commissioning_allow_non_secure', 'quick_start']
                            const rightColumnKeys = ['modules', 'third_party_modules']

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
                                        .map(([key, option]) => (
                                          <div key={key} className="config-row">
                                            <label>{option.label}:</label>
                                            {renderConfigInput(instance, key, option, app)}
                                          </div>
                                        ))}
                                    </div>

                                    {/* Right Column - Modules */}
                                    <div className="config-column-right">
                                      <h4 className="column-heading">Module Configuration</h4>
                                      {app.configurable_options && Object.entries(app.configurable_options)
                                        .filter(([key]) => rightColumnKeys.includes(key))
                                        .map(([key, option]) => (
                                          <div key={key} className="config-row-full">
                                            <label>{option.label}:</label>
                                            {renderConfigInput(instance, key, option, app)}
                                          </div>
                                        ))}
                                    </div>
                                  </div>
                                ) : (
                                  <div className="config-grid">
                                    {app.configurable_options && Object.entries(app.configurable_options).map(([key, option]) => (
                                      <div key={key} className="config-row">
                                        <label>{option.label}:</label>
                                        {renderConfigInput(instance, key, option, app)}
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}

            {/* Integrations Section (Placeholder) */}
            <div className="integrations-section">
              <h3>Integrations (Coming Soon)</h3>
              <div className="integration-item">
                <input type="checkbox" disabled />
                <label>Auto-register DBs in Ignition</label>
              </div>
              <div className="integration-item">
                <input type="checkbox" disabled />
                <label>Configure Keycloak clients</label>
              </div>
              <div className="integration-item">
                <input type="checkbox" disabled />
                <label>Connect Node-RED → MQTT</label>
              </div>
              <div className="integration-item">
                <input type="checkbox" disabled />
                <label>Enable Prometheus scraping</label>
              </div>
              <div className="integration-item">
                <input type="checkbox" disabled />
                <label>Store secrets in Vault</label>
              </div>
            </div>
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
                  Download Stack (.zip)
                </button>
              </div>
            </div>

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
