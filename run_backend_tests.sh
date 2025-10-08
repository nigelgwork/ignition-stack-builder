#!/bin/bash
# Backend API Test Suite
# Comprehensive automated tests for IIoT Stack Builder Backend

API_URL="http://localhost:8000"
PASS_COUNT=0
FAIL_COUNT=0

echo "========================================="
echo "Backend API Test Suite"
echo "========================================="
echo ""

# Helper function
run_test() {
    local test_id=$1
    local test_name=$2
    echo "Running $test_id: $test_name"
}

pass_test() {
    echo "  ✓ PASS"
    ((PASS_COUNT++))
    echo ""
}

fail_test() {
    local reason=$1
    echo "  ✗ FAIL: $reason"
    ((FAIL_COUNT++))
    echo ""
}

# BAT-003: Reverse Proxy Detection
run_test "BAT-003" "Reverse Proxy Detection"
RESULT=$(curl -s -X POST $API_URL/detect-integrations \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"app_id":"traefik","instance_name":"traefik","config":{}},{"app_id":"ignition","instance_name":"ignition-1","config":{}},{"app_id":"grafana","instance_name":"grafana","config":{}}],"global_settings":{"timezone":"UTC","restart_policy":"unless-stopped"}}')

PROVIDER=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('integrations',{}).get('reverse_proxy',{}).get('provider',''))")
TARGET_COUNT=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('integrations',{}).get('reverse_proxy',{}).get('targets',[])))")

if [ "$PROVIDER" == "traefik" ] && [ "$TARGET_COUNT" == "2" ]; then
    echo "  Provider: $PROVIDER, Targets: $TARGET_COUNT"
    pass_test
else
    fail_test "Provider=$PROVIDER (expected traefik), Targets=$TARGET_COUNT (expected 2)"
fi

# BAT-004: MQTT Detection
run_test "BAT-004" "MQTT Broker Detection"
RESULT=$(curl -s -X POST $API_URL/detect-integrations \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"app_id":"emqx","instance_name":"emqx","config":{}},{"app_id":"ignition","instance_name":"ignition-1","config":{}}],"global_settings":{"timezone":"UTC","restart_policy":"unless-stopped"}}')

HAS_MQTT=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print('mqtt_broker' in data.get('integrations',{}))")
PROVIDER_COUNT=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('integrations',{}).get('mqtt_broker',{}).get('providers',[])))")

if [ "$HAS_MQTT" == "True" ] && [ "$PROVIDER_COUNT" == "1" ]; then
    echo "  MQTT integration detected, Providers: $PROVIDER_COUNT"
    pass_test
else
    fail_test "HAS_MQTT=$HAS_MQTT, Providers=$PROVIDER_COUNT"
fi

# BAT-005: OAuth Detection
run_test "BAT-005" "OAuth Provider Detection"
RESULT=$(curl -s -X POST $API_URL/detect-integrations \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"app_id":"keycloak","instance_name":"keycloak","config":{}},{"app_id":"grafana","instance_name":"grafana","config":{}},{"app_id":"portainer","instance_name":"portainer","config":{}}],"global_settings":{"timezone":"UTC","restart_policy":"unless-stopped"}}')

HAS_OAUTH=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print('oauth_provider' in data.get('integrations',{}))")
CLIENT_COUNT=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('integrations',{}).get('oauth_provider',{}).get('clients',[])))")

if [ "$HAS_OAUTH" == "True" ] && [ "$CLIENT_COUNT" == "2" ]; then
    echo "  OAuth detected, Clients: $CLIENT_COUNT (grafana, portainer)"
    pass_test
else
    fail_test "HAS_OAUTH=$HAS_OAUTH, Clients=$CLIENT_COUNT (expected 2)"
fi

# BAT-006: Database Detection
run_test "BAT-006" "Database Integration Detection"
RESULT=$(curl -s -X POST $API_URL/detect-integrations \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"app_id":"postgres","instance_name":"postgres-1","config":{}},{"app_id":"mariadb","instance_name":"mariadb-1","config":{}},{"app_id":"ignition","instance_name":"ignition-1","config":{}},{"app_id":"grafana","instance_name":"grafana","config":{}}],"global_settings":{"timezone":"UTC","restart_policy":"unless-stopped"}}')

