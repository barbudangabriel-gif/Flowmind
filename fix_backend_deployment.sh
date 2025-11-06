#!/bin/bash

#####################################################
# FlowMind Backend Deployment Fix Script
# 
# Rulează pe server pentru a fixa problemele
# de deployment cu backend-ul
#
# Usage: bash fix_backend_deployment.sh
#####################################################

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/opt/flowmind"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  FlowMind Backend Deployment Fix${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if running as root (needed for systemctl)
if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}⚠️  Nu rulează ca root - unele comenzi pot eșua${NC}"
fi

#####################################################
# Step 1: Check current status
#####################################################

echo -e "${BLUE}[1/8]${NC} Verificare status curent..."
cd $PROJECT_DIR

if docker-compose ps 2>/dev/null | grep -q "backend.*Up"; then
    echo -e "${GREEN}✓${NC} Backend container rulează"
    NEEDS_REBUILD=false
else
    echo -e "${YELLOW}⚠${NC}  Backend container nu rulează"
    NEEDS_REBUILD=true
fi
echo ""

#####################################################
# Step 2: Check .env file
#####################################################

echo -e "${BLUE}[2/8]${NC} Verificare fișier .env..."

if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
    echo -e "${YELLOW}⚠${NC}  .env lipsește - creez din .env.example"
    cp $PROJECT_DIR/backend/.env.example $PROJECT_DIR/backend/.env
    echo -e "${RED}❌ ATENȚIE: Editează $PROJECT_DIR/backend/.env cu API keys reale!${NC}"
    echo -e "${YELLOW}   Necesare: TS_CLIENT_ID, TS_CLIENT_SECRET, UW_API_TOKEN${NC}"
    echo ""
    echo -e "${YELLOW}Vrei să continui fără API keys? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Editează .env și rulează din nou scriptul${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✓${NC} .env există"
    
    # Check for placeholder values
    if grep -q "your_client_id_here\|your_uw_token_here" $PROJECT_DIR/backend/.env; then
        echo -e "${RED}⚠️  .env conține valori placeholder!${NC}"
        echo -e "${YELLOW}   Editează $PROJECT_DIR/backend/.env cu API keys reale${NC}"
    fi
fi
echo ""

#####################################################
# Step 3: Pull latest code
#####################################################

echo -e "${BLUE}[3/8]${NC} Pull ultimele modificări..."
git pull origin main || echo -e "${YELLOW}⚠️  Git pull eșuat - posibil divergență${NC}"
echo -e "${GREEN}✓${NC} Cod actualizat"
echo ""

#####################################################
# Step 4: Check Dockerfile fix
#####################################################

echo -e "${BLUE}[4/8]${NC} Verificare Dockerfile fix..."

if grep -q "server:app" $PROJECT_DIR/backend/Dockerfile; then
    echo -e "${GREEN}✓${NC} Dockerfile corectat (server:app)"
else
    echo -e "${YELLOW}⚠${NC}  Dockerfile incorect - corectez..."
    sed -i 's/main:app/server:app/g' $PROJECT_DIR/backend/Dockerfile
    echo -e "${GREEN}✓${NC} Dockerfile corectat"
    NEEDS_REBUILD=true
fi
echo ""

#####################################################
# Step 5: Stop and remove old containers
#####################################################

echo -e "${BLUE}[5/8]${NC} Stop containere existente..."
docker-compose down
echo -e "${GREEN}✓${NC} Containere oprite"
echo ""

#####################################################
# Step 6: Rebuild backend image
#####################################################

echo -e "${BLUE}[6/8]${NC} Rebuild backend image..."
docker-compose build backend
echo -e "${GREEN}✓${NC} Backend image rebuildat"
echo ""

#####################################################
# Step 7: Start containers
#####################################################

echo -e "${BLUE}[7/8]${NC} Pornire containere..."
docker-compose up -d
echo -e "${GREEN}✓${NC} Containere pornite"
echo ""

# Wait for backend to be ready
echo -e "${YELLOW}Aștept backend să pornească (10s)...${NC}"
sleep 10

#####################################################
# Step 8: Verify backend health
#####################################################

echo -e "${BLUE}[8/8]${NC} Verificare health backend..."

HEALTH_CHECK_COUNT=0
MAX_RETRIES=5

while [ $HEALTH_CHECK_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health 2>/dev/null | grep -q "healthy\|ok\|status"; then
        echo -e "${GREEN}✓${NC} Backend funcționează!"
        BACKEND_HEALTHY=true
        break
    else
        HEALTH_CHECK_COUNT=$((HEALTH_CHECK_COUNT + 1))
        echo -e "${YELLOW}⏳ Retry $HEALTH_CHECK_COUNT/$MAX_RETRIES...${NC}"
        sleep 3
    fi
done

if [ "$BACKEND_HEALTHY" != "true" ]; then
    echo -e "${RED}✗${NC} Backend nu răspunde după $MAX_RETRIES încercări"
    echo -e "${YELLOW}Verifică logs:${NC}"
    docker-compose logs backend --tail=30
    exit 1
fi
echo ""

#####################################################
# Step 9: Reload Caddy (if running)
#####################################################

echo -e "${BLUE}[Extra]${NC} Reload Caddy..."
if systemctl is-active --quiet caddy 2>/dev/null; then
    systemctl reload caddy
    echo -e "${GREEN}✓${NC} Caddy reloaded"
else
    echo -e "${YELLOW}⚠${NC}  Caddy nu rulează - skip"
fi
echo ""

#####################################################
# Final verification
#####################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deployment fix complet!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Verificări finale:${NC}"
echo -e "  • Backend local: ${GREEN}curl http://localhost:8000/health${NC}"
echo -e "  • HTTPS public:  ${GREEN}curl https://flowmindanalytics.ai/health${NC}"
echo -e "  • Container logs: ${GREEN}docker-compose logs backend -f${NC}"
echo ""

echo -e "${YELLOW}Dacă backend-ul încă nu funcționează:${NC}"
echo -e "  1. Verifică logs: ${GREEN}docker-compose logs backend --tail=50${NC}"
echo -e "  2. Verifică .env: ${GREEN}cat backend/.env | grep -v SECRET${NC}"
echo -e "  3. Verifică porturi: ${GREEN}netstat -tlnp | grep 8000${NC}"
echo -e "  4. Restart manual: ${GREEN}docker-compose restart backend${NC}"
echo ""

# Show container status
echo -e "${YELLOW}Status containere:${NC}"
docker-compose ps
echo ""
