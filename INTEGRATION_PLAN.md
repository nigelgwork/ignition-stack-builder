# Integration & Auto-Configuration Plan
## IIoT Stack Builder - Smart Container Interconnections

---

## 📋 Project Overview

**Current State**: The Ignition Stack Builder successfully generates Docker Compose stacks with 24+ applications. Basic integrations exist (Traefik labels, database connection instructions).

**Goal**: Implement intelligent auto-configuration between containers so users can select services and have them automatically integrated without manual setup.

---

## 🎯 Core Integration Philosophy

### Principles
1. **Zero Manual Configuration**: Users should only need to run `docker-compose up` or `start.sh`
2. **Mutual Exclusivity**: Some services are alternatives (Traefik vs Nginx Proxy Manager) - enforce selection rules
3. **Smart Defaults**: Provide sensible defaults but allow customization
4. **Progressive Enhancement**: Basic functionality works immediately, advanced features configure automatically when dependencies present
5. **Configuration Injection**: Generate all config files at build time, inject into containers via volumes

---

## 🔗 Integration Categories

### 1. **Reverse Proxy Integration** (Highest Priority)
#### Traefik vs Nginx Proxy Manager (Mutually Exclusive)

**When selected**: Automatically configure reverse proxy for all web-accessible services

**Services Requiring Proxy**:
- Ignition (port 8088/8043)
- Grafana (port 3000)
- Node-RED (port 1880)
- n8n (port 5678)
- Keycloak (port 8180)
- Portainer (port 9443 → 9000)
- Dozzle (port 8888)
- EMQX Dashboard (port 18083)
- RabbitMQ Management (port 15672)
- Prometheus (port 9090)
- Guacamole (port 8080)
- Authentik (port 9000)
- Authelia (port 9091)
- MailHog Web UI (port 8025)
- Vault (port 8200)
- WhatUpDocker (port 3001)
- pgAdmin (port 5050)
- phpMyAdmin (port 8080)

**Implementation Strategy**:

##### A. Traefik (Label-Based)
**Current Implementation**: ✅ Partially done
- Docker labels added to services in `main.py:377-382`
- Static configuration generated in `main.py:881-901`
- Dynamic configuration per service in `main.py:922-948`

**Enhancements Needed**:
1. **Custom Domain Support**
   - Add UI field: "Base Domain" (default: `localhost`)
   - Allow users to specify custom domains per service
   - Generate labels: `Host(\`servicename.yourdomain.com\`)`

2. **HTTPS/TLS Support**
   - Add checkbox: "Enable Let's Encrypt"
   - Generate acme.json configuration
   - Add email field for Let's Encrypt
   - Configure cert resolvers

3. **Middleware Support**
   - Basic Auth middleware generation
   - Rate limiting for public services
   - CORS headers for APIs

##### B. Nginx Proxy Manager (UI-Based Config)
**Current Implementation**: ❌ Not implemented
- Container definition exists but no auto-config

**Implementation Strategy**:
1. **Bootstrap Configuration**
   - Pre-configure proxy hosts via API on first startup
   - Create initialization script similar to Ignition's `start.sh`
   - Use NPM's API to create proxy hosts programmatically

2. **API-Based Setup** (NPM has REST API)
   ```bash
   # On first run, script calls NPM API:
   POST /api/nginx/proxy-hosts
   {
     "domain_names": ["ignition.localhost"],
     "forward_scheme": "http",
     "forward_host": "ignition-gateway",
     "forward_port": 8088
   }
   ```

3. **Configuration File**
   - Generate `npm_setup.sh` script in ZIP download
   - Script waits for NPM to be ready, then configures all proxy hosts
   - Include in README with instructions

**Mutual Exclusivity Implementation**:
```javascript
// Frontend (App.jsx)
if (selectedInstances.some(i => i.app_id === 'traefik') && user_selects_nginx_proxy) {
  showWarning("Traefik already selected. Only one reverse proxy allowed.");
  return;
}
```

---

### 2. **SSO/OAuth Integration** (Keycloak/Authentik/Authelia)

**When Keycloak is Selected**: Auto-configure OAuth2 for compatible services

**OAuth-Compatible Services**:
- ✅ Grafana (native Keycloak support)
- ✅ Guacamole (OpenID Connect)
- ✅ Vault (OIDC auth backend)
- ✅ Portainer (OAuth)
- ✅ n8n (OAuth2)

