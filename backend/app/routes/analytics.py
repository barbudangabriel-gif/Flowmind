# --- Imports and router ---
import time
import asyncio
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime, date
import re
from ..services.gex_cache import gex_cache

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# --- GEX summary response models ---
SYMBOL_RE = re.compile(r"^[A-Z0-9\.\-]{1,10}$")
DATE_FMT = "%Y-%m-%d"

class GEXSummaryItem(BaseModel):
    expiry: str
    dte: Optional[int] = None
    netGex: float = Field(..., description="USD Gamma (semn schimbat de dealer_sign)")
    walls: Optional[dict] = None
    status: Optional[Literal["OK", "NO_DATA"]] = None

class GEXSummaryResponse(BaseModel):
    symbol: str
    asOf: str
    items: List[GEXSummaryItem]
    units: Literal["USD Gamma", "normalized", "raw"] = "USD Gamma"
    meta: dict = {}

def _gexsum_cache_key(symbol, expiries, dealer, normalize):
    return f"gexsum:{symbol}:{dealer}:{normalize}:{','.join(expiries)}"

def _parse_expiries(expiries_str: str) -> List[str]:
    parts = [p.strip() for p in expiries_str.split(",") if p.strip()]
    if not parts:
        raise HTTPException(status_code=422, detail="`expiries` is required and cannot be empty")
    seen = set()
    out: List[str] = []
    for e in parts:
        try:
            datetime.strptime(e, DATE_FMT)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid expiry date: {e} (YYYY-MM-DD expected)")
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out

# --- GEX summary endpoint with cache ---
@router.get("/gex/summary", response_model=GEXSummaryResponse, summary="Gamma Exposure summary (mock, cached)")
async def gex_summary_cached(
    symbol: str = Query(..., description="ticker, e.g. TSLA"),
    expiries: str = Query(..., description="Comma-separated expiries, e.g. 2025-11-01,2025-11-08"),
    range: Optional[str] = Query(None),
    source: Optional[str] = Query("real"),
    dealer_sign: Literal["mm_short", "mm_long"] = Query("mm_short"),
    normalize: Optional[str] = Query("none"),
):
    s = symbol.upper().strip()
    if not SYMBOL_RE.fullmatch(s):
        raise HTTPException(status_code=422, detail="Invalid symbol")
    expiry_list = _parse_expiries(expiries)
    key = _gexsum_cache_key(s, expiry_list, dealer_sign, normalize)
    cached = gex_cache.get(key)
    meta = {"cache": False, "miss": False, "hits": 0, "p95_ms": None}
    if cached:
        meta["cache"] = True
        meta["hits"] = 1
        return GEXSummaryResponse(**cached)
    entry = gex_cache.get_entry(key)
    if entry and entry.inflight:
        for _ in range(20):
            await asyncio.sleep(0.01)
            cached2 = gex_cache.get(key)
            if cached2:
                meta["cache"] = True
                meta["hits"] = 1
                return GEXSummaryResponse(**cached2)
        if entry.is_valid(time.time(), grace=30):
            return GEXSummaryResponse(**entry.value)
    if not entry:
        from ..services.gex_cache import CacheEntry
        gex_cache._cache[key] = CacheEntry(None, time.time(), gex_cache.ttl)
    gex_cache._cache[key].inflight = True
    t0 = time.time()
    try:
        from ..services.analytics_service import get_gex_summary
        items = get_gex_summary(s, expiry_list, range=range, source=source)
        sign = 1.0 if dealer_sign == "mm_short" else -1.0
        for it in items:
            try:
                it["netGex"] = sign * float(it["netGex"])
            except Exception:
                pass
            it["source"] = source
        resp = dict(
            symbol=s,
            asOf=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            items=items,
            units="USD Gamma",
            meta=meta,
        )
        gex_cache.set(key, resp)
        meta["miss"] = True
        meta["p95_ms"] = int((time.time()-t0)*1000)
        return GEXSummaryResponse(**resp)
    except Exception as e:
        meta["error"] = str(e)
        from ..services.analytics_service import get_gex_summary
        items = get_gex_summary(s, expiry_list, range=range, source="mock")
        for it in items:
            it["source"] = "mock"
        resp = dict(
            symbol=s,
            asOf=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            items=items,
            units="USD Gamma",
            meta=meta,
        )
        return GEXSummaryResponse(**resp)
    finally:
        gex_cache._cache[key].inflight = False
