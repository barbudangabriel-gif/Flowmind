#!/bin/bash
# Unusual Whales API Key Injection Script
# Injects UW_API_TOKEN from GitHub Secrets into runtime environment

set -e

echo "🔐 Unusual Whales API Key Injection"
echo "===================================="

# Check if running in GitHub Actions
if [ -n "$GITHUB_ACTIONS" ]; then
    echo "✓ Running in GitHub Actions"
    
    # API key should be in secrets
    if [ -n "$UW_API_SECRET" ]; then
        export UW_API_TOKEN="$UW_API_SECRET"
        echo "✓ UW_API_TOKEN injected from GitHub Secret"
    else
        echo "⚠️  WARNING: UW_API_SECRET not found in GitHub Secrets"
        echo "   Backend will run in DEMO MODE"
    fi
else
    echo "ℹ️  Not running in GitHub Actions"
    
    # Check local environment
    if [ -n "$UW_API_TOKEN" ]; then
        echo "✓ UW_API_TOKEN already set in environment"
    elif [ -n "$UNUSUAL_WHALES_API_KEY" ]; then
        export UW_API_TOKEN="$UNUSUAL_WHALES_API_KEY"
        echo "✓ UW_API_TOKEN set from UNUSUAL_WHALES_API_KEY"
    elif [ -n "$UW_KEY" ]; then
        export UW_API_TOKEN="$UW_KEY"
        echo "✓ UW_API_TOKEN set from UW_KEY"
    else
        echo "⚠️  WARNING: No UW API key found"
        echo "   Set UW_API_TOKEN, UNUSUAL_WHALES_API_KEY, or UW_KEY"
        echo "   Backend will run in DEMO MODE"
    fi
fi

# Verify API key is set (mask for security)
if [ -n "$UW_API_TOKEN" ]; then
    KEY_PREFIX="${UW_API_TOKEN:0:8}"
    echo "✓ API Key configured: ${KEY_PREFIX}..."
    
    # Export for child processes
    export UW_API_TOKEN
    export UW_BASE_URL="${UW_BASE_URL:-https://api.unusualwhales.com}"
    
    echo "✓ UW_BASE_URL: $UW_BASE_URL"
else
    echo "ℹ️  Running in DEMO MODE (mock data only)"
fi

echo "===================================="
echo ""
