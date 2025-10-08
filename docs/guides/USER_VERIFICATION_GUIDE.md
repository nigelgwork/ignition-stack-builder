# User Verification Guide

**Quick Start:** Open http://localhost:3500 and follow the checklist below

---

## ✅ 5-Minute Quick Verification

### Step 1: Check New UI Buttons (1 min)
**Where:** Right sidebar in the UI

Look for these buttons:
- [ ] **📦 Download Stack (.zip)** - Updated with emoji
- [ ] **🔌 Offline Bundle** - NEW button for airgapped deployments
- [ ] **💾 Save Config** - Existing button
- [ ] **📂 Load Config** - Existing button

Scroll down in right sidebar:
- [ ] **Section header: "🐳 Docker Installers"** - NEW section
- [ ] **🐧 Linux Installer** - NEW button
- [ ] **🪟 Windows Installer** - NEW button

**Expected Result:** All 7 buttons visible and properly styled

---

### Step 2: Verify Version Control Category (1 min)
**Where:** Main content area, scroll through categories

Find the "Version Control" category and verify:
- [ ] **GitLab** - with description "Complete DevOps platform..."
- [ ] **Gitea** - with description "Lightweight self-hosted Git service"
- [ ] **NO Forgejo** - should NOT appear
- [ ] **NO Gogs** - should NOT appear
- [ ] **NO RabbitMQ** - should NOT appear anywhere

**Expected Result:** Exactly 2 apps in Version Control category

---

### Step 3: Check Newly Enabled Apps (2 min)
**Where:** Various categories throughout the UI

Find and verify these are NOW selectable (not "Coming Soon"):

**Messaging & Brokers:**
- [ ] **Mosquitto** - has checkbox or "Add Instance" button

**Automation / Workflow:**
- [ ] **n8n** - has checkbox or "Add Instance" button

**Security & Secrets:**
- [ ] **Vault** - has checkbox or "Add Instance" button

**Remote Access:**
- [ ] **Guacamole** - has checkbox or "Add Instance" button

**Expected Result:** All 4 apps have active controls (not disabled)

---

### Step 4: Test Installer Downloads (1 min)
**Action:** Click the installer buttons

1. Click **🐧 Linux Installer**
   - [ ] File downloads: `install-docker-linux.sh`
   - [ ] File size: ~5-6 KB
   - [ ] Open file and verify it's a bash script (starts with `#!/bin/bash`)

2. Click **🪟 Windows Installer**
   - [ ] File downloads: `install-docker-windows.ps1`
   - [ ] File size: ~6 KB
   - [ ] Open file and verify it's a PowerShell script

**Expected Result:** Both files download successfully and are readable scripts

---

## ✅ 10-Minute Extended Verification

### Step 5: Test Offline Bundle (5 min)
**Action:** Download offline deployment bundle

1. Select some services (e.g., Gitea + Postgres)
2. Click **🔌 Offline Bundle**
3. File downloads: `iiot-stack-offline-bundle.zip`
4. Extract the ZIP file
5. Verify it contains:
   - [ ] `docker-compose.yml` - stack configuration
   - [ ] `.env` - environment variables
   - [ ] `README.md` - regular README
   - [ ] `OFFLINE-README.md` - offline deployment guide
   - [ ] `INSTRUCTIONS.txt` - step-by-step instructions
   - [ ] `pull-images.sh` - script to download Docker images
   - [ ] `load-images.sh` - script to load images on offline system
   - [ ] `configs/` directory - service configurations

**Expected Result:** ZIP contains all 8 items listed above

---

### Step 6: Test Gitea Deployment (5 min)
**Action:** Deploy Gitea using the UI

1. In UI, select **Gitea** (from Version Control category)
2. Configure:
   - Instance Name: `gitea`
   - HTTP Port: `3100` (3000 may be in use)
   - SSH Port: `2222`
3. Click **📦 Download Stack (.zip)**
4. Extract the ZIP file
5. Open terminal in extracted folder
6. Run: `docker-compose up -d`
7. Wait ~30 seconds
8. Open browser: http://localhost:3100
9. Verify Gitea installation page loads

**Expected Result:** Gitea web interface accessible and shows installation wizard

**Cleanup:**
```bash
docker-compose down -v
```

---

## ✅ 20-Minute Full Verification

### Step 7: Test n8n Deployment (5 min)
**Action:** Deploy n8n workflow automation

1. Select **n8n** (from Automation / Workflow category)
2. Configure:
   - Port: `5678`
   - Username: `admin`
   - Password: `admin123`
3. Download stack and deploy
4. Open: http://localhost:5678
5. Login with credentials
6. Verify dashboard loads

**Cleanup:**
```bash
docker-compose down -v
```

---

### Step 8: Test Vault Deployment (5 min)
**Action:** Deploy HashiCorp Vault

1. Select **Vault** (from Security & Secrets category)
2. Configure:
   - Port: `8200`
   - Root Token: `dev-root-token`
3. Download stack and deploy
4. Open: http://localhost:8200
5. Login with root token
6. Verify Vault UI loads

**Cleanup:**
```bash
docker-compose down -v
```

---

### Step 9: Test Multi-Service Stack (10 min)
**Action:** Create comprehensive stack

1. Select multiple services:
   - Gitea (port 3100)
   - Postgres (port 5432)
   - n8n (port 5678)
   - Mosquitto (default ports)
2. Download stack
3. Deploy: `docker-compose up -d`
4. Check all services:
   - [ ] `docker-compose ps` - all show "Up"
   - [ ] http://localhost:3100 - Gitea
   - [ ] http://localhost:5678 - n8n
   - [ ] Postgres: `docker exec -it postgres psql -U postgres`
5. Verify no port conflicts

**Cleanup:**
```bash
docker-compose down -v
```

---

## 📊 Verification Results

### Quick Verification (5 min)
- [ ] All new buttons visible
- [ ] Version Control category correct
- [ ] Newly enabled apps working
- [ ] Installer downloads work

**Result:** □ PASS □ FAIL

### Extended Verification (10 min)
- [ ] Offline bundle downloads with correct files
- [ ] Gitea deploys and web UI loads

**Result:** □ PASS □ FAIL

### Full Verification (20 min)
- [ ] n8n deploys successfully
- [ ] Vault deploys successfully
- [ ] Multi-service stack works

**Result:** □ PASS □ FAIL

---

## 🚨 Troubleshooting

### Issue: Buttons not visible in UI
**Solution:**
```bash
cd /git/ignition-stack-builder
docker-compose build frontend
docker-compose up -d frontend
# Refresh browser (Ctrl+F5)
```

### Issue: Port already in use
**Solution:** Change the port in the UI configuration before downloading, or:
```bash
docker ps | grep <port>  # Find what's using it
docker stop <container>   # Stop the conflicting container
```

### Issue: Download files are empty
**Solution:**
```bash
cd /git/ignition-stack-builder
docker-compose restart backend
```

---

## ✅ Automated Test Results

**All automated tests PASSED (10/10)**

See `AUTOMATED_TEST_RESULTS.md` for detailed results:
- ✅ Catalog verification (26 apps, Version Control category)
- ✅ Installer downloads (Linux & Windows scripts)
- ✅ Stack generation and download
- ✅ Offline bundle generation
- ✅ Gitea deployment and web interface

---

## 📞 Next Steps

1. **Complete Quick Verification** (5 min) - Start here!
2. **Test Extended Features** (optional, 10 min)
3. **Report any issues** found during testing
4. **Deploy to production** once verified

---

**Last Updated:** October 8, 2025
**UI URL:** http://localhost:3500
**Backend API:** http://localhost:8000
