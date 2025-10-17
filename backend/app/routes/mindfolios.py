from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["mindfolios"])

# Mock data for mindfolios
MOCK_MINDFOLIOS = [
    {
        "id": "1",
        "name": "Growth Mindfolio",
        "nav": 125430.50,
        "pnl": 12543.05,
        "pnl_pct": 11.1,
        "status": "ACTIVE"
    },
    {
        "id": "2",
        "name": "Income Mindfolio",
        "nav": 89750.25,
        "pnl": 4587.51,
        "pnl_pct": 5.4,
        "status": "ACTIVE"
    },
    {
        "id": "3",
        "name": "Tech Mindfolio",
        "nav": 156890.75,
        "pnl": -2345.67,
        "pnl_pct": -1.5,
        "status": "ACTIVE"
    }
]

@router.get("/mindfolios")
async def get_mindfolios():
    """Get all mindfolios"""
    return {
        "status": "success",
        "data": MOCK_MINDFOLIOS
    }

@router.get("/portfolios")
async def get_portfolios():
    """Get all portfolios (legacy endpoint, same as mindfolios)"""
    return {
        "status": "success",
        "data": MOCK_MINDFOLIOS
    }

@router.get("/mindfolios/{mindfolio_id}")
async def get_mindfolio(mindfolio_id: str):
    """Get single mindfolio by ID"""
    mindfolio = next((m for m in MOCK_MINDFOLIOS if m["id"] == mindfolio_id), None)
    if mindfolio:
        return {
            "status": "success",
            "data": mindfolio
        }
    return {
        "status": "error",
        "message": "Mindfolio not found"
    }

@router.get("/portfolios/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """Get single portfolio by ID (legacy endpoint)"""
    portfolio = next((p for p in MOCK_MINDFOLIOS if p["id"] == portfolio_id), None)
    if portfolio:
        # Add mock positions for detail view
        portfolio_with_positions = {
            **portfolio,
            "positions": []  # Empty for now
        }
        return {
            "status": "success",
            "data": portfolio_with_positions
        }
    return {
        "status": "error",
        "message": "Portfolio not found"
    }
