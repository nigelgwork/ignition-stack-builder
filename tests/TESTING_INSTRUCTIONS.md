# Phase 3 Testing Instructions

## Prerequisites

### 1. Ensure Stack Builder is Running

**IMPORTANT**: Before any testing session, the stack builder containers must be running.

```bash
cd /git/ignition-stack-builder/tests
./ensure_stack_running.sh
```

This script will:
- Check if containers are already running
- Start them if needed
- Verify the backend API is responding
- Wait for services to be ready

### Why This Is Needed

The stack builder containers can stop due to:
- System restarts or Docker daemon restarts
- Running system upgrade commands (e.g., `/upgrade`)
- Explicit `docker-compose down` commands
- Docker resource cleanup operations

Even though containers have `restart: unless-stopped` policy, they won't auto-start after:
- Docker daemon restart
- Explicit stop commands
- System-level operations

### 2. Verify System State

```bash
# Check Docker is running
docker ps

# Verify no port conflicts
netstat -tln | grep -E ":(8000|3500)" || echo "Ports available"

# Check available disk space (need space for volumes)
df -h /var/lib/docker
```

---

## Running Tests

### Option 1: Automated Test Runner (Recommended)

```bash
cd /git/ignition-stack-builder/tests

# Always ensure stack is running first
./ensure_stack_running.sh

# Run a single test
./test_runner.sh test_cases/T001_postgres_only.json 30

# Run multiple tests
for test in test_cases/T001*.json; do
    ./test_runner.sh "$test" 30
done
```

### Option 2: Manual Testing

```bash
cd /git/ignition-stack-builder/tests

# Ensure stack is running
./ensure_stack_running.sh

# Create test directory
mkdir -p temp/manual_test && cd temp/manual_test

# Generate stack
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d @../../test_cases/T001_postgres_only.json \
  -o stack.zip

# Extract and deploy
unzip stack.zip
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Test health (example for PostgreSQL)
docker exec postgres pg_isready

# Cleanup
docker-compose down -v
```

---

## Common Issues and Solutions

### Issue: "Connection refused" on port 8000

**Cause**: Stack builder backend is not running

**Solution**:
```bash
cd /git/ignition-stack-builder/tests
./ensure_stack_running.sh
```

### Issue: Test runner hangs or times out

**Cause**: Containers may not have started properly or API is slow

**Solution**:
```bash
# Check backend logs
cd /git/ignition-stack-builder
docker-compose logs backend

# Restart if needed
docker-compose restart backend
sleep 5

# Re-run ensure script
cd tests
./ensure_stack_running.sh
```

### Issue: "Address already in use" errors

**Cause**: Previous test deployments are still running

**Solution**:
```bash
# Find and stop conflicting containers
docker ps | grep -E "postgres|ignition|grafana"

# Navigate to test directory and clean up
cd /git/ignition-stack-builder/tests/temp/<test_name>
docker-compose down -v

# Or clean all test deployments
for dir in /git/ignition-stack-builder/tests/temp/*/; do
    if [ -f "$dir/docker-compose.yml" ]; then
        (cd "$dir" && docker-compose down -v 2>/dev/null || true)
    fi
done
```

### Issue: "No such file or directory" for volume mounts

**Cause**: This was the original bug - bind mounts failing on WSL2

**Status**: ✅ FIXED - Now using named volumes

**Verification**: Check generated `docker-compose.yml` should have:
```yaml
volumes:
  postgres-data:/var/lib/postgresql/data  # Named volume (good)
  # NOT: ./configs/postgres/data:/var/lib/... (old bind mount - bad)
```

---

## Before Starting Each Test Session

Run this checklist:

```bash
# 1. Ensure stack builder is running
cd /git/ignition-stack-builder/tests
./ensure_stack_running.sh

# 2. Clean up any previous test deployments
for dir in temp/*/; do
    if [ -f "$dir/docker-compose.yml" ]; then
        (cd "$dir" && docker-compose down -v 2>/dev/null || true)
    fi
done

# 3. Verify clean state
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"

# 4. Check Docker resources
docker system df
```

---

## Test Session Workflow

### Start of Session
1. Run `./ensure_stack_running.sh`
2. Review `PHASE3_PLAN.md` for test order
3. Create new session log entry in `SESSION_LOG.md`

### During Testing
1. Always check stack builder is running before each test
2. Document results immediately in `TEST_RESULTS.md`
3. Clean up test deployments after each test: `docker-compose down -v`
4. If you encounter any errors, check:
   - Backend logs: `docker-compose logs backend`
   - Test container logs: `docker-compose logs -f` (from test directory)

### End of Session
1. Update `TEST_RESULTS.md` with summary
2. Update `SESSION_LOG.md` with session notes
3. Commit any test case files or scripts created
4. Clean up all test deployments

---

## Quick Reference Commands

```bash
# Check stack builder status
docker ps --filter name=stack-builder

# Restart stack builder
cd /git/ignition-stack-builder
docker-compose restart

# View backend logs
docker-compose logs -f backend

# Test backend API manually
curl http://localhost:8000/catalog | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))" | head -50

# Clean all test volumes
docker volume ls | grep -E "t[0-9]{3}" | awk '{print $2}' | xargs -r docker volume rm

# Check what's using ports
netstat -tlnp | grep -E ":(8000|3500|5432|8088)"
```

---

## Automated Recovery Script

If you experience repeated issues, use this recovery script:

```bash
#!/bin/bash
# save as: tests/recover_test_environment.sh

echo "🔧 Recovering test environment..."

# Stop all test containers
cd /git/ignition-stack-builder/tests
for dir in temp/*/; do
    [ -f "$dir/docker-compose.yml" ] && (cd "$dir" && docker-compose down -v 2>/dev/null || true)
done

# Restart stack builder
cd /git/ignition-stack-builder
docker-compose down
docker-compose up -d

# Wait and verify
sleep 5
cd tests
./ensure_stack_running.sh

echo "✅ Environment recovered"
```

---

## Important Notes

1. **Always run `./ensure_stack_running.sh` at the start of testing**
2. **Clean up after each test** with `docker-compose down -v`
3. **Check backend is responding** if you get connection errors
4. **Named volumes are automatic** - no directory creation needed
5. **Test in order** - follow PHASE3_PLAN.md sequence
6. **Document immediately** - don't batch up test results

---

## Troubleshooting Decision Tree

```
Can't connect to port 8000?
├─ Run: ./ensure_stack_running.sh
└─ Still failing?
   └─ Check: docker-compose logs backend

Test deployment fails?
├─ Check: docker-compose logs (in test directory)
├─ Check: docker ps (is container running?)
└─ Check: Generated docker-compose.yml (correct volume syntax?)

Port already in use?
├─ Find conflicting container: docker ps | grep <port>
└─ Clean up: cd to test dir, docker-compose down -v

Out of disk space?
├─ Check: docker system df
└─ Clean: docker system prune -a --volumes (WARNING: removes unused data)
```
