# Project Continuity Document
## Ignition Stack Builder - Quick Start Guide for Developers

**Last Updated**: 2025-10-04
**Project Status**: Phase 1 Complete, Integration Testing In Progress

> **📋 For Current Project Status**: See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed status, completed work, pending tasks, and next steps.

> **📋 For Test Results**: See [TEST_EXECUTION_RESULTS.md](TEST_EXECUTION_RESULTS.md) for test execution details and results.

---

## 🎯 What Is This Project?

**Ignition Stack Builder** is a web-based tool that generates ready-to-deploy Docker Compose stacks for Industrial IoT environments.

**Think**: "AWS CloudFormation / Terraform, but for IIoT Docker stacks with a friendly UI"

### Core Value Proposition
- **Before**: Manually write docker-compose.yml, configure services, set up networking, etc. (Hours of work)
- **After**: Click services you want → Download ZIP → Run `docker-compose up` (Minutes)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                     http://localhost:3500                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Frontend (React)   │
                 │   Port: 3500         │
                 │   - UI for selection │
                 │   - Config forms     │
                 │   - Preview          │
                 └──────────┬───────────┘
                            │ API Calls
                            ▼
                 ┌──────────────────────┐
                 │  Backend (FastAPI)   │
                 │  Port: 8000          │
                 │  - catalog.json      │
                 │  - Generation logic  │
                 │  - ZIP download      │
                 └──────────┬───────────┘
                            │
                            ▼
              ┌──────────────────────────────┐
              │   Generated Output (ZIP)     │
              │   - docker-compose.yml       │
              │   - .env                     │
              │   - README.md                │
              │   - start.sh / start.bat     │
              │   - configs/                 │
              └──────────────────────────────┘
```

---

## 📁 Project Structure

```
ignition-stack-builder/
├── backend/
│   ├── Dockerfile              # Python FastAPI container
│   ├── main.py                 # ⭐ Main API logic
│   ├── catalog.json            # ⭐ Service definitions
│   ├── docker_hub.py           # Docker Hub API integration
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── Dockerfile              # React + Nginx container
│   ├── src/
│   │   ├── App.jsx             # ⭐ Main React component
│   │   ├── App.css             # Styling
│   │   └── main.jsx            # React entry point
│   ├── package.json            # Node dependencies
│   └── index.html              # HTML template
│
├── docker-compose.yml          # Dev environment for the builder itself
├── README.md                   # User-facing documentation
├── FEATURES.md                 # Feature changelog
├── INTEGRATION_PLAN.md         # ⭐ Master plan for Phase 2
└── CONTINUITY.md               # ⭐ This file
```

---

## 🔑 Key Files to Understand

### 1. `backend/catalog.json` (1,772 lines)
**What it is**: The "database" of all available services.

**Structure**:
```json
{
  "applications": [
    {
      "id": "ignition",                    // Unique identifier
      "name": "Ignition",                  // Display name
      "category": "Industrial Platforms",  // UI grouping
      "image": "inductiveautomation/ignition",  // Docker image
      "default_version": "latest",
      "available_versions": [...],         // Version dropdown options
      "supports_multiple": true,           // Can add multiple instances?
      "default_config": {                  // Default docker-compose config
        "ports": ["8088:8088", "8043:8043"],
        "environment": { ... },
        "volumes": [ ... ]
      },
      "configurable_options": {            // UI form fields
        "admin_username": {
          "type": "text",
          "default": "admin",
          "label": "Admin Username",
          "description": "..."
        },
        ...
      },
      "integrations": ["db_client", "mqtt_client", "oauth_client"],  // ⭐ For Phase 2
      "enabled": true                      // Show in UI?
    }
  ],
  "categories": [ ... ]
}
```

**How to add a new service**:
1. Copy an existing service entry
2. Change `id`, `name`, `image`
3. Define `configurable_options` (what user can customize)
4. Set `default_config` (ports, env vars, volumes)
5. Set `enabled: true`
6. If needed, add handling logic in `main.py` (see step 2 below)

---

### 2. `backend/main.py` (980 lines)
**What it does**:
- Serves catalog
- Fetches versions from Docker Hub
- Generates docker-compose.yml + .env + README
- Creates ZIP download

**Key Functions**:

| Function | Line | Purpose |
|----------|------|---------|
| `load_catalog()` | 33 | Loads catalog.json |
| `get_catalog()` | 60 | API endpoint: GET /catalog |
| `get_versions(app_id)` | 65 | API endpoint: GET /versions/{app_id} - fetches from Docker Hub |
| `upload_module()` | 95 | API endpoint: POST /upload-module - handles .modl file uploads |
| `generate_stack()` | 119 | ⭐ **CORE FUNCTION** - generates docker-compose from selections |
| `download_stack()` | 603 | API endpoint: POST /download - creates ZIP file |

**How `generate_stack()` works**:
1. Receives user selections (instances, config, global settings)
2. Loops through each instance
3. Builds docker-compose service definition:
   - Image name + version
   - Ports (mapped from user config)
   - Environment variables (merged from defaults + user input)
   - Volumes (with instance name replacements)
   - Traefik labels (if Traefik is selected)
4. Generates `.env` file
5. Generates `README.md` with service URLs
6. Returns all 3 as strings

**To add logic for a new service**:
- See lines 239-330 for environment variable mapping examples
- Pattern: Check `instance.app_id`, then set env vars from `config.get()`

---

### 3. `frontend/src/App.jsx`
**What it does**:
- Fetches catalog from backend
- Renders UI (categorized service cards)
- Handles instance configuration (inline forms)
- Manages state (selected instances)
- Sends to backend for generation/download

**Key State Variables**:
```javascript
const [instances, setInstances] = useState([]);         // Selected services
const [globalSettings, setGlobalSettings] = useState({
  timezone: 'Australia/Adelaide',
  restart_policy: 'unless-stopped'
});
const [dockerCompose, setDockerCompose] = useState(''); // Preview
```

**Key Functions**:
- `addInstance(app)`: Adds a new service instance
- `removeInstance(instanceId)`: Removes an instance
- `updateInstanceConfig(instanceId, field, value)`: Updates config
- `generatePreview()`: Calls `/generate` API
- `downloadStack()`: Calls `/download` API

---

## 🚀 How to Run the Project (Dev Mode)

### Prerequisites
- Docker
- Docker Compose
- Ports 3500 and 8000 available

### Steps
```bash
# 1. Clone repo
cd /git/ignition-stack-builder

