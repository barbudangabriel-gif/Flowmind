from typing import Any, Dict, List

from fastapi import APIRouter

from services.builder_engine import price_structure
from services.historical_engine import historical_series
from services.optimize_engine import suggest

router = APIRouter(prefix="/builder", tags=["builder"])


# Available strategies (54 total as per FlowMind documentation)
AVAILABLE_STRATEGIES = [
    # Single Leg Strategies
    {"id": "long-call", "name": "Long Call", "legs": 1, "category": "directional", "complexity": "basic"},
    {"id": "long-put", "name": "Long Put", "legs": 1, "category": "directional", "complexity": "basic"},
    {"id": "short-call", "name": "Short Call (Covered)", "legs": 1, "category": "income", "complexity": "basic"},
    {"id": "short-put", "name": "Short Put (Cash Secured)", "legs": 1, "category": "income", "complexity": "basic"},
    
    # Vertical Spreads
    {"id": "bull-call-spread", "name": "Bull Call Spread", "legs": 2, "category": "directional", "complexity": "intermediate"},
    {"id": "bear-call-spread", "name": "Bear Call Spread", "legs": 2, "category": "income", "complexity": "intermediate"},
    {"id": "bull-put-spread", "name": "Bull Put Spread", "legs": 2, "category": "income", "complexity": "intermediate"},
    {"id": "bear-put-spread", "name": "Bear Put Spread", "legs": 2, "category": "directional", "complexity": "intermediate"},
    
    # Income Strategies
    {"id": "iron-condor", "name": "Iron Condor", "legs": 4, "category": "neutral", "complexity": "advanced"},
    {"id": "iron-butterfly", "name": "Iron Butterfly", "legs": 4, "category": "neutral", "complexity": "advanced"},
    {"id": "short-strangle", "name": "Short Strangle", "legs": 2, "category": "neutral", "complexity": "intermediate"},
    {"id": "short-straddle", "name": "Short Straddle", "legs": 2, "category": "neutral", "complexity": "intermediate"},
    
    # Volatility Strategies
    {"id": "long-straddle", "name": "Long Straddle", "legs": 2, "category": "volatility", "complexity": "intermediate"},
    {"id": "long-strangle", "name": "Long Strangle", "legs": 2, "category": "volatility", "complexity": "intermediate"},
    {"id": "butterfly", "name": "Long Butterfly", "legs": 3, "category": "neutral", "complexity": "advanced"},
    {"id": "call-butterfly", "name": "Call Butterfly", "legs": 3, "category": "neutral", "complexity": "advanced"},
    {"id": "put-butterfly", "name": "Put Butterfly", "legs": 3, "category": "neutral", "complexity": "advanced"},
    
    # Advanced Spreads
    {"id": "calendar-spread", "name": "Calendar Spread", "legs": 2, "category": "advanced", "complexity": "advanced"},
    {"id": "diagonal-spread", "name": "Diagonal Spread", "legs": 2, "category": "advanced", "complexity": "advanced"},
    {"id": "ratio-spread", "name": "Ratio Spread", "legs": 2, "category": "advanced", "complexity": "advanced"},
]


@router.get("/strategies")
def list_strategies(
    category: str = None,
    complexity: str = None
) -> Dict[str, Any]:
    """
    Get list of available options strategies
    
    Query params:
        category: Filter by category (directional, income, neutral, volatility, advanced)
        complexity: Filter by complexity (basic, intermediate, advanced)
    
    Returns:
        strategies: List of strategy objects
        count: Total number of strategies
        categories: Available categories
        complexities: Available complexity levels
    """
    strategies = AVAILABLE_STRATEGIES
    
    # Apply filters
    if category:
        strategies = [s for s in strategies if s["category"] == category]
    if complexity:
        strategies = [s for s in strategies if s["complexity"] == complexity]
    
    return {
        "strategies": strategies,
        "count": len(strategies),
        "categories": ["directional", "income", "neutral", "volatility", "advanced"],
        "complexities": ["basic", "intermediate", "advanced"],
        "total_available": len(AVAILABLE_STRATEGIES)
    }


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
