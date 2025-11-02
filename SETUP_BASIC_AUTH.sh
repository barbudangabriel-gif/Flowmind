#!/bin/bash
# FlowMind Basic Auth Setup - Caddy
# Date: November 1, 2025
# Purpose: Protect site with username/password

echo "=== FlowMind Basic Auth Setup ==="
echo ""
echo "Step 1: Generate hashed password"
echo "Enter your desired password when prompted:"
caddy hash-password

echo ""
echo "Copy the hash output above (starts with \$2a\$14\$...)"
echo ""
echo "Step 2: Edit Caddyfile"
echo "Add basicauth block after 'flowmindanalytics.ai {'"
echo ""
cat << 'EXAMPLE'
flowmindanalytics.ai {
    # Basic Authentication
    basicauth {
        gabriel PASTE_YOUR_HASH_HERE
    }
    
    # Reverse proxy for backend API
    reverse_proxy /api/* localhost:8000
    
    # Frontend static files
    root * /opt/flowmind/frontend/build
    try_files {path} /index.html
    file_server
    
    # Logging
    log {
        output file /var/log/caddy/flowmind.log
    }
}
EXAMPLE

echo ""
echo "Step 3: Apply changes"
echo "Run: nano /etc/caddy/Caddyfile"
echo "Paste the basicauth block, save (Ctrl+O, Enter, Ctrl+X)"
echo ""
echo "Step 4: Reload Caddy"
echo "Run: systemctl reload caddy"
echo ""
echo "Step 5: Test"
echo "Visit: https://flowmindanalytics.ai"
echo "Should prompt for username (gabriel) and password"
echo ""
echo "=== Quick Commands ==="
echo "1. caddy hash-password"
echo "2. nano /etc/caddy/Caddyfile  # Add basicauth block"
echo "3. systemctl reload caddy"
echo "4. Test site"
