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
        "status": "ACTIVE",
    },
    {
        "id": "2",
        "name": "Income Mindfolio",
        "nav": 89750.25,
        "pnl": 4587.51,
        "pnl_pct": 5.4,
        "status": "ACTIVE",
    },
    {
        "id": "3",
        "name": "Tech Mindfolio",
        "nav": 156890.75,
        "pnl": -2345.67,
        "pnl_pct": -1.5,
        "status": "ACTIVE",
    },
]


@router.get("/mindfolios")
async def get_mindfolios():
    """Get all mindfolios"""
    return {"status": "success", "data": MOCK_MINDFOLIOS}


@router.get("/mindfolios/{mindfolio_id}")
async def get_mindfolio(mindfolio_id: str):
    """Get single mindfolio by ID"""
    mindfolio = next((m for m in MOCK_MINDFOLIOS if m["id"] == mindfolio_id), None)
    if mindfolio:
        # Add mock positions for detail view
        mindfolio_with_positions = {**mindfolio, "positions": []}  # Empty for now
        return {"status": "success", "data": mindfolio_with_positions}
    return {"status": "error", "message": "Mindfolio not found"}
