# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **Ignition Stack Builder** is a web-based tool for designing and deploying custom industrial IoT (IIoT) Docker stacks. Users select from a catalog of 26+ applications, configure them through a web UI, and download ready-to-run Docker Compose projects.

- **Status**: Alpha version, ready for user testing
- **Target Use Case**: Reproducible IIoT development environments, proof-of-concepts, and training labs
- **Key Feature**: Automatic integration detection and configuration generation between services (databases, MQTT, OAuth, reverse proxy, etc.)

## Architecture

### Three-Tier System

1. **Frontend (React + Vite)** - `/frontend/src/`
   - Port: 3500
   - Main entry: `App.jsx` (monolithic ~2200 lines)
   - Manages application selection, configuration forms, service preview cards
   - Handles module file uploads (.modl files) with base64 encoding

2. **Backend (FastAPI)** - `/backend/`
   - Port: 8000
   - Main entry: `main.py` (~1700 lines)
   - Key modules:
     - `catalog.json` - Application definitions with configurable options
     - `integration_engine.py` - Detects integration opportunities between services
     - `config_generator.py` - Generates config files (Mosquitto, Grafana, Traefik, Prometheus)
     - `ignition_db_registration.py` - Auto-registration scripts for Ignition databases
     - `keycloak_generator.py` - OAuth realm generation
     - `docker_hub.py` - Fetches available versions from Docker Hub

3. **Generated Stack Output**
   - `docker-compose.yml` - Complete service definitions
   - `.env` - Environment variables and credentials
   - `README.md` - Service URLs and setup instructions
   - `start.sh` / `start.bat` - Ignition-specific initialization scripts
   - `configs/` - Service-specific configuration files
   - `scripts/` - Helper scripts (database registration, monitoring)

### Integration Engine

The integration engine (`backend/integration_engine.py`) is the architectural centerpiece:

- **Detects integration patterns** between selected services:
  - Reverse Proxy (Traefik/Nginx) → web services
  - OAuth Providers (Keycloak) → clients (Grafana, n8n, Portainer)
  - Database Providers (PostgreSQL, MariaDB, MSSQL) → clients (Ignition, Grafana)
  - MQTT Brokers (EMQX, Mosquitto) → clients (Ignition, Node-RED)
  - Email Testing (MailHog) → notification-capable services

- **Generates configuration automatically**:
  - Traefik labels for routing
  - OAuth client secrets and environment variables
  - Database JDBC connection strings
  - MQTT connection profiles

- **Rules defined in**: `backend/integrations.json`
  - `integration_types` - Provider/client relationship definitions
  - `service_capabilities` - What each service can integrate with
  - `integration_rules` - Dependencies, mutual exclusivity, recommendations
  - `config_templates` - Reusable configuration patterns

### Data Flow: User → Generated Stack

1. User selects services in frontend → POST `/detect-integrations` → returns integration opportunities
2. User downloads → POST `/download` → `generate_stack()`:
   - Loads catalog from `catalog.json`
   - Runs integration engine to detect connections
   - Generates docker-compose.yml with correct ports, environment variables, volumes, labels
   - Generates configuration files (Traefik routing, Grafana datasources, Keycloak realm)
   - Creates initialization scripts for Ignition
   - Packages everything into a ZIP file

## Common Commands

### Development

```bash
# Start the stack builder web app
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart after code changes
docker-compose restart backend

# Stop everything
docker-compose down
```

### Testing

```bash
# Run backend API integration tests
./run_backend_tests.sh

# Run single test case (requires stack builder running on localhost:8000)
./tests/test_runner.sh tests/test_cases/T002_ignition_only.json

# Run test with custom wait time
./tests/test_runner.sh tests/test_cases/T302_full_iiot_stack.json 120

# Run advanced test suite
./run_advanced_tests.sh
```

### Test Structure

