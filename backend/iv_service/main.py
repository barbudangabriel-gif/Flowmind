from fastapi import FastAPI
from fastapi.routing import APIRoute
from .ts_client import summary, terms, strikes_calc, pick_calendar, pick_condor

app = FastAPI(title="FlowMind IV Service", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/_routes")
def _routes():
    return sorted([r.path for r in app.router.routes if isinstance(r, APIRoute)])

@app.get("/api/iv/summary")
async def get_summary(symbol: str = "NVDA", front_dte: int = 3, back_dte: int = 35):
    return await summary(symbol, front_dte, back_dte)

@app.get("/api/iv/term")
async def get_term(symbol: str = "NVDA"):
    return await terms(symbol)

@app.get("/api/iv/strikes")
async def get_strikes(symbol: str = "NVDA", front_dte: int = 3, back_dte: int = 35):
    return await strikes_calc(symbol, front_dte, back_dte)

@app.post("/api/iv/batch")
async def post_batch(body: dict):
    symbols = body.get("symbols", ["NVDA", "AAPL", "MSFT"])[:5] # limit 5 pentru demo
    rule = body.get("rule", "calendar")
    mult = float(body.get("mult", 0.5))

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
