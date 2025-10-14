# Port Configuration

The Ignition Stack Builder uses the following default ports, chosen to avoid common conflicts when deploying to multiple servers.

## Default Ports

| Service | Port | Previous Port | Reason for Change |
|---------|------|---------------|-------------------|
| Frontend (HTTPS) | 3443 | - | Self-signed SSL |
| Frontend (HTTP) | 3500 | - | Redirects to HTTPS |
| Backend API | 8000 | - | Standard FastAPI port |
| **PostgreSQL (auth-db)** | **15433** | 5433 | Avoid common conflicts |
| **Redis** | **16379** | 6379 | Avoid common conflicts |

## Why Higher Ports?

Ports **15433** and **16379** were chosen because:
- They're **less likely to conflict** with existing services
- PostgreSQL's default (5432) and common alternative (5433) are often in use
- Redis's default (6379) is commonly used
- Higher ports (15000+) are rarely used by system services
- Still below privileged port range (requires root)

## Configuring Ports

Ports are configured in the `.env` file in the project root:

```bash
# Authentication Database
AUTH_DB_PORT=15433

# Redis
REDIS_PORT=16379
```

## Changing Ports

If you need to use different ports:

1. **Stop the services:**
   ```bash
   docker compose down
   ```

2. **Edit the `.env` file:**
   ```bash
   nano .env
   ```

3. **Change the port values:**
   ```env
   AUTH_DB_PORT=25432  # Your custom port
   REDIS_PORT=26379    # Your custom port
   ```

4. **Restart the services:**
   ```bash
   docker compose up -d
   ```

## Port Conflicts

If you get a "port already in use" error:

1. **Find what's using the port:**
   ```bash
   sudo lsof -i :15433
   # or
   sudo netstat -tulpn | grep 15433
   ```

2. **Option A:** Stop the conflicting service
3. **Option B:** Change the port in `.env` as described above

## Access URLs

After deployment, access the Stack Builder at:

- **Frontend:** `https://YOUR_SERVER_IP:3443`
- **Backend API:** `http://YOUR_SERVER_IP:8000`

The PostgreSQL and Redis ports are for internal use only (not accessed directly from browser).

## Multiple Server Deployment

Each server can use the same ports (15433, 16379) since they're listening on different IPs. This makes deployment consistent across all servers.

## Firewall Configuration

Only the frontend and backend ports need to be accessible from outside:

```bash
# Allow HTTPS (frontend)
sudo ufw allow 3443/tcp

# Allow HTTP (frontend - optional, redirects to HTTPS)
sudo ufw allow 3500/tcp

# Allow backend API (if needed externally)
sudo ufw allow 8000/tcp

# PostgreSQL and Redis are internal only - DO NOT expose them
```

## Production Considerations

For production deployments on ports 80 and 443:

Edit `.env`:
```env
FRONTEND_PORT=80
FRONTEND_HTTPS_PORT=443
```

**Note:** Ports 80 and 443 may require running as root or using a reverse proxy.
