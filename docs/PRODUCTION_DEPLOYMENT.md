# Production Deployment Guide

This guide explains how to deploy the Ignition Stack Builder to production at `ignitionvps.gaskony.me` with automated CI/CD.

## Overview

The deployment system uses GitHub Actions to:
1. Run tests and security checks on every push
2. Build Docker images and push to Docker Hub
3. Automatically deploy to production when code is pushed to `main` branch
4. Create database backups before deployment
5. Run health checks after deployment
6. Rollback on failure

## Prerequisites

- VPS server with Ubuntu 20.04+ or similar Linux distribution
- Domain name pointing to your VPS (ignitionvps.gaskony.me)
- Docker and Docker Compose installed
- GitHub repository with Actions enabled
- Docker Hub account (for storing container images)

---

## Part 1: VPS Server Setup

### Step 1: Initial Server Setup

SSH into your VPS server:

```bash
ssh your_user@ignitionvps.gaskony.me
```

### Step 2: Run Production Setup Script

Download and run the production setup script:

```bash
# Download the setup script
curl -O https://raw.githubusercontent.com/nigelgwork/ignition-stack-builder/main/scripts/production-setup.sh

# Make it executable
chmod +x production-setup.sh

# Run the setup script
./production-setup.sh
```

The script will:
- Install Docker and Docker Compose (if needed)
- Clone the repository to `~/ignition-stack-builder`
- Create `.env` files with secure random keys
- Generate SSL certificates
- Start all services
- Run database migrations

### Step 3: Configure Environment Variables

Edit the environment files to set secure passwords:

```bash
cd ~/ignition-stack-builder

# Edit main .env file
nano .env

# Edit backend .env file
nano backend/.env
```

**Important**: Change `AUTH_DB_PASSWORD` to a secure password in both files (they must match).

### Step 4: Configure Reverse Proxy (Optional but Recommended)

If you want to use a reverse proxy like Nginx or Traefik:

**Option A: Using Nginx**

```bash
sudo apt-get install nginx

# Create nginx configuration
sudo nano /etc/nginx/sites-available/ignition-stack-builder
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name ignitionvps.gaskony.me;

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name ignitionvps.gaskony.me;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/ignitionvps.gaskony.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ignitionvps.gaskony.me/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy to frontend
    location / {
        proxy_pass https://localhost:3443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy to backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and reload Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/ignition-stack-builder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Option B: Let's Encrypt SSL Certificates**

```bash
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d ignitionvps.gaskony.me

# Auto-renewal is configured automatically
```

---

## Part 2: GitHub CI/CD Setup

### Step 1: Generate SSH Key for GitHub Actions

On your VPS server:

```bash
# Generate a new SSH key specifically for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_deploy_key

