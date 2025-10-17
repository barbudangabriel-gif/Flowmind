# app/routers/flow.py
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

router = APIRouter(prefix="/flow", tags=["flow"])


@router.get("/health")
def flow_health() -> Dict[str, Any]:
    return {"ok": True, "scope": "flow"}


# exemplu endpoint minimal; adaptează după ce ai servicii reale
@router.get("/snapshot/{symbol}")
def flow_snapshot(symbol: str) -> Dict[str, Any]:
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol required")
    # TODO: integrează cu services/tradestation.py când e gata
    return {"symbol": symbol.upper(), "snapshot": "not-implemented-yet"}
