from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from time import time
from typing import Dict, List
from fastapi import Query
from .services.fis_scoring import calc_fis
from backend.app.db.fis_store import store

app = FastAPI(title="Flowmind MCP – Analytics")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# TTL cache simplu 30s
_CACHE: Dict[str, Dict] = {}

class FISResponse(BaseModel):
    symbol: str
    score: int
    factors: Dict[str, int]
    timestamp: float

def _get_cached(key: str):
    item = _CACHE.get(key)
    if not item: return None
    if time() - item["ts"] > 30:  # 30 sec
        _CACHE.pop(key, None); return None
    return item["val"]

def _set_cache(key: str, val: Dict):
    _CACHE[key] = {"val": val, "ts": time()}

@app.get("/investment-scoring/advanced/{symbol}", response_model=FISResponse)
def get_investment_scoring(symbol: str):
    key = f"fis:{symbol.upper()}"
    cached = _get_cached(key)
    if cached:
        resp = {**cached, "timestamp": time()}
        store.save(resp)  # persistă scorul la fiecare request
        return FISResponse(**resp)
    try:
        data = calc_fis(symbol)
        resp = {**data, "timestamp": time()}
        _set_cache(key, data)
        store.save(resp)  # persistă scorul la fiecare request
        return FISResponse(**resp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/fis/history/{symbol}")
def get_fis_history(symbol: str, days: int = Query(30, ge=1, le=365)) -> List[Dict]:
    """Istoric scoruri FIS pentru ultimele N zile (implicit 30)."""
    return store.history(symbol, days=days)
