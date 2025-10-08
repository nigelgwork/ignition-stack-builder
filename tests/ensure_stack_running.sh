#!/bin/bash
# Helper script to ensure stack builder containers are running before testing

set -e

cd /git/ignition-stack-builder

echo "🔍 Checking stack builder status..."

# Check if containers are running
BACKEND_STATUS=$(docker inspect stack-builder-backend --format '{{.State.Status}}' 2>/dev/null || echo "not-found")
FRONTEND_STATUS=$(docker inspect stack-builder-frontend --format '{{.State.Status}}' 2>/dev/null || echo "not-found")

if [ "$BACKEND_STATUS" = "running" ] && [ "$FRONTEND_STATUS" = "running" ]; then
    echo "✅ Stack builder is already running"

    # Quick API check
    if curl -s http://localhost:8000/catalog > /dev/null 2>&1; then
        echo "✅ Backend API is responding"
        exit 0
    else
        echo "⚠️  Backend not responding, restarting..."
    fi
fi

echo "🚀 Starting stack builder containers..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 5

# Wait for backend API to be ready
MAX_WAIT=30
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8000/catalog > /dev/null 2>&1; then
        echo "✅ Stack builder is ready!"
        exit 0
    fi
    echo "   Waiting for backend API... (${WAITED}s/${MAX_WAIT}s)"
    sleep 2
    WAITED=$((WAITED + 2))
done

echo "❌ Backend failed to become ready in time"
echo "Check logs with: docker compose logs backend"
exit 1
