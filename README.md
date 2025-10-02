# 🏗️ Ignition Stack Builder

## 📌 Overview
The **Ignition Stack Builder** is a web-based tool that allows users to **design and deploy custom industrial IoT (IIoT) Docker stacks**.
It provides a simple **web UI** where you can:

- Select from a comprehensive catalog of 24+ applications (Ignition, databases, MQTT brokers, monitoring, security tools, and more).
- Add **multiple instances** of certain services (e.g., Ignition gateways, databases).
- Configure version selection, ports, credentials, and service-specific settings.
- Set global stack settings (timezone, restart policy).
- Preview service overview with access URLs.
- Generate a **ready-to-run project folder** with `docker-compose.yml`, `.env` file, and README documentation.

This project aims to reduce setup friction and provide **reproducible, collaborative IIoT environments** that can be deployed on single machines, shared with colleagues, or extended for larger environments.  

---

## ✨ Features
- 🔧 **Modern Dark Mode UI** – beautiful web interface with dark mode by default and light/dark toggle.
- ➕ **Multi-instance Support** – add multiple instances of Ignition, databases, and other services.
- 🎨 **Categorized Application Catalog** – organized by Industrial Platforms, Databases, Messaging, Monitoring, Authentication, DevOps, and more.
- 🔢 **Version Selection** – choose specific container versions for each service (defaults to latest).
- ⚙️ **Inline Configuration** – configure each instance immediately after selection with service-specific options.
- 🌐 **Global Settings** – set timezone (defaults to Australia/Adelaide) and restart policy for the entire stack.
- 📊 **Service Overview** – color-coded visual display of all selected services with access URLs.
- 📦 **One-Click Download** – export complete stack as ZIP file with docker-compose.yml, .env, and README.
- 🔒 **Security Ready** – optional integration with Keycloak, Authentik, Authelia, and Vault.
- 🌍 **Networking Ready** – Traefik reverse proxy for routing and HTTPS.  

---

## 🏛️ Architecture
The system is divided into three main components:

1. **Frontend (React + Vite)**
   - Modern React application with responsive dark/light theme.
   - Categorized application selection with inline configuration.
   - Service overview with color-coded cards showing access URLs.
   - Real-time docker-compose.yml preview.
   - Runs on port 3500.

2. **Backend (FastAPI)**
   - Python FastAPI REST API.
   - Application catalog stored in JSON with version management.
   - Dynamic Docker Compose and .env file generation.
   - ZIP download endpoint for complete stack packages.
   - Runs on port 8000.

3. **Generated Stack Output**
   - `docker-compose.yml` – complete service definitions with configured ports, volumes, and environment variables.
   - `.env` file – global settings, service versions, and environment variables.
   - `README.md` – documentation with service URLs, getting started instructions, and configuration details.  

---

## 🧩 Supported Categories & Applications

### Industrial Platforms
- ✅ **Ignition** (multi-instance) – SCADA platform with edition selection (Standard/Edge/Maker) and JVM memory configuration

### Databases
- ✅ **PostgreSQL** (multi-instance) – Relational database with configurable credentials and ports
- ✅ **MariaDB** (multi-instance) – MySQL-compatible database
- ✅ **MSSQL** (multi-instance) – Microsoft SQL Server with edition selection
- ✅ **SQLite** – Lightweight embedded database

### Messaging & Brokers
- ✅ **EMQX** – Enterprise MQTT broker with dashboard
- ✅ **Mosquitto** – Lightweight MQTT broker
- ✅ **RabbitMQ** – Message queue with management interface

### Automation & Workflow
- ✅ **Node-RED** – Visual programming for IoT
- ✅ **n8n** – Workflow automation platform

### Monitoring & Observability
- ✅ **Prometheus** – Metrics collection and alerting
- ✅ **Grafana** – Visualization and dashboards
- ✅ **Loki** – Log aggregation system
- ✅ **Dozzle** – Real-time Docker log viewer

### Authentication & Identity
- ✅ **Keycloak** – Open source identity and access management
- ✅ **Authentik** – Self-hosted SSO platform
- ✅ **Authelia** – Authentication and authorization server

### DevOps Tools
- ✅ **Portainer** – Docker container management UI
- ✅ **WhatUpDocker** – Container update monitoring
- ✅ **MailHog** – Email testing tool for developers

### Security & Secrets
- ✅ **HashiCorp Vault** – Secrets management

### Remote Access
- ✅ **Guacamole** – Clientless remote desktop gateway

### Networking & Proxy
- ✅ **Traefik** – Modern reverse proxy with automatic HTTPS

---

## 🔗 Planned Integrations (Coming Soon)
- **Ignition ↔ Databases**: auto-register DBs in Ignition configs.
- **Ignition ↔ MQTT**: auto-create MQTT Transmission profile.
- **Keycloak ↔ Apps**: preconfigure Grafana, Guacamole, Vault with Keycloak OAuth2.
- **Grafana ↔ Prometheus/Databases**: add Prometheus + SQL data sources.
- **Vault ↔ All Apps**: secrets injected from Vault.  

---

## 📂 Generated Project Structure
When you download a stack, you'll get a ZIP file containing:

```
iiot-stack.zip
├── docker-compose.yml          # Complete service definitions
├── .env                         # Environment variables and configuration
├── README.md                    # Service URLs and setup instructions
├── configs/                     # Placeholder for service configs
│   └── .gitkeep
└── scripts/                     # Placeholder for helper scripts
    └── .gitkeep
```

The generated `docker-compose.yml` includes:
- All selected services with configured versions
- Port mappings based on your configuration
- Volume mounts for data persistence
- Environment variables for each service
- Shared `iiot-network` for inter-service communication
- Global restart policy

