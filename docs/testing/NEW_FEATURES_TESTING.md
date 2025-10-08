# New Features Testing Requirements

## Overview
This document outlines the testing requirements for newly added features to the Ignition Stack Builder.

## Changes Made

### 1. New Applications Added

#### Version Control Category (NEW)
- **GitLab** - Complete DevOps platform with Git, CI/CD, and container registry
- **Gitea** - Lightweight self-hosted Git service

#### Enabled Applications (Previously "Coming Soon")
- **Mosquitto** - Already enabled, verify functionality
- **n8n** - Workflow automation platform (NOW ENABLED)
- **Vault** - HashiCorp Vault secrets management (NOW ENABLED)
- **Guacamole** - Clientless remote desktop gateway (NOW ENABLED)

#### Removed Applications
- **RabbitMQ** - Removed from catalog (no longer available)

### 2. New Download Features

#### Docker Installation Scripts
- **Linux Installer** (`install-docker-linux.sh`)
  - Supports: Ubuntu, Debian, CentOS, RHEL, Fedora, Arch Linux
  - Installs Docker Engine and Docker Compose
  - Configures user permissions and systemd services

- **Windows Installer** (`install-docker-windows.ps1`)
  - Supports: Windows 10/11 Pro, Enterprise, Education
  - Installs Docker Desktop with WSL 2 backend
  - PowerShell script with admin requirements

#### Offline/Airgapped Bundle
- Generates bundle with:
  - All stack configuration files
  - `pull-images.sh` - Script to download all Docker images
  - `load-images.sh` - Script to load images on offline system
  - `OFFLINE-README.md` - Instructions for offline deployment
  - `INSTRUCTIONS.txt` - Step-by-step guide

## Testing Requirements

### 1. New Applications Testing

#### GitLab (T-GL001)
- [ ] Add GitLab to stack
- [ ] Configure HTTP and SSH ports
- [ ] Generate and deploy stack
- [ ] Verify GitLab web interface accessible
- [ ] Verify SSH git operations work
- [ ] Test with multiple instances (if supported)

#### Gitea (T-GT001)
- [ ] Add Gitea to stack
- [ ] Configure HTTP and SSH ports
- [ ] Generate and deploy stack
- [ ] Verify Gitea web interface accessible
- [ ] Test repository creation and operations
- [ ] Verify data persistence across restarts

#### n8n (T-N8N001)
- [ ] Add n8n to stack
- [ ] Configure authentication
- [ ] Generate and deploy stack
- [ ] Verify web interface accessible
- [ ] Test workflow creation
- [ ] Verify data persistence

#### Vault (T-VT001)
- [ ] Add Vault to stack
- [ ] Configure root token
- [ ] Generate and deploy stack
- [ ] Verify Vault UI accessible
- [ ] Test secret storage and retrieval
- [ ] Verify dev mode vs production mode settings

#### Guacamole (T-GC001)
- [ ] Add Guacamole to stack
- [ ] Configure with required database backend
- [ ] Generate and deploy stack
- [ ] Verify web interface accessible
- [ ] Test remote connection setup
- [ ] Verify authentication system

### 2. Docker Installer Testing

#### Linux Installer (T-LIN001)
- [ ] Download Linux installer from UI
- [ ] Verify script has correct permissions in ZIP
- [ ] Test on Ubuntu 22.04 (fresh install)
- [ ] Test on Debian 12 (fresh install)
- [ ] Test on CentOS/RHEL 9 (fresh install)
- [ ] Verify Docker and Docker Compose installed
- [ ] Verify systemd services enabled
- [ ] Verify user permissions configured
- [ ] Test with existing Docker installation

#### Windows Installer (T-WIN001)
- [ ] Download Windows installer from UI
- [ ] Verify PowerShell script format
- [ ] Test on Windows 11 Pro (fresh install)
- [ ] Test on Windows 10 Pro (fresh install)
- [ ] Verify WSL 2 installation
- [ ] Verify Docker Desktop installation
- [ ] Test with existing Docker Desktop

### 3. Offline Bundle Testing

#### Bundle Generation (T-OFF001)
- [ ] Select stack with multiple applications
- [ ] Click "Offline Bundle" button
- [ ] Verify bundle downloads as ZIP
- [ ] Extract and verify contents:
  - [ ] docker-compose.yml present
  - [ ] .env file present
  - [ ] pull-images.sh present
  - [ ] load-images.sh present
  - [ ] OFFLINE-README.md present
  - [ ] INSTRUCTIONS.txt present
  - [ ] All config files included

