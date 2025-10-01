# 🏗️ IIoT Stack Builder

## 📌 Overview
The **IIoT Stack Builder** is a web-based tool that allows users to **design and deploy custom industrial IoT (IIoT) Docker stacks**.  
It provides a simple **web UI** where you can:

- Select from a catalog of applications (e.g., Ignition, databases, MQTT brokers, monitoring, security tools).  
- Add **multiple instances** of certain services (e.g., Ignition gateways, databases).  
- Configure integrations so services are automatically pre-wired to talk to each other (e.g., Ignition connected to databases, Keycloak linked with Grafana).  
- Generate a **ready-to-run project folder** with `docker-compose.yml`, configs, `.env`, and helper scripts.  

This project aims to reduce setup friction and provide **reproducible, collaborative IIoT environments** that can be deployed on single machines, shared with colleagues, or extended for larger environments.  

---

## ✨ Features
- 🔧 **Web UI (Stack Builder)** – select and configure applications by category.  
- ➕ **Multi-instance support** – add multiple Ignition gateways, databases, or other services.  
- 🔗 **Automatic Integrations** – preconfigure services (e.g., Keycloak → Grafana, Ignition → PostgreSQL).  
- 📦 **Downloadable Stack** – one-click export as a folder containing Docker Compose, configs, and scripts.  
- 🔒 **Security Ready** – optional integration with Keycloak, Authentik, Authelia, and Vault.  
- 📊 **Monitoring Ready** – Grafana and Prometheus dashboards pre-linked to services.  
- 🌍 **Networking Ready** – Traefik proxy with automated HTTPS.  

---

## 🏛️ Architecture
The system is divided into three layers:

1. **Web UI**  
   - React (or Vue/Angular alternative).  
   - Categorized checklist form with expandable options per service.  
   - Live preview of generated `docker-compose.yml`.  

2. **Backend Engine**  
   - Node.js or Python backend.  
   - Application catalog stored in JSON.  
   - Template engine (e.g., Jinja2 or Handlebars) for generating Compose and config files.  
   - Integration logic that connects selected services together.  

3. **Generated Project**  
   - `docker-compose.yml`  
   - `.env` file (ports, secrets, config)  
   - `configs/` (per-service configs like Ignition’s `databases.xml`, Keycloak realm exports, Traefik routes)  
   - `scripts/` (backup, restore, regeneration helpers)  
   - `integrations/` (post-generation logic for auto-wiring services)  

---

## 🧩 Supported Categories & Applications

### Industrial Platforms
- Ignition (multi-instance)
- Ignition Edge (multi-instance)

### Databases
- PostgreSQL (+ pgAdmin)
- MariaDB
- MSSQL
- SQLite

### Messaging & Brokers
- EMQX MQTT
- Mosquitto
- RabbitMQ

### Automation / Workflow
- Node-RED
- n8n

### Monitoring & Observability
- Prometheus
- Grafana
- Loki
- Dozzle

### Authentication & Identity
- Keycloak
- Authentik
- Authelia

### DevOps Tools
- Portainer
- WhatUpDocker

### Security & Secrets
- HashiCorp Vault
- Doppler

### Remote Access
- Guacamole

### Networking / Proxy
- Traefik (with Let’s Encrypt HTTPS automation)

---

## 🔗 Example Integrations
- **Ignition ↔ Databases**: auto-register DBs in Ignition configs.  
- **Ignition ↔ MQTT**: auto-create MQTT Transmission profile.  
- **Keycloak ↔ Apps**: preconfigure Grafana, Guacamole, Vault with Keycloak OAuth2.  
- **Grafana ↔ Prometheus/Databases**: add Prometheus + SQL data sources.  
- **Vault ↔ All Apps**: secrets injected from Vault.  

---

## 📂 Example Generated Project Structure
```
my-stack/
├── docker-compose.yml
├── .env
├── README.md
│
├── configs/
│   ├── ignition-1/
│   │   ├── databases.xml
│   │   └── gateway.xml
│   ├── postgres/
│   │   └── init.sql
│   ├── keycloak/
│   │   └── realm-export.json
│   └── traefik/traefik.yml
│
├── scripts/
│   ├── backup.sh
│   ├── restore.sh
│   └── regenerate.sh
│
└── integrations/
    └── apply_integrations.py
```

---

## 🚀 Roadmap
- [ ] Build initial catalog JSON with core apps.  
- [ ] Implement web UI with categorized selection + multi-instance support.  
- [ ] Add template engine for Docker Compose + configs.  
- [ ] Implement integration rules (Ignition + DBs, Keycloak + apps, etc.).  
- [ ] Add “Download Project” functionality.  
- [ ] Extend catalog with more optional apps.  

---

## 🤝 Contributing
Contributions are welcome!  
You can help by:  
- Adding new applications to the catalog.  
- Writing integration rules.  
- Improving UI/UX.  
- Testing and documenting real-world use cases.  

---

## 📜 License
[MIT License](LICENSE) – free to use, modify, and share.  

---

⚡ With this tool, you can spin up a **production-ready IIoT environment** in just a few clicks, tailored exactly to your project’s needs.  
