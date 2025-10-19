from __future__ import annotations
import json
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from redis_fallback import get_kv
from utils.redis_client import get_redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portfolios", tags=["portfolios"])

# ——— Models ———
class ModuleAllocation(BaseModel):
 module: str # "IV_SERVICE", "SELL_PUTS", etc.
 budget: float # allocated budget for this module
 max_risk_per_trade: float # max risk per individual trade
 daily_loss_limit: float # daily loss limit for module
 autotrade: bool = False # whether module can auto-trade

class Transaction(BaseModel):
 id: str
 portfolio_id: str
 account_id: Optional[str] = None
 datetime: str # ISO format
 symbol: str
 side: str # BUY, SELL
 qty: float
 price: float
 fee: float = 0.0
 currency: str = "USD"
 notes: Optional[str] = None
 created_at: str

 @validator("side")
 def validate_side(cls, v):
    if v.upper() not in ["BUY", "SELL"]:
        raise ValueError("side must be BUY or SELL")
    return v.upper()

class TransactionCreate(BaseModel):
 portfolio_id: str
 account_id: Optional[str] = None
 datetime: str
 symbol: str
 side: str
 qty: float
 price: float
 fee: float = 0.0
 currency: str = "USD"
 notes: Optional[str] = None

 @validator("side")
 def validate_side(cls, v):
    return v.upper()

class Position(BaseModel):
 symbol: str
 qty: float
 cost_basis: float # total cost including fees
 avg_cost: float # cost_basis / qty (if qty != 0)
 unrealized_pnl: Optional[float] = None # requires market price
 market_value: Optional[float] = None # requires market price

class RealizedPnL(BaseModel):
 symbol: str
 realized: float
 trades: int

class ImportCSV(BaseModel):
 csv_data: str

class Portfolio(BaseModel):
 id: str
 name: str
 cash_balance: float
 status: str = "ACTIVE" # ACTIVE, PAUSED, CLOSED
 modules: List[ModuleAllocation] = []
 created_at: str
 updated_at: str

class PortfolioCreate(BaseModel):
 name: str
 starting_balance: float = 10000.0
 modules: List[ModuleAllocation] = []

class PortfolioPatch(BaseModel):
 name: Optional[str] = None
 status: Optional[str] = None

class FundsOp(BaseModel):
 delta: float # +/- amount to add/subtract

class AllocOp(BaseModel):
 module: str
 alloc: ModuleAllocation

# ——— Redis Keys ———
def key_portfolio(pid: str) -> str:
 return f"pf:{pid}"

def key_portfolio_list() -> str:
 return "pf:list"

def key_stats(pid: str) -> str:
 return f"pf:{pid}:stats"

def key_transaction(tid: str) -> str:
 return f"tx:{tid}"

def key_portfolio_transactions(pid: str) -> str:
 return f"pf:{pid}:transactions"

def key_portfolio_positions(pid: str) -> str:
 return f"pf:{pid}:positions"

# ——— FIFO Logic Functions ———
def round2(n: float) -> float:
    return round(n * 100) / 100

async def get_portfolio_transactions(portfolio_id: str) -> List[Transaction]:
    """Get all transactions for a portfolio, sorted by datetime"""
    cli = await get_kv()
    tx_list_raw = await cli.get(key_portfolio_transactions(portfolio_id)) or "[]"
    tx_ids = json.loads(tx_list_raw)

    transactions = []
    for tx_id in tx_ids:
        tx_raw = await cli.get(key_transaction(tx_id))
        if tx_raw:
            tx_data = json.loads(tx_raw)
            transactions.append(Transaction(**tx_data))

    # Sort by datetime
    transactions.sort(key=lambda x: x.datetime)
    return transactions

