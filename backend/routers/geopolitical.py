"""
FlowMind - Geopolitical & News Intelligence API Endpoints

Provides macro and micro news intelligence with
integration to Investment Scoring and Options strategies
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from geopolitical_news_agent import GeopoliticalNewsAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/geopolitical", tags=["geopolitical"])

# Initialize agent (will be injected with proper dependencies in production)
news_agent = GeopoliticalNewsAgent()


@router.get("/macro")
async def get_macro_news():
    """
    Get global macro events and geopolitical news

    Returns:
    - Fed policy updates
    - Geopolitical events
    - Economic data releases
    - Market sentiment indicators
    """
    try:
        macro_events = await news_agent.get_macro_news()
        return {"status": "success", "data": macro_events}
    except Exception as e:
        logger.error(f"Failed to fetch macro news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker/{symbol}")
async def get_ticker_intelligence(
    symbol: str,
    include_fis: bool = Query(True, description="Include Investment Scoring (FIS)"),
    include_options: bool = Query(
        True, description="Include options strategy suggestions"
    ),
):
    """
    Get comprehensive intelligence for a specific ticker

    Args:
    symbol: Stock ticker (e.g., TSLA, AAPL)
    include_fis: Include FIS fundamental score
    include_options: Include options strategy recommendations

    Returns:
    - News items with timestamps
    - Aggregate sentiment score (-1 to +1)
    - Impact level (0-100)
    - FIS score (if requested)
    - Options strategy suggestions (if requested)
    - Trading recommendation
    """
    try:
        ticker_intel = await news_agent.get_ticker_news_with_sentiment(
            symbol=symbol.upper(),
            include_fis=include_fis,
            include_options=include_options,
        )

        return {"status": "success", "data": ticker_intel}
    except Exception as e:
        logger.error(f"Failed to fetch ticker intelligence for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mindfolio/{mindfolio_id}")
async def get_mindfolio_news_digest(mindfolio_id: str):
    """
    Get aggregated news intelligence for entire mindfolio

    Analyzes all positions and provides:
    - Macro market events
    - Per-ticker news and sentiment
    - Risk alerts for negative news
    - Opportunities for positive momentum
    - Mindfolio-wide sentiment score
    - Executive summary

    Args:
    mindfolio_id: Mindfolio ID

    Returns:
    Complete mindfolio news digest with alerts and opportunities
    """
    try:
        # TODO: Fetch actual positions from mindfolio service
        # For now, use demo positions
        demo_positions = [
            {"symbol": "TSLA", "quantity": 100, "cost_basis": 250},
            {"symbol": "AAPL", "quantity": 50, "cost_basis": 180},
            {"symbol": "NVDA", "quantity": 75, "cost_basis": 450},
            {"symbol": "SPY", "quantity": 200, "cost_basis": 440},
            {"symbol": "MSFT", "quantity": 60, "cost_basis": 380},
        ]

        mindfolio_digest = await news_agent.get_mindfolio_news_digest(
            mindfolio_id=mindfolio_id, positions=demo_positions
        )

        return {"status": "success", "data": mindfolio_digest}
    except Exception as e:
        logger.error(f"Failed to generate mindfolio digest for {mindfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/{mindfolio_id}")
async def get_risk_alerts(
    mindfolio_id: str,
    severity: Optional[str] = Query(
        None, description="Filter by severity: low, medium, high"
    ),
):
    """
    Get active risk alerts based on news sentiment

    Args:
    mindfolio_id: Mindfolio ID
    severity: Optional severity filter

    Returns:
    List of active risk alerts requiring attention
    """
    try:
        # Get full mindfolio digest
        demo_positions = [
            {"symbol": "TSLA", "quantity": 100},
            {"symbol": "AAPL", "quantity": 50},
            {"symbol": "NVDA", "quantity": 75},
        ]

        digest = await news_agent.get_mindfolio_news_digest(
            mindfolio_id=mindfolio_id, positions=demo_positions
        )

        # Extract and filter alerts
        alerts = digest.get("risk_alerts", [])

        if severity:
            alerts = [a for a in alerts if a.get("severity") == severity.lower()]

        return {
            "status": "success",
            "data": {
                "mindfolio_id": mindfolio_id,
                "alerts": alerts,
                "total_alerts": len(alerts),
                "high_severity_count": len(
                    [a for a in alerts if a.get("severity") == "high"]
                ),
                "medium_severity_count": len(
                    [a for a in alerts if a.get("severity") == "medium"]
                ),
            },
        }
    except Exception as e:
        logger.error(f"Failed to fetch alerts for {mindfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/opportunities/{mindfolio_id}")
async def get_trading_opportunities(mindfolio_id: str):
    """
    Get trading opportunities based on positive news momentum

    Args:
    mindfolio_id: Mindfolio ID

    Returns:
    List of bullish opportunities with strategy suggestions
    """
    try:
        demo_positions = [
            {"symbol": "TSLA", "quantity": 100},
            {"symbol": "NVDA", "quantity": 75},
        ]

        digest = await news_agent.get_mindfolio_news_digest(
            mindfolio_id=mindfolio_id, positions=demo_positions
        )

        opportunities = digest.get("opportunities", [])

        return {
            "status": "success",
            "data": {
                "mindfolio_id": mindfolio_id,
                "opportunities": opportunities,
                "total_opportunities": len(opportunities),
            },
        }
    except Exception as e:
        logger.error(f"Failed to fetch opportunities for {mindfolio_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar")
async def get_economic_calendar(
    days_ahead: int = Query(7, description="Number of days to look ahead"),
):
    """
    Get upcoming economic events and earnings calendars

    Args:
    days_ahead: Number of days to include (default 7)

    Returns:
    Upcoming macro events, earnings reports, Fed meetings, etc.
    """
    try:
        # TODO: Integrate with actual economic calendar API
        # For now, return demo calendar
        from datetime import datetime, timedelta

        today = datetime.now()

        calendar_events = [
            {
                "date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "event": "NVDA Earnings After Market",
                "type": "earnings",
                "importance": "high",
                "affected_symbols": ["NVDA"],
            },
            {
                "date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                "event": "Fed Minutes Release",
                "type": "fed_policy",
                "importance": "high",
                "affected_symbols": ["SPY", "QQQ"],
            },
            {
                "date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                "event": "CPI Data Release",
                "type": "economic_data",
                "importance": "high",
                "affected_symbols": ["SPY", "TLT", "GLD"],
            },
        ]

        return {
            "status": "success",
            "data": {
                "events": calendar_events,
                "days_ahead": days_ahead,
                "total_events": len(calendar_events),
            },
        }
    except Exception as e:
        logger.error(f"Failed to fetch economic calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))
