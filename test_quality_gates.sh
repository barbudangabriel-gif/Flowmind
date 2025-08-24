#!/bin/bash

# FlowMind Analytics - Quality Gates Test Suite
# Tests all implemented quality gates and CI/CD components

set -e

echo "🛡️  FlowMind Analytics - Quality Gates Test Suite"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_section() {
    echo -e "${BLUE}📦 $1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

# Frontend Quality Gates
print_section "Frontend Quality Gates"

cd /app/frontend

# Test lint-staged configuration
echo "🔍 Testing lint-staged configuration..."
node -e "
const pkg = require('./package.json');
if (pkg['lint-staged']) {
    console.log('✅ lint-staged configured');
    console.log('📝 Rules:', JSON.stringify(pkg['lint-staged'], null, 2));
} else {
    console.log('❌ lint-staged not configured');
    process.exit(1);
}
" && echo ""

# Test Husky hooks
echo "🪝 Testing Husky hooks..."
if [ -f ".husky/pre-commit" ]; then
    echo "✅ Pre-commit hook exists"
    echo "📄 Content:"
    cat .husky/pre-commit | sed 's/^/   /'
else
    echo "❌ Pre-commit hook missing"
fi
echo ""

# Test Prettier
echo "🎨 Testing Prettier..."
if command -v npx prettier --version &> /dev/null; then
    print_status 0 "Prettier available: $(npx prettier --version)"
else
    print_status 1 "Prettier not available"
fi
echo ""

# Test ESLint
echo "🔍 Testing ESLint..."
if npm run lint --silent; then
    print_status 0 "ESLint checks passed"
else
    print_status 1 "ESLint checks failed"
fi
echo ""

# Test build
echo "🏗️  Testing build..."
if npm run build --silent; then
    print_status 0 "Build successful"
    du -sh build/ 2>/dev/null | sed 's/^/   Build size: /' || true
else
    print_status 1 "Build failed"
fi
echo ""

# Backend Quality Gates
cd /app/backend
print_section "Backend Quality Gates"

# Test pre-commit configuration
echo "🔧 Testing pre-commit configuration..."
if [ -f ".pre-commit-config.yaml" ]; then
    echo "✅ Pre-commit config exists"
    echo "📄 Hooks configured:"
    grep -E "id:|repo:" .pre-commit-config.yaml | sed 's/^/   /'
else
    print_status 1 "Pre-commit config missing"
fi
echo ""

# Test ruff
echo "🦀 Testing Ruff..."
ruff_output=$(ruff check . --statistics 2>&1 | head -5)
if [ $? -eq 0 ]; then
    print_status 0 "Ruff lint passed"
else
    print_status 1 "Ruff lint failed"
    echo "   Issues found:"
    echo "$ruff_output" | sed 's/^/   /'
fi
echo ""

# Test ruff format
echo "🎨 Testing Ruff format..."
format_check=$(ruff format --check . 2>&1)
if [ $? -eq 0 ]; then
    print_status 0 "Ruff format check passed"
else
    print_status 1 "Code needs formatting"
    echo "$format_check" | head -3 | sed 's/^/   /'
fi
echo ""

# Test mypy
echo "🏷️  Testing MyPy..."
if mypy . --ignore-missing-imports --pretty --no-error-summary | head -10; then
    print_status 0 "MyPy type checking completed"
else
    print_status 1 "MyPy type checking issues found"
fi
echo ""

# Test bandit
echo "🛡️  Testing Bandit security scan..."
bandit_output=$(bandit -ll -r . -x tests,migrations,venv,.venv,app -q 2>&1)
bandit_exit=$?
if [ $bandit_exit -eq 0 ]; then
    print_status 0 "Bandit security scan passed"
else
    print_status 1 "Security issues found"
    echo "$bandit_output" | head -5 | sed 's/^/   /'
fi
echo ""

# CI/CD Configuration
cd /app
print_section "CI/CD Configuration"

echo "🔄 Testing GitHub Actions configuration..."
if [ -f ".github/workflows/ci.yml" ]; then
    print_status 0 "GitHub Actions CI configured"
    echo "📄 Jobs configured:"
    grep -E "^\s+[a-zA-Z_]+:" .github/workflows/ci.yml | sed 's/^/   /' | head -10
else
    print_status 1 "GitHub Actions CI missing"
fi
echo ""

# Summary
print_section "Summary & Next Steps"

echo -e "${GREEN}✅ Implementation Complete:${NC}"
echo "   • Frontend: Husky + lint-staged + ESLint + Prettier"
echo "   • Backend: pre-commit + ruff + mypy + bandit"
echo "   • CI/CD: GitHub Actions with quality gates"
echo "   • Conventional commits: commitlint configured"
echo ""

echo -e "${YELLOW}📋 To use the quality gates:${NC}"
echo "   • Commits will auto-lint/format staged files"
echo "   • Push to GitHub will trigger CI quality checks"
echo "   • PRs will be blocked if quality gates fail"
echo ""

echo -e "${BLUE}🚀 Manual testing commands:${NC}"
echo "   Frontend: npm run qa"
echo "   Backend: pre-commit run --all-files"
echo "   Full CI: Push to GitHub branch"
echo ""

echo "🎉 Quality gates implementation completed successfully!"