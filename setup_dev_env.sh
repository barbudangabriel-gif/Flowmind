#!/bin/bash
set -e

echo "================================================"
echo "  FlowMind Development Environment Setup"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "🐍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.12"

if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo -e "${RED}❌ Python 3.12+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
echo ""

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -q pre-commit black ruff flake8 mypy bandit || {
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
}
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Setup pre-commit hooks
echo "🔗 Setting up pre-commit hooks..."
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install || {
        echo -e "${RED}❌ Failed to install pre-commit hooks${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠️  No .pre-commit-config.yaml found${NC}"
fi
echo ""

# Verify VS Code settings
echo "🔧 Checking VS Code settings..."
if [ -f ".vscode/settings.json" ]; then
    if grep -q '"editor.detectIndentation": false' .vscode/settings.json; then
        echo -e "${GREEN}✅ VS Code settings correct (detectIndentation: false)${NC}"
    else
        echo -e "${YELLOW}⚠️  VS Code detectIndentation not disabled${NC}"
        echo "   Add to .vscode/settings.json:"
        echo '   "editor.detectIndentation": false'
    fi
else
    echo -e "${YELLOW}⚠️  No .vscode/settings.json found${NC}"
fi
echo ""

# Check EditorConfig
echo "📝 Checking EditorConfig..."
if [ -f ".editorconfig" ]; then
    echo -e "${GREEN}✅ EditorConfig present${NC}"
else
    echo -e "${YELLOW}⚠️  No .editorconfig found${NC}"
fi
echo ""

# Run initial validation
echo "🔍 Running initial code validation..."
echo "   This may take a few minutes on first run..."
pre-commit run --all-files || {
    echo -e "${YELLOW}⚠️  Some pre-commit checks failed${NC}"
    echo "   This is normal on first run. Run again to fix."
}
echo ""

# Backend setup
if [ -d "backend" ]; then
    echo "🔧 Backend setup..."
    cd backend
    
    # Create virtual environment if needed
    if [ ! -d "venv" ]; then
        echo "   Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -q -r requirements.txt 2>/dev/null || echo "   (requirements.txt not found)"
    fi
    
    cd ..
    echo -e "${GREEN}✅ Backend ready${NC}"
fi
echo ""

# Frontend setup
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo "🔧 Frontend setup..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "   Installing npm dependencies..."
        npm install --silent
    fi
    
    cd ..
    echo -e "${GREEN}✅ Frontend ready${NC}"
fi
echo ""

# Final summary
echo "================================================"
echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo "================================================"
echo ""
echo "📋 Quick reference:"
echo "   • Format Python: black backend/"
echo "   • Lint Python: ruff check backend/"
echo "   • Run pre-commit: pre-commit run --all-files"
echo "   • Backend start: cd backend && python -m uvicorn app.main:app --reload"
echo "   • Frontend start: cd frontend && npm start"
echo ""
echo "⚠️  IMPORTANT:"
echo "   • Always use 4-space indentation for Python"
echo "   • Format on save is enabled in VS Code"
echo "   • Pre-commit hooks will block invalid code"
echo "   • NEVER commit with --no-verify"
echo ""
echo "📖 See INDENTATION_PREVENTION_GUIDE.md for details"
echo ""
