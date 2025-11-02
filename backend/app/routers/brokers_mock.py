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
    """Mock TradeStation balances endpoint for UI testing (NO AUTH).
    
    Returns different balance structures based on account type:
    - Futures accounts: FuturesBuyingPower, InitialMargin, MaintenanceMargin, etc.
    - Equity accounts: BuyingPower, MarginUsed, DayTradingBuyingPower, etc.
    """
    log.warning(f"🔓 Using MOCK balances for {account_id} (no auth)")
    
    # Futures account structure
    if "Futures" in account_id or "789012" in account_id:
        return {
            "status": "success",
            "Balances": [
                {
                    # Main metrics
                    "FuturesBuyingPower": 1952.12,
                    "CashBalance": 1952.12,
                    "AccountValue": 1952.12,
                    
                    # Position metrics
                    "FuturesPositions": 0,
                    "RealizedPnL": 0.00,
                    "UnrealizedPnL": 0.00,
                    
                    # Margin metrics
                    "InitialMargin": 0.00,
                    "MaintenanceMargin": 0.00,
                    "OpenOrderInitialMargin": 0.00,
                    
                    # Cash metrics
                    "CashAvailableToWithdraw": 1952.12,
                    "PendingUSDDeposits": 0.00,
                    "SecuritiesOnDeposit": 0.00,
                }
            ],
        }
    
    # Equity account structure (default)
    return {
        "status": "success",
        "Balances": [
            {
                # Portfolio Overview
                "TotalPortfolioValue": 1378294.34,
                "TotalTodayChangePercent": -0.27,
                "TotalTodayChangeAmount": -3799.56,
                
                # Market Value Breakdown
                "StocksMarketValue": 692277.96,
                "CashValue": 488445.38,
                "OptionsMarketValue": 278163.00,
                "FuturesMarketValue": 0.00,
                "ShortOptionsValue": -80592.00,
                
                # Account Summaries
                "StocksOptionsAccountValue": 1376342.22,
                "StocksOptionsTodayPercent": -0.28,
                "StocksOptionsTodayAmount": -3799.56,
                "FuturesAccountValue": 1952.12,
                "FuturesTodayPercent": 0.00,
                "FuturesTodayAmount": 0.00,
                
                # Main cards
                "AccountValue": 1376342.22,
                "StocksBuyingPower": 3427851.14,
                "OptionsBuyingPower": 486493.26,  # Same as cash for options
                "CashBalance": 486493.26,
                "CashAvailableToWithdraw": 692339.17,
                
                # Stocks metrics
                "StocksValue": 692277.96,
                "StocksTodayChange": "+0.05% (+$335.94)",
                "StocksUnrealizedPnL": -37110.80,
                "OvernightBuyingPower": 1384678.34,
                "DayTradingBuyingPower": 3427851.14,
                "DayTradingQualified": True,
                "PatternDayTrader": True,
                
                # Options metrics
                "OptionsValue": 197571.00,
                "OptionsTodayChange": "−2.05% (−$4,135.50)",
                "OptionsUnrealizedPnL": -67086.00,
                "OptionsApprovalLevel": 5,
                
                # Additional info
                "AccountRealizedPnL": 0.00,
                "Equity": 1376342.22,
                "MarketValue": 889848.96,  # Stocks + Options
                "MarginUsed": 15432.10,
                "MaintenanceMargin": 8500.00,
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
                "AccountType": "Equity",  # Standardized: Equity = Margin
                "CashBalance": 75000.00,
                "Currency": "USD",
            },
            {
                "AccountID": "TT456789",
                "Name": "Tastytrade Futures",
                "AccountType": "Futures",
                "CashBalance": 25000.00,
                "Currency": "USD",
            },
            {
                "AccountID": "TT789012",
                "Name": "Tastytrade Crypto",
                "AccountType": "Crypto",
                "CashBalance": 10000.00,
                "Currency": "USD",
            },
        ],
    }


@router.get("/tastytrade/mock/accounts/{account_id}/balances")
async def get_mock_tastytrade_balances(account_id: str):
    """Mock Tastytrade balances endpoint for UI testing (NO AUTH).
    
    Returns different balance structures based on account type.
    """
    log.warning(f"🔓 Using MOCK Tastytrade balances for {account_id} (no auth)")
    
    # Futures account structure
    if "456789" in account_id or "Futures" in account_id:
        return {
            "status": "success",
            "Balances": [
                {
                    # Main metrics
                    "FuturesBuyingPower": 25000.00,
                    "CashBalance": 25000.00,
                    "AccountValue": 25000.00,
                    
                    # Position metrics
                    "FuturesPositions": 2,
                    "RealizedPnL": 1250.00,
                    "UnrealizedPnL": 340.50,
                    
                    # Margin metrics
                    "InitialMargin": 8000.00,
                    "MaintenanceMargin": 6000.00,
                    "OpenOrderInitialMargin": 1500.00,
                    
                    # Cash metrics
                    "CashAvailableToWithdraw": 16000.00,
                    "PendingUSDDeposits": 0.00,
                    "SecuritiesOnDeposit": 0.00,
                }
            ],
        }
    
    # Crypto account structure - Placeholder
    if "789012" in account_id or "Crypto" in account_id:
        return {
            "status": "success",
            "Balances": [
                {
                    "CashBalance": 10000.00,
                    "AccountValue": 12340.50,
                    "BuyingPower": 10000.00,
                    "UnrealizedPnL": 2340.50,
                    "RealizedPnL": 0.00,
                }
            ],
        }
    
    # Equity account structure (default)
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
    """Mock IBKR balances endpoint for UI testing (NO AUTH).
    
    Returns different balance structures based on account type.
    """
    log.warning(f"🔓 Using MOCK IBKR balances for {account_id} (no auth)")
    
    # Futures account structure
    if "7654321" in account_id or "Futures" in account_id:
        return {
            "status": "success",
            "Balances": [
                {
                    # Main metrics
                    "FuturesBuyingPower": 50000.00,
                    "CashBalance": 50000.00,
                    "AccountValue": 50000.00,
                    
                    # Position metrics
                    "FuturesPositions": 0,
                    "RealizedPnL": 0.00,
                    "UnrealizedPnL": 0.00,
                    
                    # Margin metrics
                    "InitialMargin": 0.00,
                    "MaintenanceMargin": 0.00,
                    "OpenOrderInitialMargin": 0.00,
                    
                    # Cash metrics
                    "CashAvailableToWithdraw": 50000.00,
                    "PendingUSDDeposits": 0.00,
                    "SecuritiesOnDeposit": 0.00,
                }
            ],
        }
    
    # Equity account structure (default)
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