**Implementation Strategy**:

#### Phase 1: Keycloak Realm Setup Script
Generate `keycloak_setup.sh` that runs on first startup:

```bash
#!/bin/bash
# Wait for Keycloak to be ready
until curl -sf http://keycloak:8080/health/ready; do sleep 5; done

# Login as admin
ADMIN_TOKEN=$(curl -X POST "http://keycloak:8080/realms/master/protocol/openid-connect/token" \
  -d "client_id=admin-cli" \
  -d "username=${KEYCLOAK_ADMIN}" \
  -d "password=${KEYCLOAK_ADMIN_PASSWORD}" \
  -d "grant_type=password" | jq -r '.access_token')

# Create IIoT realm
curl -X POST "http://keycloak:8080/admin/realms" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"realm":"iiot","enabled":true}'

# Create clients for each OAuth-enabled service
# Grafana client
curl -X POST "http://keycloak:8080/admin/realms/iiot/clients" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "grafana",
    "enabled": true,
    "redirectUris": ["http://grafana.localhost/login/generic_oauth"],
    "webOrigins": ["http://grafana.localhost"]
  }'
```

#### Phase 2: Service Environment Variables
Inject OAuth config into each service's environment:

**Grafana**:
```yaml
environment:
  GF_AUTH_GENERIC_OAUTH_ENABLED: "true"
  GF_AUTH_GENERIC_OAUTH_NAME: "Keycloak"
  GF_AUTH_GENERIC_OAUTH_CLIENT_ID: "grafana"
  GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET: "${GRAFANA_OAUTH_SECRET}"
  GF_AUTH_GENERIC_OAUTH_AUTH_URL: "http://keycloak:8080/realms/iiot/protocol/openid-connect/auth"
  GF_AUTH_GENERIC_OAUTH_TOKEN_URL: "http://keycloak:8080/realms/iiot/protocol/openid-connect/token"
  GF_AUTH_GENERIC_OAUTH_API_URL: "http://keycloak:8080/realms/iiot/protocol/openid-connect/userinfo"
```

**Portainer**:
```yaml
environment:
  PORTAINER_AUTH_PROVIDER: "oauth"
  PORTAINER_OAUTH_CLIENT_ID: "portainer"
  PORTAINER_OAUTH_AUTHORIZE_URL: "http://keycloak:8080/realms/iiot/protocol/openid-connect/auth"
  PORTAINER_OAUTH_TOKEN_URL: "http://keycloak:8080/realms/iiot/protocol/openid-connect/token"
```

#### Phase 3: User/Group Import
**UI Enhancement**:
- Add file upload: "Import Keycloak Users (CSV)"
- CSV format: `username,email,firstName,lastName,password`
- Generate user creation script

**Script Generation**:
```bash
# In keycloak_setup.sh
while IFS=, read -r username email firstname lastname password; do
  curl -X POST "http://keycloak:8080/admin/realms/iiot/users" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"$username\",
      \"email\": \"$email\",
      \"firstName\": \"$firstname\",
      \"lastName\": \"$lastname\",
      \"enabled\": true,
      \"credentials\": [{\"type\": \"password\", \"value\": \"$password\", \"temporary\": false}]
    }"
done < /tmp/users.csv
```

---

### 3. **Database Auto-Registration** (Ignition)

**When Ignition + Database Selected**: Auto-create database connections

**Supported Databases**:
- PostgreSQL
- MariaDB
- MSSQL

**Current Implementation**: ✅ Partial (connection info in README)
**Enhancement Needed**: ✅ Automatic configuration injection

**Implementation Strategy**:

#### Option A: REST API Configuration (Preferred)
Ignition Gateway has an API - use it to configure datasources:

```bash
# In start.sh after Ignition is healthy
IGNITION_URL="http://localhost:8088"
ADMIN_USER="${GATEWAY_ADMIN_USERNAME}"
ADMIN_PASS="${GATEWAY_ADMIN_PASSWORD}"

# Wait for Gateway API
until curl -sf "${IGNITION_URL}/StatusPing"; do sleep 5; done

# Configure PostgreSQL datasource
curl -X POST "${IGNITION_URL}/system/gwinfo" \
  --user "${ADMIN_USER}:${ADMIN_PASS}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PostgreSQL",
    "enabled": true,
    "driverType": "PostgreSQL",
    "connectUrl": "jdbc:postgresql://postgres-1:5432/iiot_db",
    "username": "postgres",
    "password": "postgres"
  }'
```

