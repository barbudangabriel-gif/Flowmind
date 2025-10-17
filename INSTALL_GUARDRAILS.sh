#!/bin/bash
set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🔒 FLOWMIND GUARD-RAILS INSTALLATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Frontend Dependencies
echo -e "${BLUE}📦 1. Installing Frontend Dependencies...${NC}"
cd /workspaces/Flowmind/frontend

if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}   Installing pnpm...${NC}"
    npm install -g pnpm
fi

echo -e "   Installing Prettier, ESLint, Husky, lint-staged..."
pnpm add -D prettier eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-config-prettier husky lint-staged 2>&1 | tail -5

echo -e "${GREEN}   ✓ Frontend dependencies installed${NC}"
echo ""

# 2. Initialize Husky
echo -e "${BLUE}📦 2. Initializing Husky...${NC}"
pnpm dlx husky init 2>&1 | tail -3
chmod +x .husky/pre-commit
echo -e "${GREEN}   ✓ Husky initialized${NC}"
echo ""

# 3. Backend Dependencies
echo -e "${BLUE}📦 3. Installing Backend Dependencies...${NC}"
cd /workspaces/Flowmind/backend

echo -e "   Installing Black, isort, pre-commit..."
pip install -q black isort pre-commit

echo -e "${GREEN}   ✓ Backend dependencies installed${NC}"
echo ""

# 4. Install pre-commit hooks
echo -e "${BLUE}📦 4. Installing Pre-Commit Hooks (Backend)...${NC}"
pre-commit install
echo -e "${GREEN}   ✓ Pre-commit hooks installed${NC}"
echo ""

# 5. One-time cleanup - Frontend
echo -e "${BLUE}🧹 5. Running One-Time Formatting (Frontend)...${NC}"
cd /workspaces/Flowmind/frontend
pnpm format 2>&1 | tail -3
echo -e "${GREEN}   ✓ Frontend formatted${NC}"
echo ""

# 6. One-time cleanup - Backend
echo -e "${BLUE}🧹 6. Running One-Time Formatting (Backend)...${NC}"
cd /workspaces/Flowmind/backend
black . 2>&1 | tail -5
isort . 2>&1 | tail -5
echo -e "${GREEN}   ✓ Backend formatted${NC}"
echo ""

# 7. Verify setup
echo -e "${BLUE}✅ 7. Verifying Setup...${NC}"
cd /workspaces/Flowmind/frontend
echo -n "   Frontend lint check: "
pnpm lint 2>&1 | grep -q "error" && echo -e "${YELLOW}WARNINGS${NC}" || echo -e "${GREEN}PASS${NC}"

cd /workspaces/Flowmind/backend
echo -n "   Backend black check: "
black --check . > /dev/null 2>&1 && echo -e "${GREEN}PASS${NC}" || echo -e "${YELLOW}NEEDS FORMATTING${NC}"

echo -n "   Backend isort check: "
isort --check-only . > /dev/null 2>&1 && echo -e "${GREEN}PASS${NC}" || echo -e "${YELLOW}NEEDS FORMATTING${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ GUARD-RAILS INSTALLATION COMPLETE!${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo "   1. Review SETUP_GUARDRAILS.md for usage"
echo "   2. Read COPILOT_COMMIT_CONTRACT.md before commits"
echo "   3. Test pre-commit hooks with a test commit"
echo ""
echo "🧪 Test Guard-Rails:"
echo "   cd frontend && echo 'const bad={a:1}' > test.ts && git add test.ts && git commit -m 'test'"
echo "   (should be blocked by Prettier/ESLint)"
echo ""
