#!/bin/bash

# Production Setup Script for Ignition Stack Builder
# This script sets up the production environment on ignitionvps.gaskony.me

set -e

echo "=========================================="
echo "Ignition Stack Builder - Production Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo -e "${RED}ERROR: Please do not run this script as root${NC}"
  echo "Run as your regular user with sudo privileges"
  exit 1
fi

echo -e "${GREEN}Step 1: Checking prerequisites...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}Docker installed successfully${NC}"
    echo -e "${YELLOW}Please log out and log back in for group changes to take effect${NC}"
else
    echo -e "${GREEN}Docker is already installed${NC}"
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}ERROR: docker compose is not available${NC}"
    exit 1
else
    echo -e "${GREEN}Docker Compose is available${NC}"
fi

echo ""
echo -e "${GREEN}Step 2: Creating project directory...${NC}"

# Create project directory
PROJECT_DIR="$HOME/ignition-stack-builder"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    echo -e "${GREEN}Created directory: $PROJECT_DIR${NC}"
else
    echo -e "${YELLOW}Directory already exists: $PROJECT_DIR${NC}"
fi

cd "$PROJECT_DIR"

echo ""
echo -e "${GREEN}Step 3: Cloning repository...${NC}"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git not found. Installing Git...${NC}"
    sudo apt-get update
    sudo apt-get install -y git
fi

# Clone or update repository
if [ ! -d ".git" ]; then
    echo "Enter your GitHub repository URL (or press Enter for default):"
    read -r REPO_URL
    REPO_URL=${REPO_URL:-"https://github.com/nigelgwork/ignition-stack-builder.git"}

    git clone "$REPO_URL" .
    echo -e "${GREEN}Repository cloned${NC}"
else
    echo -e "${YELLOW}Repository already exists, pulling latest changes...${NC}"
    git pull
fi

echo ""
echo -e "${GREEN}Step 4: Setting up environment variables...${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Docker Compose Configuration
COMPOSE_PROJECT_NAME=stack-builder

# Frontend Configuration
FRONTEND_PORT=3500
FRONTEND_HTTPS_PORT=3443

# Backend Configuration
BACKEND_PORT=8000

# Database Configuration
AUTH_DB_PORT=5433
AUTH_DB_NAME=stack_builder_auth
AUTH_DB_USER=stack_builder
AUTH_DB_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_VERSION=16-alpine

# Redis Configuration
REDIS_PORT=6379
REDIS_VERSION=7-alpine

# Timezone
TZ=UTC
EOF

    echo -e "${GREEN}.env file created${NC}"
    echo -e "${YELLOW}IMPORTANT: Edit .env and change AUTH_DB_PASSWORD!${NC}"
    echo ""
    read -p "Press Enter to edit .env now (or Ctrl+C to exit and edit later)..."
    ${EDITOR:-nano} .env
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Create backend .env if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env file..."

    # Generate secure random keys
    JWT_SECRET=$(openssl rand -hex 32)
    SESSION_SECRET=$(openssl rand -hex 32)

    cat > backend/.env << EOF
# JWT Configuration
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Session Configuration
SESSION_SECRET=$SESSION_SECRET

# Database Configuration
AUTH_DB_HOST=auth-db
AUTH_DB_PORT=5432
AUTH_DB_NAME=stack_builder_auth
AUTH_DB_USER=stack_builder
AUTH_DB_PASSWORD=CHANGE_ME_IN_PRODUCTION

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Application Configuration
DEBUG=False
ENABLE_MFA=True
EOF

    echo -e "${GREEN}backend/.env file created with secure keys${NC}"
    echo -e "${YELLOW}IMPORTANT: Edit backend/.env and change AUTH_DB_PASSWORD to match main .env!${NC}"
    echo ""
    read -p "Press Enter to edit backend/.env now (or Ctrl+C to exit and edit later)..."
    ${EDITOR:-nano} backend/.env
else
    echo -e "${YELLOW}backend/.env file already exists${NC}"
fi

echo ""
echo -e "${GREEN}Step 5: Generating SSL certificates...${NC}"

# Generate SSL certificates for HTTPS
if [ ! -f "frontend/certs/cert.pem" ]; then
    chmod +x scripts/generate-ssl-certs.sh
    ./scripts/generate-ssl-certs.sh
    echo -e "${GREEN}SSL certificates generated${NC}"
else
    echo -e "${YELLOW}SSL certificates already exist${NC}"
fi

echo ""
echo -e "${GREEN}Step 6: Creating required directories...${NC}"

# Create backup directory
mkdir -p backups
echo -e "${GREEN}Created backups directory${NC}"

echo ""
echo -e "${GREEN}Step 7: Building and starting services...${NC}"

# Pull latest images and start services
docker compose pull
docker compose up -d --build

echo ""
echo "Waiting for services to start..."
sleep 10

echo ""
echo -e "${GREEN}Step 8: Running database migrations...${NC}"

# Run database migrations
docker compose exec -T backend python migrations/001_create_initial_schema.py || echo -e "${YELLOW}Migration may have already been applied${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "Production setup complete!"
echo "==========================================${NC}"
echo ""
echo "Services are running at:"
echo "  HTTPS: https://ignitionvps.gaskony.me"
echo "  HTTP:  http://ignitionvps.gaskony.me:3500"
echo "  API:   http://ignitionvps.gaskony.me:8000"
echo ""
echo "To check status: docker compose ps"
echo "To view logs:    docker compose logs -f"
echo "To stop:         docker compose down"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure your reverse proxy (Nginx/Traefik) to point ignitionvps.gaskony.me to port 3443"
echo "2. Set up SSL certificates with Let's Encrypt if needed"
echo "3. Configure firewall rules"
echo ""
echo -e "${YELLOW}For CI/CD setup:${NC}"
echo "1. Generate an SSH key pair for GitHub Actions"
echo "2. Add the public key to ~/.ssh/authorized_keys on this server"
echo "3. Add secrets to GitHub repository settings"
echo ""
