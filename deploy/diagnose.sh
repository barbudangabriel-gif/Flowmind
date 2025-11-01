#!/bin/bash

# FlowMind Production Diagnostic Script
# Run this to get a complete health overview

echo "🔍 FlowMind Production Diagnostic"
echo "=================================="
echo ""

# Server Info
echo "📊 Server Information"
echo "--------------------"
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo "Uptime: $(uptime -p)"
echo ""

# Disk Space
echo "💾 Disk Space"
echo "-------------"
df -h | grep -E 'Filesystem|/dev/sda|/dev/vda' | head -2
echo ""

# Memory
echo "🧠 Memory Usage"
echo "---------------"
free -h | grep -E 'Mem:|Swap:'
echo ""

# CPU Load
echo "⚡ CPU Load"
echo "-----------"
uptime | awk -F'load average:' '{print $2}'
echo ""

# Docker Containers
echo "🐳 Docker Containers"
echo "--------------------"
if [ -f "/opt/flowmind/deploy/docker-compose.production.yml" ]; then
    cd /opt/flowmind
    docker-compose -f deploy/docker-compose.production.yml ps
else
    echo "❌ docker-compose.production.yml not found"
fi
echo ""

# Backend Health
echo "✅ Backend Health Check"
echo "-----------------------"
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is responding"
    curl -s http://localhost:8000/health | jq '.' 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ Backend is NOT responding"
fi
echo ""

# Redis
echo "✅ Redis Health Check"
echo "---------------------"
if docker exec flowmind-redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is responding: $(docker exec flowmind-redis redis-cli ping)"
    echo "Keys in database: $(docker exec flowmind-redis redis-cli dbsize 2>/dev/null | grep -o '[0-9]*')"
else
    echo "❌ Redis is NOT responding"
fi
echo ""

# Caddy
echo "🔒 Caddy Status"
echo "---------------"
if command -v systemctl > /dev/null 2>&1; then
    if systemctl is-active caddy > /dev/null 2>&1; then
        echo "✓ Caddy is active"
    else
        echo "❌ Caddy is NOT active"
    fi
else
    echo "⚠️  systemctl not available"
fi
echo ""

# Network Ports
echo "🌐 Network Ports"
echo "----------------"
echo "Port 80 (HTTP):"
if sudo lsof -i :80 > /dev/null 2>&1; then
    echo "  ✓ In use (Caddy)"
else
    echo "  ❌ Not listening"
fi

echo "Port 443 (HTTPS):"
if sudo lsof -i :443 > /dev/null 2>&1; then
    echo "  ✓ In use (Caddy)"
else
    echo "  ❌ Not listening"
fi

echo "Port 8000 (Backend):"
if lsof -i :8000 > /dev/null 2>&1; then
    echo "  ✓ In use (Backend)"
else
    echo "  ❌ Not listening"
fi
echo ""

# Recent Logs
echo "📝 Recent Backend Logs (last 10 lines)"
echo "---------------------------------------"
if [ -f "/opt/flowmind/deploy/docker-compose.production.yml" ]; then
    cd /opt/flowmind
    docker-compose -f deploy/docker-compose.production.yml logs --tail=10 backend 2>/dev/null || echo "No logs available"
else
    echo "❌ Cannot access logs"
fi
echo ""

# Backups
echo "🗄️  Recent Backups"
echo "------------------"
if [ -d "/opt/flowmind/backups" ]; then
    echo "Latest backups:"
    ls -lht /opt/flowmind/backups | head -6 | tail -5
    echo ""
    echo "Total backup size: $(du -sh /opt/flowmind/backups 2>/dev/null | cut -f1)"
else
    echo "⚠️  No backup directory found"
fi
echo ""

# Summary
echo "📊 Summary"
echo "----------"
ISSUES=0

if ! curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend not responding"
    ((ISSUES++))
fi

if ! docker exec flowmind-redis redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis not responding"
    ((ISSUES++))
fi

if command -v systemctl > /dev/null 2>&1; then
    if ! systemctl is-active caddy > /dev/null 2>&1; then
        echo "❌ Caddy not active"
        ((ISSUES++))
    fi
fi

if [ $ISSUES -eq 0 ]; then
    echo "✅ All systems operational!"
else
    echo "⚠️  Found $ISSUES issue(s)"
    echo "   Run 'docker-compose -f /opt/flowmind/deploy/docker-compose.production.yml logs' for details"
fi

echo ""
echo "For detailed troubleshooting, see: /opt/flowmind/deploy/TROUBLESHOOTING.md"
