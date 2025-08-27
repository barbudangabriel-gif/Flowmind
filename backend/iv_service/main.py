import logging
from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import BaseModel

app = FastAPI(title="FlowMind IV/EM Service", version="0.1.0")


# --- HEALTH + ROUTES DEBUG (ca să nu mai bâjbâim) ---
@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}


@app.get("/_routes", include_in_schema=False)
def _routes():
    return sorted([r.path for r in app.router.routes if isinstance(r, APIRoute)])


# --- IMPORTURI EXISTENTE (summary/strikes/term) ---
from .ts_client import TSClient

ts_client = TSClient()


class StrikesRequest(BaseModel):
    symbol: str
    rule: str
    mult: float


@app.get("/api/iv/summary")
async def summary(symbol: str = "NVDA"):
    spot = await ts_client.get_spot(symbol)
    return {"symbol": symbol, "spot": spot, "iv": 0.25}


@app.get("/api/iv/term")
async def term(symbol: str = "NVDA"):
    return {"symbol": symbol, "term": [{"dte": 7, "iv": 0.3}, {"dte": 30, "iv": 0.25}]}


@app.post("/api/iv/strikes")
async def strikes(req: StrikesRequest):
    spot = await ts_client.get_spot(req.symbol)
    k_low = int(spot * 0.95)
    k_high = int(spot * 1.05)
    return {
        "front": {"dte": 3, "strikes": [k_low, k_high]},
        "back": {"dte": 35, "strikes": [k_low, k_high]},
    }


# --- MONTEAZĂ BATCH ROUTER ---
try:
    from .batch import router as iv_batch_router

    app.include_router(iv_batch_router)
    logging.warning("Mounted iv_batch_router OK")
except Exception as e:
    logging.exception("Failed to mount iv_batch_router: %s", e)
