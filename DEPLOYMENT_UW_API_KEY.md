# 🚀 FlowMind Deployment - UW API Key Injection

**Status:** Ready for deployment with corrected UW API endpoints  
**Date:** October 13, 2025

---

## ✅ Pre-Deployment Checklist

- [x] Fixed all hallucinated UW API endpoints
- [x] Updated `uw_client.py` with correct routes
- [x] Updated `unusual_whales_service.py` with correct routes
- [x] Created comprehensive documentation
- [x] Integration tests passing
- [x] API key stored in GitHub Secrets
- [x] Docker Compose configured for env vars
- [x] Deployment scripts created

---

## 🔐 GitHub Secrets Configuration

### 1. Add Secret to GitHub Repository

**Web UI Method:**
1. Go to: `https://github.com/barbudangabriel-gif/Flowmind/settings/secrets/actions`
2. Click "New repository secret"
3. Name: `UW_API_SECRET`
4. Value: `[Your actual Unusual Whales API key]`
5. Click "Add secret"

**GitHub CLI Method:**
```bash
# Set the secret
gh secret set UW_API_SECRET --body "your_actual_uw_api_key_here"

# Verify it's set
gh secret list
```

---

## 🐳 Docker Deployment

### Method 1: Docker Compose with .env file

1. **Create `.env` file** (copy from `.env.example`):
```bash
cd /workspaces/Flowmind
cp .env.example .env
```

2. **Edit `.env` and set your API key**:
```bash
# Open in editor
nano .env

# Or use sed to set it programmatically
sed -i 's/UW_API_TOKEN=.*/UW_API_TOKEN=your_actual_key_here/' .env
```

3. **Start services**:
```bash
# Build and start
docker-compose up -d --build

# Check logs
docker-compose logs -f backend

# Should see:
# ✅ "🐋 Unusual Whales: Configured"
```

4. **Verify API is working**:
```bash
# Test flow endpoint (should return real data, not demo)
curl http://localhost:8000/api/flow/summary | jq '.mode'
# Expected: "LIVE" (not "DEMO")

# Test health
curl http://localhost:8000/health
```

### Method 2: Docker Run with Environment Variables

```bash
# Build backend image
docker build -t flowmind-backend ./backend

# Run with API key
docker run -d \
  --name flowmind-backend \
  -p 8000:8000 \
  -e UW_API_TOKEN="your_actual_key_here" \
  -e UW_BASE_URL="https://api.unusualwhales.com" \
  -e REDIS_HOST="redis" \
  flowmind-backend

# Check logs
docker logs -f flowmind-backend
```

---

## ☸️ Kubernetes Deployment

### 1. Create Secret in Kubernetes

```bash
# Create secret from literal value
kubectl create secret generic uw-api-credentials \
  --from-literal=api-token='your_actual_key_here' \
  --namespace=flowmind

# Verify secret exists
kubectl get secrets -n flowmind
kubectl describe secret uw-api-credentials -n flowmind
```

### 2. Update Deployment YAML

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flowmind-backend
  namespace: flowmind
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flowmind-backend
  template:
    metadata:
      labels:
        app: flowmind-backend
    spec:
      containers:
      - name: backend
        image: flowmind-backend:latest
        ports:
        - containerPort: 8000
        env:
        # Unusual Whales API - from secret
        - name: UW_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: uw-api-credentials
              key: api-token
        - name: UW_BASE_URL
          value: "https://api.unusualwhales.com"
        # Redis
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PORT
          value: "6379"
        # Feature flags
        - name: UW_LIVE
          value: "1"  # Enable live data in production
        - name: UW_MIN_PREMIUM
          value: "25000"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### 3. Apply Configuration

```bash
# Apply deployment
kubectl apply -f k8s/backend-deployment.yaml

# Check pod status
kubectl get pods -n flowmind

# Check logs
kubectl logs -f deployment/flowmind-backend -n flowmind

# Should see:
# ✅ "🐋 Unusual Whales: Configured"
```

---

## 🔧 GitHub Actions CI/CD

### Update Workflow to Inject Secret

```yaml
# .github/workflows/deploy.yml
name: Deploy FlowMind

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Backend
        run: |
          cd backend
          docker build -t flowmind-backend .
      
      - name: Deploy to Production
        env:
          UW_API_TOKEN: ${{ secrets.UW_API_SECRET }}
          UW_BASE_URL: https://api.unusualwhales.com
        run: |
          # Inject API key into deployment
          source scripts/inject_uw_api_key.sh
          
          # Deploy (example using docker-compose)
          docker-compose up -d --build
          
          # Verify deployment
          sleep 10
          curl http://localhost:8000/health
```

---

## 🧪 Testing After Deployment

### 1. Backend Health Check

```bash
# Basic health
curl http://your-domain.com/health

# Readiness check
curl http://your-domain.com/readyz

# Should return 200 OK
```

### 2. UW API Integration Test