#### Option B: Config File Pre-Population
Generate Ignition's `db.xml` config file and mount it:

```xml
<!-- configs/ignition-gateway/data/db.xml -->
<datasources>
  <datasource name="PostgreSQL">
    <enabled>true</enabled>
    <driver>org.postgresql.Driver</driver>
    <url>jdbc:postgresql://postgres-1:5432/iiot_db</url>
    <username>postgres</username>
    <password>postgres</password>
    <validation-query>SELECT 1</validation-query>
    <max-connections>8</max-connections>
  </datasource>
</datasources>
```

**Multi-Database Support**:
If multiple databases selected, create multiple connections:
- `PostgreSQL-1`, `PostgreSQL-2`
- `MariaDB-1`
- `MSSQL-1`

---

### 4. **MQTT Integration** (Ignition + MQTT Broker)

**When Ignition + (EMQX or Mosquitto) Selected**: Auto-configure MQTT Engine

**Implementation Strategy**:

#### A. Ignition MQTT Module Configuration
Requires MQTT Engine module to be enabled.

**Check in UI**:
```javascript
if (ignition_instance.modules.includes('mqtt-engine') && mqtt_broker_selected) {
  enable_mqtt_integration = true;
}
```

**Generate MQTT Config** (via API or config file):
```xml
<!-- configs/ignition-gateway/data/mqtt-engine.xml -->
<mqtt-engines>
  <engine name="EMQX Broker">
    <enabled>true</enabled>
    <url>tcp://emqx:1883</url>
    <client-id>ignition-gateway</client-id>
    <username></username>
    <password></password>
  </engine>
</mqtt-engines>
```

#### B. MQTT Transmission (Ignition → MQTT)
If Ignition has MQTT Transmission module:
```xml
<mqtt-transmitters>
  <transmitter name="Cloud MQTT">
    <enabled>true</enabled>
    <url>tcp://emqx:1883</url>
    <client-id>ignition-transmitter</client-id>
  </transmitter>
</mqtt-transmitters>
```

---

### 5. **Monitoring Integration** (Grafana + Prometheus/Databases)

**When Grafana + Data Source Selected**: Auto-configure datasources

**Datasource Types**:
1. **Prometheus** (if selected)
2. **PostgreSQL** (if selected)
3. **MariaDB** (if selected)
4. **MSSQL** (if selected)
5. **Loki** (if selected for logs)

**Implementation Strategy**:

#### Grafana Provisioning (Config Files)
Generate `configs/grafana/provisioning/datasources/auto.yaml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  - name: PostgreSQL
    type: postgres
    url: postgres-1:5432
    database: iiot_db
    user: postgres
    secureJsonData:
      password: postgres
    jsonData:
      sslmode: disable
      postgresVersion: 1600

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
```

**Mount in docker-compose**:
```yaml
grafana:
  volumes:
    - ./configs/grafana/provisioning:/etc/grafana/provisioning
```

**Auto-Generate Based on Selected Services**:
Backend logic in `generate_stack()`:
```python
if 'grafana' in selected_services:
    datasources = []
    if 'prometheus' in selected_services:
        datasources.append(prometheus_datasource_config)
    if 'postgres' in selected_services:
        datasources.append(postgres_datasource_config)
    # ... generate auto.yaml
```

---

### 6. **Secrets Management** (Vault Integration)

**When Vault Selected**: Inject secrets from Vault into other services

**Implementation Strategy**:

#### Phase 1: Vault Initialization
Generate `vault_setup.sh`:
```bash
#!/bin/bash
export VAULT_ADDR="http://vault:8200"
export VAULT_TOKEN="${VAULT_DEV_ROOT_TOKEN_ID}"

# Enable kv secrets engine
vault secrets enable -path=iiot kv-v2

# Store database credentials
vault kv put iiot/postgres \
  username=postgres \
  password=postgres \
  database=iiot_db

# Store Keycloak admin credentials
vault kv put iiot/keycloak \
  admin_user=admin \
  admin_password=admin
```

