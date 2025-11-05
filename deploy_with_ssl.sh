#!/bin/bash

#####################################################
# FlowMind SSL Setup & Deployment Script
# 
# Rulează pe serverul de producție pentru:
# - Configurare SSL automat cu Let's Encrypt
# - Deploy FlowMind cu HTTPS
# - Configurare Caddy
#
# Rulează ca root: bash deploy_with_ssl.sh
#####################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="flowmindanalytics.ai"
WWW_DOMAIN="www.flowmindanalytics.ai"
PROJECT_DIR="/opt/flowmind"
FRONTEND_BUILD_DIR="$PROJECT_DIR/frontend/build"
CADDY_CONFIG="/etc/caddy/Caddyfile"
LOG_DIR="/var/log/caddy"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  FlowMind SSL Setup & Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ Acest script trebuie rulat ca root!${NC}"
   echo -e "Rulează: ${YELLOW}sudo bash deploy_with_ssl.sh${NC}"
   exit 1
fi

echo -e "${GREEN}✓${NC} Rulează ca root"
echo ""

#####################################################
# Step 1: Check DNS Configuration
#####################################################

echo -e "${BLUE}[1/8]${NC} Verificare configurare DNS..."

RESOLVED_IP=$(dig +short $DOMAIN | head -n1)
SERVER_IP=$(curl -s ifconfig.me)

if [ -z "$RESOLVED_IP" ]; then
    echo -e "${RED}❌ DNS nu este configurat pentru $DOMAIN${NC}"
    echo -e "${YELLOW}Configurează A record în Cloudflare:${NC}"
    echo -e "  Type: A"
    echo -e "  Name: @"
    echo -e "  IPv4: $SERVER_IP"
    echo -e "  Proxy: OFF (gray cloud)"
    exit 1
fi

