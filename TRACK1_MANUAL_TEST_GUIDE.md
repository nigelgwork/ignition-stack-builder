# Track 1 Manual Testing Guide - Session 5

**Date**: October 8, 2025
**Tests Remaining**: 14 tests (CFT-003 to CFT-005, MET-002 to MET-004, IST-001 to IST-011)
**Estimated Time**: 45 minutes
**URL**: http://localhost:3500

---

## 🎯 Test Execution Order

**Phase 1**: Core Functionality (15 min)
- CFT-003, CFT-004, CFT-005

**Phase 2**: Mutual Exclusivity (10 min)
- MET-002, MET-003, MET-004

**Phase 3**: Integration Settings UI (30 min)
- IST-001 to IST-011

---

## ✅ PHASE 1: Core Functionality Tests (15 min)

### CFT-003: Add Single Instance Service ⏳

**Objective**: Verify checkbox-based services can be added and removed

**Steps**:
1. Open http://localhost:3500
2. Locate **Grafana** in the "Monitoring & Observability" category
3. Click the **checkbox** next to Grafana
4. **VERIFY**:
   - [ ] Checkbox becomes checked ✓
   - [ ] Configuration panel appears below Grafana
   - [ ] Panel shows fields: Instance Name, Version, Port, Admin Username, Admin Password
5. Click the **checkbox** again to uncheck
6. **VERIFY**:
   - [ ] Checkbox becomes unchecked
   - [ ] Configuration panel disappears
7. Repeat with **Postgres** (Databases category)
8. **VERIFY**:
   - [ ] Same behavior: check → panel appears, uncheck → panel disappears

**Expected Result**: ✅ Service toggles on/off, config panel appears/disappears correctly

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### CFT-004: Add Multi-Instance Service ⏳

**Objective**: Verify multi-instance services support multiple instances

**Steps**:
1. Locate **Ignition** in "Industrial Platforms" category
2. Click **"+ Add Instance"** button
3. **VERIFY**:
   - [ ] Configuration panel appears
   - [ ] Instance name defaults to "ignition" (first instance)
4. Click **"+ Add Instance"** button again
5. **VERIFY**:
   - [ ] Second configuration panel appears
   - [ ] Instance name defaults to "ignition-2" (second instance)
   - [ ] Both panels visible and independent
6. Click **"Remove"** button on the first instance
7. **VERIFY**:
   - [ ] First panel disappears
   - [ ] Second panel remains (ignition-2)
8. Click **"+ Add Instance"** again
9. **VERIFY**:
   - [ ] New panel appears
   - [ ] Instance name is "ignition-3" (not "ignition-2")

**Expected Result**: ✅ Multiple instances can be added/removed independently, naming increments correctly

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### CFT-005: Configuration Fields Work ⏳

**Objective**: Verify all configuration field types accept and store input

**Steps**:
1. Add one **Ignition** instance (if not already added)
2. Locate the configuration panel for Ignition

**Test Text Input**:
3. Find **"Admin Username"** field
4. Clear the field and type: `testadmin`
5. **VERIFY**:
   - [ ] Text appears as you type
   - [ ] Field accepts the value

**Test Number Input**:
6. Find **"HTTP Port"** field
7. Clear and type: `9088`
8. **VERIFY**:
   - [ ] Only numbers accepted
   - [ ] Value updates

**Test Password Input**:
9. Find **"Admin Password"** field
10. Type: `SecurePass123`
11. **VERIFY**:
    - [ ] Text appears as dots/asterisks (masked)
    - [ ] Password is hidden

**Test Select Dropdown**:
12. Find **"Edition"** dropdown
13. Click the dropdown
14. **VERIFY**:
    - [ ] Options appear: standard, edge, maker
    - [ ] Can select different option
15. Select **"edge"**
16. **VERIFY**:
    - [ ] Selection updates

**Test Checkbox**:
17. Find **"Enable Quick Start"** checkbox
18. Click it
19. **VERIFY**:
    - [ ] Checkbox toggles checked/unchecked
    - [ ] State changes visibly