#### Phase 2: Secret Injection (Advanced)
Use Vault Agent sidecar or init containers to inject secrets:
```yaml
ignition:
  depends_on:
    - vault
  environment:
    VAULT_ADDR: "http://vault:8200"
    VAULT_TOKEN: "${VAULT_TOKEN}"
  # Use entrypoint script that fetches secrets before starting Ignition
```

---

### 7. **Email Notification Integration** (MailHog)

**When MailHog Selected**: Configure SMTP for all services

**Services with Email**:
- Ignition (alarm notifications)
- Grafana (alert notifications)
- n8n (workflow emails)
- Keycloak (user emails)

**Auto-Configuration**:
```yaml
ignition:
  environment:
    GATEWAY_SMTP_HOST: "mailhog"
    GATEWAY_SMTP_PORT: "1025"
    GATEWAY_SMTP_FROM: "noreply@ignition.local"

grafana:
  environment:
    GF_SMTP_ENABLED: "true"
    GF_SMTP_HOST: "mailhog:1025"
    GF_SMTP_FROM_ADDRESS: "grafana@example.com"

keycloak:
  environment:
    KC_SMTP_HOST: "mailhog"
    KC_SMTP_PORT: "1025"
```

---

### 8. **Remote Access Integration** (Guacamole)

**When Guacamole Selected**: Requires MariaDB/MySQL for user database

**Auto-Configuration**:
1. Check if MariaDB/MySQL selected, if not: auto-add MariaDB
2. Create Guacamole database initialization script
3. Configure Guacamole to use that database

**Implementation**:
```python
# In generate_stack()
if 'guacamole' in selected_services:
    mysql_exists = any(i.app_id in ['mariadb', 'mysql'] for i in instances)
    if not mysql_exists:
        # Auto-add MariaDB instance for Guacamole
        instances.append(create_mariadb_for_guacamole())
```

---

### 9. **Logging Integration** (Loki + Promtail)

**When Loki Selected**: Collect logs from all containers

**Implementation**:
1. Add Promtail sidecar (auto-added when Loki selected)
2. Configure Promtail to scrape Docker logs
3. Send to Loki
4. If Grafana also selected: add Loki datasource automatically

**Promtail Config**:
```yaml
promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - ./configs/promtail/config.yml:/etc/promtail/config.yml
  command: -config.file=/etc/promtail/config.yml
  depends_on:
    - loki
```

---

## 🏗️ Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [x] **Project structure analysis** ✅ Done
- [ ] **Integration registry system**
  - Create `integrations.json` mapping integration types to services
  - Define integration metadata (dependencies, config templates)
- [ ] **Mutual exclusivity enforcement**
  - Frontend validation for Traefik vs Nginx Proxy Manager
  - UI indicators showing conflicts
- [ ] **Backend integration engine**
  - New module: `integration_engine.py`
  - Functions: `detect_integrations()`, `generate_integration_configs()`

### Phase 2: Reverse Proxy (Week 3)
- [ ] **Enhanced Traefik integration**
  - Custom domain support in UI
  - Let's Encrypt configuration
  - Middleware generation (basic auth, rate limiting)
- [ ] **Nginx Proxy Manager integration**
  - API-based setup script generation
  - Bootstrap configuration creator
  - UI for proxy host customization

### Phase 3: SSO/OAuth (Week 4-5)
- [ ] **Keycloak realm setup**
  - Auto-generate keycloak_setup.sh
  - Create clients for each OAuth-compatible service
  - User/group CSV import functionality
- [ ] **Service OAuth configuration**
  - Grafana OAuth env vars
  - Portainer OAuth setup
  - Vault OIDC backend
  - n8n OAuth config

### Phase 4: Database Integration (Week 6)
- [ ] **Ignition database auto-registration**
  - PostgreSQL connection via API
  - MariaDB connection
  - MSSQL connection
  - Multi-database support
- [ ] **Grafana datasource provisioning**
  - Auto-generate provisioning configs
  - Support for all selected databases

### Phase 5: Advanced Integrations (Week 7-8)
- [ ] **MQTT integration**
  - Ignition MQTT Engine config
  - MQTT Transmission setup
- [ ] **Email integration**
  - MailHog SMTP config for all services
- [ ] **Vault secrets management**
  - Secret initialization scripts
  - Secret injection patterns
- [ ] **Logging integration**
  - Loki + Promtail auto-configuration

### Phase 6: Testing & Documentation (Week 9-10)
- [ ] **Integration testing matrix**
  - Test all possible combinations
  - Validate auto-configurations work
