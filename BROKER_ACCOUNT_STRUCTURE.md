# Broker Account Structure - FlowMind
**Date:** November 2, 2025  
**Status:** ✅ Complete unified model

---

## 🎯 Unified Account Type Model

FlowMind uses a **standardized account type system** across all brokers:

### Account Types (3 total)

| Type | Description | Brokers | Purpose |
|------|-------------|---------|---------|
| **Equity** | Stock + Options trading (Margin) | TS, TT, IBKR | Options strategies, stocks |
| **Futures** | Futures + Futures Options | TS, TT, IBKR | Futures contracts |
| **Crypto** | Cryptocurrency trading | TT only | Digital assets |

---

## 🏦 Broker Configurations

### 1. TradeStation (TS)
```javascript
{
  broker: "TradeStation",
  accountTypes: ["Equity", "Futures"],
  environments: ["SIM", "LIVE"],
  accounts: [
    {
      id: "SIM123456",
      type: "Equity",        // Margin account for stock options
      balance: 50000.00
    },
    {
      id: "SIM789012",
      type: "Futures",       // Futures trading
      balance: 25000.00
    }
  ]
}
```

**Key Points:**
- ✅ Equity = Margin account (options enabled)
- ✅ Futures = Separate futures account
- ❌ NO crypto support

---

### 2. Tastytrade (TT)
```javascript
{
  broker: "Tastytrade",
  accountTypes: ["Equity", "Futures", "Crypto"],
  environments: ["SIM", "LIVE"],
  accounts: [
    {
      id: "TT123456",
      type: "Equity",        // Margin account for stock options
      balance: 75000.00
    },
    {
      id: "TT789012",
      type: "Crypto",        // Digital assets
      balance: 10000.00
    }
  ]
}
```

**Key Points:**
- ✅ Equity = Margin account (options enabled)
- ✅ Futures = Futures trading
- ✅ Crypto = Digital assets (ONLY TT supports this)

---

### 3. Interactive Brokers (IBKR)
```javascript
{
  broker: "IBKR",
  accountTypes: ["Equity", "Futures"],
  environments: ["PAPER", "LIVE"],
  accounts: [
    {
      id: "U1234567",
      type: "Equity",        // Individual Margin account
      balance: 100000.00
    },
    {
      id: "U7654321",
      type: "Futures",       // Futures account
      balance: 50000.00
    }
  ]
}
```

**Key Points:**
- ✅ Equity = Margin account (4:1 leverage typical)
- ✅ Futures = Futures trading
- ❌ NO direct crypto support

---

## 📊 Sidebar Navigation Structure

```
Accounts
├── Account Balance (overview)
├── TradeStation
│   ├── Equity (/account/tradestation/equity)
│   └── Futures (/account/tradestation/futures)
├── Tastytrade
│   ├── Equity (/account/tastytrade/equity)
│   ├── Futures (/account/tastytrade/futures)
│   └── Crypto (/account/tastytrade/crypto)
└── IBKR
    ├── Equity (/account/ibkr/equity)
    └── Futures (/account/ibkr/futures)
```

---

## 🔧 Backend Mock Endpoints

### TradeStation
```http
GET /api/tradestation/mock/accounts
GET /api/tradestation/mock/accounts/{account_id}/balances
```

### Tastytrade
```http
GET /api/tastytrade/mock/accounts
GET /api/tastytrade/mock/accounts/{account_id}/balances
```

### IBKR
```http
GET /api/ibkr/mock/accounts
GET /api/ibkr/mock/accounts/{account_id}/balances
```

**File:** `backend/app/routers/brokers_mock.py`

---

## 🎨 Account Page Components (TODO)

Each account type page should display:

### 1. Account Header
- Broker logo
- Account ID
- Account type badge (Equity/Futures/Crypto)
- Environment badge (SIM/LIVE/PAPER)

### 2. Balance Cards
- Cash Balance
- Buying Power
- Equity / Market Value
- Margin Used
- Maintenance Margin

### 3. Positions Table
- Symbol
- Quantity
- Entry Price
- Current Price
- P&L ($ and %)
- Actions (Close, Adjust)

### 4. Transactions History
- Date & Time
- Symbol
- Side (BUY/SELL)
- Quantity
- Price
- Total
- Fees

### 5. Quick Actions
- Add Position
- Deposit Funds
- Withdraw Funds
- View Statements

---

## 🗄️ Database Schema

### Mindfolio Model (backend/mindfolio.py)
```python
class Mindfolio(BaseModel):
    id: str
    name: str
    broker: str                    # "TradeStation" | "Tastytrade" | "IBKR"
    environment: str               # "SIM" | "LIVE" | "PAPER"
    account_type: str              # "Equity" | "Futures" | "Crypto"
    account_id: Optional[str]      # Broker's account ID
    cash_balance: float
    starting_balance: float
    status: str                    # "ACTIVE" | "PAUSED" | "CLOSED"
    created_at: str
    updated_at: str
```

**Rules:**
- All Equity accounts are Margin-enabled
- Futures require separate account
- Crypto only supported by Tastytrade

---

## ✅ Implementation Status

- [x] Sidebar navigation structure
- [x] Backend mock endpoints (TS, TT, IBKR)
- [x] Unified account type model
- [x] MindfolioTemplateModal integration
- [x] Broker configs with account type mapping
- [ ] Account detail pages (7 pages total)
- [ ] Account balance overview page
- [ ] Real broker API integration
- [ ] OAuth flows for each broker

---

## 🚀 Next Steps

1. **Create Account Pages:**
   - `/account/balance` - Overview of all accounts
   - `/account/tradestation/equity`
   - `/account/tradestation/futures`
   - `/account/tastytrade/equity`
   - `/account/tastytrade/futures`
   - `/account/tastytrade/crypto`
   - `/account/ibkr/equity`
   - `/account/ibkr/futures`

2. **Components to Build:**
   - `AccountHeader.jsx` - Broker info, account type, balance
   - `BalanceCards.jsx` - Cash, buying power, margin
   - `PositionsTable.jsx` - Live positions with P&L
   - `TransactionsTable.jsx` - Transaction history
   - `QuickActions.jsx` - Common account actions

3. **Backend Integration:**
   - Replace mock endpoints with real broker APIs
   - OAuth flows for each broker
   - Real-time balance updates
   - Position sync from brokers

---

**Status:** ✅ Structure defined, mock endpoints ready, UI implementation pending