**Test Multi-Select (Modules)**:
20. Find **"Modules"** section (checkboxes for 8.1 or 8.3)
21. Click several module checkboxes (e.g., Perspective, OPC-UA, Alarm Notification)
22. **VERIFY**:
    - [ ] Each checkbox toggles independently
    - [ ] Multiple selections possible
    - [ ] Visual indication of selected modules

**Expected Result**: ✅ All field types work correctly, accept input, and display properly

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

## ✅ PHASE 2: Mutual Exclusivity Tests (10 min)

### MET-002: Visual Indication of Conflicts ⏳

**Objective**: Verify conflicting services are visually disabled

**Setup**:
1. Ensure no services are selected (start fresh or remove all)
2. Locate **Traefik** in "Networking / Proxy" category
3. Locate **Nginx Proxy Manager** in same category

**Steps**:
4. Select **Traefik** (click checkbox)
5. **VERIFY**:
   - [ ] Traefik checkbox is checked
   - [ ] Traefik configuration panel appears
6. Look at **Nginx Proxy Manager**
7. **VERIFY**:
   - [ ] Nginx Proxy Manager is **visually disabled** (greyed out, faded, or has disabled class)
   - [ ] Checkbox or button appears disabled
   - [ ] Visual indication that it cannot be selected

**Expected Result**: ✅ When Traefik is selected, Nginx Proxy Manager is visually disabled

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### MET-003: Conflict Warning Messages ⏳

**Objective**: Verify warning messages appear for conflicts

**Steps** (continuing from MET-002):
1. With **Traefik** still selected
2. Hover over or look near **Nginx Proxy Manager**
3. **VERIFY**:
   - [ ] Warning message or tooltip appears
   - [ ] Message indicates why it's disabled
   - [ ] Message mentions "reverse proxy" or "Traefik" conflict
   - [ ] Example: "Only one reverse proxy allowed. Remove Traefik first."

**Alternative**:
4. Try to click the disabled **Nginx Proxy Manager**
5. **VERIFY**:
   - [ ] Click is prevented OR
   - [ ] Warning popup/alert appears OR
   - [ ] Tooltip shows conflict reason

**Expected Result**: ✅ Clear warning message explains why service is disabled

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### MET-004: Conflict Prevention ⏳

**Objective**: Verify system prevents selecting conflicting services

**Steps**:
1. With **Traefik** selected, attempt to check **Nginx Proxy Manager**
2. **VERIFY**:
   - [ ] Click has no effect OR
   - [ ] Service doesn't get added OR
   - [ ] Alert appears preventing the action

**Reverse Test**:
3. Uncheck **Traefik** (remove it)
4. **VERIFY**:
   - [ ] Nginx Proxy Manager becomes enabled (not greyed out)
   - [ ] Can now select Nginx Proxy Manager
5. Check **Nginx Proxy Manager**
6. **VERIFY**:
   - [ ] Nginx Proxy Manager is selected
   - [ ] Configuration panel appears
7. Look at **Traefik**
8. **VERIFY**:
   - [ ] Traefik is now disabled/greyed out
   - [ ] Conflict works in both directions

**Expected Result**: ✅ System prevents selecting both Traefik and NPM simultaneously

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

## ✅ PHASE 3: Integration Settings UI Tests (30 min)

### Setup for Integration Settings Tests
**Important**: These tests verify that integration settings appear **inline** under the provider service, not in a separate section.

---

### IST-001: MQTT Settings Display ⏳

**Objective**: Verify MQTT settings appear under MQTT broker services

**Steps**:
1. Remove all selected services (start fresh)
2. Locate **EMQX** in "Messaging & Brokers" category
3. Select **EMQX** (click checkbox/add)
4. Scroll to the EMQX configuration panel
5. **VERIFY**:
   - [ ] Configuration panel appears for EMQX
   - [ ] Below the standard EMQX config fields, there's a **separator/divider**
   - [ ] Section header shows: "📡 MQTT Broker Settings" or similar
   - [ ] MQTT integration settings appear inline (not in separate section)

**Expected Result**: ✅ MQTT settings display under EMQX configuration

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-002: MQTT TLS Configuration ⏳

**Objective**: Verify MQTT TLS settings work

