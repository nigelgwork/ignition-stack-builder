# 🏗️ Ignition Stack Builder

> **🚧 Alpha Version - Ready for User Testing**
> This project is currently in **alpha** and ready for user testing and feedback. We welcome your input to help improve the platform! Please report any issues or suggestions via [GitHub Issues](https://github.com/yourusername/ignition-stack-builder/issues).

## 📌 Overview
The **Ignition Stack Builder** is a web-based tool that allows users to **design and deploy custom industrial IoT (IIoT) Docker stacks**.
It provides a simple **web UI** where you can:

- Select from a comprehensive catalog of 26+ applications (Ignition, databases, MQTT brokers, monitoring, security tools, version control, and more).
- Add **multiple instances** of certain services (e.g., Ignition gateways, databases).
- Configure version selection, ports, credentials, and service-specific settings.
- Set global stack settings (timezone, restart policy).
- Preview service overview with access URLs.
- Generate a **ready-to-run project folder** with `docker-compose.yml`, `.env` file, and README documentation.

This project aims to reduce setup friction and provide **reproducible, collaborative IIoT environments** that can be deployed on single machines, shared with colleagues, or extended for larger environments.  

---

## ✨ Features
- 🔧 **Modern Dark Mode UI** – beautiful web interface with dark mode by default and light/dark toggle.
- 🔐 **Secure Authentication** – user registration/login with JWT tokens, optional MFA (2FA), and HTTPS encryption.
- ➕ **Multi-instance Support** – add multiple instances of Ignition, databases, and other services.
- 🎨 **Categorized Application Catalog** – organized by Industrial Platforms, Databases, Messaging, Monitoring, Authentication, DevOps, Version Control, and more.
- 🔢 **Version Selection** – choose specific container versions for each service (defaults to latest).
- ⚙️ **Inline Configuration** – configure each instance immediately after selection with service-specific options.
- 🌐 **Global Settings** – set timezone (defaults to Australia/Adelaide) and restart policy for the entire stack.
- 📊 **Service Overview** – color-coded visual display of all selected services with access URLs.
- 📦 **One-Click Download** – export complete stack as ZIP file with docker-compose.yml, .env, and README.
- 🐳 **Docker Installers** – download ready-to-run Docker installation scripts for Linux and Windows.
- 🔌 **Offline Bundle** – generate airgapped installation bundles with all Docker images for offline deployments.
- 🔒 **Security Ready** – optional integration with Keycloak, Authentik, Authelia, and Vault.
- 🌍 **Networking Ready** – Traefik reverse proxy for routing and HTTPS.
- 🛡️ **HTTPS by Default** – self-signed SSL certificates for secure local development.  

---

## 🏛️ Architecture
The system is divided into four main components:

1. **Frontend (React + Vite + Nginx)**
   - Modern React application with responsive dark/light theme.
   - User authentication with registration, login, and optional MFA.
   - Categorized application selection with inline configuration.
   - Service overview with color-coded cards showing access URLs.
   - Real-time docker-compose.yml preview.
   - Nginx web server with HTTPS support (self-signed SSL certificates).
   - Runs on port 3500 (HTTP) and 3443 (HTTPS).

2. **Backend (FastAPI)**
   - Python FastAPI REST API with JWT authentication.
   - Application catalog stored in JSON with version management.
   - User management with secure password hashing.
   - Dynamic Docker Compose and .env file generation.
   - ZIP download endpoint for complete stack packages.
   - Runs on port 8000.

3. **Authentication Database (PostgreSQL + Redis)**
   - PostgreSQL 16 for user accounts and settings storage.
   - Redis 7 for session/token caching.
   - Automatically initialized with database schema.
   - PostgreSQL runs on port 5433, Redis on port 6379.

4. **Generated Stack Output**
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

### Automation & Workflow
- ✅ **Node-RED** – Visual programming for IoT
- ✅ **n8n** – Workflow automation and integration platform

### Monitoring & Observability
- ✅ **Prometheus** – Metrics collection and alerting
- ✅ **Grafana** – Visualization and dashboards
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

### Version Control
- ✅ **GitLab** – Complete DevOps platform with Git, CI/CD, and container registry
- ✅ **Gitea** – Lightweight self-hosted Git service

### Networking & Proxy
- ✅ **Traefik** – Modern reverse proxy with automatic HTTPS
- ✅ **Nginx Proxy Manager** – Easy reverse proxy management with web UI

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
├── start.sh / start.bat        # Initialization scripts (for Ignition stacks)
├── configs/                     # Service-specific configurations
│   ├── traefik/                # Traefik configuration (if included)
│   └── .gitkeep
├── scripts/                     # Placeholder for helper scripts
│   └── .gitkeep
└── modules/                     # Uploaded 3rd party modules (if any)
    └── ignition-1/
        └── custom-module.modl
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
- Ports 3500 (HTTP), 3443 (HTTPS), 8000 (backend), 5433 (PostgreSQL), 6379 (Redis) available

### Running the Stack Builder

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ignition-stack-builder.git
   cd ignition-stack-builder
   ```

2. **Generate SSL certificates for HTTPS**
   ```bash
   ./generate-ssl-certs.sh
   ```
   This creates self-signed certificates for secure local development. Your browser will show a security warning (click "Advanced" → "Proceed to localhost").

3. **Start the Stack Builder web app**
   ```bash
   docker-compose up -d
   ```

4. **Access the web interface**

   **HTTPS (Recommended):**
   ```
   https://localhost:3443
   ```

   **HTTP (auto-redirects to HTTPS):**
   ```
   http://localhost:3500
   ```

   The backend API is available at:
   ```
   http://localhost:8000
   ```

5. **Create your account**
   - Click "Sign up" to create a new account
   - Enter your email and password (passwords must have 8+ characters, uppercase, lowercase, digit, and special character)
   - Login with your credentials

6. **Build your IIoT stack**
   - Toggle dark/light mode with the switch in the header
   - Set global settings (timezone defaults to Australia/Adelaide, restart policy)
   - Select applications from categorized sections
   - Configure each instance inline (version, ports, credentials, etc.)
   - Add multiple instances of services using "+ Add Instance" button
   - View service overview with color-coded cards and access URLs
   - Click "Generate Preview" to see the docker-compose.yml
   - Click "Download Stack" to get your complete project as a ZIP file

5. **Deploy your generated stack**

   Extract the downloaded ZIP file and navigate to the folder:
   ```bash
   unzip iiot-stack.zip
   cd iiot-stack
   ```

   For stacks with Ignition, use the initialization script:
   ```bash
   # Linux/Mac
   chmod +x start.sh
   ./start.sh

   # Windows
   start.bat
   ```

   For other stacks, start directly with Docker Compose:
   ```bash
   docker-compose up -d
   ```

   Access your services using the URLs listed in the generated README.md file.

6. **Additional Tools Available**

   **Docker Installation Scripts**
   - Click "🐧 Linux Installer" to download a script that installs Docker and Docker Compose on Ubuntu, Debian, CentOS, RHEL, Fedora, and Arch Linux
   - Click "🪟 Windows Installer" to download a PowerShell script that installs Docker Desktop on Windows 10/11
   - These scripts handle all prerequisites and setup automatically

   **Offline/Airgapped Deployment**
   - Click "🔌 Offline Bundle" to generate a bundle for airgapped environments
   - The bundle includes:
     - All your stack configuration files
     - Scripts to pull and save all Docker images
     - Scripts to load images on offline systems
     - Complete instructions for offline deployment
   - Perfect for secure environments without internet access

## ✅ Implemented Features

### Application Catalog (26+ Services)
- ✅ **Industrial Platforms**: Ignition (with edition, JVM memory, module selection, and 3rd party module upload)
- ✅ **Databases**: PostgreSQL, MariaDB, MSSQL, SQLite (with pgAdmin and phpMyAdmin options)
- ✅ **Messaging**: EMQX, Mosquitto
- ✅ **Automation**: Node-RED, n8n
- ✅ **Monitoring**: Prometheus, Grafana, Dozzle
- ✅ **Authentication**: Keycloak, Authentik, Authelia
- ✅ **DevOps**: Portainer, WhatUpDocker, MailHog
- ✅ **Security**: HashiCorp Vault
- ✅ **Remote Access**: Guacamole
- ✅ **Version Control**: GitLab, Gitea
- ✅ **Networking**: Traefik (with automatic service routing), Nginx Proxy Manager

### UI Features
- ✅ Dark mode by default with light/dark toggle
- ✅ Multi-instance support for applicable services
- ✅ Inline instance configuration
- ✅ Dynamic version selection from Docker Hub
- ✅ Module selection for Ignition (checkbox interface)
- ✅ 3rd party module file upload (.modl files)
- ✅ Global settings (timezone, restart policy)
- ✅ Service overview with color-coded cards
- ✅ Access URL display for each service
- ✅ Real-time docker-compose.yml preview

### Backend Features
- ✅ FastAPI REST API
- ✅ Dynamic Docker Compose generation
- ✅ Docker Hub API integration for version fetching
- ✅ Module file upload and encoding
- ✅ Ignition initialization scripts (start.sh / start.bat)
- ✅ Traefik configuration generation
- ✅ Environment variable management
- ✅ ZIP download with complete project structure
- ✅ Generated README documentation with service URLs
- ✅ Docker installation scripts for Linux and Windows
- ✅ Offline/airgapped bundle generation with image pull scripts

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