# 2. Start the dev environment
docker-compose up -d

# 3. Access the UI
open http://localhost:3500

# 4. Backend API docs
open http://localhost:8000/docs
```

### Making Changes

**Frontend Changes**:
- Edit `frontend/src/App.jsx`
- Changes hot-reload automatically (Vite HMR)

**Backend Changes**:
- Edit `backend/main.py` or `backend/catalog.json`
- Restart backend: `docker-compose restart backend`

**Rebuild after dependency changes**:
```bash
docker-compose down
docker-compose up --build -d
```

---

## 📊 Current Feature Status

### ✅ Completed (Phase 1)
- [x] 24+ service catalog
- [x] Multi-instance support (Ignition, databases)
- [x] Inline configuration UI
- [x] Version selection from Docker Hub
- [x] Global settings (timezone, restart policy)
- [x] Service overview with access URLs
- [x] Docker Compose generation
- [x] .env file generation
- [x] README generation with instructions
- [x] ZIP download
- [x] Ignition initialization scripts (start.sh/start.bat)
- [x] Traefik basic integration (labels + config files)
- [x] Module selection (checkbox UI for Ignition modules)
- [x] 3rd party module upload (.modl files)
- [x] PostgreSQL connection instructions for Ignition
- [x] pgAdmin/phpMyAdmin auto-add with checkboxes

### 🚧 In Progress (Phase 2 - Integrations)
See `INTEGRATION_PLAN.md` for full details. Key items:

- [ ] Auto-configuration engine
- [ ] Nginx Proxy Manager integration
- [ ] Keycloak OAuth setup automation
- [ ] Database auto-registration in Ignition (via API)
- [ ] MQTT auto-configuration
- [ ] Grafana datasource provisioning
- [ ] Vault secrets management
- [ ] Email (MailHog) auto-config

---

## 🛠️ Common Development Tasks

### Task 1: Add a New Service to Catalog

**Example**: Adding InfluxDB

1. **Add to `catalog.json`**:
```json
{
  "id": "influxdb",
  "name": "InfluxDB",
  "category": "Databases",
  "description": "Time-series database",
  "image": "influxdb",
  "default_version": "latest",
  "available_versions": ["latest", "2.7", "2.6"],
  "supports_multiple": false,
  "default_config": {
    "ports": ["8086:8086"],
    "environment": {
      "DOCKER_INFLUXDB_INIT_MODE": "setup",
      "DOCKER_INFLUXDB_INIT_USERNAME": "admin",
      "DOCKER_INFLUXDB_INIT_PASSWORD": "adminpassword",
      "DOCKER_INFLUXDB_INIT_ORG": "myorg",
      "DOCKER_INFLUXDB_INIT_BUCKET": "mybucket"
    },
    "volumes": ["./configs/{instance_name}/data:/var/lib/influxdb2"]
  },
  "configurable_options": {
    "version": {"type": "select", "default": "latest", "label": "Version"},
    "port": {"type": "number", "default": 8086, "label": "HTTP Port"},
    "admin_username": {"type": "text", "default": "admin", "label": "Admin Username"},
    "admin_password": {"type": "password", "default": "adminpassword", "label": "Password"},
    "org": {"type": "text", "default": "myorg", "label": "Organization"},
    "bucket": {"type": "text", "default": "mybucket", "label": "Initial Bucket"}
  },
  "integrations": ["db_provider", "metrics_storage"],
  "enabled": true
}
```

2. **Add environment variable mapping in `main.py`** (around line 300):
```python
elif instance.app_id == "influxdb":
    env["DOCKER_INFLUXDB_INIT_USERNAME"] = config.get("admin_username", env.get("DOCKER_INFLUXDB_INIT_USERNAME"))
    env["DOCKER_INFLUXDB_INIT_PASSWORD"] = config.get("admin_password", env.get("DOCKER_INFLUXDB_INIT_PASSWORD"))
    env["DOCKER_INFLUXDB_INIT_ORG"] = config.get("org", env.get("DOCKER_INFLUXDB_INIT_ORG"))
    env["DOCKER_INFLUXDB_INIT_BUCKET"] = config.get("bucket", env.get("DOCKER_INFLUXDB_INIT_BUCKET"))
