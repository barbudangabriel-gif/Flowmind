"""Mock broker endpoints for UI testing (NO AUTH REQUIRED).

IMPORTANT: These endpoints are for frontend development only!
They bypass authentication and return fake data.
REMOVE OR DISABLE IN PRODUCTION!

ACCOUNT TYPE MAPPING (Unified Model):
====================================
1. EQUITY (Stock Options Trading)
   - TradeStation: "Margin" account
   - Tastytrade: "Margin" account
   - All equity accounts are margin-enabled for options

2. FUTURES (Futures & Futures Options)
   - TradeStation: "Futures" account
   - Tastytrade: "Futures" account
   - Separate account required for futures trading

3. CRYPTO (Cryptocurrency Trading)
   - TradeStation: NOT SUPPORTED
   - Tastytrade: "Crypto" account
   - Digital assets only
"""

import logging

from fastapi import APIRouter

log = logging.getLogger("brokers.mock")
router = APIRouter(tags=["Brokers Mock (DEV ONLY)"])


@router.get("/tradestation/mock/accounts")
async def get_mock_ts_accounts():
    """Mock TradeStation accounts endpoint for UI testing (NO AUTH).
    
    Returns accounts with standardized AccountType:
    - "Equity" → Maps to Margin account (stock + options)
    - "Futures" → Futures trading account
    
    Note: TradeStation does NOT support crypto trading.
    """
    log.warning("🔓 Using MOCK TradeStation accounts (no auth)")
    return {
        "status": "success",
        "Accounts": [
            {
                "AccountID": "SIM123456",
                "Name": "TradeStation Equity SIM",
                "AccountType": "Equity",  # Standardized: Equity = Margin account
                "CashBalance": 50000.00,
                "Currency": "USD",
            },
            {
                "AccountID": "SIM789012",
                "Name": "TradeStation Futures SIM",
                "AccountType": "Futures",  # Standardized: Futures account
                "CashBalance": 25000.00,
                "Currency": "USD",
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


@router.get("/ibkr/mock/accounts")
async def get_mock_ibkr_accounts():
    """Mock Interactive Brokers accounts endpoint for UI testing (NO AUTH).
    
    Returns accounts with standardized AccountType:
    - "Equity" → Maps to Margin account (stock + options)
    - "Futures" → Futures trading account
    
    Note: IBKR does NOT support crypto trading directly.
    """
    log.warning("🔓 Using MOCK IBKR accounts (no auth)")
    return {
        "status": "success",
        "Accounts": [
            {
                "AccountID": "U1234567",
                "Name": "IBKR Individual Margin",
                "AccountType": "Equity",  # Standardized: Equity = Margin account
                "CashBalance": 100000.00,
                "Currency": "USD",
            },
            {
                "AccountID": "U7654321",
                "Name": "IBKR Futures Account",
                "AccountType": "Futures",  # Standardized: Futures account
                "CashBalance": 50000.00,
                "Currency": "USD",
            },
        ],
    }


@router.get("/ibkr/mock/accounts/{account_id}/balances")
async def get_mock_ibkr_balances(account_id: str):
    """Mock IBKR balances endpoint for UI testing (NO AUTH)."""
    log.warning(f"🔓 Using MOCK IBKR balances for {account_id} (no auth)")
    return {
        "status": "success",
        "Balances": [
            {
                "CashBalance": 100000.00,
                "BuyingPower": 400000.00,  # IBKR typically has 4:1 margin
                "Equity": 125500.75,
                "MarketValue": 125500.75,
                "MarginUsed": 25500.75,
                "MaintenanceMargin": 12750.38,
                "OptionBuyingPower": 100000.00,
                "AccountValue": 125500.75,
            }
        ],
    }