- [ ] **User documentation**
  - Integration guide per service
  - Troubleshooting section
- [ ] **Example templates**
  - Pre-built stack templates (SCADA + DB + Monitoring, etc.)

---

## 📊 Integration Matrix

| Service | Reverse Proxy | OAuth/SSO | Database Provider | Database Client | MQTT Broker | MQTT Client | Monitoring | Secrets | Email |
|---------|--------------|-----------|-------------------|-----------------|-------------|-------------|------------|---------|-------|
| **Ignition** | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ (Prometheus export) | ⚠️ | ✅ |
| **PostgreSQL** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ (pg_exporter) | ✅ | ❌ |
| **MariaDB** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ (mysqld_exporter) | ✅ | ❌ |
| **MSSQL** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Grafana** | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ⚠️ | ✅ |
| **Keycloak** | ✅ | ✅ (Provider) | ❌ | ✅ (needs DB) | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Traefik** | N/A | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **NPM** | N/A | ❌ | ❌ | ✅ (SQLite) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Node-RED** | ✅ | ⚠️ | ❌ | ✅ | ❌ | ✅ | ❌ | ⚠️ | ✅ |
| **n8n** | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ⚠️ | ✅ |
| **Prometheus** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | N/A | ❌ | ❌ |
| **EMQX** | ✅ (Dashboard) | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ⚠️ | ❌ |
| **Mosquitto** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Portainer** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ | ❌ |
| **Vault** | ✅ | ✅ (can use OIDC) | ❌ | ❌ | ❌ | ❌ | ✅ | N/A | ❌ |
| **Guacamole** | ✅ | ✅ | ❌ | ✅ (requires MySQL) | ❌ | ❌ | ❌ | ⚠️ | ❌ |

**Legend**:
- ✅ = Fully supported integration
- ⚠️ = Partial/advanced integration possible
- ❌ = Not applicable
- N/A = Not applicable (is the provider of that integration type)

---

## 🎨 UI/UX Enhancements for Integration

### Integration Section in UI
Add new section after "Global Settings":

```
┌─────────────────────────────────────────┐
│  🔗 Smart Integrations                  │
├─────────────────────────────────────────┤
│  ✅ Auto-configure reverse proxy        │
│  ✅ Auto-configure OAuth/SSO            │
│  ✅ Auto-register databases             │
│  ✅ Auto-configure MQTT connections     │
│  ✅ Setup monitoring datasources        │
│                                         │
│  ⚙️ Advanced Integration Settings       │
│  └─ [Show/Hide]                         │
└─────────────────────────────────────────┘
```

### Advanced Settings (Expandable)
```
┌─────────────────────────────────────────┐
│  🌐 Reverse Proxy Settings              │
│  ├─ Base Domain: [localhost        ]    │
│  ├─ Enable HTTPS: [ ] Let's Encrypt     │
│  └─ Email: [admin@example.com      ]    │
│                                         │
│  🔐 Keycloak Settings (if selected)     │
│  ├─ Realm Name: [iiot              ]    │
│  ├─ Import Users: [📁 Choose CSV    ]   │
│  └─ Auto-configure: [Grafana] [n8n] ... │
│                                         │
│  📊 Custom Service URLs                 │
│  ├─ Ignition: [ignition.localhost  ]    │
│  ├─ Grafana:  [grafana.localhost   ]    │
│  └─ ...                                 │
└─────────────────────────────────────────┘
```

---

## 🔧 Backend Architecture Changes

### New Files to Create

1. **`backend/integrations.json`**
   - Integration type definitions
   - Service capabilities mapping
   - Template configurations

2. **`backend/integration_engine.py`**
   - Core integration logic
   - Detection algorithms
   - Config generation functions

3. **`backend/config_templates/`**
   - Traefik templates
   - Keycloak setup templates
   - Grafana provisioning templates
   - MQTT config templates
   - etc.

4. **`backend/scripts/`**
   - Script templates for setup automation
   - Vault initialization
   - Keycloak setup
   - NPM configuration

### Modified Files

1. **`backend/main.py`**
   - Import `integration_engine`
   - Call integration detection in `generate_stack()`
   - Enhanced ZIP generation with integration scripts

2. **`frontend/src/App.jsx`**
   - Add Integration Settings section
   - Mutual exclusivity validation
   - Integration preview/summary

