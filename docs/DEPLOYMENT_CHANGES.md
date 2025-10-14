# Deployment System Changes - Simplified

## What Changed

The deployment system has been **greatly simplified** from automatic SSH-based deployment to a simple manual process.

### Before (Complex)
- GitHub Actions would automatically SSH into production servers
- Required SSH keys, server credentials, and multiple secrets
- Deployed automatically on every push to `main`
- Complex rollback and cleanup processes
- Hard to add additional servers

### After (Simple)
- GitHub Actions only builds and pushes Docker images
- You manually deploy on any server with a simple script
- No SSH keys or server secrets needed in GitHub
- Easy to deploy to multiple servers
- Full control over when deployments happen

## Files Changed

### Modified
- `.github/workflows/deploy.yml` - Simplified to only build and push images

### Created
- `scripts/deploy.sh` - Simple deployment script for any server
- `docs/SIMPLE_DEPLOYMENT.md` - Complete deployment guide
- `docs/DEPLOYMENT_CHANGES.md` - This file

### No Longer Needed
These GitHub secrets are no longer required:
- ❌ `PRODUCTION_HOST`
- ❌ `PRODUCTION_USER`
- ❌ `PRODUCTION_SSH_KEY`
- ❌ `PRODUCTION2_HOST`
- ❌ `PRODUCTION2_USER`
- ❌ `PRODUCTION2_SSH_KEY`
- ❌ `PRODUCTION2_URL`

### Still Required
These GitHub secrets are still needed (for Docker Hub):
- ✅ `DOCKERHUB_USERNAME`
- ✅ `DOCKERHUB_TOKEN`

## How to Deploy Now

### On GitHub (Automatic)
When you push to `main`:
1. CI tests run
2. Docker images are built
3. Images are pushed to Docker Hub

**Nothing else happens automatically.**

### On Any Server (Manual)
```bash
ssh user@your-server.com
cd /git/ignition-stack-builder
./scripts/deploy.sh
```

That's it!

## Benefits

1. **Simpler** - No complex SSH setup, no server secrets in GitHub
2. **More Control** - You decide when to deploy
3. **Multiple Servers** - Easy to deploy to any number of servers
4. **Safer** - Can test on one server before deploying to others
5. **Transparent** - You see exactly what's happening during deployment
6. **Flexible** - Each server can be on different versions if needed

## Migration Steps

If you were using the old automatic deployment:

1. **Remove old secrets from GitHub** (optional, they won't be used):
   - Go to Settings → Secrets and variables → Actions
   - Delete the PRODUCTION* secrets (keep DOCKERHUB ones)

2. **Remove old environment** (optional):
   - Go to Settings → Environments
   - Delete `production` and `production2` environments

3. **That's it!** The new system is already in place.

## Example: Deploying to Multiple Servers

```bash
# Server 1
ssh user@server1.example.com
cd /git/ignition-stack-builder
./scripts/deploy.sh
exit

# Server 2
ssh user@server2.example.com
cd /git/ignition-stack-builder
./scripts/deploy.sh
exit

# Server 3
ssh user@server3.example.com
cd /git/ignition-stack-builder
./scripts/deploy.sh
exit
```

## Rollback Process

If something goes wrong:

```bash
cd /git/ignition-stack-builder

# View recent commits
git log --oneline -10

# Rollback to previous version
git reset --hard abc123

# Redeploy
./scripts/deploy.sh
```

## What the Deploy Script Does

The `scripts/deploy.sh` script:
1. ✅ Creates database backup
2. ✅ Pulls latest code from Git
3. ✅ Pulls latest Docker images
4. ✅ Stops old containers
5. ✅ Starts new containers
6. ✅ Runs database migrations
7. ✅ Cleans up old images

All with colorful output and progress indicators!

## Questions?

See the full guide: `docs/SIMPLE_DEPLOYMENT.md`
