# Next Phases & Roadmap
**IIoT Stack Builder - Future Development Plan**

**Last Updated**: 2025-10-07
**Current Status**: Phase 1 & 2 Complete, Ready for Validation Testing

---

## Current State

### ✅ Completed Phases

**Phase 1: Integration Detection** (100%)
- 25 services with auto-detection
- 9 integration types
- Mutual exclusivity enforcement
- Visual conflict indicators

**Phase 2A/2B: Auto-Configuration** (78%)
- MQTT broker configuration
- Reverse proxy (Traefik) with HTTPS
- OAuth/SSO (Keycloak realms)
- Database provisioning
- Email/SMTP setup
- Stack monitoring

**Phase 2 Fixes** (Today)
- ✅ Fixed PostgreSQL volume mount error
- ✅ Fixed JSON import error in database registration
- ✅ Improved instance naming (first instance = simple name)
- ✅ Automatic directory creation in start.sh and README

---

## Phase 3: Stack Validation & Testing (RECOMMENDED NEXT)

### Priority: HIGH
### Estimated Time: 2-3 sessions
### Goal: Ensure all generated stacks actually work

This phase focuses on **end-to-end validation** - making sure every combination of services deploys successfully without errors.

### 3.1 Automated Stack Validation Suite

**Create test scenarios** for common stack combinations:
1. **Ignition + PostgreSQL** (your reported issue - now fixed)
2. **Ignition + MariaDB**
3. **Ignition + MSSQL**
4. **Traefik + Grafana + Prometheus**
5. **Keycloak + Grafana (OAuth)**
6. **Full monitoring stack** (Grafana + Prometheus + Loki)
7. **MQTT stack** (Mosquitto/EMQX + Node-RED)
8. **Complete IIoT stack** (Ignition + DB + MQTT + Grafana)

**Test script structure**:
```bash
#!/bin/bash
# test_stacks.sh

for test_case in test_cases/*.json; do
    echo "Testing: $test_case"

    # Generate stack
    curl -X POST /download -d @$test_case -o stack.zip

    # Extract and deploy
    unzip stack.zip -d test_deploy/
    cd test_deploy

    # Run start.sh
    ./start.sh

    # Wait for services
    sleep 60

    # Health checks
    docker ps --format "{{.Names}}: {{.Status}}"

    # Check all containers running
    if [ $(docker ps | grep -c "Up") -eq $EXPECTED_COUNT ]; then
        echo "✅ PASS"
    else
        echo "❌ FAIL"
    fi

    # Cleanup
    docker-compose down -v
    cd ..
    rm -rf test_deploy
done
```

**Files to create**:
- `tests/test_stacks.sh` - Main test runner
- `tests/test_cases/ignition_postgres.json` - Test case 1
- `tests/test_cases/traefik_grafana.json` - Test case 2
- `tests/health_checks.py` - Python script for service health verification

**Expected output**: Test report showing which stacks pass/fail

---

### 3.2 Service-Specific Health Checks

**Verify each service is actually functional**, not just running:

| Service | Health Check | Expected Result |
|---------|--------------|-----------------|
| Ignition | `curl http://localhost:8088/StatusPing` | `RUNNING` |
| PostgreSQL | `docker exec postgres pg_isready` | `accepting connections` |
| Grafana | `curl http://localhost:3000/api/health` | `{"database":"ok"}` |
| Keycloak | `curl http://localhost:8180/health/ready` | `{"status":"UP"}` |
| Traefik | `curl http://localhost:8080/api/http/routers` | JSON list of routers |
| MQTT (Mosquitto) | `mosquitto_sub -h localhost -t test -C 1` | Connection successful |
| Prometheus | `curl http://localhost:9090/-/healthy` | `Healthy` |

**Implementation**:
```python
# tests/health_checks.py
import requests
import subprocess

def check_ignition(port=8088):
    try:
        r = requests.get(f"http://localhost:{port}/StatusPing", timeout=5)
        return r.text == "RUNNING"
    except:
        return False

def check_postgres(container_name="postgres"):
    result = subprocess.run(
        ["docker", "exec", container_name, "pg_isready"],
        capture_output=True
    )
    return "accepting connections" in result.stdout.decode()

# ... etc for each service
```

