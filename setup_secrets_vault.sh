#!/bin/bash
# FlowMind Secrets Vault Setup Script
# Run this on production server to create secure secrets storage

set -e  # Exit on any error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  FlowMind Secrets Vault Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running on production server
if [ ! -d "/opt/flowmind" ]; then
    echo "❌ Error: /opt/flowmind directory not found"
    echo "   This script should be run on the production server"
    exit 1
fi

echo "📁 Step 1: Create secrets directory..."
mkdir -p /opt/flowmind/secrets
chmod 700 /opt/flowmind/secrets
echo "✅ Directory created: /opt/flowmind/secrets"
echo ""

echo "📝 Step 2: Create secrets template..."
cat > /opt/flowmind/secrets/api_keys.env.template << 'EOFTEMPLATE'
# FlowMind API Secrets - Production
# IMPORTANT: Update these values with your actual secrets!

# Unusual Whales API Token
# Get from: https://unusualwhales.com/account → API Keys
UW_API_TOKEN=your_new_uw_token_here

# TradeStation OAuth Credentials
# Get from: https://developer.tradestation.com
TS_CLIENT_ID=XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj
TS_CLIENT_SECRET=your_ts_client_secret_here
TS_REDIRECT_URI=https://flowmindanalytics.ai/api/oauth/tradestation/callback

# TradeStation Configuration
TS_MODE=LIVE
TRADESTATION_MODE=LIVE
TS_BASE_URL=https://api.tradestation.com
TS_AUTH_URL=https://signin.tradestation.com/authorize
TS_TOKEN_URL=https://signin.tradestation.com/oauth/token
TS_SCOPE=openid offline_access MarketData ReadAccount Trade OptionSpreads Matrix

# Unusual Whales Configuration
UW_BASE_URL=https://api.unusualwhales.com
UW_LIVE=1
UW_MIN_PREMIUM=25000
EOFTEMPLATE

chmod 600 /opt/flowmind/secrets/api_keys.env.template
echo "✅ Template created: api_keys.env.template"
echo ""

echo "🔐 Step 3: Instructions for creating actual secrets file..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ACTION REQUIRED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Get NEW Unusual Whales token:"
echo "   → Visit: https://unusualwhales.com/account"
echo "   → Go to API Keys section"
echo "   → Click 'Regenerate Token' (old one was exposed in git)"
echo "   → Copy the new token"
echo ""
echo "2. Create actual secrets file:"
echo "   nano /opt/flowmind/secrets/api_keys.env"
echo ""
echo "3. Copy template and replace with real values:"
echo "   cp /opt/flowmind/secrets/api_keys.env.template /opt/flowmind/secrets/api_keys.env"
echo "   nano /opt/flowmind/secrets/api_keys.env"
echo "   # Replace 'your_new_uw_token_here' with actual token"
echo "   # Replace 'your_ts_client_secret_here' with actual secret"
echo ""
echo "4. Secure the file:"
echo "   chmod 600 /opt/flowmind/secrets/api_keys.env"
echo "   chown root:root /opt/flowmind/secrets/api_keys.env"
echo ""
echo "5. Update docker-compose.yml:"
echo "   cd /opt/flowmind"
echo "   nano docker-compose.yml"
echo ""
echo "   Add under 'backend:' service:"
echo "   ┌────────────────────────────────────────────────┐"
echo "   │ env_file:                                      │"
echo "   │   - /opt/flowmind/secrets/api_keys.env        │"
echo "   └────────────────────────────────────────────────┘"
echo ""
echo "6. Restart backend:"
echo "   docker-compose restart backend"
echo ""
echo "7. Verify secrets loaded:"
echo "   docker logs flowmind-backend-1 --tail 30 | grep -i 'unusual\|whales\|tradestation'"
echo ""
echo "8. Test API:"
echo "   curl http://localhost:8000/health | jq"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Secrets vault setup complete!"
echo ""
echo "📋 Current permissions:"
ls -la /opt/flowmind/secrets/
echo ""
echo "⚠️  IMPORTANT: Never commit files from /opt/flowmind/secrets/ to git!"
echo ""
