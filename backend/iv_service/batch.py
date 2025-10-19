from fastapi import APIRouter, Query
from typing import List, Optional
import time
from .service import summary, terms, strikes, pick_calendar, pick_condor

router = APIRouter(prefix="/api/iv", tags=["iv"])

@router.get("/health")
async def health():
    return {"ok": True}

@router.get("/summary")
async def get_summary(symbol: str, front_dte: int = 3, back_dte: int = 35):
    return await summary(symbol, front_dte, back_dte)

@router.get("/term")
async def get_term(symbol: str):
    return await terms(symbol)

@router.get("/strikes")
async def get_strikes(symbol: str, front_dte: int, back_dte: int):
    return await strikes(symbol, front_dte, back_dte)

@router.api_route("/batch", methods=["GET", "POST"])
async def batch_endpoint(
    # GET params
    include: str = Query(default="health,summary,condor,calendar"),
    symbol: Optional[str] = Query(default=None),
    limit: int = Query(default=50),
    dteMax: int = Query(default=45),
    ivrMin: int = Query(default=30),
    frontDte: int = Query(default=7),
    backDte: int = Query(default=45),
    ivrMax: int = Query(default=40),
    # POST body (will be None for GET)
    body: Optional[dict] = None,
):
    # Handle POST request
    if body is not None:
        symbols = body.get("symbols", ["NVDA", "AAPL", "MSFT"])[: body.get("limit", 50)]
        rule = body.get("rule", "calendar")
        mult = float(body.get("mult", 0.5))
        return await batch_calc(symbols, rule, mult)

    # Handle GET request - return aggregated results
    started = time.time()
    results = {}
    errors = []

    # Health check
    try:
        results["health"] = {"ok": True}
    except Exception as e:
        errors.append(f"health: {e}")

    # Summary pentru demo symbols
    try:
        demo_symbols = ["NVDA", "AAPL", "MSFT"][:limit]
        batch_rows = []
        ok = fail = 0

        for sym in demo_symbols:
            try:
                s = await summary(sym)
                spot, em_usd = s["spot"], s["em_usd"]
                dc_low, dc_high = pick_calendar(spot, em_usd, 0.5)

                batch_rows.append(
                    {
                        "symbol": s["symbol"],
                        "spot": spot,
                        "iv": s["iv"],
                        "em_usd": em_usd,
                        "em_pct": s["em_pct"],
                        "front_dte": s["front_dte"],
                        "back_dte": s["back_dte"],
                        "dc_low": dc_low,
                        "dc_high": dc_high,
                        "error": None,
                    }
                )
                ok += 1
            except Exception as e:
                batch_rows.append({"symbol": sym, "error": str(e)})
                fail += 1

        results["batch"] = {
            "meta": {"count": len(demo_symbols), "ok": ok, "fail": fail},
            "rows": batch_rows,
        }

    except Exception as e:
        errors.append(f"batch: {e}")

    return {
        "ok": True,
        "tookMs": int((time.time() - started) * 1000),
        "results": results,
        "errors": errors,
    }

async def batch_calc(symbols: List[str], rule: str, mult: float):
    rows = []
    ok = fail = 0
    for sym in symbols:
        try:
            s = await summary(sym)
            spot, em_usd = s["spot"], s["em_usd"]
            row = {
                "symbol": s["symbol"],
                "spot": spot,
                "iv": s["iv"],
                "em_usd": em_usd,
                "em_pct": s["em_pct"],
                "front_dte": s["front_dte"],
                "back_dte": s["back_dte"],
                "error": None,
            }

            if rule == "calendar":
                dc_low, dc_high = pick_calendar(spot, em_usd, mult)
                row.update({"dc_low": dc_low, "dc_high": dc_high})
            else: # condor
                shorts, wings = pick_condor(spot, em_usd)
                row.update({"ic_shorts": shorts, "ic_wings": wings})

            rows.append(row)
            ok += 1
        except Exception as e:
            rows.append(
                {
                    "symbol": sym,
                    "error": str(e),
                    "spot": 0,
                    "iv": 0,
                    "em_usd": 0,
                    "em_pct": 0,
                    "front_dte": 0,
                    "back_dte": 0,
                }
            )
            fail += 1

    return {"meta": {"count": len(symbols), "ok": ok, "fail": fail}, "rows": rows}