- **Test cases**: `tests/test_cases/*.json` - JSON configurations for different stack combinations
- **Test runner**: `tests/test_runner.sh` - Generates, extracts, deploys, and validates stacks
- **Health checks**: `tests/health_checks.py` - Service-specific health verification
- **Results**: `tests/results/` - Test execution summaries
- **Temp deployments**: `tests/temp/` - Extracted and running test stacks

Test naming convention:
- `T001-T099`: Single service tests
- `T101-T199`: Two-service integration tests
- `T201-T299`: Multi-service integration tests
- `T301-T399`: Complex real-world scenarios

## Adding New Applications

### 1. Update `backend/catalog.json`

Add new application entry with:
- `id`, `name`, `category`, `description`
- `image`, `default_version`, `available_versions`
- `supports_multiple` (true for databases, Ignition, etc.)
- `default_config` with ports, environment variables, volumes
- `configurable_options` - UI form fields (text, password, number, select, checkbox, multiselect, textarea)
- `integrations` - Array of integration capabilities (e.g., `["db_provider"]`, `["oauth_client"]`)
- `enabled: true` to activate

### 2. Update Integration Definitions

If the service provides or consumes integrations, update `backend/integrations.json`:

**Add to `service_capabilities`**:
```json
"myservice": {
  "integrations": {
    "db_provider": {
      "type": "provider",
      "jdbc_url_template": "jdbc:mydb://{host}:{port}/{database}",
      "default_port": 5432
    }
  }
}
```

**Add to integration type lists**:
```json
"integration_types": {
  "db_provider": {
    "providers": ["postgres", "mariadb", "mssql", "myservice"]
  }
}
```

### 3. Update Backend Logic

If the service requires special handling:

**In `backend/main.py`**, add logic to `generate_stack()` function:
- Custom port mapping logic (around line 370-400)
- Environment variable configuration (around line 400-550)
- Volume handling (around line 570-580)
- Integration-specific configuration (around line 660-730)

**Example**: If service needs OAuth integration, add OAuth env var generation around line 490-540.

### 4. Update Frontend (Optional)

For custom UI behavior, update `frontend/src/App.jsx`:
- Custom validation in `validateInstances()` (line ~1200-1300)
- Special rendering in service overview cards (line ~1500-1700)
- Version-specific option visibility (line ~800-900)

### 5. Add Test Case

Create `tests/test_cases/T0XX_myservice.json`:
```json
{
  "instances": [
    {
      "app_id": "myservice",
      "instance_name": "myservice-1",
      "config": {
        "version": "latest",
        "port": 5000
      }
    }
  ],
  "global_settings": {
    "timezone": "UTC",
    "restart_policy": "unless-stopped"
  }
}
```

Run test: `./tests/test_runner.sh tests/test_cases/T0XX_myservice.json`

## Special Service Behaviors

### Ignition Gateway

- **Volume initialization**: Requires two-phase startup handled by `start.sh` / `start.bat` scripts
- **Module selection**: Version-specific (`modules_81` vs `modules_83`) based on Ignition version
- **Third-party modules**: URLs in `third_party_modules` textarea → `GATEWAY_MODULE_RELINK` environment variable
- **Database auto-registration**: Python script generated in `scripts/register_databases.py` when databases are detected
- **Quick start disabled**: `IGNITION_QUICKSTART` removed due to volume persistence issues

### Traefik Reverse Proxy

- **Automatic routing**: When Traefik is selected, all web services get Docker labels for automatic routing
- **Configuration files**: Generated in `configs/traefik/traefik.yml` (static) and `configs/traefik/dynamic/services.yml`
- **Domain-based routing**: Subdomain = first part of instance name (e.g., `ignition-1` → `ignition.localhost`)
- **HTTPS support**: Optional with Let's Encrypt integration via `integration_settings.reverse_proxy`

### Keycloak (OAuth Provider)

- **Realm generation**: Full realm JSON with client secrets generated pre-emptively in `generate_stack()`
- **Client secrets**: Shared between Keycloak realm import and OAuth client environment variables
- **Import on startup**: Keycloak container command modified to `start-dev --import-realm`
- **Volume mount**: Realm JSON placed in `configs/keycloak/import/realm-{name}.json`

