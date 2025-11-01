#!/bin/bash
set -e

# FlowMind Hetzner Deployment Script
# Usage: Run this on a fresh Ubuntu 22.04/24.04 Hetzner server

echo "🚀 FlowMind Hetzner Setup Script"
echo "=================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker & Docker Compose
echo "🐳 Installing Docker..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose (standalone)
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Caddy (reverse proxy with auto HTTPS)
echo "🔒 Installing Caddy..."
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy

# Install Git
echo "📥 Installing Git..."
sudo apt-get install -y git

# Create app directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/flowmind
sudo chown $USER:$USER /opt/flowmind

# Clone repository (you'll need to provide the URL)
echo "📦 Clone your repository manually:"
echo "  cd /opt/flowmind"
echo "  git clone https://github.com/barbudangabriel-gif/Flowmind.git ."
echo ""

# Create data directories
sudo mkdir -p /opt/flowmind/data/redis
sudo mkdir -p /opt/flowmind/data/mindfolios
sudo mkdir -p /opt/flowmind/logs
sudo chown -R $USER:$USER /opt/flowmind/data
sudo chown -R $USER:$USER /opt/flowmind/logs

# Firewall setup
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

echo ""
echo "✅ Base setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone repository: cd /opt/flowmind && git clone https://github.com/barbudangabriel-gif/Flowmind.git ."
echo "2. Create .env file: cp deploy/.env.production.example deploy/.env.production"
echo "3. Edit .env with your API keys"
echo "4. Setup domain DNS: Point your domain to this server's IP"
echo "5. Update Caddyfile with your domain"
echo "6. Run: cd /opt/flowmind && ./deploy/production-deploy.sh"
echo ""