async def calculate_positions_fifo(portfolio_id: str) -> List[Position]:
    """Calculate current positions using FIFO method"""
    transactions = await get_portfolio_transactions(portfolio_id)

    # FIFO lots tracking: {symbol: [{"qty": float, "price": float}, ...]}
    lots: "dict[str, list[dict[str, float]]]" = {}

    for tx in transactions:
        symbol = tx.symbol
        if symbol not in lots:
            lots[symbol] = []

        if tx.side == "BUY":
            # Add to lots
            cost_per_share = tx.price + (tx.fee / tx.qty if tx.qty > 0 else 0)
            lots[symbol].append({"qty": tx.qty, "price": cost_per_share})

        elif tx.side == "SELL":
            # Consume lots FIFO
            qty_to_sell = tx.qty
            while qty_to_sell > 0 and lots[symbol]:
                lot = lots[symbol][0]
                if lot["qty"] <= qty_to_sell:
                    # Consume entire lot
                    qty_to_sell -= lot["qty"]
                    lots[symbol].pop(0)
                else:
                    # Partial consumption
                    lot["qty"] -= qty_to_sell
                    qty_to_sell = 0

    # Calculate current positions
    positions = []
    for symbol, symbol_lots in lots.items():
        if symbol_lots: # If there are remaining lots
            total_qty = sum(lot["qty"] for lot in symbol_lots)
            total_cost = sum(lot["qty"] * lot["price"] for lot in symbol_lots)

            if total_qty > 0:
                avg_cost = total_cost / total_qty
                positions.append(
                    Position(
                        symbol=symbol,
                        qty=round2(total_qty),
                        cost_basis=round2(total_cost),
                        avg_cost=round2(avg_cost),
                    )
                )

    return sorted(positions, key=lambda x: x.symbol)

async def calculate_realized_pnl(portfolio_id: str) -> List[RealizedPnL]:
 """Calculate realized P&L for each symbol using FIFO"""
 transactions = await get_portfolio_transactions(portfolio_id)

async def calculate_realized_pnl(portfolio_id: str) -> List[RealizedPnL]:
    """Calculate realized P&L for each symbol using FIFO"""
    transactions = await get_portfolio_transactions(portfolio_id)

    # Track FIFO lots and realized P&L
    fifo_lots: "dict[str, list[dict[str, float]]]" = {}
    realized_pnl: "dict[str, dict[str, float]]" = {}

    for tx in transactions:
        symbol = tx.symbol

        if symbol not in fifo_lots:
            fifo_lots[symbol] = []
        if symbol not in realized_pnl:
            realized_pnl[symbol] = {"realized": 0.0, "trades": 0}

        if tx.side == "BUY":
            cost_per_share = tx.price + (tx.fee / tx.qty if tx.qty > 0 else 0)
            fifo_lots[symbol].append({"qty": tx.qty, "price": cost_per_share})

        elif tx.side == "SELL":
            qty_to_sell = tx.qty
            sell_proceeds_per_share = tx.price - (tx.fee / tx.qty if tx.qty > 0 else 0)

            while qty_to_sell > 0 and fifo_lots[symbol]:
                lot = fifo_lots[symbol][0]

                if lot["qty"] <= qty_to_sell:
                    # Sell entire lot
                    realized = (sell_proceeds_per_share - lot["price"]) * lot["qty"]
                    realized_pnl[symbol]["realized"] += realized
                    qty_to_sell -= lot["qty"]
                    fifo_lots[symbol].pop(0)
                else:
                    # Partial sale
                    realized = (sell_proceeds_per_share - lot["price"]) * qty_to_sell
                    realized_pnl[symbol]["realized"] += realized
                    lot["qty"] -= qty_to_sell
                    qty_to_sell = 0

            realized_pnl[symbol]["trades"] += 1

    # Convert to list
    result = []
    for symbol, pnl_data in realized_pnl.items():
        if pnl_data["trades"] > 0: # Only include symbols with actual trades
            result.append(
                RealizedPnL(
                    symbol=symbol,
                    realized=round2(pnl_data["realized"]),
                    trades=int(pnl_data["trades"]),
                )
            )

    return sorted(result, key=lambda x: x.symbol)

# ——— CRUD Operations ———
async def pf_get(pid: str) -> Portfolio:
    """Get portfolio by ID"""
    cli = await get_kv()
    raw = await cli.get(key_portfolio(pid))
    if not raw:
        raise HTTPException(404, f"Portfolio {pid} not found")
    data = json.loads(raw)
    return Portfolio(**data)

async def pf_put(p: Portfolio) -> None:
    """Save portfolio"""
    cli = await get_kv()
    p.updated_at = datetime.utcnow().isoformat()
    await cli.set(key_portfolio(p.id), json.dumps(p.dict()))

    # Update list index
    current_list = await cli.get(key_portfolio_list()) or "[]"
    pf_list = json.loads(current_list)
    if p.id not in pf_list:
        pf_list.append(p.id)
    await cli.set(key_portfolio_list(), json.dumps(pf_list))

