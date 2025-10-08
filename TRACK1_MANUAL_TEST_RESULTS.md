# Track 1 Manual Test Results - Session 5

**Date**: October 8, 2025
**Test Session**: Session 5 (Continuation from Oct 4-7)
**Tester**: Manual UI Testing
**Test Environment**: http://localhost:3500
**Total Tests**: 14 tests

---

## 📊 Test Summary

| Phase | Tests | Passed | Failed | Pending | Pass Rate |
|-------|-------|--------|--------|---------|-----------|
| **Phase 1: Core Functionality** | 3 | 0 | 0 | 3 | 0% |
| **Phase 2: Mutual Exclusivity** | 3 | 0 | 0 | 3 | 0% |
| **Phase 3: Integration Settings UI** | 11 | 0 | 0 | 11 | 0% |
| **TOTAL** | **17** | **0** | **0** | **17** | **0%** |

---

## ✅ PHASE 1: Core Functionality Tests (0/3)

### CFT-003: Add Single Instance Service ⏳ PENDING

**Objective**: Verify checkbox-based services can be added and removed

**Test Execution**:
- [ ] Step 1: Opened http://localhost:3500
- [ ] Step 2: Located Grafana in "Monitoring & Observability" category
- [ ] Step 3: Clicked checkbox next to Grafana
- [ ] Step 4: Verified checkbox becomes checked ✓
- [ ] Step 5: Verified configuration panel appears below Grafana
- [ ] Step 6: Verified panel shows: Instance Name, Version, Port, Admin Username, Admin Password
- [ ] Step 7: Clicked checkbox again to uncheck
- [ ] Step 8: Verified checkbox becomes unchecked
- [ ] Step 9: Verified configuration panel disappears
- [ ] Step 10: Repeated test with Postgres
- [ ] Step 11: Verified same behavior for Postgres

**Expected Result**: ✅ Service toggles on/off, config panel appears/disappears correctly

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### CFT-004: Add Multi-Instance Service ⏳ PENDING

**Objective**: Verify multi-instance services support multiple instances

**Test Execution**:
- [ ] Step 1: Located Ignition in "Industrial Platforms" category
- [ ] Step 2: Clicked "+ Add Instance" button
- [ ] Step 3: Verified configuration panel appears
- [ ] Step 4: Verified instance name defaults to "ignition"
- [ ] Step 5: Clicked "+ Add Instance" button again
- [ ] Step 6: Verified second configuration panel appears
- [ ] Step 7: Verified instance name defaults to "ignition-2"
- [ ] Step 8: Verified both panels visible and independent
- [ ] Step 9: Clicked "Remove" button on first instance
- [ ] Step 10: Verified first panel disappears
- [ ] Step 11: Verified second panel remains (ignition-2)
- [ ] Step 12: Clicked "+ Add Instance" again
- [ ] Step 13: Verified new panel appears with name "ignition-3"

**Expected Result**: ✅ Multiple instances can be added/removed independently, naming increments correctly

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### CFT-005: Configuration Fields Work ⏳ PENDING

**Objective**: Verify all configuration field types accept and store input

**Test Execution**:

**Text Input**:
- [ ] Step 1: Added one Ignition instance
- [ ] Step 2: Found "Admin Username" field
- [ ] Step 3: Cleared field and typed: `testadmin`
- [ ] Step 4: Verified text appears as you type
- [ ] Step 5: Verified field accepts the value

**Number Input**:
- [ ] Step 6: Found "HTTP Port" field
- [ ] Step 7: Cleared and typed: `9088`
- [ ] Step 8: Verified only numbers accepted
- [ ] Step 9: Verified value updates

**Password Input**:
- [ ] Step 10: Found "Admin Password" field
- [ ] Step 11: Typed: `SecurePass123`
- [ ] Step 12: Verified text appears as dots/asterisks (masked)
- [ ] Step 13: Verified password is hidden

**Select Dropdown**:
- [ ] Step 14: Found "Edition" dropdown
- [ ] Step 15: Clicked the dropdown
- [ ] Step 16: Verified options appear: standard, edge, maker
- [ ] Step 17: Selected "edge"
- [ ] Step 18: Verified selection updates

**Checkbox**:
- [ ] Step 19: Found "Enable Quick Start" checkbox
- [ ] Step 20: Clicked it
- [ ] Step 21: Verified checkbox toggles checked/unchecked
- [ ] Step 22: Verified state changes visibly