```bash
# Test flow summary (should be LIVE, not DEMO)
curl http://your-domain.com/api/flow/summary | jq '{mode: .mode, count: (.items | length)}'

# Expected output:
# {
#   "mode": "LIVE",
#   "count": 24
# }

# Test live flow for specific symbol
curl "http://your-domain.com/api/flow/live?symbol=TSLA&minPremium=50000" | jq '.rows | length'

# Should return > 0 rows
```

### 3. Run Integration Tests

```bash
# SSH into server or run locally against deployed backend
export REACT_APP_BACKEND_URL="http://your-domain.com"
export UW_API_TOKEN="your_actual_key"

cd /path/to/flowmind
python uw_correct_endpoints_test.py

# All tests should pass with real data
```

### 4. Check Backend Logs

```bash
# Docker Compose
docker-compose logs backend | grep -i "unusual\|uw\|flow"

# Kubernetes
kubectl logs -f deployment/flowmind-backend -n flowmind | grep -i "unusual\|uw\|flow"

# Should see:
# ✅ "🐋 Unusual Whales: Configured"
# ✅ Flow requests returning data
# ❌ Should NOT see: "404 Not Found", "API token not configured", "using demo mode"
```

---

## 🚨 Troubleshooting

### Issue: "API token not configured"

**Symptom:**
```
Error making request to /api/flow-alerts: API token not configured
Using mock options flow data due to API error
```

**Solution:**
```bash
# Verify env var is set
docker exec flowmind-backend env | grep UW

# Should show:
# UW_API_TOKEN=580...

# If not, restart with correct env:
docker-compose down
docker-compose up -d
```

---

### Issue: "404 Not Found" on UW endpoints

**Symptom:**
```
Client error '404 Not Found' for url 'https://api.unusualwhales.com/api/flow-alerts'
```

**Solution:**
1. Verify you're using the **updated code** (after migration)
2. Check backend logs for old endpoint paths
3. Rebuild Docker images: `docker-compose up -d --build`
4. Verify API key is valid: Test manually with `curl`:

```bash
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.unusualwhales.com/api/flow-alerts?limit=1
```

---

### Issue: Backend returns "mode": "DEMO"

**Symptom:**
```json
{"mode": "DEMO", "items": [...]}
```

**Solution:**
```bash
# 1. Set UW_LIVE=1 in environment
export UW_LIVE=1

# 2. Restart backend
docker-compose restart backend

# 3. Verify in logs
docker-compose logs backend | grep "UW_LIVE\|Unusual Whales"
```

---

### Issue: Rate Limit Exceeded

**Symptom:**
```
Rate limit exceeded
```

**Solution:**
1. Increase `rate_limit_delay` in `unusual_whales_service.py` (currently 1.0s)
2. Implement request batching
3. Use Redis cache more aggressively (increase TTL)
4. Contact UW support for higher rate limits

---

## 📊 Monitoring After Deployment

### Key Metrics to Watch

1. **UW API Success Rate**
   - Should be > 99%
   - Check: `docker logs backend | grep "UW.*error" | wc -l`

2. **Demo Mode Usage**
   - Should be < 1% in production
   - Check: `curl /api/flow/summary | jq '.mode'` → should be "LIVE"

3. **Response Times**
   - Flow endpoints: < 500ms
   - Check: Add timing logs or use Prometheus metrics

4. **Error Rates**
   - 5xx errors: < 0.1%
   - 4xx errors: < 1%

### Setup Alerts (Optional)

```bash
# Example: Alert if demo mode detected in production
while true; do
  MODE=$(curl -s http://localhost:8000/api/flow/summary | jq -r '.mode')
  if [ "$MODE" == "DEMO" ]; then
    echo "⚠️  ALERT: Backend in DEMO mode! Check UW API key."
    # Send notification (email, Slack, etc.)
  fi
  sleep 300  # Check every 5 minutes
done
```

---

## ✅ Deployment Complete Checklist

After deployment, verify:

- [ ] Backend starts without errors
- [ ] `/health` endpoint returns 200
- [ ] UW API key is configured (log message: "🐋 Unusual Whales: Configured")
- [ ] Flow summary returns `"mode": "LIVE"` (not "DEMO")
- [ ] Flow data contains real tickers and premiums
- [ ] No 404 errors on UW endpoints in logs
- [ ] Frontend can fetch flow data
- [ ] Market overview page works
- [ ] Builder page can fetch options chains
- [ ] Portfolio page loads correctly

---

## 📞 Support Contacts

- **UW API Support:** Dan @ Unusual Whales (support@unusualwhales.com)
- **UW API Docs:** https://api.unusualwhales.com/docs
- **FlowMind Repo:** https://github.com/barbudangabriel-gif/Flowmind

---

**Deployment Status:** Ready ✅  
**Last Updated:** October 13, 2025  
**Migration:** UW API hallucinated endpoints → Correct endpoints
