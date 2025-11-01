#!/bin/bash

# Quick update script for production
# Use this for fast deployments after code changes

echo "🔄 Quick Update (no rebuild)"

cd /opt/flowmind

# Pull latest code
echo "📥 Pulling latest code..."
git pull

# Rebuild frontend
echo "📦 Rebuilding frontend..."
cd frontend
REACT_APP_BACKEND_URL="" npm run build
cd ..

# Restart containers
echo "🔄 Restarting containers..."
docker-compose -f deploy/docker-compose.production.yml restart backend

# Reload Caddy
echo "🔄 Reloading Caddy..."
sudo systemctl reload caddy

echo "✅ Update complete!"