#### Bundle Execution (T-OFF002)
- [ ] On internet-connected system:
  - [ ] Extract offline bundle
  - [ ] Run `pull-images.sh`
  - [ ] Verify all images downloaded
  - [ ] Verify `docker-images.tar.gz` created
- [ ] Transfer to offline system:
  - [ ] Copy all files to offline/airgapped system
  - [ ] Run `load-images.sh`
  - [ ] Verify all images loaded with `docker images`
  - [ ] Run `docker-compose up -d`
  - [ ] Verify all services start successfully

### 4. UI/UX Testing

#### New Buttons (T-UI001)
- [ ] Verify "🐧 Linux Installer" button visible
- [ ] Verify "🪟 Windows Installer" button visible
- [ ] Verify "🔌 Offline Bundle" button visible
- [ ] Verify buttons properly styled and themed
- [ ] Verify tooltips show helpful information
- [ ] Test in dark mode
- [ ] Test in light mode

#### Version Control Category (T-UI002)
- [ ] Verify "Version Control" category appears in UI
- [ ] Verify all 4 git applications appear in category
- [ ] Verify application descriptions accurate
- [ ] Verify configuration options work
- [ ] Verify version selection works

#### Removed Applications (T-UI003)
- [ ] Verify RabbitMQ no longer appears in UI
- [ ] Verify no broken references to RabbitMQ
- [ ] Verify "Messaging & Brokers" category still works

### 5. Integration Testing

#### Multiple Git Servers (T-INT001)
- [ ] Add both Gitea and GitLab to same stack
- [ ] Verify port conflicts handled
- [ ] Verify both start successfully
- [ ] Test with different port configurations

#### Offline Bundle + New Apps (T-INT002)
- [ ] Create stack with GitLab, n8n, Vault
- [ ] Generate offline bundle
- [ ] Verify all images for new apps included
- [ ] Test offline deployment
- [ ] Verify all new apps start in offline environment

#### Full Stack with All New Features (T-INT003)
- [ ] Create comprehensive stack including:
  - [ ] Ignition
  - [ ] PostgreSQL
  - [ ] GitLab or Gitea
  - [ ] n8n
  - [ ] Vault
  - [ ] Guacamole
  - [ ] Mosquitto
- [ ] Generate stack
- [ ] Download as ZIP
- [ ] Deploy and verify all services
- [ ] Generate offline bundle
- [ ] Test offline deployment

### 6. Documentation Testing

#### README Updates (T-DOC001)
- [ ] Verify README.md reflects 28+ applications
- [ ] Verify Version Control category documented
- [ ] Verify RabbitMQ removed from documentation
- [ ] Verify new features documented:
  - [ ] Docker installers
  - [ ] Offline bundles
- [ ] Verify all links and examples work

#### Generated Documentation (T-DOC002)
- [ ] Create stack with new applications
- [ ] Generate and extract ZIP
- [ ] Verify README.md includes new apps
- [ ] Verify service URLs correct
- [ ] Verify getting started instructions accurate

## Test Execution Checklist

### Priority 1 (Critical - Must Test Before Release)
- [ ] T-UI001: New buttons display and function
- [ ] T-UI002: Version Control category works
- [ ] T-UI003: RabbitMQ removed
- [ ] T-GT001: Gitea basic functionality
- [ ] T-N8N001: n8n basic functionality
- [ ] T-OFF001: Offline bundle generation
- [ ] T-LIN001: Linux installer (Ubuntu only)
- [ ] T-DOC001: README documentation

### Priority 2 (Important - Should Test)
- [ ] T-GL001: GitLab functionality
- [ ] T-VT001: Vault functionality
- [ ] T-GC001: Guacamole functionality
- [ ] T-FJ001: Forgejo functionality
- [ ] T-OFF002: Offline bundle execution
- [ ] T-INT001: Multiple git servers

### Priority 3 (Nice to Have - Can Test Later)
- [ ] T-GS001: Gogs functionality
- [ ] T-WIN001: Windows installer
- [ ] T-INT002: Offline bundle + new apps
- [ ] T-INT003: Full stack with all new features
- [ ] T-LIN001: Linux installer (all distros)

## Success Criteria
- All Priority 1 tests pass
- At least 80% of Priority 2 tests pass
- No critical bugs discovered
- Documentation is accurate and complete
- New features work as expected in common use cases

## Known Issues / Limitations
- None identified yet - to be updated during testing

## Test Environment Requirements
- Docker Engine 20.10+ or Docker Desktop
- 8GB RAM minimum (16GB recommended for full stack)
- 50GB disk space (for offline bundle testing)
- Internet connection (for image downloads)
- Offline/airgapped system for offline bundle testing

---

**Last Updated:** $(date)
**Status:** Testing Required
