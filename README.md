# FlowMind - Options Analytics Platform

**Advanced options analytics, real-time flow monitoring, and portfolio management platform**

[![Security](https://img.shields.io/badge/security-hardened-green.svg)](./SECURITY_CI_IMPROVEMENTS_2025-10-14.md)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitLab-orange.svg)](./.gitlab-ci.yml)
[![Health](https://img.shields.io/badge/health-monitored-blue.svg)](#health-endpoints)

---

## 🚀 Quick Start

### Prerequisites
- **Backend:** Python 3.11+, FastAPI, Redis (optional, has fallback)
- **Frontend:** Node 20+, React 19
- **Optional:** MongoDB (portfolios), TradeStation API, Unusual Whales API

### Development Setup

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn server:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

**Docker Compose (Full Stack):**
```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Redis: localhost:6379
```

---

## 🏗️ Architecture

### Backend (FastAPI)
- **Options Module:** 54+ strategies, Greeks calculation, quality scoring
- **Flow Analysis:** Real-time unusual options activity (Unusual Whales integration)
- **Portfolio Management:** FIFO position tracking, P&L, performance analytics
- **Data Providers:** TradeStation (options chains, spot prices), UW (flow/news)
- **Caching:** Redis with intelligent fallback to in-memory (zero downtime)

### Frontend (React 19)
- **Strategy Builder:** Interactive multi-leg options builder with live pricing
- **Flow Dashboard:** Real-time options flow, dark pool, congress trades
- **Portfolio Tracker:** Multi-portfolio management, charts, rebalancing AI
- **Market Intelligence:** Gamma exposure (GEX), IV analysis, scanner

### Data Storage
- **Redis:** Primary cache (TTL-based), fallback to AsyncTTLDict
- **MongoDB:** Portfolios, transactions, user data (optional)
- **SQLite:** Alternative storage (see `backend/database.py`)

---

## 🏥 Health Endpoints

### Available Endpoints

| Endpoint | Purpose | Response Time (Dev) |
|----------|---------|---------------------|
| `GET /health` | Basic health check | ~1.5ms sequential |
| `GET /healthz` | Kubernetes-style liveness | ~1.5ms sequential |
| `GET /readyz` | Readiness probe (checks Redis) | ~1.4ms sequential |
| `GET /api/health/redis` | **NEW** Cache stats & monitoring | ~1.5ms sequential |

### Redis Health Endpoint

**GET `/api/health/redis`** - Detailed cache statistics:

```json
{
  "status": "healthy",
  "mode": "redis",  // or "in-memory"
  "connected": true,
  "keys_total": 1234,
  "memory_used": "2.5MB",
  "fallback_active": false,
  "timestamp": "2025-10-14T14:52:00Z"
}
```

**Use Cases:**
- Monitor cache performance in production
- Detect Redis failures early
- Track memory usage trends
- Verify fallback mode activation

**Test Locally:**
```bash
curl http://localhost:8000/api/health/redis | jq
```

---

## 🔒 Security

### Recent Security Hardening (Oct 14, 2025)

✅ **Eliminated 76% of CWE-330 warnings**
- Replaced `random` → `secrets` in 5 backend files
- Demo data generation follows security best practices
- Zero HIGH/MEDIUM security issues

✅ **CI/CD Security Gates**
- Bandit (Python SAST): `-ll` (low severity or higher)
- npm audit: `--audit-level=high`
- pip-audit: `--strict`
- Zero tolerance on HIGH/CRITICAL issues

See: [ABCD_IMPROVEMENTS_2025-10-14.md](./ABCD_IMPROVEMENTS_2025-10-14.md), [SECURITY_CI_IMPROVEMENTS_2025-10-14.md](./SECURITY_CI_IMPROVEMENTS_2025-10-14.md)

---

## 📊 Performance

### Health Endpoints Benchmarks (Dev Container)

**Sequential Performance:**
- Min: ~1.4ms
- Mean: ~1.7ms
- P95: ~2.6ms
- **100% success rate**

**Concurrent Load (1000 requests, 100 concurrent):**
- Mean: ~340ms
- P95: ~1000ms
- Throughput: ~3 req/s
- **100% success rate**

**Note:** Production performance significantly better (dedicated resources, no container overhead).

Run performance tests:
```bash
python performance_health_test.py
```

---

## 🧪 Testing

### Backend Tests

**Unit Tests:**
```bash
cd backend
pytest -q --maxfail=1 --disable-warnings
```

**Integration Tests (Root Level):**
```bash
# Comprehensive backend smoke test
python go_no_go_backend_test.py

# Options module tests
python options_backend_test.py

# Builder tests
python builder_backend_test.py

# Flow tests
python flow_backend_test.py
```

**Linting & Security:**
```bash
cd backend
ruff check .                              # Linter
mypy . --ignore-missing-imports          # Type checking
bandit -ll -r .                          # Security audit
pip-audit --strict                       # Dependency vulnerabilities
```

### Frontend Tests

```bash
cd frontend
npm run lint                             # ESLint
npm run build                            # Production build test
npm audit --audit-level=high            # Dependency audit
npm test                                 # Jest tests (if configured)
```

---

## 🚀 CI/CD (GitLab)

### Pipeline Stages
1. **Build:** Docker image creation
2. **Frontend:** Lint, build, audit, test
3. **Backend:** Lint (ruff), types (mypy), security (bandit), audit (pip-audit), tests (pytest), **health check** 🆕
4. **Test:** IV smoke test
5. **Quality:** Code quality analysis
6. **SAST:** Security scanning (dependency, container, SAST)
7. **SBOM:** Software Bill of Materials
8. **Gate:** Enforce quality/security thresholds

### Backend Stage (Enhanced Oct 14, 2025)

**NEW: Automated Health Endpoint Validation**

```yaml
backend:
  services:
    - redis:latest  # Real Redis for testing
  script:
    - # ... existing linting/testing ...
    
    # Health endpoint validation
    - python -m uvicorn server:app --host 0.0.0.0 --port 8000 &
    - sleep 5
    - curl -f http://localhost:8000/health || exit 1
    - curl -f http://localhost:8000/healthz || exit 1
    - curl -f http://localhost:8000/readyz || exit 1
    - curl -f http://localhost:8000/api/health/redis || exit 1
    - echo "✅ All health endpoints working"
```

**Benefits:**
- Early detection of broken health endpoints
- Validates Redis connectivity during CI
- Fails fast if critical monitoring breaks
- Production parity (tests with real Redis)

See: [.gitlab-ci.yml](./.gitlab-ci.yml)

---

## 📚 Key Documentation

### General
- [Platform Guide](./PLATFORM_GUIDE.md) - Architecture overview
- [Options Module Blueprint](./FlowMind_Options_Module_Blueprint.md) - Strategy engine docs
- [Development Guidelines](./DEVELOPMENT_GUIDELINES.md) - Coding standards (Romanian)

### API Integration
- [TradeStation Setup](./TRADESTATION_SETUP_GUIDE.md) - OAuth configuration
- [Unusual Whales API](./UW_API_MIGRATION_README.md) - Integration guide
- [UW Correct Endpoints](./UW_API_CORRECT_ENDPOINTS.md) - Endpoint reference

### Security & CI/CD
- [Enterprise Security Gates](./ENTERPRISE_SECURITY_GATES.md) - Security policies
- [Quality Gates](./QUALITY_GATES.md) - CI/CD thresholds
- [Container Security](./CONTAINER_SECURITY_COMPLETE.md) - Docker hardening
- [SBOM](./ENTERPRISE_SBOM_COMPLETE.md) - Software Bill of Materials

### Recent Improvements (Oct 14, 2025)
- [ABCD Improvements](./ABCD_IMPROVEMENTS_2025-10-14.md) - API/DB/Testing/Security
- [Security + CI Improvements](./SECURITY_CI_IMPROVEMENTS_2025-10-14.md) - Random→Secrets, health checks
- [WebSocket Streaming](./WEBSOCKET_STREAMING_DOCS.md) - Real-time data feeds

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=flowmind

# Cache
REDIS_URL=redis://localhost:6379/0
FM_FORCE_FALLBACK=0              # 1 to force in-memory cache
FM_REDIS_REQUIRED=0              # 1 to fail if Redis unavailable

# APIs
UW_API_TOKEN=your_uw_token       # Unusual Whales Pro tier
TS_CLIENT_ID=your_ts_id          # TradeStation OAuth
TS_CLIENT_SECRET=your_ts_secret
TS_REDIRECT_URI=http://localhost:8000/callback

# Features
WARMUP_ENABLED=1                 # Cache warmup on startup
```

**Frontend (.env.local):**
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## 🎯 Key Features

### Options Strategy Builder
- 54+ pre-configured strategies (spreads, condors, butterflies, etc.)
- Interactive multi-leg builder
- Real-time Greeks calculation (Delta, Gamma, Theta, Vega)
- P&L visualization with Plotly charts
- Spread quality scoring
- Historical backtesting

### Real-Time Flow Monitoring
- WebSocket streaming (3 verified + 3 experimental channels with REST fallback)
- Unusual options activity alerts
- Dark pool trades
- Congress trading filings
- Gamma exposure (GEX) tracking

### Portfolio Management
- Multi-portfolio support
- FIFO position tracking
- Realized/unrealized P&L
- Performance charts
- AI-powered rebalancing recommendations

### Market Intelligence
- Options flow summary
- IV analysis and scanner
- Market movers
- Institutional holdings
- ETF data

---

## 🐳 Deployment

### Production Checklist

- [ ] Set all required environment variables
- [ ] Configure Redis (or accept in-memory fallback)
- [ ] Set up MongoDB (optional, for portfolios)
- [ ] Configure TradeStation OAuth (for real options chains)
- [ ] Set Unusual Whales API token (for live flow data)
- [ ] Verify health endpoints: `/health`, `/readyz`, `/api/health/redis`
- [ ] Test with real API keys (not demo mode)
- [ ] Configure reverse proxy (Caddy/Nginx)
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for frontend domain

### Docker Production

```bash
# Build
docker build -t flowmind-backend .

# Run with Redis
docker-compose -f docker-compose.prod.yml up -d

# Verify
curl https://your-domain.com/api/health/redis
```

---

## 🤝 Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes, follow [DEVELOPMENT_GUIDELINES.md](./DEVELOPMENT_GUIDELINES.md)
3. Run tests: `pytest -q` (backend), `npm test` (frontend)
4. Run linters: `ruff check .` (backend), `npm run lint` (frontend)
5. Run security audit: `bandit -ll -r .` (backend), `npm audit` (frontend)
6. Commit with descriptive message
7. Push and create Pull Request
8. Wait for CI/CD pipeline (GitLab) to pass

### Code Quality Standards
- **Linting:** ruff (backend), ESLint (frontend)
- **Type Checking:** mypy (backend), TypeScript (if used)
- **Security:** Bandit, npm audit, pip-audit
- **Test Coverage:** Minimum 60%
- **Documentation:** All public APIs documented

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/barbudangabriel-gif/Flowmind/issues)
- **Docs:** See [documentation directory](./docs) or root-level .md files
- **API Questions:** Check [UW_API_CORRECT_ENDPOINTS.md](./UW_API_CORRECT_ENDPOINTS.md) or [TRADESTATION_SETUP_GUIDE.md](./TRADESTATION_SETUP_GUIDE.md)

---

## 📄 License

See LICENSE file (if applicable)

---

## 🎓 Learning Resources

- **Options Theory:** [FlowMind_Options_Module_Blueprint.md](./FlowMind_Options_Module_Blueprint.md)
- **FIFO Position Calc:** See docstring in `backend/portfolios.py`
- **WebSocket Streaming:** [WEBSOCKET_STREAMING_DOCS.md](./WEBSOCKET_STREAMING_DOCS.md)
- **Quality Scoring:** `backend/services/quality.py`

---

**Last Updated:** October 14, 2025  
**Version:** 3.0.0  
**Status:** ✅ Production Ready

---

## CI/QA Gates (Quick Reference)

### Local Testing (Before Push)

**Frontend:**
```bash
cd frontend && npm ci && npm run lint && npm run build && npm audit --audit-level=high
```

**Backend:**
```bash
cd backend && pip install -r requirements.txt || true
pip install ruff mypy bandit pytest pip-audit
ruff check . && mypy . --ignore-missing-imports && bandit -ll -r . && pip-audit -r requirements.txt --strict
pytest -q --maxfail=1 --disable-warnings
```

**Health Endpoints:**
```bash
python -m uvicorn server:app --port 8000 &
sleep 5
curl http://localhost:8000/api/health/redis
pkill -f uvicorn
```
