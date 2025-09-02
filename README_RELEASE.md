# Release PR (Security + CI + Observability + K8s)

## Branch & PR
```bash
git checkout -b release/hardening
# copy files from this bundle into repo root, then:
git add .github backend k8s Dockerfile requirements*.txt .pre-commit-config.yaml
git commit -m "release: security hardening, CI, observability, k8s, docker"
git push -u origin release/hardening
# Open PR to main and require green checks
```

## Wire in FastAPI (`backend/main.py`)
Add (or adapt) the following:
```python
from fastapi import FastAPI
from backend.config import get_settings
from backend.observability import wire, setup_cors, setup_rate_limit

app = FastAPI()
wire(app)
s = get_settings()
setup_cors(app, s.allowed_origins)
setup_rate_limit(app, s.rate_limit)
```

## Kubernetes
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.example.yaml   # replace with real Secret or external secrets
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/prometheus-rules.yaml
```

## CI
- Runs: lint/format/type-check, tests, SBOM, grype, gitleaks, docker build.
- Pre-commit blocks TODO fără ticket, commit în `main`, și patterns de secrete.

## Notes
- `APP_MODE=prod` impune prezența secretelor la pornire.
- Replace `app.example.com` CORS origin în `k8s/configmap.yaml`.
- Consider canary rollout la 10% → 50% → 100% cu guard pe 5xx<1%, p95<500ms.
