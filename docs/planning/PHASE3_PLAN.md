# Phase 3: Stack Validation Testing Plan
**IIoT Stack Builder - Systematic Testing Approach**

**Created**: 2025-10-07
**Status**: Planning Complete, Ready to Execute
**Goal**: Verify all generated stacks deploy and function correctly

---

## Testing Philosophy

**Approach**: Incremental, systematic, documented
- Start simple (single services)
- Progress to complex (multi-service integrations)
- Document every test result
- Fix issues immediately when found
- Re-test after fixes

---

## Test Infrastructure

### Directory Structure
```
tests/
├── test_runner.sh              # Main test orchestrator
├── health_checks.py            # Service health verification
├── integration_tests.py        # Integration verification
├── test_cases/                 # Test scenario definitions
│   ├── T001_postgres_only.json
│   ├── T002_ignition_only.json
│   ├── T003_ignition_postgres.json
│   ├── T004_traefik_grafana.json
│   ├── T005_keycloak_grafana_oauth.json
│   ├── T006_grafana_postgres_datasource.json
│   ├── T007_mqtt_nodered.json
│   ├── T008_full_iiot_stack.json
│   └── ...
├── results/                    # Test execution results
│   ├── session_2025-10-07.md
│   └── summary.json
└── temp/                       # Temporary deployment directory (gitignored)
```