# Imports
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime, date
import re

# Router instance
router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# --- GEX summary response models ---
SYMBOL_RE = re.compile(r"^[A-Z0-9\.\-]{1,10}$")
DATE_FMT = "%Y-%m-%d"

class GEXSummaryItem(BaseModel):
    expiry: str
    dte: Optional[int] = None
    netGex: float = Field(..., description="USD Gamma (semn schimbat de dealer_sign)")
    walls: Optional[dict] = None
    status: Optional[Literal["OK", "NO_DATA"]] = None

class GEXSummaryResponse(BaseModel):
    symbol: str
    asOf: str
    items: List[GEXSummaryItem]
    units: Literal["USD Gamma", "normalized", "raw"] = "USD Gamma"
    meta: dict = {}

def _parse_expiries(expiries_str: str) -> List[str]:
    parts = [p.strip() for p in expiries_str.split(",") if p.strip()]
    if not parts:
        raise HTTPException(status_code=422, detail="`expiries` is required and cannot be empty")
    seen = set()
    out: List[str] = []
    for e in parts:
        try:
            datetime.strptime(e, DATE_FMT)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid expiry date: {e} (YYYY-MM-DD expected)")
        if e not in seen:
            seen.add(e)
            out.append(e)
    return out

@router.get("/gex/summary", response_model=GEXSummaryResponse, summary="Gamma Exposure summary (mock)")
def gex_summary(
    symbol: str = Query(..., description="ticker, e.g. TSLA"),
    expiries: str = Query(..., description="Comma-separated expiries, e.g. 2025-11-01,2025-11-08"),
    range: Optional[str] = Query(None),
    source: Optional[str] = Query("mock"),
    dealer_sign: Literal["mm_short", "mm_long"] = Query("mm_short"),
):
    s = symbol.upper().strip()
    if not SYMBOL_RE.fullmatch(s):
        raise HTTPException(status_code=422, detail="Invalid symbol")

    expiry_list = _parse_expiries(expiries)
    from ..services.analytics_service import get_gex_summary
    items = get_gex_summary(s, expiry_list, range=range, source=source)
    sign = 1.0 if dealer_sign == "mm_short" else -1.0
    for it in items:
        try:
            it["netGex"] = sign * float(it["netGex"])
        except Exception:
            pass
    return GEXSummaryResponse(
        symbol=s,
        asOf=datetime.utcnow().isoformat() + "Z",
        items=[GEXSummaryItem(**it) for it in items],
        units="USD Gamma",
        meta={"dealerSign": dealer_sign, "range": range, "source": source},
    )


class IVXResponse(BaseModel):
    symbol: str
    window: int
    ivx: float
    rank: float
    ts: datetime
    source: str
    note: Optional[str] = None


# GEX response model
class GEXResponse(BaseModel):
    symbol: str = Field(..., pattern=r'^[A-Z0-9\.]{1,10}$')
    gex: float
    unit: Literal["USD"]
    flip_level: Optional[float] = None
    ts: datetime
    source: str = "mock"
    note: Optional[str] = None

@router.get("/ivx", response_model=IVXResponse, summary="IV Index (mock)")
def ivx(
    symbol: str = Query(..., min_length=1, max_length=10),
    window: int = Query(30, ge=7, le=180),
):
    sym = symbol.upper().strip()
    if not sym.isalnum():
        raise HTTPException(status_code=400, detail="Ticker invalid")

    # importul îl facem aici ca să evităm importuri circulare în timpul încărcării modulului
    from ..services.analytics_service import get_ivx
    return get_ivx(sym, window)


# GEX endpoint
@router.get("/gex", response_model=GEXResponse, summary="Gamma Exposure (mock)")
def gex(symbol: str = Query(..., description="Ticker, e.g. SPY/TSLA/QQQ")):
    s = symbol.upper().strip()
    if not re.fullmatch(r"[A-Z0-9\.]{1,10}", s):
        raise HTTPException(status_code=422, detail="Invalid symbol")
    from ..services.analytics_service import get_gex
    data = get_gex(s)
    return GEXResponse(**data)
