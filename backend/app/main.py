# backend/app/main.py

from fastapi import FastAPI
from backend.app.fis_app import app as fis_app  # importă aplicația FIS (cu rutele /investment-scoring și /analytics)

# Creează aplicația principală (fără OpenAPI propriu)
app = FastAPI(
    title="Flowmind API",
    docs_url=None,       # dezactivăm /docs aici
    redoc_url=None,
    openapi_url=None
)

# Montează aplicația FIS ca root (toate rutele și /docs vin din fis_app)
app.mount("/", fis_app)

@app.get("/healthz")
def healthz():
    return {"ok": True}