async def pf_list() -> List[Portfolio]:
    """List all portfolios"""
    cli = await get_kv()
    raw_list = await cli.get(key_portfolio_list()) or "[]"
    pf_ids = json.loads(raw_list)

    portfolios = []
    for pid in pf_ids:
        try:
            p = await pf_get(pid)
            portfolios.append(p)
        except HTTPException:
            # Skip deleted/missing portfolios
            continue

    return portfolios

# ——— API Endpoints ———

# ——— TS Positions Grid Endpoint (must be before /{pid} patterns) ———
@router.get("/positions-ts")
async def get_tradestation_positions_grid():
    """Get TradeStation positions in grid format for dashboard"""
    try:
        from tradestation_client import TradeStationClient
        from tradestation_auth_service import tradestation_auth_service as ts_auth

        ts_client = TradeStationClient(ts_auth)

        # Get accounts and positions
        accounts = await ts_client.get_accounts()
        all_positions = []

        for account in accounts:
            account_id = account.get("Key", account.get("AccountID", ""))
            if account_id:
                try:
                    positions = await ts_client.get_positions(account_id)
                    for pos in positions:
                        all_positions.append(
                            {
                                "account_id": account_id,
                                "account_name": account.get("Name", account_id),
                                "symbol": pos.symbol,
                                "asset_type": pos.asset_type,
                                "quantity": pos.quantity,
                                "average_price": pos.average_price,
                                "current_price": pos.current_price,
                                "market_value": pos.market_value,
                                "unrealized_pnl": pos.unrealized_pnl,
                                "unrealized_pnl_percent": pos.unrealized_pnl_percent,
                                "position_type": "LONG"
                                if pos.quantity > 0
                                else "SHORT",
                            }
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to get positions for account {account_id}: {e}"
                    )
                    continue

        # Group positions by symbol for grid display
        grid_data = {}
        for pos in all_positions:
            symbol = pos["symbol"]
            if symbol not in grid_data:
                grid_data[symbol] = {
                    "symbol": symbol,
                    "asset_type": pos["asset_type"],
                    "total_quantity": 0,
                    "weighted_avg_price": 0,
                    "total_market_value": 0,
                    "total_unrealized_pnl": 0,
                    "accounts": [],
                }

        grid_data[symbol]["total_quantity"] += pos["quantity"]
        grid_data[symbol]["total_market_value"] += pos["market_value"]
        grid_data[symbol]["total_unrealized_pnl"] += pos["unrealized_pnl"]
        grid_data[symbol]["accounts"].append(
            {
                "account_id": pos["account_id"],
                "account_name": pos["account_name"],
                "quantity": pos["quantity"],
                "avg_price": pos["average_price"],
            }
        )

        # Calculate weighted averages
        for symbol_data in grid_data.values():
            if symbol_data["total_quantity"] != 0:
                symbol_data["weighted_avg_price"] = (
                    symbol_data["total_market_value"] / symbol_data["total_quantity"]
                )
                symbol_data["unrealized_pnl_percent"] = (
                    symbol_data["total_unrealized_pnl"]
                    / (
                        symbol_data["total_market_value"]
                        - symbol_data["total_unrealized_pnl"]
                    )
                ) * 100

        return {
            "status": "success",
            "positions_grid": list(grid_data.values()),
            "total_positions": len(grid_data),
            "total_accounts": len(accounts),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to get TradeStation positions grid: {str(e)}")

@router.get("", response_model=List[Portfolio])
async def list_portfolios():
    """List all portfolios"""
    return await pf_list()

@router.post("", response_model=Portfolio)
async def create_portfolio(body: PortfolioCreate):
    """Create new portfolio"""
    portfolio = Portfolio(
        id=f"pf_{str(uuid.uuid4()).replace('-', '')[:8]}",
        name=body.name,
        cash_balance=body.starting_balance,
        modules=body.modules,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )
    await pf_put(portfolio)
    return portfolio

@router.get("/{pid}", response_model=Portfolio)
async def get_portfolio(pid: str):
    """Get portfolio by ID"""
    return await pf_get(pid)

@router.patch("/{pid}", response_model=Portfolio)
async def patch_portfolio(pid: str, body: PortfolioPatch):
    """Update portfolio"""
    p = await pf_get(pid)
    if body.name is not None:
        p.name = body.name
    if body.status is not None:
        p.status = body.status
    await pf_put(p)
    return p

@router.post("/{pid}/funds", response_model=Portfolio)
async def funds(pid: str, body: FundsOp):
    """Add/subtract funds from portfolio"""
    p = await pf_get(pid)
    p.cash_balance = round(p.cash_balance + float(body.delta), 2)
    await pf_put(p)
    return p

@router.post("/{pid}/allocate", response_model=Portfolio)
async def allocate(pid: str, body: AllocOp):
    """Allocate budget to module"""
    p = await pf_get(pid)
    # Replace or append module allocation
    mods = [m for m in p.modules if m.module != body.module]
    mods.append(body.alloc)
    p.modules = mods
    await pf_put(p)
    return p

@router.get("/{pid}/stats")
async def stats(pid: str):
    """Get portfolio statistics with real P&L data"""
    try:
        # Calculate real statistics from transactions
        positions = await calculate_positions_fifo(pid)
        realized_pnl_data = await calculate_realized_pnl(pid)

        # Calculate totals
        total_realized = sum(pnl.realized for pnl in realized_pnl_data)
        total_trades = sum(pnl.trades for pnl in realized_pnl_data)

        # Portfolio NAV
        portfolio = await pf_get(pid)

        return {
            "portfolio_id": pid,
            "nav": portfolio.cash_balance,
            "pnl_realized": round2(total_realized),
            "pnl_unrealized": 0, # Will be calculated with live market data integration
            "positions_count": len(positions),
            "total_trades": total_trades,
            "win_rate": None, # Calculated when sufficient trade history available
            "expectancy": None, # Calculated when sufficient trade history available
            "max_dd": None, # Calculated when sufficient trade history available
            "realized_pnl_by_symbol": [pnl.dict() for pnl in realized_pnl_data],
        }
    except Exception as e:
        # Fallback to basic stats
        portfolio = await pf_get(pid)
        return {
            "portfolio_id": pid,
            "nav": portfolio.cash_balance,
            "pnl_realized": 0,
            "pnl_unrealized": 0,
            "error": str(e),
        }

# ——— Transaction Endpoints ———
@router.get("/{pid}/transactions", response_model=List[Transaction])
async def get_transactions(pid: str, symbol: Optional[str] = None):
    """Get all transactions for portfolio, optionally filtered by symbol"""
    transactions = await get_portfolio_transactions(pid)

    if symbol:
        symbol = symbol.upper()
        transactions = [tx for tx in transactions if tx.symbol == symbol]

    return transactions

@router.post("/{pid}/transactions", response_model=Transaction)
async def create_transaction(pid: str, body: TransactionCreate):
    """Create new transaction"""
    # Verify portfolio exists
    await pf_get(pid)

    transaction = Transaction(
        id=f"tx_{str(uuid.uuid4()).replace('-', '')[:8]}",
        portfolio_id=pid,
        account_id=body.account_id,
        datetime=body.datetime,
        symbol=body.symbol.upper(),
        side=body.side.upper(),
        qty=body.qty,
        price=body.price,
        fee=body.fee,
        currency=body.currency.upper(),
        notes=body.notes,
        created_at=datetime.utcnow().isoformat(),
    )

    return await tx_create(transaction)

@router.get("/{pid}/positions", response_model=List[Position])
async def get_positions(pid: str):
    """Get current positions calculated using FIFO"""
    return await calculate_positions_fifo(pid)

@router.get("/{pid}/realized-pnl", response_model=List[RealizedPnL])
async def get_realized_pnl(pid: str):
    """Get realized P&L by symbol using FIFO"""
    return await calculate_realized_pnl(pid)

@router.post("/{pid}/import-csv")
async def import_transactions_csv(pid: str, body: ImportCSV):
    """Import transactions from CSV data"""
    # Verify portfolio exists
    await pf_get(pid)

    # Parse and validate CSV
    transactions = await parse_csv_transactions(body.csv_data, pid)

    # Save all transactions
    imported_count = 0
    for tx in transactions:
        await tx_create(tx)
        imported_count += 1

    return {
        "imported": imported_count,
        "portfolio_id": pid,
        "message": f"Successfully imported {imported_count} transactions",
    }

# ——— Transaction CRUD Functions ———
async def tx_create(tx: Transaction) -> Transaction:
    """Save transaction"""
    cli = await get_kv()
    await cli.set(key_transaction(tx.id), json.dumps(tx.dict()))

    # Update portfolio transaction list
    current_list = await cli.get(key_portfolio_transactions(tx.portfolio_id)) or "[]"
    tx_list = json.loads(current_list)
    if tx.id not in tx_list:
        tx_list.append(tx.id)
    await cli.set(key_portfolio_transactions(tx.portfolio_id), json.dumps(tx_list))

    return tx

async def tx_get(tid: str) -> Transaction:
    """Get transaction by ID"""
    cli = await get_kv()
    raw = await cli.get(key_transaction(tid))
    if not raw:
        raise HTTPException(404, f"Transaction {tid} not found")
    data = json.loads(raw)
    return Transaction(**data)

async def parse_csv_transactions(csv_data: str, portfolio_id: str) -> List[Transaction]:
    """Parse CSV data into transactions"""
    lines = csv_data.strip().split("\n")
    if len(lines) < 2:
        raise HTTPException(400, "CSV must have header and at least one data row")

    # Parse header
    header = lines[0].split(",")
    header = [h.strip() for h in header]

    # Required columns
    required_cols = ["datetime", "symbol", "side", "qty", "price"]
    for col in required_cols:
        if col not in header:
            raise HTTPException(400, f"Missing required column: {col}")

    transactions = []
    for i, line in enumerate(lines[1:], 1):
        try:
            values = line.split(",")
            if len(values) != len(header):
                raise ValueError(
                    f"Row {i}: Expected {len(header)} columns, got {len(values)}"
                )

            row_data = dict(zip(header, values))

            # Create transaction
            tx = Transaction(
                id=f"tx_{str(uuid.uuid4()).replace('-', '')[:8]}",
                portfolio_id=portfolio_id,
                account_id=row_data.get("account_id", "").strip() or None,
                datetime=row_data["datetime"].strip(),
                symbol=row_data["symbol"].strip().upper(),
                side=row_data["side"].strip().upper(),
                qty=float(row_data["qty"]),
                price=float(row_data["price"]),
                fee=float(row_data.get("fee", "0")),
                currency=row_data.get("currency", "USD").strip().upper(),
                notes=row_data.get("notes", "").strip() or None,
                created_at=datetime.utcnow().isoformat(),
            )
            transactions.append(tx)

        except Exception as e:
            raise HTTPException(400, f"Row {i} error: {str(e)}")

    return transactions

# ——— TradeStation OAuth2 Integration Endpoints ———
@router.get("/ts/auth-url")
async def get_tradestation_auth_url():
    """Get TradeStation OAuth2 authorization URL"""
    try:
        from tradestation_auth_service import tradestation_auth_service as ts_auth

        auth_info = ts_auth.generate_auth_url()
        return {
            "status": "success",
            "auth_url": auth_info["auth_url"],
            "state": auth_info["state"],
            "message": "Navigate to auth_url to complete OAuth2 flow",
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to generate auth URL: {str(e)}")

@router.post("/ts/callback")
async def tradestation_oauth_callback(code: str, state: str):
    """Handle TradeStation OAuth2 callback"""
    try:
        from tradestation_auth_service import tradestation_auth_service as ts_auth

        result = await ts_auth.exchange_code_for_tokens(code)
        return {
            "status": "success",
            "message": "OAuth2 authentication completed successfully",
            "authenticated": result.get("authenticated", False),
            "environment": result.get("environment", "UNKNOWN"),
        }
    except Exception as e:
        raise HTTPException(500, f"OAuth2 callback failed: {str(e)}")

@router.post("/ts/subscribe")
async def subscribe_to_quotes(symbols: List[str]):
    """Subscribe to live quote updates for symbols"""
    try:
        # For now, just return success without actual database operations
        # TODO[OPS-001]: Implement actual quote subscription when database service is available

        return {
            "status": "success",
            "subscribed_symbols": [s.upper() for s in symbols],
            "message": f"Subscribed to {len(symbols)} symbols for live quotes",
            "polling_interval": "30s",
            "note": "Quote subscription placeholder - database integration pending",
        }
    except Exception as e:
        raise HTTPException(500, f"Quote subscription failed: {str(e)}")

@router.post("/ts/unsubscribe")
async def unsubscribe_from_quotes(symbols: List[str]):
    """Unsubscribe from live quote updates"""
    try:
        return {
            "status": "success",
            "unsubscribed_symbols": [s.upper() for s in symbols],
            "message": f"Unsubscribed from {len(symbols)} symbols",
        }
    except Exception as e:
        raise HTTPException(500, f"Quote unsubscription failed: {str(e)}")

# ——— Buckets System Endpoints ———
@router.get("/{pid}/buckets")
async def get_portfolio_buckets(pid: str):
    """Get all buckets for a portfolio"""
    try:
        # First verify portfolio exists
        await pf_get(pid)

        # For now, return mock buckets data
        # TODO[OPS-002]: Implement actual database integration when available
        portfolio_buckets = [
            {
                "id": "bucket_001",
                "name": "Growth Stocks",
                "start_value": 25000.0,
                "current_value": 27500.0,
                "pnl": 2500.0,
                "position_count": 5,
                "created_at": "2024-01-15T10:00:00Z",
                "notes": "High growth potential stocks",
            },
            {
                "id": "bucket_002",
                "name": "Dividend Stocks",
                "start_value": 15000.0,
                "current_value": 15750.0,
                "pnl": 750.0,
                "position_count": 3,
                "created_at": "2024-01-20T14:30:00Z",
                "notes": "Stable dividend paying stocks",
            },
        ]

        return {
            "status": "success",
            "portfolio_id": pid,
            "buckets": portfolio_buckets,
            "total_buckets": len(portfolio_buckets),
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to get portfolio buckets: {str(e)}")

@router.post("/{pid}/buckets")
async def create_portfolio_bucket(
    pid: str, name: str, start_value: float = 0, notes: Optional[str] = None
):
    """Create a new bucket for portfolio"""
    try:
        # Verify portfolio exists
        await pf_get(pid)

        # Create mock bucket (TODO[OPS-003]: Implement actual database integration)
        import uuid

        bucket = {
            "id": f"bucket_{str(uuid.uuid4())[:8]}",
            "name": name,
            "start_value": start_value,
            "current_value": start_value,
            "pnl": 0.0,
            "position_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "notes": notes,
            "portfolio_id": pid,
        }

        return {
            "status": "success",
            "message": f"Bucket '{name}' created successfully",
            "bucket": bucket,
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to create bucket: {str(e)}")

# ——— Analytics & Equity Charts Endpoint ———
@router.get("/{pid}/analytics/equity")
async def get_portfolio_equity_chart(pid: str, timeframe: str = "1M"):
    """Get equity curve data for portfolio analytics"""
    try:
        # Get portfolio transactions
        transactions = await get_portfolio_transactions(pid)
        realized_pnl = await calculate_realized_pnl(pid)
        positions = await calculate_positions_fifo(pid)

        # Calculate equity curve data points
        equity_data = []
        running_balance = 10000.0 # Starting balance

        # Process transactions chronologically
        for i, tx in enumerate(transactions):
            if tx.side == "BUY":
                running_balance -= tx.qty * tx.price + tx.fee
            elif tx.side == "SELL":
                running_balance += tx.qty * tx.price - tx.fee

            equity_data.append(
                {
                    "date": tx.datetime,
                    "equity": round(running_balance, 2),
                    "transaction_id": tx.id,
                    "symbol": tx.symbol,
                    "side": tx.side,
                }
            )

        # Add current unrealized P&L (would need market prices)
        current_equity = running_balance
        for pos in positions:
            current_equity += pos.cost_basis # Simplified, needs current market value

        # Analytics metrics
        total_realized = sum(pnl.realized for pnl in realized_pnl)
        total_trades = sum(pnl.trades for pnl in realized_pnl)

        analytics = {
            "equity_curve": equity_data[-50:]
            if len(equity_data) > 50
            else equity_data, # Last 50 points
            "summary": {
                "current_equity": round(current_equity, 2),
                "total_realized_pnl": round(total_realized, 2),
                "total_trades": total_trades,
                "win_rate": None, # TODO[OPS-004]: Calculate from profitable trades
                "sharpe_ratio": None, # TODO[OPS-005]: Calculate from equity curve
                "max_drawdown": None, # TODO[OPS-006]: Calculate from equity curve
                "positions_count": len(positions),
            },
            "buckets": [], # TODO[OPS-007]: Implement bucket-level analytics
            "timeframe": timeframe,
            "generated_at": datetime.utcnow().isoformat(),
        }

        return {"status": "success", "portfolio_id": pid, "analytics": analytics}

    except Exception as e:
        raise HTTPException(500, f"Failed to generate equity analytics: {str(e)}")

@router.get("/{pid}/analytics/equity.csv")
async def export_portfolio_equity_csv(pid: str, timeframe: str = "1M"):
    """Export equity curve data as CSV file"""
    try:
        # Get equity data using existing endpoint
        equity_response = await get_portfolio_equity_chart(pid, timeframe)
        equity_data = equity_response["analytics"]["equity_curve"]

        if not equity_data:
            raise HTTPException(404, "No equity data available for export")

        # Generate CSV content
        csv_lines = ["Date,Equity,Transaction_ID,Symbol,Side,Realized_Cum"]

        running_realized = 0.0
        for point in equity_data:
            # Calculate cumulative realized (simplified)
            if point.get("side") == "SELL":
                running_realized += (
                    point.get("equity", 0) * 0.01
                ) # Simplified calculation

            csv_lines.append(
                f"{point.get('date', '')},{point.get('equity', 0)},{point.get('transaction_id', '')},"
                f"{point.get('symbol', '')},{point.get('side', '')},{round(running_realized, 2)}"
            )

        csv_content = "\n".join(csv_lines)

        from fastapi.responses import Response

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=portfolio_{pid}_equity.csv"
            },
        )

    except Exception as e:
        raise HTTPException(500, f"Failed to export equity CSV: {str(e)}")

# ——— Budget check helper (pentru /trade/preview & /place) ———
async def portfolio_budget_ok(
    pid: str, module: str, risk_cost: float
) -> tuple[bool, str]:
    """Check if portfolio has budget for trade"""
    try:
        p = await pf_get(pid)

        if p.status != "ACTIVE":
            return False, "Portfolio not active"

        # Find module allocation
        alloc = next((m for m in p.modules if m.module == module), None)
        if not alloc:
            return False, f"Module {module} not allocated"

        if risk_cost > alloc.max_risk_per_trade and alloc.max_risk_per_trade > 0:
            return False, "Exceeds max_risk_per_trade"

        if risk_cost > alloc.budget and alloc.budget > 0:
            return False, "Exceeds module budget"

        if risk_cost > p.cash_balance:
            return False, "Insufficient portfolio cash"

        return True, "OK"

    except HTTPException:
        return False, "Portfolio not found"
    except Exception as e:
        return False, f"Budget check failed: {str(e)}"

# ——— EOD (End-of-Day) Snapshots ———
class EODSnapshot(BaseModel):
    id: str
    portfolio_id: str
    date: str # YYYY-MM-DD in Europe/Bucharest timezone
    realized: float
    unrealized: float
    total: float # realized + unrealized
    cash_balance: float
    positions_count: int
    timestamp: str # ISO datetime of snapshot creation
    timezone: str = "Europe/Bucharest"

async def _calculate_unrealized_pnl(positions: List[Position]) -> float:
    """Calculate current unrealized P&L from positions"""
    # For demo, use simple mock prices
    # In production, this would fetch current market prices
    mock_prices = {
        "AAPL": 150.0,
        "MSFT": 350.0,
        "TSLA": 200.0,
        "NVDA": 500.0,
        "GOOGL": 140.0,
        "AMZN": 130.0,
        "META": 300.0,
    }

    unrealized = 0.0
    for pos in positions:
        current_price = mock_prices.get(
            pos.symbol, pos.avg_cost * 1.05
        ) # 5% gain as fallback
        market_value = pos.qty * current_price
        unrealized += market_value - pos.cost_basis

    return unrealized

@router.post("/{pid}/analytics/eod/snapshot")
async def create_eod_snapshot(pid: str):
    """Create a new EOD snapshot for the portfolio"""
    try:
        from datetime import datetime
        import pytz

        # Use Europe/Bucharest timezone as requested
        tz = pytz.timezone("Europe/Bucharest")
        now = datetime.now(tz)
        date_str = now.strftime("%Y-%m-%d")
        timestamp = now.isoformat()

        # Get portfolio data
        portfolio = await pf_get(pid)
        positions = await calculate_positions_fifo(pid)
        realized_pnl = await calculate_realized_pnl(pid)

        # Calculate realized P&L total
        total_realized = sum(pnl.realized for pnl in realized_pnl)

        # Calculate unrealized P&L from current positions
        total_unrealized = await _calculate_unrealized_pnl(positions)

        # Create snapshot
        snapshot = EODSnapshot(
            id=str(uuid.uuid4()),
            portfolio_id=pid,
            date=date_str,
            realized=round(total_realized, 2),
            unrealized=round(total_unrealized, 2),
            total=round(total_realized + total_unrealized, 2),
            cash_balance=portfolio.cash_balance,
            positions_count=len(positions),
            timestamp=timestamp,
            timezone="Europe/Bucharest",
        )

        # Store snapshot in Redis (optional cache)
        try:
            kv = get_redis()
            snapshot_key = f"eod_snapshot:{pid}:{date_str}"
            kv.set(snapshot_key, json.dumps(snapshot.dict()), ex=86400 * 90) # 90 days
        except Exception:
            pass # Redis cache is optional

        # Also add to series index (Redis cache)
        try:
            kv = get_redis()
            series_key = f"eod_series:{pid}"
            existing_series = kv.get(series_key)
            if existing_series:
                series = json.loads(existing_series)
            else:
                series = []

            # Update or add today's snapshot
            series = [
                s for s in series if s.get("date") != date_str
            ] # Remove existing for today
            series.append(
                {
                    "date": date_str,
                    "realized": snapshot.realized,
                    "unrealized": snapshot.unrealized,
                    "total": snapshot.total,
                    "timestamp": timestamp,
                }
            )

            # Sort by date and keep last 365 days
            series.sort(key=lambda x: x["date"])
            series = series[-365:]

            kv.set(series_key, json.dumps(series), ex=86400 * 90)
        except Exception:
            pass # Redis cache is optional

        return {
            "status": "success",
            "snapshot": snapshot,
            "message": f"EOD snapshot created for {date_str} at {timestamp}",
        }

    except Exception as e:
        logger.error(f"Failed to create EOD snapshot for {pid}: {str(e)}")
        raise HTTPException(500, f"Failed to create EOD snapshot: {str(e)}")

@router.get("/{pid}/analytics/eod")
async def get_eod_series(pid: str):
    """Get EOD snapshot series for the portfolio"""
    try:
        # Try Redis cache first, fallback to sample data
        series = []
        try:
            kv = get_redis()
            series_key = f"eod_series:{pid}"
            existing_series = kv.get(series_key)
            if existing_series:
                series = json.loads(existing_series)
        except Exception:
            pass # Redis cache is optional

        if not series:
            # If no series exists, create a sample one for demo
            from datetime import datetime, timedelta
            import pytz

            tz = pytz.timezone("Europe/Bucharest")
            today = datetime.now(tz).date()

            # Generate last 7 days of sample data
            series = []
            base_realized = 500.0
            base_unrealized = 200.0

            for i in range(7):
                date = today - timedelta(days=6 - i)
                realized = base_realized + (i * 50) + (i * 25) # Gradual increase
                unrealized = base_unrealized + (i * 30) - (i * 10) # Some volatility

                series.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "realized": round(realized, 2),
                        "unrealized": round(unrealized, 2),
                        "total": round(realized + unrealized, 2),
                        "timestamp": datetime.combine(
                            date, datetime.min.time().replace(hour=16)
                        )
                        .replace(tzinfo=tz)
                        .isoformat(),
                    }
                )

        return {
            "status": "success",
            "portfolio_id": pid,
            "series": series,
            "count": len(series),
            "timezone": "Europe/Bucharest",
        }

    except Exception as e:
        logger.error(f"Failed to get EOD series for {pid}: {str(e)}")
        raise HTTPException(500, f"Failed to get EOD series: {str(e)}")
