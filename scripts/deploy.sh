#!/bin/bash
# Simple deployment script for Ignition Stack Builder
# Run this on any production server to deploy the latest version

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Ignition Stack Builder - Deployment"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}ERROR: docker-compose.yml not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Create backup if database is running
echo -e "${YELLOW}Creating database backup...${NC}"
mkdir -p backups
if docker compose ps auth-db | grep -q "Up"; then
    docker compose exec -T auth-db pg_dump -U stack_builder stack_builder_auth > backups/backup_$(date +%Y%m%d_%H%M%S).sql || true
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo "  Database not running - skipping backup"
fi
echo ""

# Pull latest code (if this is a git repo)
if [ -d ".git" ]; then
    echo -e "${YELLOW}Pulling latest code from Git...${NC}"
    git pull origin main
    echo -e "${GREEN}✓ Code updated${NC}"
    echo ""
fi

# Configure production ports (if needed)
echo -e "${YELLOW}Configuring production settings...${NC}"
if [ -f ".env" ]; then
    # Set HTTPS port to 443 if not already set
    if ! grep -q "FRONTEND_HTTPS_PORT=443" .env; then
        if grep -q "FRONTEND_HTTPS_PORT" .env; then
            sed -i 's/FRONTEND_HTTPS_PORT=.*/FRONTEND_HTTPS_PORT=443/' .env
        else
            echo "FRONTEND_HTTPS_PORT=443" >> .env
        fi
        echo "  Set FRONTEND_HTTPS_PORT=443"
    fi

    # Set HTTP port to 80 if not already set
    if ! grep -q "FRONTEND_PORT=80" .env; then
        if grep -q "FRONTEND_PORT" .env; then
            sed -i 's/FRONTEND_PORT=.*/FRONTEND_PORT=80/' .env
        else
            echo "FRONTEND_PORT=80" >> .env
        fi
        echo "  Set FRONTEND_PORT=80"
    fi
fi
echo -e "${GREEN}✓ Settings configured${NC}"
echo ""

# Pull latest Docker images (or build if needed)
echo -e "${YELLOW}Pulling latest Docker images...${NC}"
if docker compose pull backend frontend 2>/dev/null; then
    echo -e "${GREEN}✓ Images pulled from Docker Hub${NC}"
else
    echo -e "${YELLOW}⚠ Could not pull images (may be ARM architecture)${NC}"
    echo -e "${YELLOW}Building images locally instead...${NC}"
    docker compose build backend frontend
    echo -e "${GREEN}✓ Images built locally${NC}"
fi
echo ""

# Stop and remove old containers
echo -e "${YELLOW}Stopping old containers...${NC}"
docker compose stop backend frontend
docker compose rm -f backend frontend
echo -e "${GREEN}✓ Old containers removed${NC}"
echo ""

# Start new containers
echo -e "${YELLOW}Starting new containers...${NC}"
docker compose up -d backend frontend
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker compose exec -T backend python migrations/001_create_initial_schema.py || true
echo -e "${GREEN}✓ Migrations complete${NC}"
echo ""

# Health check
echo -e "${YELLOW}Running health check...${NC}"
sleep 10
if docker compose ps | grep -q "backend.*Up"; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running - check logs with: docker compose logs backend${NC}"
fi

if docker compose ps | grep -q "frontend.*Up"; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not running - check logs with: docker compose logs frontend${NC}"
fi
echo ""

# Clean up old images (optional)
echo -e "${YELLOW}Cleaning up old Docker images...${NC}"
docker image prune -a -f --filter "until=72h" || true
echo -e "${GREEN}✓ Old images cleaned up${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "View logs:"
echo "  docker compose logs -f"
echo ""
echo "Check status:"
echo "  docker compose ps"
echo ""
echo "View recent backups:"
echo "  ls -lh backups/"
echo ""