### pgAdmin / phpMyAdmin

- **Conditional inclusion**: Checkbox in PostgreSQL/MariaDB config → dynamically added to instances list
- **Hidden from catalog**: `"hidden": true` in catalog.json
- **Auto-configuration**: PMA_HOST/PMA_PORT automatically set to target database instance

## Integration System Architecture

### Detection Flow

1. **User selects services** → Frontend sends list to `/detect-integrations`
2. **Integration engine analyzes**:
   - Checks mutual exclusivity (e.g., can't have Traefik + Nginx Proxy Manager)
   - Detects providers (services that offer capabilities)
   - Finds consumers (services that can use those capabilities)
   - Generates recommendations (e.g., "Add Prometheus for monitoring")
3. **Returns detection result**:
   ```json
   {
     "integrations": { "reverse_proxy": {...}, "oauth_provider": {...} },
     "conflicts": [],
     "warnings": [],
     "recommendations": []
   }
   ```

### Code Generation Flow

During `generate_stack()` in `backend/main.py`:

1. **Re-run detection** to get integration mappings
2. **Pre-generate secrets** (Keycloak realm with client secrets) BEFORE processing instances
3. **Process each instance**:
   - Build base service definition (image, ports, volumes)
   - Apply integration-specific environment variables using pre-generated secrets
   - Add Traefik labels if reverse proxy present
4. **Generate config files**:
   - Traefik static/dynamic configs
   - Grafana datasource provisioning
   - Keycloak realm import JSON
   - Mosquitto config/password files
   - Prometheus scrape configs
5. **Package everything** into ZIP

### Key Insight: Two-Pass Secret Generation

OAuth integration uses a two-pass approach:
1. **First pass** (line 285-315): Generate Keycloak realm with client secrets
2. **Store secrets** in `keycloak_clients` variable
3. **Second pass** (line 490-540): Use stored secrets when generating OAuth client environment variables

This ensures the same client secret appears in both:
- Keycloak's realm import JSON
- The OAuth client's environment variables (e.g., `GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET`)

## File Organization

```
ignition-stack-builder/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API routes and stack generation logic
│   ├── catalog.json        # Application definitions
│   ├── integrations.json   # Integration rules and capabilities
│   ├── integration_engine.py
│   ├── config_generator.py
│   ├── ignition_db_registration.py
│   ├── keycloak_generator.py
│   ├── ntfy_monitor.py
│   └── docker_hub.py
├── frontend/               # React frontend
│   └── src/
│       ├── App.jsx         # Main application component
│       └── App.css         # Styles with dark/light theme
├── scripts/                # Installation scripts
│   ├── install-docker-linux.sh
│   └── install-docker-windows.ps1
├── tests/                  # Testing infrastructure
│   ├── test_runner.sh      # Main test execution script
│   ├── test_cases/         # JSON test configurations
│   ├── health_checks.py    # Service health validators
│   ├── temp/               # Active test deployments
│   └── results/            # Test output summaries
├── docs/                   # Documentation
│   ├── testing/            # Test reports
│   ├── planning/           # Design documents
│   └── guides/             # User guides
├── docker-compose.yml      # Stack builder itself
├── run_backend_tests.sh    # Backend API test suite
└── run_advanced_tests.sh   # Full integration tests
```

## Important Patterns

### Service Name vs Instance Name vs Container Name

- **Service ID** (`app_id`): Catalog identifier (e.g., `"postgres"`)
- **Instance Name**: User-provided or auto-generated (e.g., `"postgres-1"`)
- **Container Name**: Stack name prefix + instance name (e.g., `"iiot-stack-postgres-1"`)
- **Docker Compose Service Name**: Uses instance name as-is

### Volume Types

**Named volumes**: Managed by Docker, no directory creation needed
- Example: `ignition-1-data:/usr/local/bin/ignition/data`
- Automatically declared in `volumes:` section of docker-compose.yml

**Bind mounts**: Require directory creation
- Config files: `./configs/traefik/traefik.yml:/etc/traefik/traefik.yml:ro`
- Directories created by `start.sh` or documented in README

### Environment Variable Patterns

1. **Direct mapping**: User config → container env var
2. **Integration-based**: Generated from detected integrations
3. **Template-based**: Use placeholders replaced during generation

Example in `main.py` around line 420:
```python
env["GATEWAY_ADMIN_USERNAME"] = config.get("admin_username", env.get("GATEWAY_ADMIN_USERNAME"))
```

### Version-Specific Configuration

Ignition modules use version constraints:
- `modules_81`: For Ignition 8.1.x
- `modules_83`: For Ignition 8.3.x and later
- Version detection: Check if version string starts with "8.3", "8.4", etc., or is "latest"
- See `main.py` lines 428-450

## Known Issues & Gotchas

1. **Ignition Quick Start**: `IGNITION_QUICKSTART` environment variable causes issues with volume persistence, intentionally removed
2. **Named volumes vs bind mounts**: Older versions created directories for named volumes (unnecessary), fixed by distinguishing bind mounts
3. **Module selection state**: Frontend must track `modules_81` and `modules_83` separately per instance
4. **OAuth client secrets**: Must generate Keycloak realm BEFORE processing service environment variables to ensure secrets match
5. **Git status**: Several files modified in working directory; use `git status` to see current state before commits

## API Endpoints

- `GET /` - API info
- `GET /catalog` - Full application catalog
- `GET /versions/{app_id}` - Fetch versions from Docker Hub
- `POST /upload-module` - Upload .modl files (returns base64 encoded)
- `POST /detect-integrations` - Detect integration opportunities
- `POST /generate` - Generate docker-compose.yml and configs (JSON response)
- `POST /download` - Download complete stack as ZIP
- `POST /validate-config` - Validate imported configuration
- `POST /generate-offline-bundle` - Create airgapped deployment bundle
- `GET /download/docker-installer/linux` - Docker installer for Linux
- `GET /download/docker-installer/windows` - Docker installer for Windows

## Debugging Tips

**Backend issues**:
- Check logs: `docker-compose logs -f backend`
- Inspect generated output before it's zipped: Add logging in `generate_stack()` around line 980
- Validate JSON: Use Python's json.loads() on catalog.json or integrations.json

**Frontend issues**:
- Check browser console for errors
- Inspect API calls in Network tab
- Component is monolithic; search for function names in App.jsx

**Integration issues**:
- Enable debug logging in `integration_engine.py`
- Check `integrations.json` for missing service capabilities
- Verify integration type lists include new services

**Test failures**:
- Check `tests/temp/{TEST_ID}/deploy.log` for startup errors
- Inspect generated files: `tests/temp/{TEST_ID}/docker-compose.yml`
- Manually run health check: `python3 tests/health_checks.py <service> <container_name>`
- Increase wait time: `./tests/test_runner.sh test_case.json 180`

## Multi-Instance Support

Services with `"supports_multiple": true`:
- Ignition
- PostgreSQL, MariaDB, MSSQL

Each instance gets:
- Unique instance name
- Unique port configuration
- Separate named volume (e.g., `postgres-1-data`, `postgres-2-data`)
- Independent integration detection

## Offline/Airgapped Deployment

The `/generate-offline-bundle` endpoint creates:
- `pull-images.sh` - Runs on internet-connected system to pull and save all Docker images
- `docker-images.tar.gz` - Compressed archive of all images
- `load-images.sh` - Runs on offline system to load images
- All stack configuration files
- Comprehensive README with transfer instructions

Workflow:
1. Generate bundle on dev machine
2. Run pull-images.sh (with internet) to download images
3. Transfer entire bundle (including docker-images.tar.gz) to offline system
4. Run load-images.sh on offline system
5. Deploy with `docker compose up -d`
