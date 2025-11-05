#!/bin/bash

#####################################################
# Pre-Deployment Checker
# 
# Verifică că totul e pregătit pentru deployment
#####################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  FlowMind Deployment Pre-Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

DOMAIN="flowmindanalytics.ai"
ALL_CHECKS_PASSED=true

# Check 1: DNS Resolution
echo -e "${BLUE}[1/5]${NC} Verificare DNS..."
RESOLVED_IP=$(dig +short $DOMAIN 2>/dev/null | head -n1)

if [ -z "$RESOLVED_IP" ]; then
    echo -e "${RED}❌ DNS nu rezolvă pentru $DOMAIN${NC}"
    echo -e "${YELLOW}   Configurează A record în Cloudflare!${NC}"
    ALL_CHECKS_PASSED=false
else
    echo -e "${GREEN}✓${NC} DNS OK: $DOMAIN → $RESOLVED_IP"
fi
echo ""

# Check 2: Git & Required Files
echo -e "${BLUE}[2/5]${NC} Verificare fișiere deployment..."

if [ ! -f "deploy_with_ssl.sh" ]; then
    echo -e "${RED}❌ deploy_with_ssl.sh nu există!${NC}"
    ALL_CHECKS_PASSED=false
else
    echo -e "${GREEN}✓${NC} deploy_with_ssl.sh există"
fi

if [ ! -f "quick_update.sh" ]; then
    echo -e "${RED}❌ quick_update.sh nu există!${NC}"
    ALL_CHECKS_PASSED=false
else
    echo -e "${GREEN}✓${NC} quick_update.sh există"
fi

if [ ! -f "Caddyfile.with-auth" ]; then
    echo -e "${RED}❌ Caddyfile.with-auth nu există!${NC}"
    ALL_CHECKS_PASSED=false
else
    echo -e "${GREEN}✓${NC} Caddyfile.with-auth există"
fi
echo ""

# Check 3: Frontend Build Requirements
echo -e "${BLUE}[3/5]${NC} Verificare frontend..."

if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules nu există (va fi instalat pe server)${NC}"
else
    echo -e "${GREEN}✓${NC} node_modules există"
fi

if [ ! -f "frontend/package.json" ]; then
    echo -e "${RED}❌ frontend/package.json nu există!${NC}"
    ALL_CHECKS_PASSED=false
else
    echo -e "${GREEN}✓${NC} package.json există"
fi
echo ""

# Check 4: Backend Configuration
echo -e "${BLUE}[4/5]${NC} Verificare backend..."

if [ ! -f "backend/.env.example" ]; then
    echo -e "${RED}❌ backend/.env.example nu există!${NC}"
    ALL_CHECKS_PASSED=false
else
    echo -e "${GREEN}✓${NC} .env.example există"
fi

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml nu există!${NC}"
    ALL_CHECKS_PASSED=false
else
    echo -e "${GREEN}✓${NC} docker-compose.yml există"
fi
echo ""

# Check 5: Git Status
echo -e "${BLUE}[5/5]${NC} Verificare Git status..."

if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Ai modificări uncommitted!${NC}"
    echo -e "${YELLOW}   Consideră să faci commit înainte de deployment.${NC}"
else
    echo -e "${GREEN}✓${NC} Git clean - toate modificările sunt committed"
fi
echo ""

# Final Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ "$ALL_CHECKS_PASSED" = true ]; then
    echo -e "${GREEN}✅ Gata pentru deployment!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. SSH to server: ${YELLOW}ssh root@$DOMAIN${NC}"
    echo -e "  2. Clone/pull repo: ${YELLOW}cd /opt/flowmind && git pull${NC}"
    echo -e "  3. Run deployment: ${YELLOW}bash deploy_with_ssl.sh${NC}"
    echo ""
    echo -e "${BLUE}SAU direct:${NC}"
    echo -e "  ${YELLOW}ssh root@$DOMAIN 'cd /opt/flowmind && git pull && bash deploy_with_ssl.sh'${NC}"
else
    echo -e "${RED}❌ Unele verificări au eșuat!${NC}"
    echo -e "Rezolvă problemele de mai sus înainte de deployment."
fi
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
