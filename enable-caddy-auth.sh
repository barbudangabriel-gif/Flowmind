#!/bin/bash
# Script automat pentru activare Caddy auth

echo "=== Activare Caddy Auth ==="

# Backup
cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup
echo "✓ Backup creat"

# Copiază config cu auth
cp /opt/flowmind/Caddyfile.with-auth /etc/caddy/Caddyfile
echo "✓ Config cu auth copiat"

# Validare
caddy validate --config /etc/caddy/Caddyfile
if [ $? -eq 0 ]; then
    echo "✓ Config valid"
    
    # Reload
    systemctl reload caddy
    echo "✓ Caddy reloaded"
    
    echo ""
    echo "=== GATA! ==="
    echo "User: gabriel"
    echo "Pass: (parola din Caddyfile.with-auth)"
    echo ""
    echo "Testează: https://flowmindanalytics.ai"
else
    echo "✗ Config invalid, restore backup"
    cp /etc/caddy/Caddyfile.backup /etc/caddy/Caddyfile
fi