```

3. **Add service URL generation in `main.py`** (around line 490):
```python
elif instance.app_id == "influxdb":
    port = config.get("port", 8086)
    url = f"http://localhost:{port}"
```

4. **Test**:
- Restart backend
- Add InfluxDB in UI
- Configure and download
- Verify docker-compose.yml has correct config

---

### Task 2: Add a New Configurable Option to Existing Service

**Example**: Add "Enable SSL" checkbox to PostgreSQL

1. **Edit `catalog.json`** - find PostgreSQL entry, add to `configurable_options`:
```json
"enable_ssl": {
  "type": "checkbox",
  "default": false,
  "label": "Enable SSL",
  "description": "Require SSL connections (recommended for production)"
}
```

2. **Edit `main.py`** - add environment variable logic (around line 240):
```python
elif instance.app_id == "postgres":
    env["POSTGRES_DB"] = config.get("database", env.get("POSTGRES_DB"))
    env["POSTGRES_USER"] = config.get("username", env.get("POSTGRES_USER"))
    env["POSTGRES_PASSWORD"] = config.get("password", env.get("POSTGRES_PASSWORD"))

    # New SSL option
    if config.get("enable_ssl", False):
        env["POSTGRES_INITDB_ARGS"] = "-c ssl=on"
```

3. **Frontend automatically picks it up** - no changes needed! The UI dynamically renders form fields based on `configurable_options`.

---

### Task 3: Debug Generation Issues

**Common Issue**: Docker-compose.yml has wrong environment variables

**Debugging Steps**:

1. **Check the API response**:
```bash
# Generate a stack via API directly
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      {
        "app_id": "postgres",
        "instance_name": "postgres-1",
        "config": {"version": "latest", "port": 5432, "database": "test"}
      }
    ],
    "global_settings": {"timezone": "UTC", "restart_policy": "unless-stopped"}
  }' | jq .