---

### 3.3 Integration Verification

**Test that integrations actually work**, not just that configs are generated:

**Test 1: Keycloak + Grafana OAuth**
- Generate stack with Keycloak + Grafana
- Start stack
- Verify Grafana redirects to Keycloak for login
- Verify OAuth credentials in environment variables match Keycloak realm

**Test 2: Grafana + PostgreSQL Datasource**
- Generate stack with Grafana + PostgreSQL
- Start stack
- Check Grafana datasources: `curl -u admin:admin http://localhost:3000/api/datasources`
- Verify PostgreSQL datasource exists and is connected

**Test 3: Traefik + Service Routing**
- Generate stack with Traefik + Grafana
- Start stack
- Test routing: `curl -H "Host: grafana.localhost" http://localhost:80`
- Verify it reaches Grafana

**Test 4: MQTT Authentication**
- Generate stack with Mosquitto + auth enabled
- Start stack
- Try connect without credentials (should fail)
- Try connect with credentials (should succeed)

---

### 3.4 Known Issues Discovery

**Goal**: Find and document all edge cases, bugs, and limitations

**Create issue tracker** in `KNOWN_ISSUES.md`:
```markdown
# Known Issues

## Critical (Blocks deployment)
- [ ] Issue description
- Workaround: ...

## Major (Requires manual fix)
- [ ] Issue description
- Workaround: ...

## Minor (Cosmetic/docs)
- [ ] Issue description
```

**Test scenarios that might reveal issues**:
1. Multiple instances of same service (e.g., 3 Ignitions)
2. Port conflicts (two services wanting same port)
3. Very large stacks (20+ services)
4. Minimum configuration (no optional fields)
5. Maximum configuration (all fields filled)

---

## Phase 4: User Experience Enhancements

### Priority: MEDIUM
### Estimated Time: 3-4 sessions

### 4.1 Stack Templates

**Pre-configured bundles** for common use cases:

```javascript
// templates/scada_basic.json
{
  "name": "Basic SCADA Stack",
  "description": "Ignition + PostgreSQL + Grafana",
  "instances": [
    {"app_id": "ignition", ...},
    {"app_id": "postgres", ...},
    {"app_id": "grafana", ...}
  ]
}
```

**Templates to create**:
- `scada_basic` - Ignition + PostgreSQL
- `scada_full` - Ignition + PostgreSQL + MQTT + Grafana
- `monitoring` - Grafana + Prometheus + Loki
- `development` - All services for testing

**UI**: Add "Load Template" button that populates services

---

### 4.2 Stack Validation UI

**Real-time feedback** as user builds stack:

```javascript
// Show warnings
if (ignition && !database) {
  showWarning("Ignition works best with a database. Consider adding PostgreSQL.")
}

if (grafana && !prometheus && !database) {
  showWarning("Grafana has no datasources. Add Prometheus or a database.")
}
```

**Visual indicators**:
- ✅ Green checkmark: Integration will be auto-configured
- ⚠️  Yellow warning: Manual configuration needed
- ❌ Red X: Conflicting services

---

### 4.3 Deployment Verification UI

**After download**, show checklist:

```markdown
✅ Downloaded iiot-stack.zip
⏳ Next steps:
1. [ ] Extract ZIP file
2. [ ] Review docker-compose.yml
3. [ ] Run ./start.sh (or start.bat on Windows)
4. [ ] Wait 2-3 minutes for services to start
5. [ ] Access services at the URLs below

📋 Service URLs:
- Ignition: http://localhost:8088
- Grafana: http://localhost:3000
```

---

## Phase 5: Advanced Features

### Priority: LOW
### Estimated Time: 5+ sessions

### 5.1 Stack Export/Import

**Save and share stack configurations**:
- Export button → downloads `.iiotstack` JSON file
- Import button → loads configuration
- Share URL: `https://builder.example.com/?config=<base64>`

### 5.2 Docker Compose V2 Features

- Use newer `docker compose` (no hyphen) commands
- Health checks in compose file
- Depends_on with conditions
- Resource limits (CPU/memory)

### 5.3 Stack Upgrades

