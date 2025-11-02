#!/bin/bash
# Fix Production Build - Rebuild with Correct Backend URL
# Date: November 1, 2025
# Issue: Built with REACT_APP_BACKEND_URL="" (empty) instead of actual backend URL

echo "=== FlowMind Production Build Fix ==="
echo "This will rebuild the frontend with the correct backend URL"
echo ""

# SSH to production and rebuild
cat << 'REMOTE_SCRIPT' > /tmp/rebuild_frontend.sh
#!/bin/bash
set -e

echo "Step 1: Navigate to frontend directory"
cd /opt/flowmind/frontend

echo "Step 2: Create production .env file with backend URL"
cat > .env.production << 'EOF'
# Production Frontend Configuration
# Backend API endpoint (Docker internal network)
REACT_APP_BACKEND_URL=http://localhost:8080
EOF

echo "Step 3: Rebuild frontend with production environment"
npm run build

echo "Step 4: Verify build output"
ls -lh build/

echo "Step 5: Reload Caddy to serve new build"
sudo systemctl reload caddy

echo "Step 6: Verify Caddy status"
sudo systemctl status caddy --no-pager -l | head -10

echo ""
echo "✅ Frontend rebuilt successfully!"
echo "✅ Backend URL hardcoded: http://localhost:8080"
echo ""
echo "Test the site now:"
echo "  1. Open https://flowmindanalytics.ai/builder"
echo "  2. Hard refresh: Ctrl+Shift+R"
echo "  3. Check browser console - error should be gone!"
REMOTE_SCRIPT

chmod +x /tmp/rebuild_frontend.sh

echo "To fix production, SSH to server and run:"
echo ""
echo "ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64 'bash -s' < /tmp/rebuild_frontend.sh"
echo ""
echo "OR manually:"
echo "1. SSH: ssh -i ~/.ssh/flowmind_ed25519 root@91.107.206.64"
echo "2. cd /opt/flowmind/frontend"
echo "3. echo 'REACT_APP_BACKEND_URL=http://localhost:8080' > .env.production"
echo "4. npm run build"
echo "5. systemctl reload caddy"
