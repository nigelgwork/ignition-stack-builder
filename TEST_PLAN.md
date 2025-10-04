# IIoT Stack Builder - Comprehensive Test Plan

**Version**: 1.0
**Date**: 2025-10-04
**Test Environment**: http://localhost:3500 (Frontend) | http://localhost:8000 (Backend)

---

## Test Categories

1. [Core Functionality Tests](#core-functionality-tests)
2. [Integration Detection Tests](#integration-detection-tests)
3. [Mutual Exclusivity Tests](#mutual-exclusivity-tests)
4. [Integration Settings UI Tests](#integration-settings-ui-tests)
5. [Backend API Tests](#backend-api-tests)
6. [Docker Compose Generation Tests](#docker-compose-generation-tests)
7. [Edge Cases & Error Handling](#edge-cases--error-handling)
8. [Performance Tests](#performance-tests)

---

## Core Functionality Tests

### CFT-001: Application Loads Successfully
**Objective**: Verify the frontend loads without errors
**Steps**:
1. Navigate to http://localhost:3500
2. Check browser console for errors
3. Verify UI renders completely

**Expected Result**: UI loads, no console errors, all sections visible
**Status**: PENDING
**Result**:

---

### CFT-002: Catalog Loads All Services
**Objective**: Verify all 24+ services are displayed
**Steps**:
1. Check each category has services
2. Verify enabled services are clickable
3. Verify "Coming Soon" services are disabled

**Expected Result**: All services displayed, categorized correctly
**Status**: PENDING
**Result**:

---

### CFT-003: Add Single Instance Service
**Objective**: Verify checkbox-based services can be added
**Steps**:
1. Select a single-instance service (e.g., Grafana)
2. Verify checkbox is checked
3. Verify configuration panel appears
4. Uncheck the service
5. Verify configuration panel disappears

**Expected Result**: Service toggles on/off correctly
**Status**: PENDING
**Result**:

---

### CFT-004: Add Multi-Instance Service
**Objective**: Verify multi-instance services can be added
**Steps**:
1. Click "+ Add Instance" on Ignition
2. Verify "ignition-1" configuration appears
3. Click "+ Add Instance" again
4. Verify "ignition-2" configuration appears
5. Remove "ignition-1"
6. Verify only "ignition-2" remains

**Expected Result**: Multiple instances can be added/removed independently
**Status**: PENDING
**Result**:

---

### CFT-005: Configuration Fields Work
**Objective**: Verify all config field types work
**Steps**:
1. Add Ignition instance
2. Test text input (admin username)
3. Test number input (port)
4. Test password input (admin password)
5. Test select dropdown (edition)
6. Test checkbox (Quick Start)
7. Test multi-select checkboxes (modules)

**Expected Result**: All field types accept and store input
**Status**: PENDING
**Result**:

---

### CFT-006: Global Settings Work
**Objective**: Verify global settings can be changed
**Steps**:
1. Change timezone to "UTC"
2. Change restart policy to "always"
3. Verify values persist when switching between services

**Expected Result**: Global settings update correctly
**Status**: PENDING
**Result**:

---

## Integration Detection Tests

### IDT-001: Reverse Proxy Detection
**Objective**: Detect Traefik + web services integration
**Steps**:
1. Add Traefik
2. Add Ignition
3. Verify Integration Status appears
4. Check for reverse_proxy integration in status

**Expected Result**: Detects Traefik → Ignition routing
**Status**: PENDING
**Result**:

---

### IDT-002: MQTT Broker Detection
**Objective**: Detect MQTT broker + client integration
**Steps**:
1. Add EMQX
2. Add Ignition
3. Verify mqtt_broker integration detected
4. Check Integration Settings shows MQTT options

**Expected Result**: Detects EMQX → Ignition MQTT connection
**Status**: PENDING
**Result**:

---

### IDT-003: OAuth Provider Detection
**Objective**: Detect OAuth provider + clients
**Steps**:
1. Add Keycloak
2. Add Grafana
3. Verify oauth_provider integration detected
4. Check "Will configure: grafana" message appears

**Expected Result**: Detects Keycloak → Grafana OAuth
**Status**: PENDING
**Result**:

---

### IDT-004: Database Integration Detection
**Objective**: Detect database + client connections
**Steps**:
1. Add PostgreSQL
2. Add Ignition
3. Add Grafana
4. Verify db_provider integration detected
5. Check multiple clients detected (Ignition, Grafana)

**Expected Result**: Detects PostgreSQL → Ignition + Grafana
**Status**: PENDING
**Result**:

---

### IDT-005: Email Integration Detection
**Objective**: Detect MailHog + email clients
**Steps**:
1. Add MailHog
2. Add Grafana
3. Add Ignition
4. Verify email_testing integration detected

**Expected Result**: Detects MailHog → clients
**Status**: PENDING
**Result**:

---

### IDT-006: Visualization Integration Detection
**Objective**: Detect Grafana + datasources
**Steps**:
1. Add Grafana
2. Add Prometheus
3. Add PostgreSQL
4. Verify visualization integration detected
5. Check datasources list includes both

**Expected Result**: Detects Grafana datasources
**Status**: PENDING
**Result**:

---

### IDT-007: Multiple Integrations Simultaneously
**Objective**: Detect multiple integration types at once
**Steps**:
1. Add Traefik + Keycloak + PostgreSQL + EMQX + Grafana + Ignition
2. Verify all integration types detected:
   - reverse_proxy
   - oauth_provider
   - db_provider
   - mqtt_broker
   - visualization

**Expected Result**: All 5 integration types detected correctly
**Status**: PENDING
**Result**:

---

## Mutual Exclusivity Tests

### MET-001: Traefik Disables NPM
**Objective**: Verify selecting Traefik disables Nginx Proxy Manager
**Steps**:
1. Add Traefik
2. Navigate to Reverse Proxies category
3. Verify Nginx Proxy Manager is greyed out
4. Verify lock icon (🔒) appears
5. Verify reason message displays
6. Try to click NPM (should not work)

**Expected Result**: NPM disabled and greyed out
**Status**: PENDING
**Result**:

---

### MET-002: NPM Disables Traefik
**Objective**: Verify selecting NPM disables Traefik
**Steps**:
1. Clear all selections
2. Add Nginx Proxy Manager
3. Navigate to Reverse Proxies category
4. Verify Traefik is greyed out
5. Verify lock icon appears

**Expected Result**: Traefik disabled and greyed out
**Status**: PENDING
**Result**:

---

### MET-003: Removing Proxy Re-enables Alternative
**Objective**: Verify removing one proxy re-enables the other
**Steps**:
1. Add Traefik (NPM should be disabled)
2. Remove Traefik
3. Verify NPM is now enabled (not greyed out)
4. Verify lock icon removed

**Expected Result**: NPM re-enabled when Traefik removed
**Status**: PENDING
**Result**:

---

### MET-004: Conflict Reported in Integration Status
**Objective**: Verify conflicts show in Integration Status
**Steps**:
1. Use browser dev tools to bypass UI and add both
2. Check Integration Status for conflict message

**Expected Result**: Conflict error message appears
**Status**: PENDING
**Result**:

---

## Integration Settings UI Tests

### IST-001: Reverse Proxy Settings Appear
**Objective**: Verify reverse proxy settings show when proxy selected
**Steps**:
1. Add Traefik
2. Add Ignition
3. Scroll to Integration Settings section
4. Verify "🌐 Reverse Proxy (traefik)" subsection exists
5. Verify fields present:
   - Base Domain input
   - Enable HTTPS checkbox
   - Let's Encrypt Email (hidden initially)

**Expected Result**: Reverse proxy settings visible
**Status**: PENDING
**Result**:

---

### IST-002: HTTPS Toggle Shows Email Field
**Objective**: Verify enabling HTTPS reveals email field
**Steps**:
1. Have Traefik + Ignition selected
2. Find "Enable HTTPS/TLS" checkbox
3. Check the box
4. Verify "Let's Encrypt Email" field appears
5. Uncheck the box
6. Verify email field disappears

**Expected Result**: Email field toggles with HTTPS checkbox
**Status**: PENDING
**Result**:

---

### IST-003: Base Domain Input Works
**Objective**: Verify base domain can be changed
**Steps**:
1. Have reverse proxy settings visible
2. Change "Base Domain" from "localhost" to "example.com"
3. Verify value updates
4. Verify value persists when navigating away and back

**Expected Result**: Base domain value updates and persists
**Status**: PENDING
**Result**:

---

### IST-004: MQTT Settings Appear
**Objective**: Verify MQTT settings show when broker + client selected
**Steps**:
1. Add EMQX
2. Add Ignition
3. Verify "📡 MQTT Broker" subsection appears
4. Verify fields present:
   - Enable TLS/MQTTS checkbox
   - Username input
   - Password input

**Expected Result**: MQTT settings visible
**Status**: PENDING
**Result**:

---

### IST-005: MQTT TLS Toggle Shows Port Field
**Objective**: Verify enabling MQTTS reveals TLS port field
**Steps**:
1. Have MQTT settings visible
2. Check "Enable TLS/MQTTS"
3. Verify "TLS Port" field appears with value 8883
4. Uncheck TLS
5. Verify port field disappears

**Expected Result**: TLS port field toggles correctly
**Status**: PENDING
**Result**:

---

### IST-006: MQTT Username/Password Inputs Work
**Objective**: Verify MQTT credentials can be entered
**Steps**:
1. Have MQTT settings visible
2. Enter username: "mqtt_admin"
3. Enter password: "securepass123"
4. Verify password field masks input (shows dots)
5. Verify values persist

**Expected Result**: Credentials can be entered and persist
**Status**: PENDING
**Result**:

---

### IST-007: OAuth Settings Appear
**Objective**: Verify OAuth settings show with provider + client
**Steps**:
1. Add Keycloak
2. Add Grafana
3. Verify "🔐 OAuth/SSO (keycloak)" subsection appears
4. Verify fields:
   - Realm Name input (default: "iiot")
   - Auto-configure Services checkbox (checked by default)
5. Verify message "Will configure: grafana" appears

**Expected Result**: OAuth settings visible with correct defaults
**Status**: PENDING
**Result**:

---

### IST-008: OAuth Realm Name Input Works
**Objective**: Verify realm name can be changed
**Steps**:
1. Have OAuth settings visible
2. Change "Realm Name" from "iiot" to "production"
3. Verify value updates

**Expected Result**: Realm name updates correctly
**Status**: PENDING
**Result**:

---

### IST-009: Database Settings Appear
**Objective**: Verify database settings show with DB + client
**Steps**:
1. Add PostgreSQL
2. Add Ignition
3. Verify "🗄️ Database Integration" subsection appears
4. Verify "Auto-register in Ignition" checkbox (checked by default)
5. Verify message "Detected: postgres → ignition" appears

**Expected Result**: Database settings visible
**Status**: PENDING
**Result**:

---

### IST-010: Email Settings Appear
**Objective**: Verify email settings show with MailHog
**Steps**:
1. Add MailHog
2. Add Grafana
3. Verify "📧 Email Testing (MailHog)" subsection appears
4. Verify fields:
   - From Address input (default: "noreply@iiot.local")
   - Auto-configure Services checkbox (checked)

**Expected Result**: Email settings visible
**Status**: PENDING
**Result**:

---

### IST-011: Settings Panel Shows Multiple Integrations
**Objective**: Verify multiple integration settings can coexist
**Steps**:
1. Add full stack: Traefik + Keycloak + PostgreSQL + EMQX + MailHog + Grafana + Ignition
2. Verify Integration Settings shows all subsections:
   - Reverse Proxy
   - MQTT
   - OAuth/SSO
   - Database
   - Email
3. Verify all fields are present and functional

**Expected Result**: All integration settings visible simultaneously
**Status**: PENDING
**Result**:

---

## Backend API Tests

### BAT-001: GET /catalog Returns Data
**Objective**: Verify catalog endpoint works
**Steps**:
1. Call: `curl http://localhost:8000/catalog`
2. Verify JSON response contains "applications" array
3. Verify response contains "categories" array

**Expected Result**: Catalog data returned successfully
**Status**: PENDING
**Result**:

---

### BAT-002: POST /detect-integrations Works
**Objective**: Verify integration detection API
**Steps**:
1. POST to /detect-integrations with Traefik + Ignition
2. Verify response contains "integrations.reverse_proxy"
3. Verify response contains "conflicts", "warnings", "recommendations"

**Expected Result**: Integration detection returns correct structure
**Status**: PENDING
**Result**:

---

### BAT-003: Integration Detection - Reverse Proxy
**Objective**: Test reverse proxy detection via API
**Steps**:
1. POST: Traefik + Ignition + Grafana
2. Verify integrations.reverse_proxy.provider == "traefik"
3. Verify integrations.reverse_proxy.targets contains 2 services
4. Verify targets include ignition and grafana

**Expected Result**: Correct reverse proxy integration detected
**Status**: PENDING
**Result**:

---

### BAT-004: Integration Detection - MQTT
**Objective**: Test MQTT detection via API
**Steps**:
1. POST: EMQX + Ignition
2. Verify integrations.mqtt_broker exists
3. Verify providers contains EMQX
4. Verify clients contains Ignition

**Expected Result**: MQTT integration detected correctly
**Status**: PENDING
**Result**:

---

### BAT-005: Integration Detection - OAuth
**Objective**: Test OAuth detection via API
**Steps**:
1. POST: Keycloak + Grafana + Portainer
2. Verify integrations.oauth_provider exists
3. Verify providers contains "keycloak"
4. Verify clients contains grafana and portainer

**Expected Result**: OAuth integration detected for multiple clients
**Status**: PENDING
**Result**:

---

### BAT-006: Integration Detection - Database
**Objective**: Test database detection via API
**Steps**:
1. POST: PostgreSQL + MariaDB + Ignition + Grafana
2. Verify integrations.db_provider exists
3. Verify providers contains postgres and mariadb
4. Verify clients contains ignition and grafana
5. Verify matched_providers are assigned to each client

**Expected Result**: Multiple databases and clients detected
**Status**: PENDING
**Result**:

---

### BAT-007: Mutual Exclusivity Detection
**Objective**: Test conflict detection via API
**Steps**:
1. POST: Traefik + Nginx Proxy Manager
2. Verify response.conflicts.length > 0
3. Verify conflict.group == "reverse_proxy"
4. Verify conflict.level == "error"

**Expected Result**: Conflict detected and reported
**Status**: PENDING
**Result**:

---

### BAT-008: Recommendations Generation
**Objective**: Test recommendation logic
**Steps**:
1. POST: Ignition + PostgreSQL
2. Verify recommendations suggests Grafana + Prometheus
3. POST: Grafana alone (no datasources)
4. Verify warning about missing datasources

**Expected Result**: Recommendations generated based on selections
**Status**: PENDING
**Result**:

---

### BAT-009: POST /generate with Integration Settings
**Objective**: Verify generation accepts integration_settings
**Steps**:
1. POST to /generate with integration_settings object
2. Verify no errors
3. Verify response contains docker_compose, env, readme

**Expected Result**: Generation succeeds with integration settings
**Status**: PENDING
**Result**:

---

### BAT-010: POST /download Creates ZIP
**Objective**: Verify download endpoint works
**Steps**:
1. POST to /download with valid stack config
2. Verify response is application/zip
3. Verify response has Content-Disposition header

**Expected Result**: ZIP file download initiated
**Status**: PENDING
**Result**:

---

## Docker Compose Generation Tests

### DGT-001: Basic Compose Generation
**Objective**: Verify docker-compose.yml is generated
**Steps**:
1. Add Ignition
2. Click "Download Stack"
3. Extract ZIP
4. Verify docker-compose.yml exists
5. Verify structure is valid YAML

**Expected Result**: Valid docker-compose.yml generated
**Status**: PENDING
**Result**:

---

### DGT-002: .env File Generation
**Objective**: Verify .env file is generated
**Steps**:
1. Add any service
2. Download stack
3. Extract ZIP
4. Verify .env exists
5. Verify contains TZ and RESTART_POLICY

**Expected Result**: .env file generated with correct variables
**Status**: PENDING
**Result**:

---

### DGT-003: README Generation
**Objective**: Verify README is generated
**Steps**:
1. Add services
2. Download stack
3. Verify README.md exists
4. Verify contains service URLs
5. Verify contains instructions

**Expected Result**: README generated with helpful content
**Status**: PENDING
**Result**:

---

### DGT-004: Multi-Instance Generation
**Objective**: Verify multiple instances generate correctly
**Steps**:
1. Add 3 Ignition instances with different ports
2. Download stack
3. Verify docker-compose has 3 separate services
4. Verify port mappings are unique

**Expected Result**: Multiple instances generated correctly
**Status**: PENDING
**Result**:

---

### DGT-005: Traefik Labels Generation
**Objective**: Verify Traefik labels are added when Traefik selected
**Steps**:
1. Add Traefik + Ignition
2. Download stack
3. Check Ignition service in docker-compose.yml
4. Verify has traefik.enable=true label
5. Verify has routing labels

**Expected Result**: Traefik labels present on web services
**Status**: PENDING
**Result**:

---

### DGT-006: Environment Variables Applied
**Objective**: Verify custom config values appear in environment
**Steps**:
1. Add Ignition with custom admin username "testadmin"
2. Download stack
3. Check Ignition service environment section
4. Verify GATEWAY_ADMIN_USERNAME=testadmin

**Expected Result**: Custom config values in environment
**Status**: PENDING
**Result**:

---

### DGT-007: Volumes Generation
**Objective**: Verify volume mounts are generated
**Steps**:
1. Add Ignition
2. Download stack
3. Check Ignition service volumes
4. Verify data volume mapped correctly

**Expected Result**: Volumes configured properly
**Status**: PENDING
**Result**:

---

### DGT-008: Networks Generation
**Objective**: Verify Docker networks are created
**Steps**:
1. Add multiple services
2. Download stack
3. Check networks section in docker-compose.yml
4. Verify all services on same network

**Expected Result**: Network configured for all services
**Status**: PENDING
**Result**:

---

## Edge Cases & Error Handling

### ECT-001: Empty Stack Generation
**Objective**: Verify behavior with no services selected
**Steps**:
1. Don't select any services
2. Click "Download Stack"
3. Verify appropriate message or empty stack

**Expected Result**: Handles empty selection gracefully
**Status**: PENDING
**Result**:

---

### ECT-002: Port Conflict Detection
**Objective**: Verify warning for duplicate ports (future)
**Steps**:
1. Add Ignition-1 (port 8088)
2. Add Ignition-2 (also port 8088)
3. Check for port conflict warning

**Expected Result**: Port conflict detected (or allowed for now)
**Status**: PENDING
**Result**:

---

### ECT-003: Invalid Configuration Values
**Objective**: Verify validation on config fields
**Steps**:
1. Add Ignition
2. Enter invalid port (e.g., "abc" or 70000)
3. Verify validation or error handling

**Expected Result**: Invalid values handled gracefully
**Status**: PENDING
**Result**:

---

### ECT-004: Backend Unavailable
**Objective**: Verify frontend handles backend errors
**Steps**:
1. Stop backend: `docker-compose stop backend`
2. Try to add a service
3. Verify error message or graceful degradation

**Expected Result**: Error handled gracefully
**Status**: PENDING
**Result**:

---

### ECT-005: Very Large Configuration
**Objective**: Verify performance with many services
**Steps**:
1. Add 10+ services
2. Verify UI remains responsive
3. Verify detection still works
4. Download and verify stack generates

**Expected Result**: Handles large configs well
**Status**: PENDING
**Result**:

---

## Performance Tests

### PT-001: Initial Load Time
**Objective**: Measure page load performance
**Steps**:
1. Clear browser cache
2. Load http://localhost:3500
3. Measure time to interactive

**Expected Result**: Loads in < 3 seconds
**Status**: PENDING
**Result**:

---

### PT-002: Integration Detection Speed
**Objective**: Measure detection API response time
**Steps**:
1. Add 5 services
2. Measure time for Integration Status to update
3. Verify < 500ms

**Expected Result**: Detection completes in < 500ms
**Status**: PENDING
**Result**:

---

### PT-003: Stack Generation Speed
**Objective**: Measure generation time
**Steps**:
1. Configure full stack (10 services)
2. Click Download
3. Measure time to ZIP download

**Expected Result**: Generates in < 2 seconds
**Status**: PENDING
**Result**:

---

## Test Execution Summary

**Total Tests**: 80
**Passed**: 0
**Failed**: 0
**Skipped**: 0
**Pending**: 80

---

## Test Execution Log

### Execution Date: [TO BE FILLED]
**Tester**: Claude Code
**Environment**:
- Frontend: v1.0.0
- Backend: v1.0.0
- Docker Compose: v2.x

### Issues Found During Testing:
[TO BE DOCUMENTED]

### Fixes Applied:
[TO BE DOCUMENTED]

---

## Sign-off

**Test Lead**: _____________
**Date**: _____________
**Status**: [ ] All Tests Passed [ ] Issues Identified [ ] In Progress