PROVIDER_COUNT=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('integrations',{}).get('db_provider',{}).get('providers',[])))")
CLIENT_COUNT=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('integrations',{}).get('db_provider',{}).get('clients',[])))")

if [ "$PROVIDER_COUNT" == "2" ] && [ "$CLIENT_COUNT" -ge "2" ]; then
    echo "  DB Providers: $PROVIDER_COUNT, Clients: $CLIENT_COUNT"
    pass_test
else
    fail_test "Providers=$PROVIDER_COUNT (expected 2), Clients=$CLIENT_COUNT"
fi

# BAT-007: Mutual Exclusivity Detection
run_test "BAT-007" "Mutual Exclusivity Conflict Detection"
RESULT=$(curl -s -X POST $API_URL/detect-integrations \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"app_id":"traefik","instance_name":"traefik","config":{}},{"app_id":"nginx-proxy-manager","instance_name":"nginx-proxy-manager","config":{}}],"global_settings":{"timezone":"UTC","restart_policy":"unless-stopped"}}')

CONFLICT_COUNT=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('conflicts',[])))")
CONFLICT_GROUP=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('conflicts',[])[0].get('group','') if data.get('conflicts') else '')")

if [ "$CONFLICT_COUNT" == "1" ] && [ "$CONFLICT_GROUP" == "reverse_proxy" ]; then
    echo "  Conflict detected: $CONFLICT_GROUP"
    pass_test
else
    fail_test "Conflicts=$CONFLICT_COUNT (expected 1), Group=$CONFLICT_GROUP"
fi

# BAT-008: Recommendations
run_test "BAT-008" "Recommendation Generation"
RESULT=$(curl -s -X POST $API_URL/detect-integrations \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"app_id":"ignition","instance_name":"ignition-1","config":{}},{"app_id":"postgres","instance_name":"postgres-1","config":{}}],"global_settings":{"timezone":"UTC","restart_policy":"unless-stopped"}}')

REC_COUNT=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('recommendations',[])))")

if [ "$REC_COUNT" -gt "0" ]; then
    echo "  Recommendations generated: $REC_COUNT"
    pass_test
else
    fail_test "No recommendations generated"
fi

# BAT-009: Generate with Integration Settings
run_test "BAT-009" "POST /generate with Integration Settings"
RESULT=$(curl -s -X POST $API_URL/generate \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"app_id":"ignition","instance_name":"ignition-1","config":{"version":"latest"}}],"global_settings":{"timezone":"UTC","restart_policy":"unless-stopped"},"integration_settings":{"mqtt":{"enable_tls":true,"username":"test"}}}')

HAS_COMPOSE=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print('docker_compose' in data)")
HAS_ENV=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print('env' in data)")
HAS_README=$(echo $RESULT | python3 -c "import sys, json; data=json.load(sys.stdin); print('readme' in data)")

if [ "$HAS_COMPOSE" == "True" ] && [ "$HAS_ENV" == "True" ] && [ "$HAS_README" == "True" ]; then
    echo "  Generated: docker_compose, env, readme"
    pass_test
else
    fail_test "Missing outputs: compose=$HAS_COMPOSE, env=$HAS_ENV, readme=$HAS_README"
fi

# BAT-010: Download endpoint (test without actually downloading)
run_test "BAT-010" "POST /download Returns ZIP"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $API_URL/download \
  -H "Content-Type: application/json" \
  -d '{"instances":[{"app_id":"ignition","instance_name":"ignition-1","config":{"version":"latest"}}],"global_settings":{"timezone":"UTC","restart_policy":"unless-stopped"}}')

if [ "$HTTP_CODE" == "200" ]; then
    echo "  HTTP Status: $HTTP_CODE (OK)"
    pass_test
else
    fail_test "HTTP Status: $HTTP_CODE (expected 200)"
fi

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "PASSED: $PASS_COUNT"
echo "FAILED: $FAIL_COUNT"
echo "TOTAL:  $((PASS_COUNT + FAIL_COUNT))"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    exit 0
else
    echo "✗ SOME TESTS FAILED"
    exit 1
fi
