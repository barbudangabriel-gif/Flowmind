#!/bin/bash
# TradeStation OAuth Flow Initiator

echo "🔐 TradeStation OAuth Flow"
echo "================================"
echo ""

# Read credentials from .env
source /workspaces/Flowmind/backend/.env

echo "Client ID: ${TS_CLIENT_ID:0:10}..."
echo "Mode: $TS_MODE"
echo ""

# Build authorization URL
if [ "$TS_MODE" = "LIVE" ]; then
    AUTH_URL="https://signin.tradestation.com/authorize"
else
    AUTH_URL="https://sim-signin.tradestation.com/authorize"
fi

# OAuth parameters
OAUTH_URL="${AUTH_URL}?client_id=${TS_CLIENT_ID}&response_type=code&redirect_uri=${TS_REDIRECT_URI}&audience=https://api.tradestation.com&scope=openid profile MarketData ReadAccount Trade Crypto offline_access"

echo "📋 PAȘI PENTRU CONECTARE LIVE:"
echo ""
echo "1. Deschide acest URL în browser:"
echo ""
echo "$OAUTH_URL"
echo ""
echo "2. Login cu contul tău TradeStation"
echo ""
echo "3. Autorizează aplicația"
echo ""
echo "4. Vei fi redirectat către: http://localhost:8000/api/oauth/tradestation/callback?code=..."
echo ""
echo "5. Copiază codul din URL (parametrul 'code=')"
echo ""
echo "6. Folosește codul pentru a schimba cu token-uri:"
echo ""
echo "curl -X POST 'https://signin.tradestation.com/oauth/token' \\"
echo "  -H 'Content-Type: application/x-www-form-urlencoded' \\"
echo "  -d 'grant_type=authorization_code' \\"
echo "  -d 'client_id=${TS_CLIENT_ID}' \\"
echo "  -d 'client_secret=${TS_CLIENT_SECRET}' \\"
echo "  -d 'code=YOUR_CODE_HERE' \\"
echo "  -d 'redirect_uri=${TS_REDIRECT_URI}'"
echo ""
echo "================================"
echo ""
echo "🌐 SAU deschide direct în browser cu:"
echo ""
echo "\$BROWSER \"$OAUTH_URL\""
