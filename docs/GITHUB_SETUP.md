# GitHub Actions Setup Guide

This guide explains how to configure GitHub Actions for the Ignition Stack Builder project, including all required secrets and environment configurations.

## Table of Contents

- [Overview](#overview)
- [Required GitHub Secrets](#required-github-secrets)
- [Setting Up Secrets](#setting-up-secrets)
- [Environment Configuration](#environment-configuration)
- [CI/CD Workflows](#cicd-workflows)
- [Manual Approval Setup](#manual-approval-setup)
- [Troubleshooting](#troubleshooting)

## Overview

The project uses two main GitHub Actions workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`) - Runs automatically on push and pull requests
2. **Deployment Workflow** (`.github/workflows/deploy.yml`) - Manual deployment with approval gates

## Required GitHub Secrets

### Authentication Secrets

These secrets are used for JWT token generation and session management in the application.

| Secret Name | Description | How to Generate | Required For |
|-------------|-------------|-----------------|--------------|
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `openssl rand -base64 32` | CI, Deployment |
| `SESSION_SECRET` | Secret key for session management | `openssl rand -base64 32` | CI, Deployment |

### Docker Hub Secrets

Required for pushing Docker images to Docker Hub.

| Secret Name | Description | How to Obtain | Required For |
|-------------|-------------|---------------|--------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | Docker Hub account | Deployment |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Docker Hub → Account Settings → Security → New Access Token | Deployment |

### Staging Environment Secrets

Required for deploying to staging environment.

| Secret Name | Description | Example | Required For |
|-------------|-------------|---------|--------------|
| `STAGING_SSH_KEY` | Private SSH key for staging server | Contents of `~/.ssh/id_rsa` | Deployment (Staging) |
| `STAGING_HOST` | Staging server hostname or IP | `staging.example.com` or `192.168.1.100` | Deployment (Staging) |
| `STAGING_USER` | SSH username for staging | `ubuntu` or `deploy` | Deployment (Staging) |

### Production Environment Secrets

Required for deploying to production environment.

| Secret Name | Description | Example | Required For |
|-------------|-------------|---------|--------------|
| `PRODUCTION_SSH_KEY` | Private SSH key for production server | Contents of `~/.ssh/id_rsa` | Deployment (Production) |
| `PRODUCTION_HOST` | Production server hostname or IP | `ignition-stack-builder.com` | Deployment (Production) |
| `PRODUCTION_USER` | SSH username for production | `ubuntu` or `deploy` | Deployment (Production) |

## Setting Up Secrets

### Step 1: Generate Authentication Secrets

Generate secure random secrets for JWT and sessions:

```bash
# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)
echo "JWT_SECRET_KEY: $JWT_SECRET"

# Generate session secret
SESSION_SECRET=$(openssl rand -base64 32)
echo "SESSION_SECRET: $SESSION_SECRET"
```

### Step 2: Create Docker Hub Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to **Account Settings** → **Security**
3. Click **New Access Token**
4. Name it `github-actions-ignition-stack-builder`
5. Select **Read, Write, Delete** permissions
6. Click **Generate**
7. Copy the token immediately (you won't be able to see it again)

### Step 3: Generate SSH Keys for Deployment

If you don't already have SSH keys for your servers:

```bash
# Generate SSH key for staging
ssh-keygen -t ed25519 -C "github-actions-staging" -f ~/.ssh/github_staging_ed25519

# Generate SSH key for production
ssh-keygen -t ed25519 -C "github-actions-production" -f ~/.ssh/github_production_ed25519
```

Copy the public keys to your servers:

```bash
# Copy to staging
ssh-copy-id -i ~/.ssh/github_staging_ed25519.pub user@staging-server

# Copy to production
ssh-copy-id -i ~/.ssh/github_production_ed25519.pub user@production-server
```

### Step 4: Add Secrets to GitHub

1. Navigate to your GitHub repository
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its corresponding value

#### Adding Authentication Secrets

- **Name**: `JWT_SECRET_KEY`
- **Value**: Output from JWT_SECRET generation
- Click **Add secret**

Repeat for `SESSION_SECRET`.

#### Adding Docker Hub Secrets

- **Name**: `DOCKERHUB_USERNAME`
- **Value**: Your Docker Hub username
- Click **Add secret**

- **Name**: `DOCKERHUB_TOKEN`
- **Value**: Docker Hub access token from Step 2
- Click **Add secret**

#### Adding Staging Secrets

- **Name**: `STAGING_SSH_KEY`
- **Value**: Contents of `~/.ssh/github_staging_ed25519` (private key)
  ```bash
  cat ~/.ssh/github_staging_ed25519
  ```
- Click **Add secret**

- **Name**: `STAGING_HOST`
- **Value**: `staging.example.com` or IP address
- Click **Add secret**

- **Name**: `STAGING_USER`
- **Value**: SSH username (e.g., `ubuntu`)
- Click **Add secret**

#### Adding Production Secrets

Repeat the same process for production secrets with production values.

## Environment Configuration

### Setting Up GitHub Environments

GitHub Environments provide deployment protection rules and approval gates.

#### 1. Create Staging Environment

1. Go to **Settings** → **Environments**
2. Click **New environment**
3. Name it **`staging`**
4. Configure:
   - ✅ **Required reviewers**: (Optional) Add reviewers
   - ✅ **Wait timer**: 0 minutes
   - ✅ **Deployment branches**: Selected branches (e.g., `main`, `develop`)

#### 2. Create Production Approval Environment

1. Create a new environment named **`production-approval`**
2. Configure:
   - ✅ **Required reviewers**: Add team members who can approve production deployments
   - ✅ **Wait timer**: 0 minutes
   - ✅ **Deployment branches**: Only `main`

#### 3. Create Production Environment

1. Create a new environment named **`production`**
2. Configure:
   - ✅ **Required reviewers**: (Optional) Additional reviewers
   - ✅ **Wait timer**: (Optional) 5-10 minutes
   - ✅ **Deployment branches**: Only `main`
   - **Environment URL**: `https://ignition-stack-builder.example.com`

## CI/CD Workflows

### CI Workflow (Automatic)

The CI workflow runs automatically on:
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`

**What it does:**
1. ✅ Runs backend API tests (auth + MFA)
2. ✅ Performs code quality checks (flake8, black, isort)
3. ✅ Runs security scans (bandit, safety, pip-audit)
4. ✅ Validates Docker builds
5. ✅ Checks for secrets in code (TruffleHog)
6. ✅ Validates configuration files

**CI workflow will fail if:**
- Any test fails
- Security vulnerabilities are found (moderate or higher)
- Code quality issues are detected
- Docker builds fail
- Secrets are found in code

### Deployment Workflow (Manual)

The deployment workflow must be triggered manually:

1. Go to **Actions** tab
2. Select **Deploy to Production** workflow
3. Click **Run workflow**
4. Select environment:
   - **staging**: Deploys immediately to staging
   - **production**: Requires manual approval before deploying

**Deployment Process:**

#### Staging Deployment
```
1. Build Docker images
2. Push to Docker Hub
3. SSH to staging server
4. Pull new images
5. Run docker-compose up
6. Run migrations
7. Health checks
```

#### Production Deployment
```
1. Build Docker images
2. Push to Docker Hub
3. ⏳ WAIT FOR MANUAL APPROVAL
4. Create database backup
5. SSH to production server
6. Pull new images
7. Run docker-compose up
8. Run migrations
9. Health checks
10. Smoke tests
11. Rollback on failure
```

## Manual Approval Setup

### Configuring Production Approvers

To require approval for production deployments:

1. Go to **Settings** → **Environments** → **production-approval**
2. Under **Deployment protection rules**:
   - Enable **Required reviewers**
   - Add team members who should approve:
     - Project lead
     - DevOps engineer
     - Technical lead
3. Save changes

### Approval Process

When someone triggers a production deployment:

1. GitHub sends notification to approvers
2. Approvers see pending deployment in **Actions** tab
3. Approver clicks **Review deployments**
4. Approver can:
   - ✅ **Approve** - Deployment continues
   - ❌ **Reject** - Deployment is canceled
5. Deployment proceeds or stops based on decision

## Verifying Setup

### Test CI Workflow

1. Create a test branch:
   ```bash
   git checkout -b test/ci-setup
   ```

2. Make a small change:
   ```bash
   echo "# Test CI" >> README.md
   git add README.md
   git commit -m "Test CI workflow"
   git push origin test/ci-setup
   ```

3. Create a pull request
4. Check **Actions** tab for workflow run
5. All checks should pass ✅

### Test Deployment Workflow

1. Go to **Actions** → **Deploy to Production**
2. Click **Run workflow**
3. Select **staging**
4. Click **Run workflow**
5. Monitor deployment progress
6. Check staging environment

## Troubleshooting

### Common Issues

#### 1. "Secret not found" errors

**Problem**: Workflow fails with "Secret JWT_SECRET_KEY not found"

**Solution**:
- Verify secret name matches exactly (case-sensitive)
- Check secret is added to repository (not organization)
- Ensure workflow has access to secrets

#### 2. SSH connection failures

**Problem**: "Permission denied (publickey)" during deployment

**Solution**:
```bash
# Verify SSH key is correct
ssh -i ~/.ssh/github_staging_ed25519 user@staging-host

# Check authorized_keys on server
cat ~/.ssh/authorized_keys

# Ensure private key is added as GitHub secret
cat ~/.ssh/github_staging_ed25519 | pbcopy
```

#### 3. Docker Hub authentication failures

**Problem**: "unauthorized: incorrect username or password"

**Solution**:
- Verify `DOCKERHUB_USERNAME` is correct
- Regenerate Docker Hub access token
- Ensure token has **Read, Write** permissions
- Update `DOCKERHUB_TOKEN` secret

#### 4. Tests fail in CI but pass locally

**Problem**: Tests pass on local machine but fail in GitHub Actions

**Solution**:
- Check database connection (PostgreSQL service might not be ready)
- Increase wait time before running tests
- Check environment variables are set correctly
- Review CI logs for specific error messages

#### 5. Manual approval not working

**Problem**: Production deployment doesn't wait for approval

**Solution**:
- Ensure `production-approval` environment exists
- Verify **Required reviewers** is enabled
- Check approvers are added to environment
- Ensure workflow references correct environment name

### Getting Help

If you encounter issues:

1. Check workflow logs in **Actions** tab
2. Review error messages carefully
3. Verify all secrets are set correctly
4. Test SSH connections manually
5. Consult GitHub Actions documentation
6. Open an issue in the repository

## Security Best Practices

### Rotating Secrets

Rotate sensitive secrets regularly:

```bash
# Generate new secrets
new_jwt_secret=$(openssl rand -base64 32)
new_session_secret=$(openssl rand -base64 32)

# Update in GitHub
# Settings → Secrets → JWT_SECRET_KEY → Update

# Update on servers
ssh user@server "cd /opt/ignition-stack-builder && sed -i 's/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$new_jwt_secret/' backend/.env"

# Restart services
ssh user@server "cd /opt/ignition-stack-builder && docker-compose restart backend"
```

### Monitoring

- Enable GitHub Advanced Security for additional scanning
- Review **Security** tab regularly for alerts
- Monitor deployment logs for suspicious activity
- Set up alerts for failed deployments

### Access Control

- Limit who can:
  - Approve production deployments
  - Access GitHub secrets
  - Trigger manual workflows
  - Push to protected branches
- Use branch protection rules
- Require pull request reviews
- Enable two-factor authentication

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments)
- [Docker Hub Access Tokens](https://docs.docker.com/docker-hub/access-tokens/)
- [SSH Key Management](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

---

**Last Updated**: 2025-10-13
**Maintained By**: DevOps Team
