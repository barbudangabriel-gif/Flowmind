from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class IVXResponse(BaseModel):
    symbol: str
    window: int
    ivx: float
    rank: float
    ts: datetime
    source: str
    note: str | None = None


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
