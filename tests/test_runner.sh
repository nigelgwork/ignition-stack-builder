#!/bin/bash
# IIoT Stack Builder - Test Runner
# Systematically tests generated stacks for deployment and functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8000"
TEST_CASE=$1
WAIT_TIME=${2:-60}  # Default wait time for services to start

if [ -z "$TEST_CASE" ]; then
    echo "Usage: $0 <test_case.json> [wait_time_seconds]"
    echo "Example: $0 test_cases/T001_postgres_only.json 30"
    exit 1
fi

if [ ! -f "$TEST_CASE" ]; then
    echo -e "${RED}❌ Test case not found: $TEST_CASE${NC}"
    exit 1
fi

# Extract test info
TEST_ID=$(basename "$TEST_CASE" .json)
TEST_DIR="temp/${TEST_ID}"
START_TIME=$(date +%s)
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  IIoT Stack Builder - Test Runner     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}🧪 Test ID:${NC} $TEST_ID"
echo -e "${YELLOW}📁 Test Case:${NC} $TEST_CASE"
echo -e "${YELLOW}⏰ Start Time:${NC} $TIMESTAMP"
echo ""

# Clean previous deployment
if [ -d "$TEST_DIR" ]; then
    echo -e "${YELLOW}🧹 Cleaning previous deployment...${NC}"
    cd "$TEST_DIR" 2>/dev/null && docker compose down -v 2>/dev/null || true
    cd - >/dev/null
    rm -rf "$TEST_DIR"
fi

mkdir -p "$TEST_DIR"

# Step 1: Generate stack from API
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📥 Step 1: Generating stack from API...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

HTTP_CODE=$(curl -s -w "%{http_code}" -X POST "${API_URL}/download" \
    -H "Content-Type: application/json" \
    -d @"$TEST_CASE" \
    -o "${TEST_DIR}/stack.zip")

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}❌ FAIL: Stack generation failed (HTTP $HTTP_CODE)${NC}"
    if [ -f "${TEST_DIR}/stack.zip" ]; then
        echo "Error response:"
        cat "${TEST_DIR}/stack.zip"
    fi
    exit 1
fi

if [ ! -f "${TEST_DIR}/stack.zip" ] || [ ! -s "${TEST_DIR}/stack.zip" ]; then
    echo -e "${RED}❌ FAIL: Stack ZIP file not created or empty${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Stack generated successfully${NC}"

# Step 2: Extract stack
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📦 Step 2: Extracting stack files...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

unzip -q "${TEST_DIR}/stack.zip" -d "$TEST_DIR"

if [ ! -f "${TEST_DIR}/docker compose.yml" ]; then
    echo -e "${RED}❌ FAIL: docker compose.yml not found in extracted files${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Stack extracted${NC}"
echo "Files:"
ls -lh "$TEST_DIR" | grep -v "^total" | awk '{print "  - " $9}'

# Step 3: Deploy stack
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🚀 Step 3: Deploying stack...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$TEST_DIR"

# Use start.sh if it exists (for Ignition stacks), otherwise docker compose
if [ -f "start.sh" ]; then
    echo "Using start.sh for deployment..."
    chmod +x start.sh
    ./start.sh > deploy.log 2>&1 &
    DEPLOY_PID=$!
    echo "Deployment started (PID: $DEPLOY_PID)"
else
    echo "Using docker compose for deployment..."
    docker compose up -d > deploy.log 2>&1
fi

cd - >/dev/null

# Step 4: Wait for services
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⏳ Step 4: Waiting for services to start (${WAIT_TIME}s)...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

sleep "$WAIT_TIME"

# Step 5: Check container status
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔍 Step 5: Checking container status...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$TEST_DIR"

# Get expected services
EXPECTED_SERVICES=$(docker compose config --services | wc -l)
echo "Expected services: $EXPECTED_SERVICES"

# Get running containers
RUNNING_CONTAINERS=$(docker compose ps | grep "Up" | wc -l)
echo "Running containers: $RUNNING_CONTAINERS"

# Show container status
echo ""
docker compose ps

cd - >/dev/null

# Determine test result
SUCCESS=false
if [ "$RUNNING_CONTAINERS" -eq "$EXPECTED_SERVICES" ] && [ "$EXPECTED_SERVICES" -gt 0 ]; then
    SUCCESS=true
fi

# Step 6: Run health checks (if available)
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🏥 Step 6: Running health checks...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Extract service types from test case
SERVICES=$(cat "$TEST_CASE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(' '.join([i['app_id'] for i in data['instances']]))")

for service in $SERVICES; do
    CONTAINER=$(cat "$TEST_CASE" | python3 -c "import json,sys; data=json.load(sys.stdin); inst=[i for i in data['instances'] if i['app_id']=='$service'][0]; print(inst['instance_name'])")
    echo ""
    echo "Checking $service ($CONTAINER)..."
    python3 health_checks.py "$service" "$CONTAINER" || true
done

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Final result
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📊 Test Result${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$SUCCESS" = true ]; then
    echo -e "${GREEN}✅ PASS${NC} - All containers running ($RUNNING_CONTAINERS/$EXPECTED_SERVICES)"
else
    echo -e "${RED}❌ FAIL${NC} - Some containers not running ($RUNNING_CONTAINERS/$EXPECTED_SERVICES)"
fi

echo "Duration: ${DURATION}s"
echo ""

# Save result summary
RESULT_FILE="results/${TEST_ID}_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "Test: $TEST_ID"
    echo "Status: $([ "$SUCCESS" = true ] && echo "PASS" || echo "FAIL")"
    echo "Timestamp: $TIMESTAMP"
    echo "Duration: ${DURATION}s"
    echo "Containers: $RUNNING_CONTAINERS/$EXPECTED_SERVICES"
    echo ""
    echo "Container Status:"
    cd "$TEST_DIR" && docker compose ps && cd - >/dev/null
} > "$RESULT_FILE"

echo -e "${BLUE}📝 Results saved to: $RESULT_FILE${NC}"
echo ""

# Cleanup prompt
echo -e "${YELLOW}🧹 Cleanup:${NC}"
echo "  Keep running: Containers remain active for inspection"
echo "  Stop now:     cd $TEST_DIR && docker compose down -v"
echo ""

# Return exit code based on success
if [ "$SUCCESS" = true ]; then
    exit 0
else
    exit 1
fi