**Multi-Select (Modules)**:
- [ ] Step 23: Found "Modules" section
- [ ] Step 24: Clicked several module checkboxes (Perspective, OPC-UA, Alarm Notification)
- [ ] Step 25: Verified each checkbox toggles independently
- [ ] Step 26: Verified multiple selections possible
- [ ] Step 27: Verified visual indication of selected modules

**Expected Result**: ✅ All field types work correctly, accept input, and display properly

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

## ✅ PHASE 2: Mutual Exclusivity Tests (0/3)

### MET-002: Visual Indication of Conflicts ⏳ PENDING

**Objective**: Verify conflicting services are visually disabled

**Test Execution**:
- [ ] Step 1: Ensured no services are selected (start fresh)
- [ ] Step 2: Located Traefik in "Networking / Proxy" category
- [ ] Step 3: Located Nginx Proxy Manager in same category
- [ ] Step 4: Selected Traefik (clicked checkbox)
- [ ] Step 5: Verified Traefik checkbox is checked
- [ ] Step 6: Verified Traefik configuration panel appears
- [ ] Step 7: Looked at Nginx Proxy Manager
- [ ] Step 8: Verified Nginx Proxy Manager is visually disabled (greyed out, faded, disabled class)
- [ ] Step 9: Verified checkbox or button appears disabled
- [ ] Step 10: Verified visual indication that it cannot be selected

**Expected Result**: ✅ When Traefik is selected, Nginx Proxy Manager is visually disabled

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### MET-003: Conflict Warning Messages ⏳ PENDING

**Objective**: Verify warning messages appear for conflicts

**Test Execution**:
- [ ] Step 1: With Traefik still selected (from MET-002)
- [ ] Step 2: Hovered over Nginx Proxy Manager
- [ ] Step 3: Verified warning message or tooltip appears
- [ ] Step 4: Verified message indicates why it's disabled
- [ ] Step 5: Verified message mentions "reverse proxy" or "Traefik" conflict
- [ ] Step 6: Verified message example: "Only one reverse proxy allowed. Remove Traefik first."

**Alternative Test**:
- [ ] Step 7: Tried to click disabled Nginx Proxy Manager
- [ ] Step 8: Verified click is prevented OR warning popup/alert appears OR tooltip shows conflict reason

**Expected Result**: ✅ Clear warning message explains why service is disabled

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### MET-004: Conflict Prevention ⏳ PENDING

**Objective**: Verify system prevents selecting conflicting services

**Test Execution**:
- [ ] Step 1: With Traefik selected, attempted to check Nginx Proxy Manager
- [ ] Step 2: Verified click has no effect OR service doesn't get added OR alert appears preventing action

**Reverse Test**:
- [ ] Step 3: Unchecked Traefik (removed it)
- [ ] Step 4: Verified Nginx Proxy Manager becomes enabled (not greyed out)
- [ ] Step 5: Verified can now select Nginx Proxy Manager
- [ ] Step 6: Checked Nginx Proxy Manager
- [ ] Step 7: Verified Nginx Proxy Manager is selected
- [ ] Step 8: Verified configuration panel appears
- [ ] Step 9: Looked at Traefik
- [ ] Step 10: Verified Traefik is now disabled/greyed out
- [ ] Step 11: Verified conflict works in both directions

**Expected Result**: ✅ System prevents selecting both Traefik and NPM simultaneously

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

## ✅ PHASE 3: Integration Settings UI Tests (0/11)

### IST-001: MQTT Settings Display ⏳ PENDING

**Objective**: Verify MQTT settings appear under MQTT broker services

**Test Execution**:
- [ ] Step 1: Removed all selected services (start fresh)
- [ ] Step 2: Located EMQX in "Messaging & Brokers" category
- [ ] Step 3: Selected EMQX (clicked checkbox/add)
- [ ] Step 4: Scrolled to EMQX configuration panel
- [ ] Step 5: Verified configuration panel appears for EMQX
- [ ] Step 6: Verified separator/divider below standard EMQX config fields
- [ ] Step 7: Verified section header shows: "📡 MQTT Broker Settings" or similar
- [ ] Step 8: Verified MQTT integration settings appear inline (not in separate section)

**Expected Result**: ✅ MQTT settings display under EMQX configuration

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-002: MQTT TLS Configuration ⏳ PENDING

**Objective**: Verify MQTT TLS settings work

