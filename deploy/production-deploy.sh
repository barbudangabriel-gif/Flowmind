#!/bin/bash
set -e

# FlowMind Production Deployment Script
# Run this from /opt/flowmind directory

echo "🚀 FlowMind Production Deployment"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "deploy/docker-compose.production.yml" ]; then
    echo "❌ Error: Must run from FlowMind root directory"
    echo "   cd /opt/flowmind && ./deploy/production-deploy.sh"
    exit 1
fi

# Check if .env.production exists
if [ ! -f "deploy/.env.production" ]; then
    echo "❌ Error: deploy/.env.production not found"
    echo "   Copy deploy/.env.production.example and fill in your values"
    exit 1
fi

# Load environment variables
set -a
source deploy/.env.production
set +a

echo "📦 Building frontend..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "  Installing npm dependencies..."
    npm install
fi

# Build production frontend
echo "  Building React app..."
REACT_APP_BACKEND_URL="" npm run build

# Verify build
if [ ! -d "build" ]; then
    echo "❌ Frontend build failed"
    exit 1
fi

echo "✅ Frontend build complete"

cd ..

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f deploy/docker-compose.production.yml down

# Build and start containers
echo "🐳 Building and starting Docker containers..."
docker-compose -f deploy/docker-compose.production.yml build --no-cache
docker-compose -f deploy/docker-compose.production.yml up -d

# Wait for backend to be healthy
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        docker-compose -f deploy/docker-compose.production.yml logs backend
        exit 1
    fi
    sleep 2
done

# Setup Caddy
echo "🔒 Setting up Caddy reverse proxy..."
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile

# Validate Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile

# Reload Caddy
sudo systemctl reload caddy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
docker-compose -f deploy/docker-compose.production.yml ps
echo ""
echo "📝 Next steps:"
echo "  - Check logs: docker-compose -f deploy/docker-compose.production.yml logs -f"
echo "  - Test backend: curl http://localhost:8000/health"
echo "  - Test frontend: curl https://${DOMAIN}"
echo "  - Monitor Caddy: sudo journalctl -u caddy -f"
echo ""
echo "🌐 Your app should be live at: https://${DOMAIN}"
echo ""