---

## 📝 Example Integration Scenarios

### Scenario 1: Complete SCADA Stack
**User Selects**:
- Ignition (Standard Edition)
- PostgreSQL
- Grafana
- Prometheus
- Traefik
- Keycloak

**Auto-Configuration**:
1. ✅ Traefik routes all services (ignition.localhost, grafana.localhost, keycloak.localhost)
2. ✅ PostgreSQL auto-registered in Ignition as datasource
3. ✅ Grafana configured with Keycloak OAuth
4. ✅ Grafana provisioned with PostgreSQL + Prometheus datasources
5. ✅ Prometheus scraping Ignition metrics (if Prometheus module enabled)

**Generated Files**:
```
iiot-stack.zip
├── docker-compose.yml
├── .env
├── README.md
├── start.sh
├── configs/
│   ├── traefik/
│   │   ├── traefik.yml
│   │   └── dynamic/
│   │       ├── ignition.yml
│   │       ├── grafana.yml
│   │       └── keycloak.yml
│   ├── grafana/
│   │   └── provisioning/
│   │       └── datasources/
│   │           └── auto.yaml
│   └── ignition-gateway/
│       └── postgres_connection_info.txt
└── scripts/
    ├── keycloak_setup.sh
    └── db_init.sh
```

### Scenario 2: IoT Messaging Hub
**User Selects**:
- Ignition
- EMQX
- Node-RED
- PostgreSQL
- Nginx Proxy Manager

**Auto-Configuration**:
1. ✅ NPM setup script creates proxy hosts for all services
2. ✅ Ignition MQTT Engine configured for EMQX broker
3. ✅ Node-RED MQTT nodes pre-configured with EMQX connection
4. ✅ PostgreSQL registered in both Ignition and Node-RED

---

## 🚦 Success Metrics

1. **Integration Coverage**: 80%+ of services auto-configure when dependencies present
2. **User Effort**: Zero manual configuration for standard scenarios
3. **Startup Time**: All integrations active within 2 minutes of `docker-compose up`
4. **Documentation**: Each integration has clear troubleshooting guide

---

## ⚠️ Edge Cases & Considerations

1. **Port Conflicts**: Detect and warn about port conflicts in UI before generation
2. **Resource Limits**: Warn users when selecting >10 services (high resource usage)
3. **Dependency Chains**: If Keycloak selected, recommend PostgreSQL for production
4. **Version Compatibility**: Ensure Ignition version matches MQTT module version
5. **Custom Configurations**: Always allow user to override auto-config via advanced settings

---

## 📚 Documentation Requirements

### For Each Integration:
1. **How It Works**: Technical explanation
2. **Prerequisites**: What must be selected
3. **What Gets Configured**: Detailed list
4. **Manual Override**: How to customize
5. **Troubleshooting**: Common issues and fixes

### Example (Keycloak OAuth Integration):
```markdown
# Keycloak OAuth Integration

## How It Works
When Keycloak is selected alongside OAuth-compatible services (Grafana, Portainer, n8n, Vault),
the Stack Builder automatically:
1. Generates a Keycloak realm called "iiot"
2. Creates OAuth clients for each selected service
3. Injects OAuth environment variables into service configs
4. Provides a setup script that configures Keycloak on first run

## Prerequisites
- Keycloak must be selected
- At least one OAuth-compatible service selected
- (Recommended) PostgreSQL for Keycloak's database

## What Gets Configured
- Grafana: Generic OAuth with Keycloak provider
- Portainer: OAuth authentication
- n8n: OAuth2 login
- Vault: OIDC auth backend

## Manual Override
Edit `scripts/keycloak_setup.sh` before first run to customize:
- Realm name (default: "iiot")
- Client IDs
- Redirect URIs

## Troubleshooting
**Issue**: OAuth login fails with "Invalid redirect URI"
**Solution**: Check that service URLs match Traefik/NPM routing configuration
```

---

## 🎯 Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize integrations** based on user needs (survey/feedback)
3. **Create integration registry** (`integrations.json`)
4. **Build integration engine** (`integration_engine.py`)
5. **Implement Phase 1** (foundation + reverse proxy)
6. **Iterate based on testing**

---

**Document Version**: 1.0
**Last Updated**: 2025-10-04
**Status**: Draft - Ready for Implementation
