#!/bin/bash

#####################################################
# FlowMind Server Deployment Diagnostic
# 
# Verifică statusul deployment-ului pe server
# Rulează: bash check_server_deployment.sh
#####################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  FlowMind Deployment Diagnostic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

DOMAIN="flowmindanalytics.ai"

#####################################################
# 1. Check if backend is accessible on server
#####################################################

echo -e "${BLUE}[1/6]${NC} Verificare backend pe server (port 8000)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null | grep -q "200"; then
    echo -e "${GREEN}✓${NC} Backend local răspunde (port 8000)"
else
    echo -e "${RED}✗${NC} Backend NU răspunde pe port 8000"
    echo -e "${YELLOW}  Verifică: docker-compose ps${NC}"
    echo -e "${YELLOW}  Logs: docker-compose logs backend --tail=50${NC}"
fi
echo ""

#####################################################
# 2. Check Docker containers
#####################################################

echo -e "${BLUE}[2/6]${NC} Verificare containere Docker..."
if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Containere Docker active"
    docker-compose ps | tail -n +2
else
    echo -e "${RED}✗${NC} Containere Docker nu rulează"
    echo -e "${YELLOW}  Rulează: cd /opt/flowmind && docker-compose up -d${NC}"
fi
echo ""

#####################################################
# 3. Check Caddy status
#####################################################

echo -e "${BLUE}[3/6]${NC} Verificare Caddy..."
if systemctl is-active --quiet caddy 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Caddy rulează"
    CADDY_VERSION=$(caddy version 2>/dev/null | head -n1 || echo "unknown")
    echo -e "  Version: $CADDY_VERSION"
else
    echo -e "${RED}✗${NC} Caddy NU rulează"
    echo -e "${YELLOW}  Pornește: systemctl start caddy${NC}"
fi
echo ""

#####################################################
# 4. Check HTTPS endpoint
#####################################################

echo -e "${BLUE}[4/6]${NC} Verificare HTTPS endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} HTTPS funcționează (https://$DOMAIN/health)"
elif [ "$HTTP_CODE" = "401" ]; then
    echo -e "${YELLOW}⚠${NC}  HTTPS funcționează dar cere autentificare (401)"
    echo -e "  Normal dacă ai basic auth activat"
else
    echo -e "${RED}✗${NC} HTTPS NU funcționează (HTTP $HTTP_CODE)"
    echo -e "${YELLOW}  Verifică Caddy logs: journalctl -u caddy -n 50${NC}"
fi
echo ""

#####################################################
# 5. Check SSL certificate
#####################################################

echo -e "${BLUE}[5/6]${NC} Verificare certificat SSL..."
if echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | grep -q "Verify return code: 0"; then
    echo -e "${GREEN}✓${NC} Certificat SSL valid"
    EXPIRY=$(echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -dates | grep "notAfter" | cut -d= -f2)
    echo -e "  Expiră: $EXPIRY"
else
    echo -e "${YELLOW}⚠${NC}  Certificat SSL problematic"
    echo -e "${YELLOW}  Verifică: echo | openssl s_client -connect $DOMAIN:443${NC}"
fi
echo ""

#####################################################
# 6. Check frontend build
#####################################################

echo -e "${BLUE}[6/6]${NC} Verificare frontend build..."
if [ -d "/opt/flowmind/frontend/build" ]; then
    BUILD_SIZE=$(du -sh /opt/flowmind/frontend/build 2>/dev/null | cut -f1)
    FILE_COUNT=$(find /opt/flowmind/frontend/build -type f 2>/dev/null | wc -l)
    echo -e "${GREEN}✓${NC} Frontend build există"
    echo -e "  Size: $BUILD_SIZE"
    echo -e "  Files: $FILE_COUNT"
    
    # Check if index.html exists
    if [ -f "/opt/flowmind/frontend/build/index.html" ]; then
        echo -e "${GREEN}✓${NC} index.html găsit"
    else
        echo -e "${RED}✗${NC} index.html lipsește!"
        echo -e "${YELLOW}  Rebuild: cd /opt/flowmind/frontend && npm run build${NC}"
    fi
else
    echo -e "${RED}✗${NC} Frontend build NU există"
    echo -e "${YELLOW}  Rulează: cd /opt/flowmind/frontend && npm run build${NC}"
fi
echo ""

#####################################################
# Summary & Recommendations
#####################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Recomandări${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Comenzi utile:${NC}"
echo -e "  • Verifică backend: ${GREEN}curl http://localhost:8000/health${NC}"
echo -e "  • Logs backend: ${GREEN}docker-compose logs backend --tail=50${NC}"
echo -e "  • Logs Caddy: ${GREEN}journalctl -u caddy -n 50${NC}"
echo -e "  • Restart backend: ${GREEN}docker-compose restart backend${NC}"
echo -e "  • Restart Caddy: ${GREEN}systemctl restart caddy${NC}"
echo -e "  • Rebuild frontend: ${GREEN}cd frontend && npm run build${NC}"
echo ""

echo -e "${YELLOW}Dacă backend nu pornește:${NC}"
echo -e "  1. ${GREEN}cd /opt/flowmind${NC}"
echo -e "  2. ${GREEN}docker-compose down${NC}"
echo -e "  3. ${GREEN}docker-compose up -d${NC}"
echo -e "  4. ${GREEN}docker-compose logs backend -f${NC}"
echo ""

echo -e "${YELLOW}Dacă Caddy nu proxy-ază corect:${NC}"
echo -e "  1. Verifică Caddyfile: ${GREEN}cat /etc/caddy/Caddyfile${NC}"
echo -e "  2. Test config: ${GREEN}caddy validate --config /etc/caddy/Caddyfile${NC}"
echo -e "  3. Reload: ${GREEN}systemctl reload caddy${NC}"
echo ""
