from fastapi import APIRouter, Query
from typing import Optional
from services.optimize_engine import suggest

router = APIRouter(prefix="/optimize", tags=["optimize"])


@router.get("/suggest")
def optimize_suggest(
    symbol: str,
    sentiment: str = "bullish",
    target_price: Optional[float] = None,
    budget: Optional[float] = Query(None, description="Max capital (USD)"),
    dte: int = 30,
    risk_bias: int = 0,
):
    return suggest(
        symbol=symbol,
        sentiment=sentiment,
        target_price=target_price,
        budget=budget,
        dte=dte,
        risk_bias=risk_bias,
    )