**Help users update existing stacks**:
- "Upgrade" button that compares current vs new
- Shows diff of changes
- Preserves custom modifications

### 5.4 Custom Service Support

**Allow users to add their own services**:
- UI for adding custom service definitions
- JSON schema validation
- Save to user's service library

### 5.5 Multi-Environment Support

**Generate for dev/staging/prod**:
- Different port mappings per environment
- Environment-specific .env files
- Separate docker-compose files

---

## Phase 2C: Remaining Integrations (Optional)

### Priority: LOW (22% of integrations, rarely requested)

### 5.1 Nginx Proxy Manager Integration
- API-based proxy host creation
- Alternative to Traefik
- Bootstrap setup script

### 5.2 Vault Secrets Management
- Secret initialization script
- Secret injection into services
- Dynamic credential rotation

### 5.3 Loki + Promtail Logging
- Log aggregation setup
- Promtail sidecar configuration
- Grafana Loki datasource

### 5.4 Prometheus Service Discovery
- Automatic scrape configuration
- Target discovery from containers
- Alertmanager setup

### 5.5 Advanced MQTT Features
- TLS certificate generation
- ACL (Access Control List) configuration
- MQTT bridge for multi-broker

---

## Recommended Priority Order

Based on your requirement *"make sure that all of the functionality that we have tried to build so far works seamlessly"*, here's the recommended order:

### Immediate (Next 1-2 Sessions)
1. **✅ Phase 3.1: Automated Stack Validation** - Test common combinations
2. **✅ Phase 3.2: Service Health Checks** - Verify services actually work
3. **✅ Phase 3.3: Integration Verification** - Test OAuth, datasources, routing

### Short-term (Next 3-5 Sessions)
4. **Phase 3.4: Known Issues Discovery** - Find and document edge cases
5. **Phase 4.1: Stack Templates** - Make it easier for users to get started
6. **Phase 4.2: Stack Validation UI** - Real-time warnings and suggestions

### Long-term (Future)
7. Phase 4.3: Deployment Verification UI
8. Phase 5: Advanced Features (as needed)
9. Phase 2C: Remaining Integrations (if requested by users)

---

## Success Metrics

### Phase 3 Completion Criteria
- [ ] 8/8 test scenarios pass automated validation
- [ ] All service health checks implemented and passing
- [ ] OAuth integration verified working end-to-end
- [ ] Datasource provisioning verified working
- [ ] Traefik routing verified working
- [ ] MQTT auth verified working
- [ ] Zero critical bugs in KNOWN_ISSUES.md

### Phase 4 Completion Criteria
- [ ] 4+ stack templates available
- [ ] Real-time validation warnings implemented
- [ ] Deployment checklist UI implemented
- [ ] User feedback collected and incorporated

---

## Next Session TODO

**Start Phase 3: Stack Validation**

1. Create `tests/` directory structure
2. Write `test_stacks.sh` script
3. Create test case JSON files for:
   - Ignition + PostgreSQL
   - Traefik + Grafana
   - Keycloak + Grafana (OAuth)
4. Run tests and document results
5. Fix any issues discovered

**Commands to run**:
```bash
mkdir -p tests/test_cases
touch tests/test_stacks.sh
chmod +x tests/test_stacks.sh

# Create first test case
cat > tests/test_cases/ignition_postgres.json <<'EOF'
{
  "instances": [
    {"app_id": "ignition", "instance_name": "ignition", "config": {"version": "latest", "http_port": 8088}},
    {"app_id": "postgres", "instance_name": "postgres", "config": {"version": "latest", "port": 5432}}
  ]
}
EOF
```

---

## Questions to Consider

1. **Target users**: Who will use this tool? (DevOps, IIoT engineers, beginners?)
2. **Deployment environment**: Docker Desktop, Linux server, cloud?
3. **Production readiness**: Is this for dev/test or production deployments?
4. **Support model**: Self-service docs or active support?
5. **Release strategy**: When to announce/share with wider audience?

---

**Current Status**: 🟢 Healthy, ready for validation testing
**Blockers**: None
**Risk**: Low (core functionality working, need to verify edge cases)
**Recommendation**: Proceed with Phase 3 validation before adding new features

---

*This roadmap should be reviewed and updated at the start of each development session.*
