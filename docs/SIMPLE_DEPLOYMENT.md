# Simple Deployment Guide

This guide explains the simplified deployment process for the Ignition Stack Builder.

## Overview

The deployment process is now simple and manual:
1. GitHub Actions builds Docker images and pushes to Docker Hub when you push to `main`
2. You manually deploy on any server by pulling the latest code and running a script

## Deployment Workflow

### 1. GitHub Actions (Automatic)

When you push to `main`:
- ✅ Runs CI tests and security checks
- ✅ Builds Docker images
- ✅ Pushes images to Docker Hub

**No automatic deployment happens** - you control when and where to deploy.

### 2. Deploy on Production Server (Manual)

On any production server:

```bash
cd /git/ignition-stack-builder
./scripts/deploy.sh
```

That's it! The script will:
1. Create a database backup
2. Pull latest code from Git
3. Pull latest Docker images from Docker Hub
4. Stop old containers
5. Start new containers
6. Run database migrations
7. Clean up old images

## Initial Server Setup

For a new server, you need to set it up once:

### Step 1: Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes to take effect.

### Step 2: Install Docker Compose

```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### Step 3: Clone the Repository

```bash
mkdir -p /git
cd /git
git clone https://github.com/nigelgwork/ignition-stack-builder.git
cd ignition-stack-builder
```

### Step 4: Generate SSL Certificates

```bash
./scripts/generate-ssl-certs.sh
```

### Step 5: Configure Environment

Create or edit `.env` file:

```bash
nano .env
```

Make sure to set a secure password for `AUTH_DB_PASSWORD`.

### Step 6: Initial Deployment

```bash
./scripts/deploy.sh
```

## Deploying Updates

Whenever you want to deploy the latest version:

```bash
cd /git/ignition-stack-builder
./scripts/deploy.sh
```

The script handles everything automatically including:
- Backing up the database
- Pulling latest code
- Pulling latest Docker images
- Restarting containers
- Running migrations

## Multiple Production Servers

You can deploy to as many servers as you want:

1. Set up each server using the initial setup steps above
2. Deploy to any server by SSH'ing in and running `./scripts/deploy.sh`

**Example:**

```bash
# Deploy to server 1
ssh user@server1.example.com
cd /git/ignition-stack-builder
./scripts/deploy.sh
exit

# Deploy to server 2
ssh user@server2.example.com
cd /git/ignition-stack-builder
./scripts/deploy.sh
exit
```

## Rollback

If a deployment goes wrong:

```bash
cd /git/ignition-stack-builder

# View recent commits
git log --oneline -10

# Rollback to previous commit
git reset --hard COMMIT_SHA

# Redeploy
./scripts/deploy.sh
```

Or restore from a backup:

```bash
cd /git/ignition-stack-builder

# View backups
ls -lh backups/

# Stop services
docker compose down

# Restore database
cat backups/backup_YYYYMMDD_HHMMSS.sql | docker compose exec -T auth-db psql -U stack_builder stack_builder_auth

# Restart
docker compose up -d
```

## Useful Commands

```bash
# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend

# Check status
docker compose ps

# Restart a service
docker compose restart backend

# View backups
ls -lh backups/

# Clean up old images manually
docker image prune -a
```

## GitHub Secrets Required

You only need these secrets in GitHub (for building and pushing images):

| Secret Name | Description |
|------------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

**No SSH keys or server details needed!**

## Security Notes

1. **Use strong passwords** in the `.env` file
2. **Set up firewall** on each server:
   ```bash
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```
3. **Keep servers updated**:
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```
4. **Monitor logs regularly**:
   ```bash
   docker compose logs -f
   ```

## Monitoring

Check your servers regularly:

```bash
# SSH to server
ssh user@server.example.com

# Check if services are running
cd /git/ignition-stack-builder
docker compose ps

# Check disk space
df -h

# Check memory
free -h

# View recent logs
docker compose logs --tail=100
```

## Troubleshooting

### Services won't start

```bash
docker compose logs backend
docker compose logs frontend

# Full restart
docker compose down
docker compose up -d
```

### Can't pull latest code

```bash
# Stash local changes
git stash

# Pull
git pull origin main

# Reapply changes if needed
git stash pop
```

### Database issues

```bash
# Check database logs
docker compose logs auth-db

# Check database is running
docker compose ps auth-db

# Restart database
docker compose restart auth-db
```

---

**That's it! Simple and straightforward deployment that you control.**