**Steps** (continuing from IST-001):
1. In the MQTT Broker Settings section under EMQX
2. Find **"Enable TLS/MQTTS"** checkbox
3. **VERIFY**:
   - [ ] Checkbox is present
   - [ ] Initially unchecked
4. Click the **"Enable TLS/MQTTS"** checkbox
5. **VERIFY**:
   - [ ] Checkbox becomes checked
   - [ ] **"TLS Port"** field appears (conditional display)
   - [ ] Default port shown (e.g., 8883)
6. Change TLS Port to: `8884`
7. **VERIFY**:
   - [ ] Port value updates
8. Uncheck **"Enable TLS/MQTTS"**
9. **VERIFY**:
   - [ ] TLS Port field disappears (conditional)

**Expected Result**: ✅ TLS toggle works, port field appears/disappears conditionally

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-003: MQTT Authentication ⏳

**Objective**: Verify MQTT username/password fields work

**Steps** (continuing from IST-002):
1. In MQTT Broker Settings under EMQX
2. Find **"Username (optional)"** field
3. Type: `mqtt_test_user`
4. **VERIFY**:
   - [ ] Text appears in field
5. Find **"Password (optional)"** field
6. Type: `mqtt_password_123`
7. **VERIFY**:
   - [ ] Password appears masked (dots/asterisks)
   - [ ] Password field works
8. Below these fields, find the info text
9. **VERIFY**:
   - [ ] Info text shows something like: "Will be configured for: [service names]"
   - [ ] Lists any MQTT client services selected (e.g., Ignition, Node-RED)

**Expected Result**: ✅ MQTT auth fields work, info text shows client services

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-004: Reverse Proxy Settings Display ⏳

**Objective**: Verify reverse proxy settings appear under Traefik/NPM

**Steps**:
1. Remove EMQX if selected
2. Select **Traefik** (Networking / Proxy)
3. Scroll to Traefik configuration panel
4. **VERIFY**:
   - [ ] Traefik basic config appears (ports, version, etc.)
   - [ ] Separator/divider below standard config
   - [ ] Section header: "🌐 Reverse Proxy Settings" or similar
   - [ ] Reverse proxy settings appear inline under Traefik

**Expected Result**: ✅ Reverse proxy settings display under Traefik

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-005: Reverse Proxy Domain Configuration ⏳

**Objective**: Verify base domain field works

**Steps** (continuing from IST-004):
1. In Reverse Proxy Settings section
2. Find **"Base Domain"** field
3. **VERIFY**:
   - [ ] Field exists
   - [ ] Default value: "localhost"
4. Clear and type: `example.com`
5. **VERIFY**:
   - [ ] Value updates to example.com

**Expected Result**: ✅ Base domain field accepts input

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-006: Reverse Proxy HTTPS Toggle ⏳

**Objective**: Verify HTTPS enable toggle works

**Steps** (continuing from IST-005):
1. Find **"Enable HTTPS"** checkbox
2. **VERIFY**:
   - [ ] Checkbox exists
   - [ ] Initially unchecked
3. Check the **"Enable HTTPS"** checkbox
4. **VERIFY**:
   - [ ] Checkbox becomes checked
   - [ ] **"Let's Encrypt Email"** field appears (conditional)
5. Type email in Let's Encrypt field: `admin@example.com`
6. **VERIFY**:
   - [ ] Email field accepts input
7. Uncheck **"Enable HTTPS"**
8. **VERIFY**:
   - [ ] Email field disappears

**Expected Result**: ✅ HTTPS toggle works, email field conditional

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-007: OAuth Settings Display ⏳

**Objective**: Verify OAuth settings appear under Keycloak

**Steps**:
1. Remove Traefik
2. Select **Keycloak** (Authentication & Identity)
3. Scroll to Keycloak configuration panel
4. **VERIFY**:
   - [ ] Keycloak basic config appears
   - [ ] Separator/divider below
   - [ ] Section header: "🔐 OAuth/SSO Settings" or similar
   - [ ] OAuth settings appear inline under Keycloak

**Expected Result**: ✅ OAuth settings display under Keycloak

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-008: OAuth Realm Configuration ⏳

**Objective**: Verify OAuth realm name field works

