# CI/CD Setup Checklist

Quick checklist for setting up automated deployment to `ignitionvps.gaskony.me`.

## On Your VPS Server

### 1. Run Production Setup Script
```bash
ssh your_user@ignitionvps.gaskony.me

# Download and run setup script
curl -O https://raw.githubusercontent.com/nigelgwork/ignition-stack-builder/main/scripts/production-setup.sh
chmod +x production-setup.sh
./production-setup.sh
```

- [ ] Docker installed
- [ ] Repository cloned to `~/ignition-stack-builder`
- [ ] `.env` files created and passwords changed
- [ ] SSL certificates generated
- [ ] Services started successfully
- [ ] Database migrations completed

### 2. Generate SSH Key for GitHub Actions
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_deploy_key
cat ~/.ssh/github_actions_deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

- [ ] SSH key generated
- [ ] Public key added to authorized_keys
- [ ] Private key copied (for GitHub Secrets)

### 3. Get Server Details
```bash
echo "Host: $(hostname -I | awk '{print $1}')"
echo "User: $(whoami)"
cat ~/.ssh/github_actions_deploy_key
```

- [ ] Production host identified
- [ ] Production user identified
- [ ] Private SSH key saved

## On GitHub

### 4. Add Repository Secrets

Go to: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

- [ ] `PRODUCTION_HOST` = `ignitionvps.gaskony.me` (or your server IP)
- [ ] `PRODUCTION_USER` = your SSH username
- [ ] `PRODUCTION_SSH_KEY` = entire private key (including BEGIN/END lines)
- [ ] `DOCKERHUB_USERNAME` = your Docker Hub username
- [ ] `DOCKERHUB_TOKEN` = Docker Hub access token (create at https://hub.docker.com/settings/security)

Optional (for enhanced security):
- [ ] `JWT_SECRET_KEY` = random 32+ character string
- [ ] `SESSION_SECRET` = random 32+ character string

### 5. Configure Production Environment

Go to: **Settings** → **Environments** → **New environment**

- [ ] Environment name: `production`
- [ ] Environment URL: `https://ignitionvps.gaskony.me`
- [ ] (Optional) Add required reviewers for approval before deployment
- [ ] (Optional) Restrict to `main` branch only

### 6. Test the Pipeline

```bash
# In your local dev environment
cd /git/ignition-stack-builder

# Make a test change
echo "<!-- CI/CD Test -->" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin main
```

Then watch the deployment:
- [ ] Go to **Actions** tab in GitHub
- [ ] Watch workflow: CI Tests → Build Images → Deploy to Production
- [ ] Verify deployment at https://ignitionvps.gaskony.me

## Verification

### 7. Verify Deployment

Check that everything is working:

```bash
# Check services on server
ssh your_user@ignitionvps.gaskony.me
cd ~/ignition-stack-builder
docker compose ps
```

Expected output:
```
NAME                     STATUS
stack-builder-auth-db    Up (healthy)
stack-builder-backend    Up
stack-builder-frontend   Up
stack-builder-redis      Up (healthy)
```

Check the website:
- [ ] Frontend accessible at https://ignitionvps.gaskony.me
- [ ] Can create user account
- [ ] Can login successfully
- [ ] Can select services and generate stack

### 8. Check GitHub Actions Status

- [ ] CI workflow passing (green checkmark)
- [ ] Deploy workflow completed successfully
- [ ] No errors in Action logs

## Troubleshooting

### SSH Connection Fails
```bash
# Test SSH key locally
ssh -i ~/.ssh/github_actions_deploy_key your_user@ignitionvps.gaskony.me "echo 'Success'"
```

If this fails:
- [ ] Check public key is in `~/.ssh/authorized_keys` on server
- [ ] Verify private key in GitHub Secrets has no extra spaces/newlines
- [ ] Check server firewall allows SSH (port 22)

### Deployment Fails
- [ ] Check GitHub Actions logs for specific error
- [ ] Verify all secrets are set correctly in GitHub
- [ ] Check server has enough disk space: `df -h`
- [ ] Verify Docker is running: `docker ps`

### Services Won't Start
```bash
ssh your_user@ignitionvps.gaskony.me
cd ~/ignition-stack-builder

# Check logs
docker compose logs backend
docker compose logs frontend

# Restart services
docker compose restart

# Full rebuild
docker compose down
docker compose up -d --build
```

## Success! 🎉

Your CI/CD pipeline is now active. Every push to `main` will automatically deploy to production!

**What happens on every push:**
1. ✅ Tests run automatically
2. ✅ Docker images built and pushed
3. ✅ Database backup created
4. ✅ Code deployed to production
5. ✅ Health checks verify deployment
6. ✅ Old images/backups cleaned up

**Next steps:**
- Set up monitoring/alerting
- Configure Let's Encrypt for SSL
- Set up staging environment (optional)
- Add notification webhooks (Slack/Discord)

---

For detailed documentation, see: [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)