# Display the public key
cat ~/.ssh/github_actions_deploy_key.pub
```

Add the public key to authorized_keys:

```bash
cat ~/.ssh/github_actions_deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Display the private key (you'll need this for GitHub):

```bash
cat ~/.ssh/github_actions_deploy_key
```

**Copy the entire private key output (including the BEGIN and END lines).**

### Step 2: Get Your Server Details

Collect the following information:

1. **Production Host**: Your server's IP address or hostname
   ```bash
   echo "Production Host: $(hostname -I | awk '{print $1}')"
   # Or: ignitionvps.gaskony.me
   ```

2. **Production User**: Your username on the server
   ```bash
   echo "Production User: $(whoami)"
   ```

3. **SSH Key**: The private key from Step 1

### Step 3: Configure GitHub Secrets

Go to your GitHub repository:

1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each of the following:

#### Required Secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `PRODUCTION_HOST` | `ignitionvps.gaskony.me` or IP | Your VPS hostname or IP address |
| `PRODUCTION_USER` | Your SSH username | The user to SSH as (e.g., `ubuntu`, `root`, etc.) |
| `PRODUCTION_SSH_KEY` | Private key from Step 1 | The entire private SSH key (including BEGIN/END lines) |
| `DOCKERHUB_USERNAME` | Your Docker Hub username | Used to push Docker images |
| `DOCKERHUB_TOKEN` | Your Docker Hub access token | Create at https://hub.docker.com/settings/security |

#### Optional Secrets (if not set, will use defaults):

| Secret Name | Value | Description |
|------------|-------|-------------|
| `JWT_SECRET_KEY` | Random string (32+ chars) | JWT token signing key |
| `SESSION_SECRET` | Random string (32+ chars) | Session encryption key |

**To create Docker Hub token:**
1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name: "github-actions"
4. Permissions: Read & Write
5. Copy the token and save it to GitHub secrets

### Step 4: Configure GitHub Environment

1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name: `production`
4. (Optional) Add protection rules:
   - Required reviewers (for manual approval before deployment)
   - Deployment branches (only allow `main` branch)

### Step 5: Test the CI/CD Pipeline

Make a small change to trigger the workflow:

```bash
# In your local dev environment
cd /git/ignition-stack-builder

# Make a change (e.g., update README)
echo "" >> README.md
echo "<!-- CI/CD Test -->" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main
```

Watch the deployment:

1. Go to **Actions** tab in GitHub
2. Click on the workflow run
3. Monitor progress through: CI Tests → Build Images → Deploy to Production

---

## Part 3: Deployment Workflow

### Automatic Deployment

Every time you push to the `main` branch:

1. **CI Tests Run** (5-10 minutes)
   - Backend API tests
   - Code quality checks (flake8, black, isort)
   - Security scanning (Bandit, Safety)
   - Docker build verification

2. **Build and Push Images** (3-5 minutes)
   - Build backend and frontend Docker images
   - Push to Docker Hub with `latest` and commit SHA tags

3. **Deploy to Production** (2-3 minutes)
   - SSH to production server
   - Create database backup
   - Pull latest code from GitHub
   - Pull latest Docker images
   - Restart services with `docker compose up -d --build`
   - Run database migrations
   - Health checks

4. **Cleanup** (1 minute)
   - Remove old Docker images (older than 72 hours)
   - Remove old backups (older than 7 days)

### Manual Deployment

You can also trigger deployment manually:

1. Go to **Actions** tab
2. Click **Deploy to Production**
3. Click **Run workflow**
4. Select branch (usually `main`)
5. Click **Run workflow**

---

## Part 4: Monitoring and Maintenance

### Check Service Status

```bash
# SSH to server
ssh your_user@ignitionvps.gaskony.me

# Check running services
cd ~/ignition-stack-builder
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
```

### View Backups

```bash
cd ~/ignition-stack-builder/backups
ls -lah
```

### Restore from Backup

```bash
cd ~/ignition-stack-builder

# Stop services
docker compose down

# Restore database
cat backups/backup_YYYYMMDD_HHMMSS.sql | docker compose exec -T auth-db psql -U stack_builder stack_builder_auth

# Restart services
docker compose up -d
```

### Manual Deployment

```bash
cd ~/ignition-stack-builder

# Create backup
mkdir -p backups
docker compose exec -T auth-db pg_dump -U stack_builder stack_builder_auth > backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql

# Pull latest code
git pull origin main

# Pull and restart services
docker compose pull
docker compose up -d --build

# Run migrations if needed
docker compose exec backend python migrations/001_create_initial_schema.py
```

### Rollback to Previous Version

```bash
cd ~/ignition-stack-builder

# View recent commits
git log --oneline -10

# Rollback to specific commit
git reset --hard COMMIT_SHA

# Restart services
docker compose up -d --build
```

---

## Part 5: Troubleshooting

### Deployment Failed

1. **Check GitHub Actions logs**: Go to Actions tab and view the failed job
2. **Check server logs**:
   ```bash
   ssh your_user@ignitionvps.gaskony.me
   cd ~/ignition-stack-builder
   docker compose logs -f
   ```

### Services Won't Start

```bash
# Check Docker status
docker compose ps

# View error logs
docker compose logs backend
docker compose logs frontend

# Restart services
docker compose restart

# Full rebuild
docker compose down
docker compose up -d --build
```

### Database Connection Issues

```bash
# Check database is running
docker compose ps auth-db

# Check database logs
docker compose logs auth-db

# Verify credentials in .env files
cat .env | grep AUTH_DB
cat backend/.env | grep AUTH_DB
```

### SSH Connection Issues from GitHub Actions

1. **Verify SSH key in GitHub Secrets**:
   - Make sure you copied the entire private key including BEGIN/END lines
   - No extra spaces or newlines

2. **Test SSH connection from local machine**:
   ```bash
   # Save GitHub Actions key to file locally
   cat > /tmp/test_key << 'EOF'
   [paste private key here]
   EOF
   chmod 600 /tmp/test_key

   # Test connection
   ssh -i /tmp/test_key your_user@ignitionvps.gaskony.me "echo 'Connection successful'"
   ```

3. **Check server's authorized_keys**:
   ```bash
   cat ~/.ssh/authorized_keys
   ```

### Port Already in Use

```bash
# Find what's using the port
sudo lsof -i :3500
sudo lsof -i :8000

# Stop conflicting service
sudo systemctl stop [service_name]

# Or change ports in .env file
nano .env
```

---

## Part 6: Security Best Practices

### 1. Keep Secrets Secure

- Never commit `.env` files to git
- Rotate secrets regularly (every 90 days)
- Use strong, random passwords (32+ characters)

### 2. Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 3. Regular Updates

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Update Docker images
cd ~/ignition-stack-builder
docker compose pull
docker compose up -d
```

### 4. Monitor Logs

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/ignition-stack-builder

# Add:
/home/your_user/ignition-stack-builder/backups/*.sql {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

### 5. Backup Strategy

- Database backups are created automatically before each deployment
- Backups older than 7 days are automatically deleted
- Consider setting up off-site backup storage (S3, Backblaze, etc.)

---

## Part 7: Advanced Configuration

### Using Custom Docker Registry

If you want to use a private Docker registry instead of Docker Hub:

1. Update `.github/workflows/deploy.yml`:
   ```yaml
   - name: Log in to Docker Registry
     uses: docker/login-action@v3
     with:
       registry: registry.your-domain.com
       username: ${{ secrets.REGISTRY_USERNAME }}
       password: ${{ secrets.REGISTRY_PASSWORD }}
   ```

2. Update image names in the workflow

### Adding Staging Environment

Create a staging server and add staging secrets to GitHub:
- `STAGING_HOST`
- `STAGING_USER`
- `STAGING_SSH_KEY`

Then modify the workflow to include staging deployment step.

### Notification Integration

Add notifications on deployment success/failure:

**Slack:**
```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment ${{ job.status }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

**Discord:**
```yaml
- name: Notify Discord
  if: always()
  run: |
    curl -H "Content-Type: application/json" \
         -d '{"content": "Deployment ${{ job.status }}"}' \
         ${{ secrets.DISCORD_WEBHOOK }}
```

---

## Quick Reference

### Useful Commands

```bash
# Check deployment status
cd ~/ignition-stack-builder && docker compose ps

# View logs
docker compose logs -f

# Restart services
docker compose restart

# Update to latest version
git pull && docker compose up -d --build

# Create manual backup
docker compose exec -T auth-db pg_dump -U stack_builder stack_builder_auth > backups/manual_$(date +%Y%m%d).sql

# View recent backups
ls -lh backups/

# Clean up old images
docker image prune -a -f

# Check disk space
df -h
```

### Important File Locations

- **Project directory**: `~/ignition-stack-builder`
- **Environment files**: `~/ignition-stack-builder/.env` and `~/ignition-stack-builder/backend/.env`
- **Backups**: `~/ignition-stack-builder/backups/`
- **SSL certificates**: `~/ignition-stack-builder/frontend/certs/`
- **Docker volumes**: `/var/lib/docker/volumes/`

---

## Support

For issues or questions:
1. Check GitHub Actions logs for deployment errors
2. Review server logs: `docker compose logs -f`
3. Open an issue on GitHub: https://github.com/nigelgwork/ignition-stack-builder/issues

---

**Deployment is now fully automated! 🚀**

Every push to `main` will automatically deploy to production at `https://ignitionvps.gaskony.me`