The `.env` file contains:
- Global settings (timezone, restart policy)
- Service-specific environment variables
- Container version tags
- Database credentials
- Admin passwords and API keys

---

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Ports 3500 (frontend) and 8000 (backend) available

### Running the Stack Builder

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd ignition-stack-builder
   ```

2. **Start the Stack Builder web app**
   ```bash
   docker-compose up -d
   ```

3. **Access the web interface**
   Open your browser and navigate to:
   ```
   http://localhost:3500
   ```

4. **Build your IIoT stack**
   - Toggle dark/light mode with the switch in the header
   - Set global settings (timezone defaults to Australia/Adelaide, restart policy)
   - Select applications from categorized sections
   - Configure each instance inline (version, ports, credentials, etc.)
   - Add multiple instances of services using "+ Add Instance" button
   - View service overview with color-coded cards and access URLs
   - Click "Generate Preview" to see the docker-compose.yml
   - Click "Download Stack" to get your complete project as a ZIP file

5. **Deploy your generated stack**
   ```bash
   unzip iiot-stack.zip
   cd iiot-stack
   docker-compose up -d
   ```

   Access your services using the URLs listed in the generated README.md file.

## ✅ Implemented Features

### Application Catalog (24+ Services)
- ✅ **Industrial Platforms**: Ignition (with edition and JVM memory configuration)
- ✅ **Databases**: PostgreSQL, MariaDB, MSSQL, SQLite
- ✅ **Messaging**: EMQX, Mosquitto, RabbitMQ
- ✅ **Automation**: Node-RED, n8n
- ✅ **Monitoring**: Prometheus, Grafana, Loki, Dozzle
- ✅ **Authentication**: Keycloak, Authentik, Authelia
- ✅ **DevOps**: Portainer, WhatUpDocker, MailHog
- ✅ **Security**: HashiCorp Vault
- ✅ **Remote Access**: Guacamole
- ✅ **Networking**: Traefik

### UI Features
- ✅ Dark mode by default with light/dark toggle
- ✅ Multi-instance support for applicable services
- ✅ Inline instance configuration
- ✅ Version selection for all containers
- ✅ Global settings (timezone, restart policy)
- ✅ Service overview with color-coded cards
- ✅ Access URL display for each service
- ✅ Real-time docker-compose.yml preview

### Backend Features
- ✅ FastAPI REST API
- ✅ Dynamic Docker Compose generation
- ✅ Environment variable management
- ✅ Version-tagged container images
- ✅ ZIP download with complete project structure
- ✅ Generated README documentation

## 🔮 Planned Features
- 🔄 Auto-integration engine (database auto-registration, OAuth configuration)
- 🔄 Custom configuration file generation
- 🔄 Pre-configured integration templates
- 🔄 Advanced networking options
- 🔄 Backup/restore script generation
- 🔄 Stack validation and dependency checking

---

## 🚀 Roadmap

### Phase 1: Core Platform ✅ (Complete)
- [x] Build comprehensive catalog JSON with 24+ applications
- [x] Implement modern React UI with dark/light mode
- [x] Create categorized application selection interface
- [x] Add multi-instance support for services
- [x] Implement inline instance configuration
- [x] Build FastAPI backend with Docker Compose generation
- [x] Add version selection for all containers
- [x] Implement global settings (timezone, restart policy)
- [x] Create service overview with access URLs
- [x] Add ZIP download functionality

### Phase 2: Integration Engine 🚧 (In Progress)
- [ ] Auto-register databases in Ignition
- [ ] Configure MQTT connections automatically
- [ ] Set up OAuth/SSO between services
- [ ] Pre-configure Grafana data sources
- [ ] Implement Vault secrets injection

### Phase 3: Advanced Features 📋 (Planned)
- [ ] Stack templates for common use cases
- [ ] Configuration validation and health checks
- [ ] Backup and restore script generation
- [ ] Custom networking options
- [ ] Import/export stack configurations
- [ ] Stack versioning and updates

---

## 🛠️ Technology Stack

### Frontend
- **React 18** – Modern UI framework
- **Vite** – Fast build tool and dev server
- **Axios** – HTTP client for API communication
- **CSS Variables** – Theme system for dark/light modes

### Backend
- **FastAPI** – Modern Python web framework
- **Pydantic** – Data validation and settings management
- **PyYAML** – YAML generation for docker-compose
- **Uvicorn** – ASGI server

### DevOps
- **Docker** – Containerization
- **Docker Compose** – Multi-container orchestration
- **Nginx** – Frontend web server

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Adding Applications to the Catalog
1. Edit `backend/catalog.json`
2. Add your application with required fields:
   - `id`, `name`, `category`, `description`
   - `image`, `default_version`, `available_versions`
   - `configurable_options` with types (text, number, password, select, checkbox)
   - `default_config` with ports, environment, volumes
3. Update `backend/main.py` to handle app-specific logic if needed

### Improving the UI
- Frontend code is in `frontend/src/`
- Main component: `App.jsx`
- Styles: `App.css`
- Follow the existing dark/light theme patterns

### Testing
- Test with various service combinations
- Verify generated docker-compose files
- Check that downloaded stacks deploy correctly

### Documentation
- Update README.md for new features
- Document integration patterns
- Share real-world use cases

---

## 📜 License
[MIT License](LICENSE) – free to use, modify, and share.

---

## 🎯 Use Cases

This tool is perfect for:
- **Developers** setting up local IIoT development environments
- **System Integrators** deploying standardized stacks for clients
- **Training & Education** creating reproducible lab environments
- **Proof of Concepts** quickly assembling multi-service demos
- **DevOps Teams** maintaining consistent deployment configurations

---

⚡ **With Ignition Stack Builder, you can spin up a production-ready IIoT environment in just a few clicks, tailored exactly to your project's needs.**  
