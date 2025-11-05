#!/bin/bash

#####################################################
# FlowMind Quick Update Script
# 
# Rulează pe server când faci modificări în cod
# Rapid și simplu - doar update + restart
#
# Usage: bash quick_update.sh
#####################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="/opt/flowmind"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  FlowMind Quick Update${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 1. Pull changes
echo -e "${BLUE}[1/4]${NC} Pull ultimele modificări..."
cd $PROJECT_DIR
git pull origin main
echo -e "${GREEN}✓${NC} Cod actualizat"
echo ""

# 2. Rebuild frontend
echo -e "${BLUE}[2/4]${NC} Rebuild frontend..."
cd frontend
npm install --legacy-peer-deps 2>/dev/null || npm install
npm run build
echo -e "${GREEN}✓${NC} Frontend rebuild complet"
echo ""

# 3. Restart backend
echo -e "${BLUE}[3/4]${NC} Restart backend..."
cd $PROJECT_DIR
docker-compose restart backend
sleep 3
echo -e "${GREEN}✓${NC} Backend restartat"
echo ""

# 4. Reload Caddy
echo -e "${BLUE}[4/4]${NC} Reload Caddy..."
systemctl reload caddy
echo -e "${GREEN}✓${NC} Caddy reloaded"
echo ""

# Verify
echo -e "${BLUE}Verificare...${NC}"
if curl -s https://flowmindanalytics.ai/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Site funcționează!${NC}"
else
    echo -e "${YELLOW}⚠️  Site nu răspunde. Verifică logs:${NC}"
    echo -e "docker-compose logs backend --tail=20"
fi

echo ""
echo -e "${GREEN}Update complet! 🚀${NC}"
echo ""