**Test Execution**:
- [ ] Step 1: In MQTT Broker Settings section under EMQX (from IST-001)
- [ ] Step 2: Found "Enable TLS/MQTTS" checkbox
- [ ] Step 3: Verified checkbox is present
- [ ] Step 4: Verified initially unchecked
- [ ] Step 5: Clicked "Enable TLS/MQTTS" checkbox
- [ ] Step 6: Verified checkbox becomes checked
- [ ] Step 7: Verified "TLS Port" field appears (conditional display)
- [ ] Step 8: Verified default port shown (e.g., 8883)
- [ ] Step 9: Changed TLS Port to: `8884`
- [ ] Step 10: Verified port value updates
- [ ] Step 11: Unchecked "Enable TLS/MQTTS"
- [ ] Step 12: Verified TLS Port field disappears (conditional)

**Expected Result**: ✅ TLS toggle works, port field appears/disappears conditionally

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-003: MQTT Authentication ⏳ PENDING

**Objective**: Verify MQTT username/password fields work

**Test Execution**:
- [ ] Step 1: In MQTT Broker Settings under EMQX (from IST-002)
- [ ] Step 2: Found "Username (optional)" field
- [ ] Step 3: Typed: `mqtt_test_user`
- [ ] Step 4: Verified text appears in field
- [ ] Step 5: Found "Password (optional)" field
- [ ] Step 6: Typed: `mqtt_password_123`
- [ ] Step 7: Verified password appears masked (dots/asterisks)
- [ ] Step 8: Verified password field works
- [ ] Step 9: Found info text below fields
- [ ] Step 10: Verified info text shows: "Will be configured for: [service names]"
- [ ] Step 11: Verified lists any MQTT client services selected (e.g., Ignition, Node-RED)

**Expected Result**: ✅ MQTT auth fields work, info text shows client services

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-004: Reverse Proxy Settings Display ⏳ PENDING

**Objective**: Verify reverse proxy settings appear under Traefik/NPM

**Test Execution**:
- [ ] Step 1: Removed EMQX if selected
- [ ] Step 2: Selected Traefik (Networking / Proxy)
- [ ] Step 3: Scrolled to Traefik configuration panel
- [ ] Step 4: Verified Traefik basic config appears (ports, version, etc.)
- [ ] Step 5: Verified separator/divider below standard config
- [ ] Step 6: Verified section header: "🌐 Reverse Proxy Settings" or similar
- [ ] Step 7: Verified reverse proxy settings appear inline under Traefik

**Expected Result**: ✅ Reverse proxy settings display under Traefik

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-005: Reverse Proxy Domain Configuration ⏳ PENDING

**Objective**: Verify base domain field works

**Test Execution**:
- [ ] Step 1: In Reverse Proxy Settings section (from IST-004)
- [ ] Step 2: Found "Base Domain" field
- [ ] Step 3: Verified field exists
- [ ] Step 4: Verified default value: "localhost"
- [ ] Step 5: Cleared and typed: `example.com`
- [ ] Step 6: Verified value updates to example.com

**Expected Result**: ✅ Base domain field accepts input

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-006: Reverse Proxy HTTPS Toggle ⏳ PENDING

**Objective**: Verify HTTPS enable toggle works

**Test Execution**:
- [ ] Step 1: Found "Enable HTTPS" checkbox (from IST-005)
- [ ] Step 2: Verified checkbox exists
- [ ] Step 3: Verified initially unchecked
- [ ] Step 4: Checked "Enable HTTPS" checkbox
- [ ] Step 5: Verified checkbox becomes checked
- [ ] Step 6: Verified "Let's Encrypt Email" field appears (conditional)
- [ ] Step 7: Typed email: `admin@example.com`
- [ ] Step 8: Verified email field accepts input
- [ ] Step 9: Unchecked "Enable HTTPS"
- [ ] Step 10: Verified email field disappears

**Expected Result**: ✅ HTTPS toggle works, email field conditional

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-007: OAuth Settings Display ⏳ PENDING

**Objective**: Verify OAuth settings appear under Keycloak

**Test Execution**:
- [ ] Step 1: Removed Traefik
- [ ] Step 2: Selected Keycloak (Authentication & Identity)
- [ ] Step 3: Scrolled to Keycloak configuration panel
- [ ] Step 4: Verified Keycloak basic config appears
- [ ] Step 5: Verified separator/divider below
- [ ] Step 6: Verified section header: "🔐 OAuth/SSO Settings" or similar
- [ ] Step 7: Verified OAuth settings appear inline under Keycloak

