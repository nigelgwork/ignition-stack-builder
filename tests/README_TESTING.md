# Phase 3 Testing - Quick Start

## ⚠️ IMPORTANT: Before Every Test Session

Stack builder containers may stop due to system operations (upgrades, Docker restarts, etc.). **Always run this first:**

```bash
cd /git/ignition-stack-builder/tests
./ensure_stack_running.sh
```

This takes 5-10 seconds and ensures the backend API is ready.

---

## Problem & Solution Summary

### The Issue
When you run system commands (like `/upgrade`) or Docker restarts, the stack builder containers stop. Even though they have `restart: unless-stopped`, they don't auto-start after:
- Docker daemon restarts
- Explicit stop commands
- System-level operations

### The Solution
Always run `./ensure_stack_running.sh` before testing. This script:
- ✅ Checks if containers are running
- ✅ Starts them if needed
- ✅ Waits for API to be ready
- ✅ Verifies backend is responding

---

## Quick Test Run

```bash
# 1. Ensure stack is running (ALWAYS DO THIS FIRST)
cd /git/ignition-stack-builder/tests
./ensure_stack_running.sh

# 2. Run a test
./test_runner.sh test_cases/T001_postgres_only.json 30

# 3. Or test manually
mkdir -p temp/my_test && cd temp/my_test
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d @../../test_cases/T001_postgres_only.json \
  -o stack.zip
unzip stack.zip
docker-compose up -d
docker-compose ps
docker-compose down -v  # Clean up when done
```

---

## Critical Bug Fixed ✅

**Issue**: Bind mount volumes failed on WSL2 with "no such file or directory" errors

**Fix**: Switched all services to use named volumes
- Before: `./configs/postgres/data:/var/lib/postgresql/data` ❌
- After: `postgres-data:/var/lib/postgresql/data` ✅

**Status**: Fully implemented and verified working

---

## Complete Documentation

- **TESTING_INSTRUCTIONS.md** - Full testing guide with troubleshooting
- **PHASE3_PLAN.md** - Complete test plan (35 tests)
- **SESSION_LOG.md** - Detailed session notes and progress
- **TEST_RESULTS.md** - Test results and findings

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused on port 8000` | Stack builder not running | `./ensure_stack_running.sh` |
| `Address already in use` | Previous test still running | `docker-compose down -v` in test dir |
| `No such file or directory` (volume) | Old bind mount bug | ✅ Fixed - regenerate stack |

---

## Test Status

- ✅ T001 (PostgreSQL) - PASS
- ⏸️ T002 (Ignition) - Ready to test
- ⏸️ T003-T035 - Pending

---

**Remember**: Run `./ensure_stack_running.sh` before EVERY test session!
