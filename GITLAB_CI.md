# 🦊 FlowMind Analytics - GitLab CI Quality Gates

## GitLab CI Implementation

Complete quality gates implementation for GitLab CI/CD with comprehensive testing and security scanning.

## Quick Setup

### 1. Pipeline Configuration

The `.gitlab-ci.yml` file is already configured with:

- **3 stages**: `fe`, `be`, `gate`
- **Auto-detection**: Yarn vs NPM support
- **Caching**: NPM and Pip dependencies
- **Artifacts**: Build outputs and test reports
- **Security**: npm audit + pip-audit + bandit

### 2. GitLab Project Settings

#### Required Settings:

```bash
# Navigate to your GitLab project
Settings → CI/CD → Runners
# Ensure Shared Runners are enabled

Settings → General → Merge request approvals 
# Check "Pipelines must succeed"
# This blocks MRs with failed quality gates

Settings → Repository → Protected branches
# Protect main/master branch
# Require merge requests
```

#### Optional but Recommended:
```bash
Settings → General → Merge request approvals
# "Reset approvals when new commits are added"
# "Enable 'Delete source branch' option by default"

Settings → CI/CD → General pipelines
# "Auto-cancel redundant pipelines"
```

### 3. Local Development Setup

#### Frontend (Husky + lint-staged):
```bash
cd frontend

# If using NPM
npm ci
npx husky install

# If using Yarn 
corepack enable
yarn install --immutable
yarn husky install
```

#### Backend (pre-commit):
```bash
cd backend
pip install pre-commit ruff mypy bandit
pre-commit install
```

## Pipeline Stages

### Stage 1: Frontend (`fe`)
```yaml
 Auto-detects Yarn vs NPM
 Installs dependencies with caching
 Runs ESLint with zero tolerance
 Builds application (if build script exists)
 Security audit (high-level vulnerabilities)
 Saves build artifacts for 1 week
```

### Stage 2: Backend (`be`) 
```yaml
 Python 3.11 environment
 Installs all quality tools
 Ruff linting with GitHub output format
 Ruff format checking
 MyPy type checking
 Bandit security scanning (low-level+)
 pip-audit dependency security (strict)
 pytest testing (optional, continues on failure)
 Caches pip dependencies and tool caches
```

### Stage 3: Gate (`gate`)
```yaml
 Requires both frontend AND backend to pass
 Lightweight Alpine image for fast execution
 Final checkpoint before allowing merge
```

## 🛠️ Configuration Options

### Adjusting Strictness

#### Frontend Audit Levels:
```yaml
# Current (strict)
yarn audit --level high
npm audit --audit-level=high

# Less strict (only critical)
yarn audit --level critical 
npm audit --audit-level=critical

# Warning only (doesn't fail pipeline)
yarn audit --level high || true
npm audit --audit-level=high || true
```

#### Backend Security Levels:
```yaml
# Current (strict - fails on any vulnerability)
pip-audit -r requirements.txt --strict

# Less strict (only reports, doesn't fail)
pip-audit -r requirements.txt

# Bandit levels
bandit -ll -r . # Low-level and above (current)
bandit -l -r . # Medium-level and above 
bandit -h -r . # High-level only
```

### Yarn vs NPM Detection

The pipeline automatically detects package manager:

```yaml
# Auto-detection logic
if [ -f yarn.lock ]; then
 # Use Yarn
 corepack enable
 yarn install --immutable
 yarn run lint
else
 # Use NPM 
 npm ci
 npm run lint
fi
```

### Caching Strategy

```yaml
# Frontend caching
cache:
 key: "${CI_COMMIT_REF_SLUG}-fe"
 paths:
 - .cache/npm/ # NPM cache
 - node_modules/ # Node modules

# Backend caching
cache:
 key: "${CI_COMMIT_REF_SLUG}-be" 
 paths:
 - .cache/pip/ # Pip cache
 - backend/.ruff_cache/ # Ruff cache
 - backend/.mypy_cache/ # MyPy cache
```

## Usage Examples

### Manual Pipeline Trigger
```bash
# Push to trigger pipeline
git push origin feature-branch

# Create MR to trigger MR pipeline
# GitLab will automatically run quality gates
```

### Local Testing (matches CI exactly)
```bash
# Frontend
cd frontend
npm run lint # Same as CI
npm run build # Same as CI
npm audit --audit-level=high # Same as CI

# Backend
cd backend
ruff check . # Same as CI
ruff format --check # Same as CI 
mypy . --ignore-missing-imports --pretty # Same as CI
bandit -ll -r . -x tests # Same as CI
pip-audit -r requirements.txt --strict # Same as CI
```

## Pipeline Artifacts

### Frontend Artifacts:
- `frontend/build/` - Built application (1 week retention)
- Lint reports and build logs

### Backend Artifacts: 
- `junit*.xml` - Test reports (GitLab integration)
- `.ruff_cache/` - Ruff caching data
- `.mypy_cache/` - MyPy caching data
- Security scan reports

## 🔧 Troubleshooting

### Common Issues:

#### 1. Runner Out of Memory
```yaml
variables:
 NODE_OPTIONS: --max-old-space-size=4096 # Increase from 2048
```

#### 2. Slow Dependency Installation
```yaml
# Enable more aggressive caching
cache:
 key: "${CI_COMMIT_REF_SLUG}"
 paths:
 - node_modules/
 - .cache/
 policy: pull-push
```

#### 3. False Positives in Security Scans
```yaml
# Bandit: exclude specific issues
bandit -ll -r . -x tests -s B101,B601

# pip-audit: ignore specific vulnerabilities 
pip-audit --ignore-vuln GHSA-xxxx-xxxx-xxxx
```

#### 4. Different Behavior Local vs CI
```bash
# Use exact same environment locally
docker run --rm -v $(pwd):/workspace -w /workspace node:20 bash
# Then run same commands as CI
```

## Quality Gate Rules

### MR Blocking Conditions:
- ESLint errors or warnings
- Build failures 
- High/critical npm security vulnerabilities
- Ruff linting errors
- Ruff formatting issues
- MyPy type checking errors
- Bandit security issues (low-level+)
- pip-audit security vulnerabilities

### MR Allows:
- pytest failures (continues with warning)
- Minor formatting differences (ruff auto-fixes)
- MyPy warnings on missing imports

## Benefits

### Development Experience:
- **Fast feedback**: Quality issues caught immediately
- **Consistent environment**: CI matches local development
- **Automated fixes**: Many issues auto-resolved by pre-commit hooks
- **Security focus**: Comprehensive vulnerability scanning

### Team Benefits:
- **Code consistency**: Enforced formatting and linting
- **Security assurance**: Multi-layer security scanning 
- **Quality confidence**: No low-quality code reaches main
- **Review efficiency**: MRs pre-validated for quality

---

## Migration from GitHub Actions

If switching from GitHub Actions to GitLab CI:

1. Keep all local hooks (husky, pre-commit) - they work identically
2. Replace `.github/workflows/ci.yml` with `.gitlab-ci.yml` 
3. Configure GitLab project settings as documented above
4. Same quality standards, same local development experience

Both platforms now supported with identical quality enforcement! 