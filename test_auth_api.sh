#!/bin/bash
# Comprehensive Authentication API Test Script
# Tests all authentication endpoints systematically

set -e

API_URL="http://localhost:8000/api"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="TestPass123!@#"
TEST_NAME="Test User"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Authentication API Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test an endpoint
test_endpoint() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local headers="$5"
    local expected_status="$6"

    echo -e "${YELLOW}Testing:${NC} $test_name"

    if [ -n "$headers" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "$headers" \
            -d "$data" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        ((TESTS_PASSED++))
        echo "$body"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected HTTP $expected_status, got $http_code)"
        ((TESTS_FAILED++))
        echo "Response: $body"
        return 1
    fi
    echo ""
}

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. User Registration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 1: Register new user
REGISTER_RESPONSE=$(test_endpoint \
    "Register new user" \
    "POST" \
    "/auth/register" \
    "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"$TEST_NAME\"}" \
    "" \
    "201")

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. User Login${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 2: Login with correct credentials
LOGIN_RESPONSE=$(test_endpoint \
    "Login with correct credentials" \
    "POST" \
    "/auth/login" \
    "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
    "" \
    "200")

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"refresh_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}ERROR: Could not extract access token${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Access token obtained${NC}"
echo ""

# Test 3: Login with wrong password
test_endpoint \
    "Login with wrong password (should fail)" \
    "POST" \
    "/auth/login" \
    "{\"email\":\"$TEST_EMAIL\",\"password\":\"WrongPassword123!\"}" \
    "" \
    "401"

echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. Protected Endpoints${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 4: Get current user info
test_endpoint \
    "Get current user info" \
    "GET" \
    "/auth/me" \
    "" \
    "Authorization: Bearer $ACCESS_TOKEN" \
    "200"

echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4. Settings Management${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 5: Get user settings
test_endpoint \
    "Get user settings" \
    "GET" \
    "/settings" \
    "" \
    "Authorization: Bearer $ACCESS_TOKEN" \
    "200"

echo ""

# Test 6: Update settings
test_endpoint \
    "Update user settings" \
    "PUT" \
    "/settings" \
    "{\"theme\":\"light\",\"timezone\":\"UTC\",\"notifications_enabled\":true}" \
    "Authorization: Bearer $ACCESS_TOKEN" \
    "200"

echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}5. Stack Management${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 7: Create stack
STACK_RESPONSE=$(test_endpoint \
    "Create new stack" \
    "POST" \
    "/stacks" \
    "{\"stack_name\":\"Test Stack\",\"description\":\"A test stack\",\"config_json\":{\"services\":[\"ignition\"]},\"is_public\":false}" \
    "Authorization: Bearer $ACCESS_TOKEN" \
    "201")

# Extract stack ID
STACK_ID=$(echo "$STACK_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4 | head -1)

if [ -z "$STACK_ID" ]; then
    echo -e "${YELLOW}⚠ Could not extract stack ID (may not be critical)${NC}"
fi

echo ""

# Test 8: List stacks
test_endpoint \
    "List user stacks" \
    "GET" \
    "/stacks" \
    "" \
    "Authorization: Bearer $ACCESS_TOKEN" \
    "200"

echo ""

if [ -n "$STACK_ID" ]; then
    # Test 9: Get specific stack
    test_endpoint \
        "Get specific stack" \
        "GET" \
        "/stacks/$STACK_ID" \
        "" \
        "Authorization: Bearer $ACCESS_TOKEN" \
        "200"

    echo ""

    # Test 10: Update stack
    test_endpoint \
        "Update stack" \
        "PUT" \
        "/stacks/$STACK_ID" \
        "{\"stack_name\":\"Updated Test Stack\",\"description\":\"An updated test stack\"}" \
        "Authorization: Bearer $ACCESS_TOKEN" \
        "200"

    echo ""

    # Test 11: Delete stack
    test_endpoint \
        "Delete stack" \
        "DELETE" \
        "/stacks/$STACK_ID" \
        "" \
        "Authorization: Bearer $ACCESS_TOKEN" \
        "204"

    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}6. Token Refresh${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 12: Refresh token
test_endpoint \
    "Refresh access token" \
    "POST" \
    "/auth/refresh" \
    "\"$REFRESH_TOKEN\"" \
    "" \
    "200"

echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}7. Logout${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 13: Logout
test_endpoint \
    "Logout user" \
    "POST" \
    "/auth/logout" \
    "" \
    "Authorization: Bearer $ACCESS_TOKEN" \
    "200"

echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}8. Authorization Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 14: Access protected endpoint without token
test_endpoint \
    "Access protected endpoint without token (should fail)" \
    "GET" \
    "/auth/me" \
    "" \
    "" \
    "403"

echo ""

# Test 15: Access with invalid token
test_endpoint \
    "Access with invalid token (should fail)" \
    "GET" \
    "/auth/me" \
    "" \
    "Authorization: Bearer invalid_token_12345" \
    "401"

echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