**Steps** (continuing from IST-007):
1. In OAuth/SSO Settings section
2. Find **"Realm Name"** field
3. **VERIFY**:
   - [ ] Field exists
   - [ ] Default value: "iiot" or similar
4. Clear and type: `production`
5. **VERIFY**:
   - [ ] Value updates to production

**Expected Result**: ✅ Realm name field works

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-009: OAuth Auto-Configure Toggle ⏳

**Objective**: Verify auto-configure toggle works

**Steps** (continuing from IST-008):
1. Find **"Auto-Configure Services"** checkbox
2. **VERIFY**:
   - [ ] Checkbox exists
   - [ ] Initially checked (default true)
3. Uncheck it
4. **VERIFY**:
   - [ ] Checkbox becomes unchecked
5. Check it again
6. **VERIFY**:
   - [ ] Returns to checked state
7. Below settings, find info text
8. **VERIFY**:
   - [ ] Info shows which services will be configured
   - [ ] Lists OAuth client services (e.g., Grafana, Portainer)

**Expected Result**: ✅ Auto-configure toggle works, shows client list

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-010: Email Settings Display ⏳

**Objective**: Verify email settings appear under MailHog

**Steps**:
1. Remove Keycloak
2. Select **MailHog** (DevOps Tools)
3. Scroll to MailHog configuration panel
4. **VERIFY**:
   - [ ] MailHog basic config appears (SMTP port, Web UI port)
   - [ ] Separator/divider below
   - [ ] Section header: "📧 Email Testing Settings" or similar
   - [ ] Email settings appear inline under MailHog

**Expected Result**: ✅ Email settings display under MailHog

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

### IST-011: Email Configuration ⏳

**Objective**: Verify email from address field works

**Steps** (continuing from IST-010):
1. In Email Testing Settings section
2. Find **"From Address"** field
3. **VERIFY**:
   - [ ] Field exists
   - [ ] Default: "noreply@iiot.local" or similar
4. Clear and type: `test@example.com`
5. **VERIFY**:
   - [ ] Value updates
6. Find **"Auto-Configure Services"** checkbox
7. **VERIFY**:
   - [ ] Checkbox exists
8. Toggle it on/off
9. **VERIFY**:
   - [ ] Checkbox state changes
10. Below settings, check for info text
11. **VERIFY**:
    - [ ] Shows which services will use email testing
    - [ ] Lists email clients (e.g., Ignition, Grafana)

**Expected Result**: ✅ Email config fields work, shows client list

**Actual Result**: [ ] PASS [ ] FAIL

**Notes**:


---

## 📊 Test Results Summary

### Core Functionality Tests
- [ ] CFT-003: Add Single Instance Service
- [ ] CFT-004: Add Multi-Instance Service
- [ ] CFT-005: Configuration Fields Work

### Mutual Exclusivity Tests
- [ ] MET-002: Visual Indication of Conflicts
- [ ] MET-003: Conflict Warning Messages
- [ ] MET-004: Conflict Prevention

### Integration Settings UI Tests
- [ ] IST-001: MQTT Settings Display
- [ ] IST-002: MQTT TLS Configuration
- [ ] IST-003: MQTT Authentication
- [ ] IST-004: Reverse Proxy Settings Display
- [ ] IST-005: Reverse Proxy Domain Configuration
- [ ] IST-006: Reverse Proxy HTTPS Toggle
- [ ] IST-007: OAuth Settings Display
- [ ] IST-008: OAuth Realm Configuration
- [ ] IST-009: OAuth Auto-Configure Toggle
- [ ] IST-010: Email Settings Display
- [ ] IST-011: Email Configuration

**Total**: 0/14 Completed

**Pass Rate**: ____%

---

## 🐛 Issues Found

| Test ID | Issue Description | Severity | Screenshot/Notes |
|---------|------------------|----------|------------------|
|         |                  |          |                  |
|         |                  |          |                  |

---

## ✅ Final Status

**Tests Passed**: ___/14
**Tests Failed**: ___/14
**Completion**: ___%

**Overall Assessment**: [ ] PASS [ ] FAIL

**Tester**: ________________
**Date Completed**: ________________
**Time Taken**: ________________

---

## 📝 Notes

(Add any additional observations, recommendations, or issues here)

