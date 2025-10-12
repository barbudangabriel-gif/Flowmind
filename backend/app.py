from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from time import time
from typing import Dict
from services.scoring import calc_fis

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
        return FISResponse(**cached, timestamp=time())
    try:
        data = calc_fis(symbol)
        resp = {"symbol": data["symbol"], "score": data["score"], "factors": data["factors"]}
        _set_cache(key, resp)
        return FISResponse(**resp, timestamp=time())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FIS error: {str(e)}")

# MCP-style alias (opțional): /analytics/fis?symbol=TSLA
@app.get("/analytics/fis", response_model=FISResponse)
def mcp_fis(symbol: str):
    return get_investment_scoring(symbol)
