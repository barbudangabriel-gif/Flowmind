from typing import Any, Dict

from fastapi import APIRouter

from services.builder_engine import price_structure
from services.historical_engine import historical_series
from services.optimize_engine import suggest

router = APIRouter(prefix="/builder", tags=["builder"])


@router.post("/price")
def builder_price(payload: Dict[str, Any]):
    return price_structure(payload)


@router.post("/historical")
def builder_historical(payload: Dict[str, Any]):
    return historical_series(payload)


@router.post("/optimize")
def builder_optimize(payload: Dict[str, Any]):
    """
    Generate strategy recommendations for Optimize tab.
    
    Payload:
        symbol: str - Stock ticker (e.g., "TSLA")
        direction: str - "bullish", "bearish", "neutral", or "volatile"
        target_price: float - Expected price at expiration (optional)
        budget: float - Maximum budget for strategy (optional)
        slider_position: int - 0-10, where 0=max return, 10=max chance (default: 5)
        expiry: str - Expiration date (optional, defaults to nearest expiry)
        dte: int - Days to expiration (optional, calculated from expiry)
    
    Returns:
        meta: Market data and parameters
        strategies: List of recommended strategies with pricing and metrics
    """
    symbol = payload.get("symbol", "TSLA")
    direction = payload.get("direction", "bullish")
    target_price = payload.get("target_price")
    budget = payload.get("budget")
    slider_position = int(payload.get("slider_position", 5))
    dte = payload.get("dte", 30)
    
    # Map slider position (0-10) to risk_bias (-2 to 2)
    # 0 = max return (risk_bias=-2), 5 = balanced (0), 10 = max chance (risk_bias=2)
    risk_bias = int((slider_position - 5) * 0.4)
    
    # Call optimize engine with correct parameters
    result = suggest(
        symbol=symbol,
        sentiment=direction,
        target_price=target_price,
        budget=budget,
        dte=dte,
        risk_bias=risk_bias
    )
    
    return result