### Supporting Files
- `TEST_RESULTS.md` - Master test results document (always up-to-date)
- `.gitignore` - Exclude temp/, results/*.zip, test deployments

---

## Test Categories

### Category 1: Single Service Validation (Basic)
**Purpose**: Verify each service can start independently
**Priority**: HIGH
**Estimated Time**: 30 minutes

| Test ID | Services | Purpose | Expected Containers |
|---------|----------|---------|---------------------|
| T001 | PostgreSQL | Database starts, accepts connections | 1 |
| T002 | Ignition | Gateway starts, web UI accessible | 1 |
| T003 | Grafana | Dashboard accessible | 1 |
| T004 | Traefik | Reverse proxy operational | 1 |
| T005 | Keycloak | Auth server starts | 1 |
| T006 | Mosquitto | MQTT broker accepts connections | 1 |
| T007 | Prometheus | Metrics collector operational | 1 |
| T008 | MariaDB | Database starts | 1 |

**Success Criteria**:
- ✅ Container starts (status: Up)
- ✅ Service port accessible
- ✅ Basic health check passes
- ✅ No error logs

---

### Category 2: Service Pair Integration (Core)
**Purpose**: Verify basic integrations work
**Priority**: HIGH
**Estimated Time**: 45 minutes

| Test ID | Services | Integration Tested | Expected Result |
|---------|----------|-------------------|-----------------|
| T101 | Ignition + PostgreSQL | Database registration | Volume mount works, both start |
| T102 | Grafana + PostgreSQL | Datasource provisioning | Datasource auto-configured |
| T103 | Traefik + Grafana | Reverse proxy routing | Access via subdomain |
| T104 | Keycloak + PostgreSQL | Keycloak DB backend | Keycloak uses PostgreSQL |
| T105 | Mosquitto + Node-RED | MQTT connectivity | Node-RED connects to MQTT |
| T106 | Prometheus + Grafana | Metrics datasource | Prometheus datasource added |
| T107 | Ignition + MariaDB | Alternate DB | MariaDB registration script |
| T108 | Grafana + InfluxDB | Time-series datasource | InfluxDB datasource added |

**Success Criteria**:
- ✅ Both containers start
- ✅ Integration config files generated
- ✅ Services can communicate
- ✅ Integration health check passes

---

### Category 3: Complex Integrations (Advanced)
**Purpose**: Verify advanced features and multi-service stacks
**Priority**: MEDIUM
**Estimated Time**: 60 minutes

| Test ID | Services | Integration Tested | Expected Result |
|---------|----------|-------------------|-----------------|
| T201 | Keycloak + Grafana | OAuth/SSO | Grafana redirects to Keycloak |
| T202 | Traefik + Grafana + Prometheus | Multi-service routing | Both accessible via subdomains |
| T203 | Ignition + Postgres + Grafana | Multi-tier monitoring | All three communicate |
| T204 | MQTT + TLS + Auth | Secure MQTT | Auth required, TLS config present |
| T205 | Traefik + HTTPS + Let's Encrypt | SSL certificates | Traefik config has cert resolver |
| T206 | Multiple Ignitions | Multi-instance | ignition, ignition-2, ignition-3 all start |

**Success Criteria**:
- ✅ All containers start
- ✅ Complex integration works end-to-end
- ✅ Configuration applied correctly
- ✅ No port conflicts

---

### Category 4: Full Stack Scenarios (Real-World)
**Purpose**: Test complete production-like stacks
**Priority**: MEDIUM
**Estimated Time**: 45 minutes

| Test ID | Stack Name | Services | Purpose |
|---------|------------|----------|---------|
| T301 | Basic SCADA | Ignition + PostgreSQL + Grafana | Common IIoT setup |
| T302 | Full IIoT | Ignition + Postgres + MQTT + Node-RED + Grafana | Complete solution |
| T303 | Monitoring Stack | Grafana + Prometheus + Traefik | Observability platform |
| T304 | Secure Stack | Ignition + Postgres + Keycloak + Traefik HTTPS | Production security |

**Success Criteria**:
- ✅ All containers start (5+ services)
- ✅ All integrations work
- ✅ Stack usable for intended purpose
- ✅ Startup time < 5 minutes

---

### Category 5: Edge Cases & Stress Tests (Robustness)
**Purpose**: Find breaking points and edge cases
**Priority**: LOW
**Estimated Time**: 30 minutes

| Test ID | Scenario | Purpose | Expected Behavior |
|---------|----------|---------|-------------------|
| T401 | Empty configuration | Minimal config values | Uses all defaults |
| T402 | Maximum services | 20+ services | All start, no conflicts |
| T403 | Port conflicts | Same port for two services | Generation warning or auto-adjust |
| T404 | Invalid configuration | Missing required fields | Validation error |
| T405 | Duplicate service names | Two services same name | Name auto-increment |

**Success Criteria**:
- ✅ Graceful error handling
- ✅ Clear error messages
- ✅ No crashes or silent failures

---

## Test Execution Plan

### Session 1: Foundation (This Session)
**Estimated Time**: 60-90 minutes
**Goal**: Set up infrastructure and test basic functionality

#### Tasks:
1. **✅ Create test infrastructure** (15 min)
   - Create `tests/` directory structure
   - Set up `.gitignore`
   - Create `TEST_RESULTS.md` template

2. **✅ Implement test runner** (20 min)
   - Write `test_runner.sh` script
   - Download stack from API
   - Extract and deploy
   - Capture container status
   - Record results

3. **✅ Create health check utilities** (15 min)
   - Write `health_checks.py`
   - Implement basic checks (HTTP, port, docker inspect)
   - Service-specific checks

4. **✅ Execute Category 1 Tests** (30 min)
   - T001-T008: Single service tests
   - Document results in real-time
   - Fix any critical issues found

5. **✅ Execute Category 2 Tests (partial)** (10 min)
   - T101-T103: Core integrations
   - Document results

**Deliverables**:
- Functional test infrastructure
- 8-11 tests executed and documented
- Any critical bugs fixed
- Clear path for next session

---

### Session 2: Core Integrations
**Estimated Time**: 60 minutes
**Goal**: Complete Category 2 and start Category 3

#### Tasks:
1. Complete Category 2 tests (T104-T108)
2. Start Category 3 tests (T201-T203)
3. Fix any issues found
4. Update TEST_RESULTS.md

**Deliverables**:
- Category 2: 100% complete
- Category 3: 50% complete
- Updated test results

---

### Session 3: Advanced & Full Stacks
**Estimated Time**: 60 minutes
**Goal**: Complete Categories 3 and 4

#### Tasks:
1. Complete Category 3 tests (T204-T206)
2. Execute Category 4 tests (T301-T304)
3. Document integration test results
4. Fix any non-critical issues

**Deliverables**:
- Categories 3-4: 100% complete
- Integration verification complete
- Known issues documented

---

### Session 4: Edge Cases & Final Report
**Estimated Time**: 45 minutes
**Goal**: Complete testing and create final report

#### Tasks:
1. Execute Category 5 tests (T401-T405)
2. Re-test any previously failed tests
3. Create final test report
4. Update documentation with findings

**Deliverables**:
- All 30+ tests complete
- Final test report with pass/fail rates
- Bug fixes or workarounds for all issues
- Updated user documentation

---

## Test Runner Implementation

### test_runner.sh (Pseudocode)

```bash
#!/bin/bash
# Test runner for IIoT Stack Builder

TEST_CASE=$1
TEST_ID=$(basename $TEST_CASE .json)
RESULT_FILE="results/$(date +%Y%m%d_%H%M%S)_${TEST_ID}.md"
DEPLOY_DIR="temp/${TEST_ID}"

echo "🧪 Running test: $TEST_ID"
echo "Test case: $TEST_CASE"

# 1. Clean previous deployment
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# 2. Generate stack from API
echo "📥 Generating stack..."
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d @$TEST_CASE \
  -o ${DEPLOY_DIR}/stack.zip

# 3. Check if download succeeded
if [ ! -f ${DEPLOY_DIR}/stack.zip ]; then
  echo "❌ FAIL: Stack generation failed"
  record_failure "Stack generation failed"
  exit 1
fi

# 4. Extract stack
unzip -q ${DEPLOY_DIR}/stack.zip -d $DEPLOY_DIR

# 5. Deploy stack
cd $DEPLOY_DIR
if [ -f start.sh ]; then
  chmod +x start.sh
  ./start.sh > deploy.log 2>&1 &
else
  docker-compose up -d > deploy.log 2>&1
fi

# 6. Wait for containers to start
echo "⏳ Waiting for containers to start..."
sleep 30

# 7. Check container status
CONTAINERS=$(docker-compose ps --services)
RUNNING=$(docker-compose ps | grep "Up" | wc -l)
EXPECTED=$(echo "$CONTAINERS" | wc -l)

if [ $RUNNING -eq $EXPECTED ]; then
  echo "✅ All containers running ($RUNNING/$EXPECTED)"
else
  echo "❌ Some containers failed ($RUNNING/$EXPECTED)"
  docker-compose ps
fi

# 8. Run health checks
python3 ../health_checks.py --test-id $TEST_ID

# 9. Record results
record_results $TEST_ID $RUNNING $EXPECTED

# 10. Cleanup
docker-compose down -v
cd ../..
rm -rf $DEPLOY_DIR
```

---

### health_checks.py (Pseudocode)

```python
#!/usr/bin/env python3
"""Health check utilities for service validation"""

import requests
import subprocess
import socket
import time
from typing import Dict, List, Tuple

class HealthChecker:
    def check_http(self, url: str, expected_status: int = 200) -> bool:
        """Check if HTTP endpoint is accessible"""
        try:
            r = requests.get(url, timeout=5)
            return r.status_code == expected_status
        except:
            return False

    def check_port(self, host: str, port: int) -> bool:
        """Check if port is open"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0

    def check_ignition(self, port: int = 8088) -> Tuple[bool, str]:
        """Check Ignition Gateway health"""
        try:
            r = requests.get(f"http://localhost:{port}/StatusPing", timeout=5)
            if r.text.strip() == "RUNNING":
                return True, "Gateway running"
            return False, f"Gateway status: {r.text}"
        except Exception as e:
            return False, str(e)

    def check_postgres(self, container: str = "postgres") -> Tuple[bool, str]:
        """Check PostgreSQL health"""
        result = subprocess.run(
            ["docker", "exec", container, "pg_isready"],
            capture_output=True, text=True
        )
        if "accepting connections" in result.stdout:
            return True, "Database accepting connections"
        return False, result.stdout

    def check_grafana(self, port: int = 3000) -> Tuple[bool, str]:
        """Check Grafana health"""
        try:
            r = requests.get(f"http://localhost:{port}/api/health", timeout=5)
            data = r.json()
            if data.get("database") == "ok":
                return True, "Grafana healthy"
            return False, f"Health: {data}"
        except Exception as e:
            return False, str(e)

    def check_traefik(self, port: int = 8080) -> Tuple[bool, str]:
        """Check Traefik health"""
        try:
            r = requests.get(f"http://localhost:{port}/api/http/routers", timeout=5)
            routers = r.json()
            return True, f"Traefik running ({len(routers)} routers)"
        except Exception as e:
            return False, str(e)

    def check_keycloak(self, port: int = 8180) -> Tuple[bool, str]:
        """Check Keycloak health"""
        try:
            r = requests.get(f"http://localhost:{port}/health/ready", timeout=5)
            data = r.json()
            if data.get("status") == "UP":
                return True, "Keycloak ready"
            return False, f"Status: {data}"
        except Exception as e:
            return False, str(e)

# Service-specific health check mapping
HEALTH_CHECKS = {
    "ignition": check_ignition,
    "postgres": check_postgres,
    "grafana": check_grafana,
    "traefik": check_traefik,
    "keycloak": check_keycloak,
}
```

---

## Result Recording Format

### TEST_RESULTS.md Structure

```markdown
# Phase 3 Test Results

**Last Updated**: 2025-10-07
**Tests Executed**: 11 / 35
**Pass Rate**: 91% (10 passed, 1 failed)

---

## Test Summary by Category

| Category | Total | Passed | Failed | Skipped | Pass Rate |
|----------|-------|--------|--------|---------|-----------|
| 1. Single Service | 8 | 8 | 0 | 0 | 100% |
| 2. Service Pairs | 3 | 2 | 1 | 5 | 67% |
| 3. Complex Integration | 0 | 0 | 0 | 6 | N/A |
| 4. Full Stacks | 0 | 0 | 0 | 4 | N/A |
| 5. Edge Cases | 0 | 0 | 0 | 5 | N/A |

---

## Test Results Detail

### T001: PostgreSQL Only ✅ PASS
**Date**: 2025-10-07 14:23:15
**Duration**: 45 seconds
**Containers**: 1/1 running

**Steps**:
1. Generated stack - ✅
2. Extracted files - ✅
3. Deployed stack - ✅
4. Container started - ✅
5. Port 5432 accessible - ✅
6. Health check passed - ✅

**Health Check Results**:
- `docker exec postgres pg_isready`: accepting connections ✅
- Port 5432: OPEN ✅

**Notes**: Clean deployment, no issues.

---

### T002: Ignition Only ✅ PASS
**Date**: 2025-10-07 14:25:42
**Duration**: 90 seconds
**Containers**: 1/1 running

**Steps**:
1. Generated stack - ✅
2. Deployed with start.sh - ✅
3. Container started - ✅
4. HTTP port accessible - ✅
5. Health check passed - ✅

**Health Check Results**:
- `curl http://localhost:8088/StatusPing`: RUNNING ✅
- Web UI accessible - ✅

**Notes**: First run initialization took 60s (expected).

---

### T101: Ignition + PostgreSQL ❌ FAIL
**Date**: 2025-10-07 14:28:30
**Duration**: 120 seconds
**Containers**: 1/2 running
**Error**: PostgreSQL failed to start

**Steps**:
1. Generated stack - ✅
2. Deployed with start.sh - ✅
3. Containers starting - ⚠️
4. PostgreSQL failed - ❌
5. Ignition running - ✅

**Error Logs**:
```
postgres | ERROR: directory "/var/lib/postgresql/data" not writable
```

**Root Cause**: Directory permissions issue

**Fix Applied**: Updated start.sh to set permissions
**Status**: FIXED - Re-test required

---

## Known Issues

### Issue #1: PostgreSQL Permissions ✅ FIXED
- **Severity**: HIGH
- **Tests Affected**: T101, T104
- **Description**: PostgreSQL container fails with permission error
- **Fix**: Added permission fix to start.sh
- **Status**: Fixed in commit abc123

### Issue #2: Keycloak Slow Startup
- **Severity**: LOW
- **Tests Affected**: T005, T104, T201
- **Description**: Keycloak takes 90-120s to become ready
- **Workaround**: Increase health check timeout
- **Status**: OPEN (expected behavior)

---

## Session Notes

### Session 2025-10-07
**Duration**: 90 minutes
**Tests Completed**: 11
**Issues Found**: 2
**Issues Fixed**: 1

**Summary**:
- Set up test infrastructure ✅
- Created test runner and health checks ✅
- Executed Category 1 tests (8/8 passed) ✅
- Started Category 2 tests (2/3 passed) ⏸️
- Found and fixed PostgreSQL permissions issue ✅

**Next Session**:
- Re-test T101 after fix
- Complete Category 2 tests
- Begin Category 3 tests
```

---

## Test Case JSON Examples

### T001_postgres_only.json
```json
{
  "instances": [
    {
      "app_id": "postgres",
      "instance_name": "postgres",
      "config": {
        "version": "latest",
        "port": 5432,
        "database": "testdb",
        "username": "testuser",
        "password": "testpass"
      }
    }
  ],
  "global_settings": {
    "timezone": "UTC",
    "restart_policy": "unless-stopped"
  }
}
```

### T101_ignition_postgres.json
```json
{
  "instances": [
    {
      "app_id": "ignition",
      "instance_name": "ignition",
      "config": {
        "version": "latest",
        "http_port": 8088,
        "admin_username": "admin",
        "admin_password": "password"
      }
    },
    {
      "app_id": "postgres",
      "instance_name": "postgres",
      "config": {
        "version": "latest",
        "port": 5432,
        "database": "ignition",
        "username": "ignition",
        "password": "password"
      }
    }
  ]
}
```

---

## Success Criteria for Phase 3

### Minimum Acceptable:
- [ ] 80% of Category 1 tests pass (6/8)
- [ ] 70% of Category 2 tests pass (6/8)
- [ ] All critical bugs fixed
- [ ] Known issues documented

### Target Goals:
- [ ] 100% of Category 1 tests pass (8/8)
- [ ] 90% of Category 2 tests pass (7/8)
- [ ] 75% of Category 3 tests pass (5/6)
- [ ] 50% of Category 4 tests pass (2/4)
- [ ] No critical or high-severity bugs

### Stretch Goals:
- [ ] 100% of Categories 1-2 pass
- [ ] 85% of Category 3 pass
- [ ] 75% of Category 4 pass
- [ ] All Category 5 edge cases handled gracefully

---

## Risk Mitigation

### Potential Blockers:
1. **Docker resource limits** - Large stacks may exceed available RAM/CPU
   - Mitigation: Test on clean system, close other containers

2. **Network port conflicts** - Other services using required ports
   - Mitigation: Check ports before testing, use custom ports in tests

3. **Slow container startup** - Some services take 2-3 minutes
   - Mitigation: Increase timeouts, use health checks instead of sleep

4. **Database initialization** - First-run DB setup can be slow
   - Mitigation: Expect longer times, wait for health checks

### Contingency Plans:
- If test infrastructure takes too long: Simplify, use manual testing
- If too many failures: Focus on critical paths only
- If session runs long: Save progress, continue next session

---

## Tools & Dependencies

### Required:
- Docker & Docker Compose (running)
- curl (for API calls)
- Python 3.8+ (for health checks)
- jq (for JSON parsing - optional)
- unzip (for extracting stacks)

### Python Dependencies:
```
requests
```

### Installation:
```bash
pip3 install requests
```

---

## Execution Commands

### Run single test:
```bash
cd tests
./test_runner.sh test_cases/T001_postgres_only.json
```

### Run all Category 1 tests:
```bash
for test in test_cases/T00*.json; do
  ./test_runner.sh $test
done
```

### Generate test report:
```bash
python3 generate_report.py results/ > TEST_RESULTS.md
```

### Clean all test artifacts:
```bash
docker-compose down -v  # In any test deployment
rm -rf temp/*
```

---

**Status**: ✅ Plan Complete - Ready to Execute
**Next Step**: Create test infrastructure (Task 1)
**Estimated Total Time**: 3-4 hours across 4 sessions
**Current Session Budget**: 60-90 minutes

---

*This plan will be updated as testing progresses.*
