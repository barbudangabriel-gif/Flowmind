"""Mock broker endpoints for UI testing (NO AUTH REQUIRED).

IMPORTANT: These endpoints are for frontend development only!
They bypass authentication and return fake data.
REMOVE OR DISABLE IN PRODUCTION!
"""

import logging

from fastapi import APIRouter

log = logging.getLogger("brokers.mock")
router = APIRouter(tags=["Brokers Mock (DEV ONLY)"])


@router.get("/tradestation/mock/accounts")
async def get_mock_ts_accounts():
    """Mock TradeStation accounts endpoint for UI testing (NO AUTH)."""
    log.warning("🔓 Using MOCK TradeStation accounts (no auth)")
    return {
        "status": "success",
        "Accounts": [
            {
                "AccountID": "SIM123456",
                "Name": "TradeStation Equity SIM",
                "AccountType": "Margin",
                "CashBalance": 50000.00,
            },
            {
                "AccountID": "SIM789012",
                "Name": "TradeStation Futures SIM",
                "AccountType": "Futures",
                "CashBalance": 25000.00,
            },
        ],
    }


@router.get("/tradestation/mock/accounts/{account_id}/balances")
async def get_mock_ts_balances(account_id: str):
    """Mock TradeStation balances endpoint for UI testing (NO AUTH)."""
    log.warning(f"🔓 Using MOCK balances for {account_id} (no auth)")
    return {
        "status": "success",
        "Balances": [
            {
                "CashBalance": 50000.00,
                "BuyingPower": 200000.00,
                "Equity": 65432.10,
                "MarketValue": 65432.10,
                "MarginUsed": 15432.10,
                "MaintenanceMargin": 8500.00,
                "DayTradingBuyingPower": 100000.00,
                "AccountValue": 65432.10,
            }
        ],
    }


@router.get("/tastytrade/mock/accounts")
async def get_mock_tastytrade_accounts():
    """Mock Tastytrade accounts endpoint for UI testing (NO AUTH)."""
    log.warning("🔓 Using MOCK Tastytrade accounts (no auth)")
    return {
        "status": "success",
        "Accounts": [
            {
                "AccountID": "TT123456",
                "Name": "Tastytrade Individual",
                "AccountType": "Margin",
                "CashBalance": 75000.00,
            },
            {
                "AccountID": "TT789012",
                "Name": "Tastytrade Crypto",
                "AccountType": "Crypto",
                "CashBalance": 10000.00,
            },
        ],
    }


@router.get("/tastytrade/mock/accounts/{account_id}/balances")
async def get_mock_tastytrade_balances(account_id: str):
    """Mock Tastytrade balances endpoint for UI testing (NO AUTH)."""
    log.warning(f"🔓 Using MOCK Tastytrade balances for {account_id} (no auth)")
    return {
        "status": "success",
        "Balances": [
            {
                "CashBalance": 75000.00,
                "BuyingPower": 150000.00,
                "Equity": 82340.50,
                "MarketValue": 82340.50,
                "MarginUsed": 7340.50,
                "MaintenanceMargin": 4200.00,
                "OptionBuyingPower": 75000.00,
                "AccountValue": 82340.50,
            }
        ],
    }