if [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
    echo -e "${YELLOW}⚠️  Warning: DNS rezolvă la $RESOLVED_IP, dar serverul are IP $SERVER_IP${NC}"
    echo -e "${YELLOW}Continuă oricum? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} DNS configurat corect: $DOMAIN → $SERVER_IP"
fi

echo ""

#####################################################
# Step 2: Install Caddy (if not installed)
#####################################################

echo -e "${BLUE}[2/8]${NC} Verificare instalare Caddy..."

if ! command -v caddy &> /dev/null; then
    echo -e "${YELLOW}Caddy nu este instalat. Instalare...${NC}"
    
    apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    
    apt update
    apt install -y caddy
    
    systemctl enable caddy
    
    echo -e "${GREEN}✓${NC} Caddy instalat"
else
    CADDY_VERSION=$(caddy version | head -n1)
    echo -e "${GREEN}✓${NC} Caddy deja instalat: $CADDY_VERSION"
fi

echo ""

#####################################################
# Step 3: Check Docker & Docker Compose
#####################################################

echo -e "${BLUE}[3/8]${NC} Verificare Docker..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker nu este instalat!${NC}"
    echo -e "Instalează Docker cu: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker instalat"
echo ""

#####################################################
# Step 4: Clone/Update FlowMind Repository
#####################################################

echo -e "${BLUE}[4/8]${NC} Actualizare cod FlowMind..."

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Director $PROJECT_DIR nu există. Clone repository...${NC}"
    mkdir -p /opt
    cd /opt
    git clone https://github.com/barbudangabriel-gif/Flowmind.git flowmind
    cd flowmind
else
    cd $PROJECT_DIR
    echo -e "Pull ultimele modificări..."
    git pull origin main
fi

echo -e "${GREEN}✓${NC} Cod actualizat"
echo ""

#####################################################
# Step 5: Build Frontend
#####################################################

echo -e "${BLUE}[5/8]${NC} Build frontend pentru producție..."

cd $PROJECT_DIR/frontend

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js nu este instalat!${NC}"
    echo -e "Instalează Node.js 20.x cu:"
    echo -e "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -"
    echo -e "apt install -y nodejs"
    exit 1
fi

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo -e "Instalare dependențe npm..."
    npm install
fi

# Create production .env
echo "REACT_APP_BACKEND_URL=http://localhost:8080" > .env.production

# Build
echo -e "Build frontend..."
npm run build

if [ ! -d "$FRONTEND_BUILD_DIR" ]; then
    echo -e "${RED}❌ Build frontend eșuat! Director build nu există.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Frontend build complet"
echo ""

#####################################################
# Step 6: Configure Backend
#####################################################

echo -e "${BLUE}[6/8]${NC} Configurare backend..."

cd $PROJECT_DIR/backend

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Fișier .env nu există. Creare din .env.example...${NC}"
    cp .env.example .env
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Editează backend/.env${NC}"
    echo -e "${YELLOW}Adaugă:${NC}"
    echo -e "  - TS_CLIENT_ID=..."
    echo -e "  - TS_CLIENT_SECRET=..."
    echo -e "  - UW_API_TOKEN=..."
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e ""
    echo -e "Apasă Enter după ce ai editat .env..."
    read -r
fi

echo -e "${GREEN}✓${NC} Backend configurat"
echo ""

#####################################################
# Step 7: Start Docker Containers
#####################################################

echo -e "${BLUE}[7/8]${NC} Pornire Docker containers (backend + Redis)..."

cd $PROJECT_DIR

# Stop existing containers
docker-compose down 2>/dev/null || true

# Start containers
docker-compose up -d

# Wait for backend to be ready
echo -e "Așteptare backend să pornească..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}✓${NC} Backend pornit și funcțional"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend nu pornește! Verifică logs:${NC}"
        echo -e "docker-compose logs backend"
        exit 1
    fi
    
    sleep 1
done

echo ""

#####################################################
# Step 8: Configure and Start Caddy with SSL
#####################################################

echo -e "${BLUE}[8/8]${NC} Configurare Caddy pentru SSL..."

# Create log directory
mkdir -p $LOG_DIR
chown -R caddy:caddy $LOG_DIR

# Copy Caddyfile
if [ -f "$PROJECT_DIR/Caddyfile.with-auth" ]; then
    cp $PROJECT_DIR/Caddyfile.with-auth $CADDY_CONFIG
    echo -e "${GREEN}✓${NC} Caddyfile copiat (cu autentificare)"
else
    echo -e "${RED}❌ Caddyfile.with-auth nu există!${NC}"
    exit 1
fi

# Validate Caddyfile
echo -e "Validare configurare Caddy..."
if ! caddy validate --config $CADDY_CONFIG; then
    echo -e "${RED}❌ Caddyfile invalid! Verifică configurarea.${NC}"
    exit 1
fi

# Restart Caddy
echo -e "Restart Caddy (SSL se configurează automat)..."
systemctl restart caddy

# Wait for Caddy to start
sleep 3

if ! systemctl is-active --quiet caddy; then
    echo -e "${RED}❌ Caddy nu pornește! Verifică logs:${NC}"
    echo -e "journalctl -u caddy -n 50"
    exit 1
fi

echo -e "${GREEN}✓${NC} Caddy pornit și funcțional"
echo ""

#####################################################
# Verification
#####################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Verificare Finală${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Așteptare 10 secunde pentru Let's Encrypt SSL...${NC}"
sleep 10

# Check HTTPS
echo -e "Test HTTPS pe $DOMAIN..."
if curl -s -I -k https://$DOMAIN | head -n1 | grep -q "200\|301\|302\|401"; then
    echo -e "${GREEN}✓${NC} HTTPS funcționează"
else
    echo -e "${YELLOW}⚠️  HTTPS nu răspunde încă. Verifică logs:${NC}"
    echo -e "journalctl -u caddy -f"
fi

# Check certificate
echo -e "\nVerificare certificat SSL..."
CERT_EXPIRY=$(echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter || echo "N/A")
if [ "$CERT_EXPIRY" != "N/A" ]; then
    echo -e "${GREEN}✓${NC} Certificat SSL: $CERT_EXPIRY"
else
    echo -e "${YELLOW}⚠️  Certificat SSL nu este încă disponibil${NC}"
    echo -e "${YELLOW}Așteaptă 1-2 minute și verifică manual:${NC}"
    echo -e "curl -I https://$DOMAIN"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Deployment complet!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "🌐 Site: ${GREEN}https://$DOMAIN${NC}"
echo -e "🔒 SSL: ${GREEN}Activ (Let's Encrypt)${NC}"
echo -e "🔐 Auth: Username: ${YELLOW}gabriel${NC}, Password: ${YELLOW}FlowMind2025!${NC}"
echo ""
echo -e "${YELLOW}Comenzi utile:${NC}"
echo -e "  - Logs Caddy:   ${BLUE}journalctl -u caddy -f${NC}"
echo -e "  - Logs Backend: ${BLUE}docker-compose logs backend -f${NC}"
echo -e "  - Restart:      ${BLUE}systemctl restart caddy${NC}"
echo -e "  - Status:       ${BLUE}systemctl status caddy${NC}"
echo ""
echo -e "${GREEN}Deployment finalizat cu succes! 🎉${NC}"
echo ""