**Expected Result**: ✅ OAuth settings display under Keycloak

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-008: OAuth Realm Configuration ⏳ PENDING

**Objective**: Verify OAuth realm name field works

**Test Execution**:
- [ ] Step 1: In OAuth/SSO Settings section (from IST-007)
- [ ] Step 2: Found "Realm Name" field
- [ ] Step 3: Verified field exists
- [ ] Step 4: Verified default value: "iiot" or similar
- [ ] Step 5: Cleared and typed: `production`
- [ ] Step 6: Verified value updates to production

**Expected Result**: ✅ Realm name field works

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-009: OAuth Auto-Configure Toggle ⏳ PENDING

**Objective**: Verify auto-configure toggle works

**Test Execution**:
- [ ] Step 1: Found "Auto-Configure Services" checkbox (from IST-008)
- [ ] Step 2: Verified checkbox exists
- [ ] Step 3: Verified initially checked (default true)
- [ ] Step 4: Unchecked it
- [ ] Step 5: Verified checkbox becomes unchecked
- [ ] Step 6: Checked it again
- [ ] Step 7: Verified returns to checked state
- [ ] Step 8: Found info text below settings
- [ ] Step 9: Verified info shows which services will be configured
- [ ] Step 10: Verified lists OAuth client services (e.g., Grafana, Portainer)

**Expected Result**: ✅ Auto-configure toggle works, shows client list

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-010: Email Settings Display ⏳ PENDING

**Objective**: Verify email settings appear under MailHog

**Test Execution**:
- [ ] Step 1: Removed Keycloak
- [ ] Step 2: Selected MailHog (DevOps Tools)
- [ ] Step 3: Scrolled to MailHog configuration panel
- [ ] Step 4: Verified MailHog basic config appears (SMTP port, Web UI port)
- [ ] Step 5: Verified separator/divider below
- [ ] Step 6: Verified section header: "📧 Email Testing Settings" or similar
- [ ] Step 7: Verified email settings appear inline under MailHog

**Expected Result**: ✅ Email settings display under MailHog

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

### IST-011: Email Configuration ⏳ PENDING

**Objective**: Verify email from address field works

**Test Execution**:
- [ ] Step 1: In Email Testing Settings section (from IST-010)
- [ ] Step 2: Found "From Address" field
- [ ] Step 3: Verified field exists
- [ ] Step 4: Verified default: "noreply@iiot.local" or similar
- [ ] Step 5: Cleared and typed: `test@example.com`
- [ ] Step 6: Verified value updates
- [ ] Step 7: Found "Auto-Configure Services" checkbox
- [ ] Step 8: Verified checkbox exists
- [ ] Step 9: Toggled it on/off
- [ ] Step 10: Verified checkbox state changes
- [ ] Step 11: Checked for info text below settings
- [ ] Step 12: Verified shows which services will use email testing
- [ ] Step 13: Verified lists email clients (e.g., Ignition, Grafana)

**Expected Result**: ✅ Email config fields work, shows client list

**Actual Result**: ⏳ PENDING

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:


**Screenshots**:


**Issues Found**:


---

## 🐛 Issues Found

| Test ID | Issue Description | Severity | Status | Notes |
|---------|------------------|----------|--------|-------|
|         |                  |          |        |       |
|         |                  |          |        |       |

---

## ✅ Test Environment

**Application URL**: http://localhost:3500
**Backend API**: http://localhost:8000
**Backend Status**: Up 2 hours
**Frontend Status**: Up 2 hours
**Platform**: Linux WSL2
**Browser**: (To be specified by tester)

---

## 📊 Final Results

**Tests Executed**: 0/17
**Tests Passed**: 0
**Tests Failed**: 0
**Tests Blocked**: 0
**Pass Rate**: 0%

**Overall Status**: ⏳ PENDING

---

## 📝 Testing Notes

### Session Start
- Date: October 8, 2025
- Time: (To be recorded)
- Frontend confirmed accessible
- Backend confirmed responding
- Catalog verified: 26 apps, 11 categories

### Session End
- Date: ________________
- Time: ________________
- Duration: ________________

### General Observations

(Add any general observations about the UI, performance, or user experience here)

---

**Test Guide Reference**: See `TRACK1_MANUAL_TEST_GUIDE.md` for detailed step-by-step instructions.