```

2. **Check backend logs**:
```bash
docker-compose logs -f backend
```

3. **Common Fixes**:
- Missing env var mapping in `main.py` → Add it
- Wrong field name in frontend → Check console for config object
- Type mismatch → Check `configurable_options` type (text vs number vs select)

---

## 🔍 Understanding the Data Flow

### User Journey
1. **User opens UI** → Frontend fetches `/catalog`
2. **User selects Ignition** → `addInstance('ignition')` called
3. **User configures** (port 8088, admin password, etc.) → `updateInstanceConfig()` updates state
4. **User clicks "Download Stack"** → `downloadStack()` posts to `/download`
5. **Backend generates** → `generate_stack()` creates docker-compose, env, README
6. **Backend zips** → `download_stack()` creates ZIP in memory
7. **User receives** → `iiot-stack.zip` downloaded

### Data Structures

**Frontend State** (`instances`):
```javascript
[
  {
    app_id: "ignition",
    instance_name: "ignition-gateway",
    instanceId: 1234567890,  // Timestamp for React key
    config: {
      version: "latest",
      http_port: 8088,
      https_port: 8043,
      admin_username: "admin",
      admin_password: "password",
      edition: "standard",
      modules_83: ["perspective", "vision", "tag-historian"],
      uploaded_modules: [
        {filename: "module.modl", size: 12345, encoded: "base64..."}
      ]
    }
  }
]
```

**Sent to Backend** (POST /generate):
```json
{
  "instances": [ ... ],
  "global_settings": {
    "timezone": "Australia/Adelaide",
    "restart_policy": "unless-stopped"
  }
}
```

**Backend Returns**:
```json
{
  "docker_compose": "services:\n  ignition-gateway:\n    image: ...",
  "env": "TZ=Australia/Adelaide\nRESTART_POLICY=unless-stopped\n...",
  "readme": "# IIoT Stack\n\n## Services\n- ignition-gateway..."
}
```

---

## 🧪 Testing

### Manual Testing Checklist

**Basic Flow**:
- [ ] Start dev environment
- [ ] UI loads without errors
- [ ] Catalog displays all categories
- [ ] Can add Ignition instance
- [ ] Can configure Ignition (ports, version, modules)
- [ ] Can add PostgreSQL
- [ ] Can toggle "Include pgAdmin" checkbox
- [ ] Preview shows valid docker-compose.yml
- [ ] Download creates ZIP
- [ ] Extract ZIP and run `docker-compose up -d`
- [ ] Services start successfully
- [ ] Access URLs work

**Advanced Testing**:
- [ ] Multi-instance: Add 2 Ignition instances with different ports
- [ ] Module upload: Upload .modl file, verify it's in ZIP
- [ ] Traefik integration: Add Traefik + Ignition, verify labels
- [ ] PostgreSQL + Ignition: Verify connection instructions in README

---

## 🐛 Known Issues & Workarounds

### Issue 1: Ignition Volume Permissions
**Problem**: When mounting volumes directly, Ignition fails to start due to permission issues.
**Solution**: Use the `start.sh` script which does a two-phase initialization (see `main.py:639-829`).

### Issue 2: Port Conflicts
**Problem**: User selects two services with same default port.
**Status**: Not yet handled in UI.
**TODO**: Add port conflict detection in frontend before download.

### Issue 3: Traefik + HTTPS
**Problem**: Traefik config doesn't include Let's Encrypt setup yet.
**Status**: Basic HTTP routing works, HTTPS planned for Phase 2.

---

## 📚 Resources & References

### Docker Compose
- [Compose file spec](https://docs.docker.com/compose/compose-file/)
- [Environment variables](https://docs.docker.com/compose/environment-variables/)

### Services
- [Ignition Docker](https://docs.inductiveautomation.com/display/DOC81/Docker+Image)
- [Traefik Docs](https://doc.traefik.io/traefik/)
- [Keycloak Docker](https://www.keycloak.org/server/containers)
- [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)

### APIs
- [Docker Hub API](https://docs.docker.com/registry/spec/api/)
- [Keycloak Admin REST API](https://www.keycloak.org/docs-api/latest/rest-api/)

---

## 🎯 Next Steps (Prioritized)

### Immediate (This Week)
1. **Review integration plan** (`INTEGRATION_PLAN.md`)
2. **Create `integrations.json`** (registry of integration types)
3. **Add port conflict detection** to frontend
4. **Implement mutual exclusivity** (Traefik vs Nginx Proxy Manager)

### Short-term (Next 2 Weeks)
5. **Enhanced Traefik integration**:
   - Custom domain input
   - Let's Encrypt toggle
   - Generate proper certificates config
6. **Nginx Proxy Manager**:
   - API-based configuration script
   - Bootstrap setup on first run

### Medium-term (Next Month)
7. **Keycloak integration**:
   - Realm setup script
   - OAuth client creation
   - User import from CSV
8. **Database auto-registration**:
   - Use Ignition API to create datasources
   - Test with PostgreSQL, MariaDB, MSSQL

### Long-term (Next Quarter)
9. **Stack templates** (pre-configured bundles)
10. **Import/export stack configs**
11. **Integration testing suite**

---

## 💡 Tips for Contributors

1. **Start small**: Add a simple service first to understand the flow
2. **Follow patterns**: Look at existing services for reference (Postgres, Ignition)
3. **Test end-to-end**: Always download and run the generated stack
4. **Document changes**: Update this file and INTEGRATION_PLAN.md as needed
5. **Use FastAPI docs**: http://localhost:8000/docs for interactive API testing

---

## 🆘 Getting Help

**Common Questions**:

**Q**: Where do I add a new service?
**A**: `backend/catalog.json` - copy an existing entry and modify.

**Q**: How do I customize the docker-compose generation?
**A**: Edit `backend/main.py` in the `generate_stack()` function (line 119).

**Q**: Why isn't my config option showing in the UI?
**A**: Check `configurable_options` in catalog.json. Frontend auto-generates forms from this.

**Q**: How do integrations work?
**A**: Currently basic (Traefik labels, README instructions). Advanced auto-config is Phase 2 - see `INTEGRATION_PLAN.md`.

---

## 📝 Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-04 | Created INTEGRATION_PLAN.md and CONTINUITY.md | Claude Code |
| 2025-10-03 | Added module upload and enhanced Ignition config | Previous |
| 2025-10-02 | Initial project structure | Previous |

---

**Remember**: The goal is to make IIoT stack deployment so easy that a non-Docker expert can do it in minutes. Every integration we automate gets us closer to that vision.

**Need to pause and come back later?** Re-read this document + INTEGRATION_PLAN.md. You'll be back up to speed in 10 minutes.
