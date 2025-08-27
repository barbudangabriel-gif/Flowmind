import os
import time
import math
import asyncio
import json
import urllib.request
from typing import Any, Dict, List, Tuple, Optional
from fastapi import APIRouter, Query, Body

router = APIRouter(prefix="/api/iv", tags=["iv-batch"])

# --- Config ---
SEM_LIMIT = int(os.getenv("IV_BATCH_CONCURRENCY", "5"))
TTL_SECONDS = int(os.getenv("IV_BATCH_TTL", "300"))
DEFAULT_BASE_IV = float(os.getenv("IV_BASE", "0.25"))
TS_STUB_ON = os.getenv("TS_STUB", "0") == "1"
WATCHLIST_URL = os.getenv("WATCHLIST_URL", "http://localhost:8080")

# --- Cache simplu (symbol -> (exp_ts, row)) ---
_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _now() -> float:
    return time.time()


def _norm_rule(x):
    return str(x or "calendar").strip().lower()


def _from_cache(symbol: str) -> Optional[Dict[str, Any]]:
    item = _CACHE.get(symbol)
    if not item:
        return None
    exp, row = item
    if exp < _now():
        _CACHE.pop(symbol, None)
        return None
    return row


def _to_cache(symbol: str, row: Dict[str, Any]) -> None:
    _CACHE[symbol] = (_now() + TTL_SECONDS, row)


def _expected_move_pct(iv: float, dte: int) -> float:
    T = max(0.0, int(dte)) / 365.0
    return max(0.0, float(iv)) * math.sqrt(T)


async def _get_spot(symbol: str) -> Optional[float]:
    # STUB determinist; pe integrarea reală înlocuiești cu TS client
    if TS_STUB_ON:
        return 182.0
    return None  # semnal că nu avem integrare reală încă


async def _get_chain(symbol: str) -> List[Dict[str, Any]]:
    if TS_STUB_ON:
        return [{"dte": 3}, {"dte": 31}]
    return []


def _choose_front_back(
    exps: List[Dict[str, Any]], front_hint: Optional[int], back_hint: Optional[int]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not exps:
        return {}, {}
    exps_sorted = sorted(exps, key=lambda e: e.get("dte", 0))
    if front_hint is not None:
        front = min(exps_sorted, key=lambda e: abs(e.get("dte", 0) - int(front_hint)))
    else:
        front = next((e for e in exps_sorted if e.get("dte", 0) >= 2), exps_sorted[0])
    back_target = int(back_hint) if back_hint is not None else 31
    back = min(exps_sorted, key=lambda e: abs(e.get("dte", 0) - back_target))
    return front, back


async def _row_for_symbol(
    symbol: str,
    rule: str,
    mult: float,
    front_dte: Optional[int],
    back_dte: Optional[int],
    no_cache: bool = False,
) -> Dict[str, Any]:
    symbol = str(symbol).upper().strip()
    rule = _norm_rule(rule)
    if not symbol:
        return {"symbol": symbol, "error": "empty_symbol"}

    if not no_cache:
        cached = _from_cache(symbol)
        if cached:
            return cached

    spot = await _get_spot(symbol)
    if spot is None:
        row = {"symbol": symbol, "rule": rule, "error": "no_ts_or_stub_off"}
        _to_cache(symbol, row)
        return row

    chain = await _get_chain(symbol)
    if not isinstance(chain, list) or not chain:
        chain = [{"dte": 3}, {"dte": 31}]

    front, back = _choose_front_back(chain, front_dte, back_dte)
    fd, bd = int(front.get("dte", 0) or 0), int(back.get("dte", 0) or 0)

    em_pct = _expected_move_pct(DEFAULT_BASE_IV, fd)
    em_usd = spot * em_pct

    dc_low = round(spot - (mult or 0.5) * em_usd)
    dc_high = round(spot + (mult or 0.5) * em_usd)

    row: Dict[str, Any] = {
        "symbol": symbol,
        "rule": rule,
        "spot": float(spot),
        "front_dte": fd,
        "back_dte": bd,
        "em_pct": float(em_pct),
        "em_usd": float(em_usd),
        "dc_low": float(dc_low),
        "dc_high": float(dc_high),
        "error": None,
    }

    if rule == "condor":
        shorts_low = round(spot - 1.0 * em_usd)
        shorts_high = round(spot + 1.0 * em_usd)
        wings_low = round(spot - 1.5 * em_usd)
        wings_high = round(spot + 1.5 * em_usd)
        row["ic_shorts"] = [float(shorts_low), float(shorts_high)]
        row["ic_wings"] = [float(wings_low), float(wings_high)]

    _to_cache(symbol, row)
    return row


async def _run_batch(
    symbols: List[str],
    rule: str,
    mult: float,
    front_dte: Optional[int],
    back_dte: Optional[int],
    no_cache: bool = False,
) -> Dict[str, Any]:
    sem = asyncio.Semaphore(SEM_LIMIT)

    async def _wrapped(sym):
        async with sem:
            return await _row_for_symbol(
                sym, rule, mult, front_dte, back_dte, no_cache=no_cache
            )

    rows = await asyncio.gather(*[_wrapped(s) for s in symbols])
    ok = sum(1 for r in rows if not r.get("error"))
    fail = len(rows) - ok
    return {"meta": {"count": len(rows), "ok": ok, "fail": fail}, "rows": rows}


@router.get("/batch")
async def iv_batch_get(
    watchlist: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    rule: str = Query("calendar"),
    mult: float = Query(0.5),
    front_dte: Optional[int] = Query(None, ge=0),
    back_dte: Optional[int] = Query(None, ge=0),
    no_cache: int = Query(0),
):
    rule = _norm_rule(rule)
    symbols: List[str] = []
    # încearcă să citești watchlist din backend; dacă pică, folosește fallback stabil
    try:
        url = f"{WATCHLIST_URL}/api/watchlists/{watchlist}"
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            lst = data.get("symbols") or []
            symbols = [str(s).upper() for s in lst][offset : offset + limit]
    except Exception as e:
        symbols = ["NVDA", "AAPL", "MSFT", "TSLA", "AMD"][offset : offset + limit]
        batch = await _run_batch(
            symbols, rule, mult, front_dte, back_dte, no_cache=bool(no_cache)
        )
        batch["meta"].update(
            {"watchlist": watchlist, "warning": f"watchlist_fetch_failed:{e}"}
        )
        return batch

    batch = await _run_batch(
        symbols, rule, mult, front_dte, back_dte, no_cache=bool(no_cache)
    )
    batch["meta"]["watchlist"] = watchlist
    return batch


@router.post("/batch")
async def iv_batch_post(payload: Dict[str, Any] = Body(...)):
    symbols = payload.get("symbols") or []
    rule = _norm_rule(payload.get("rule"))
    mult = float(payload.get("mult") or (1.0 if rule == "condor" else 0.5))
    front_dte = payload.get("front_dte")
    back_dte = payload.get("back_dte")
    no_cache = bool(payload.get("no_cache") or False)
    if not symbols or not isinstance(symbols, list):
        return {
            "meta": {"count": 0, "ok": 0, "fail": 0},
            "rows": [],
            "error": "symbols_required",
        }
    return await _run_batch(
        [str(s).upper() for s in symbols],
        rule,
        mult,
        front_dte,
        back_dte,
        no_cache=no_cache,
    )
