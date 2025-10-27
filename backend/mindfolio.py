from __future__ import annotations

import json
import logging
import os
import secrets
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, validator

from redis_fallback import get_kv

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mindfolio", tags=["mindfolio"])

# Persistent backup directory
BACKUP_DIR = Path("/workspaces/Flowmind/data/mindfolios")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ——— Models ———
class ModuleAllocation(BaseModel):
    module: str  # "IV_SERVICE", "SELL_PUTS", etc.
    budget: float  # allocated budget for this module
    max_risk_per_trade: float  # max risk per individual trade
    daily_loss_limit: float  # daily loss limit for module
    autotrade: bool = False  # whether module can auto-trade


class Transaction(BaseModel):
    id: str
    mindfolio_id: str
    account_id: Optional[str] = None
    datetime: str  # ISO format
    symbol: str
    side: str  # BUY, SELL
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
    mindfolio_id: str
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
    cost_basis: float  # total cost including fees
    avg_cost: float  # cost_basis / qty (if qty != 0)
    unrealized_pnl: Optional[float] = None  # requires market price
    market_value: Optional[float] = None  # requires market price


class RealizedPnL(BaseModel):
    symbol: str
    realized: float
    trades: int


class ImportCSV(BaseModel):
    csv_data: str


class Mindfolio(BaseModel):
    id: str
    name: str

    # Broker account information (NEW)
    broker: str = "TradeStation"  # "TradeStation" | "TastyTrade"
    environment: str = "SIM"  # "SIM" | "LIVE"
    account_type: str = "Equity"  # "Equity" | "Futures" | "Crypto"
    account_id: Optional[str] = None  # Broker's account number (optional)

    # Financial data
    cash_balance: float
    starting_balance: float = 10000.0  # Track initial balance for ROI calculation
    status: str = "ACTIVE"  # ACTIVE, PAUSED, CLOSED

    # Configuration
    modules: List[ModuleAllocation] = []

    # Metadata
    created_at: str
    updated_at: str


class MindfolioCreate(BaseModel):
    name: str
    starting_balance: float = 10000.0
    modules: List[ModuleAllocation] = []


class MindfolioPatch(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None


class FundsOp(BaseModel):
    delta: float  # +/- amount to add/subtract


class AllocOp(BaseModel):
    module: str
    alloc: ModuleAllocation


# ——— Redis Keys ———
def key_mindfolio(pid: str) -> str:
    return f"mf:{pid}"


def key_mindfolio_list() -> str:
    return "mf:list"


def key_stats(pid: str) -> str:
    return f"mf:{pid}:stats"


def key_transaction(tid: str) -> str:
    return f"tx:{tid}"


def key_mindfolio_transactions(pid: str) -> str:
    return f"mf:{pid}:transactions"


def key_mindfolio_positions(pid: str) -> str:
    return f"mf:{pid}:positions"


# ——— Backup/Restore Functions ———
async def backup_mindfolio_to_disk(mindfolio: Mindfolio) -> None:
    """Save mindfolio to JSON file as backup (includes positions from Redis)"""
    try:
        # Fetch positions from Redis
        cli = await get_kv()
        positions_json = await cli.get(key_mindfolio_positions(mindfolio.id)) or "[]"
        positions = json.loads(positions_json)
        
        # Create backup dict with positions
        backup_data = mindfolio.dict()
        backup_data["positions"] = positions
        
        backup_file = BACKUP_DIR / f"{mindfolio.id}.json"
        backup_file.write_text(json.dumps(backup_data, indent=2))
        logger.info(f"Backed up mindfolio {mindfolio.id} to disk with {len(positions)} positions")
    except Exception as e:
        logger.error(f"Failed to backup mindfolio {mindfolio.id}: {e}")


async def restore_mindfolio_from_disk(mindfolio_id: str) -> Optional[Mindfolio]:
    """Restore mindfolio from JSON backup (includes positions restoration to Redis)"""
    try:
        backup_file = BACKUP_DIR / f"{mindfolio_id}.json"
        if backup_file.exists():
            data = json.loads(backup_file.read_text())
            
            # Extract positions if they exist in backup
            positions = data.pop("positions", [])
            
            # Restore positions to Redis
            if positions:
                cli = await get_kv()
                positions_json = json.dumps(positions)
                await cli.set(key_mindfolio_positions(mindfolio_id), positions_json)
                logger.info(f"Restored {len(positions)} positions for mindfolio {mindfolio_id}")
            
            logger.info(f"Restored mindfolio {mindfolio_id} from disk backup")
            return Mindfolio(**data)
    except Exception as e:
        logger.error(f"Failed to restore mindfolio {mindfolio_id}: {e}")
    return None


def delete_mindfolio_backup(mindfolio_id: str) -> None:
    """Delete mindfolio backup file"""
    try:
        backup_file = BACKUP_DIR / f"{mindfolio_id}.json"
        if backup_file.exists():
            backup_file.unlink()
            logger.info(f"Deleted backup for mindfolio {mindfolio_id}")
    except Exception as e:
        logger.error(f"Failed to delete backup for {mindfolio_id}: {e}")


# ——— FIFO Logic Functions ———
def round2(n: float) -> float:
    return round(n * 100) / 100


async def get_mindfolio_transactions(mindfolio_id: str) -> List[Transaction]:
    """Get all transactions for a mindfolio, sorted by datetime"""
    cli = await get_kv()
    tx_list_raw = await cli.get(key_mindfolio_transactions(mindfolio_id)) or "[]"
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


async def calculate_positions_fifo(mindfolio_id: str) -> List[Position]:
    """Calculate current positions using FIFO method"""
    transactions = await get_mindfolio_transactions(mindfolio_id)

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
        if symbol_lots:  # If there are remaining lots
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


async def calculate_realized_pnl(mindfolio_id: str) -> List[RealizedPnL]:
    """Calculate realized P&L for each symbol using FIFO"""
    transactions = await get_mindfolio_transactions(mindfolio_id)

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
        if pnl_data["trades"] > 0:  # Only include symbols with actual trades
            result.append(
                RealizedPnL(
                    symbol=symbol,
                    realized=round2(pnl_data["realized"]),
                    trades=int(pnl_data["trades"]),
                )
            )

    return sorted(result, key=lambda x: x.symbol)


# ——— CRUD Operations ———
async def pf_get(pid: str) -> Mindfolio:
    """Get mindfolio by ID"""
    cli = await get_kv()
    raw = await cli.get(key_mindfolio(pid))
    if not raw:
        raise HTTPException(404, f"Mindfolio {pid} not found")
    data = json.loads(raw)
    return Mindfolio(**data)


async def pf_put(p: Mindfolio) -> None:
    """Save mindfolio to Redis + disk backup"""
    cli = await get_kv()
    p.updated_at = datetime.utcnow().isoformat()
    await cli.set(key_mindfolio(p.id), json.dumps(p.dict()))

    # Update list index
    current_list = await cli.get(key_mindfolio_list()) or "[]"
    pf_list = json.loads(current_list)
    if p.id not in pf_list:
        pf_list.append(p.id)
        await cli.set(key_mindfolio_list(), json.dumps(pf_list))
    
    # BACKUP to disk (now async to fetch positions)
    await backup_mindfolio_to_disk(p)


async def pf_list() -> List[Mindfolio]:
    """List all mindfolios"""
    cli = await get_kv()
    raw_list = await cli.get(key_mindfolio_list()) or "[]"
    pf_ids = json.loads(raw_list)

    mindfolios = []
    for pid in pf_ids:
        try:
            p = await pf_get(pid)
            mindfolios.append(p)
        except HTTPException:
            # Skip deleted/missing mindfolios
            continue

    return mindfolios


# ——— API Endpoints ———


@router.post("/restore-from-backup")
async def restore_all_from_backup():
    """Restore all mindfolios from disk backups (in case Redis is cleared)"""
    restored = []
    failed = []
    
    for backup_file in BACKUP_DIR.glob("*.json"):
        try:
            mindfolio_id = backup_file.stem
            mindfolio = await restore_mindfolio_from_disk(mindfolio_id)
            if mindfolio:
                await pf_put(mindfolio)
                restored.append(mindfolio_id)
            else:
                failed.append(mindfolio_id)
        except Exception as e:
            logger.error(f"Failed to restore {backup_file.name}: {e}")
            failed.append(backup_file.stem)
    
    return {
        "status": "success",
        "restored": len(restored),
        "failed": len(failed),
        "mindfolios": restored
    }


# ——— TS Positions Grid Endpoint (must be before /{pid} patterns) ———
@router.get("/positions-ts")
async def get_tradestation_positions_grid():
    """Get TradeStation positions in grid format for dashboard"""
    try:
        from tradestation_auth_service import tradestation_auth_service as ts_auth
        from tradestation_client import TradeStationClient

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
                                "position_type": (
                                    "LONG" if pos.quantity > 0 else "SHORT"
                                ),
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


@router.get("", response_model=List[Mindfolio])
async def list_mindfolios():
    """List all mindfolios"""
    return await pf_list()


@router.post("", response_model=Mindfolio)
async def create_mindfolio(body: MindfolioCreate):
    """Create new mindfolio with module budget validation"""
    mindfolio = Mindfolio(
        id=f"mf_{str(uuid.uuid4()).replace('-', '')[:12]}",  # Changed prefix to 'mf' for mindfolio
        name=body.name,
        cash_balance=body.starting_balance,
        starting_balance=body.starting_balance,  # Save initial balance for ROI tracking
        modules=body.modules,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )

    # Validate module budgets
    is_valid, error_msg = validate_module_budget_allocation(mindfolio)
    if not is_valid:
        raise HTTPException(400, f"Invalid module budget allocation: {error_msg}")

    await pf_put(mindfolio)
    logger.info(
        f"Created mindfolio {mindfolio.id} with {len(mindfolio.modules)} modules, total budget: ${sum(m.budget for m in mindfolio.modules):,.2f}"
    )
    return mindfolio


@router.get("/{pid}", response_model=Mindfolio)
async def get_mindfolio(pid: str):
    """Get mindfolio by ID"""
    return await pf_get(pid)


@router.patch("/{pid}", response_model=Mindfolio)
async def patch_mindfolio(pid: str, body: MindfolioPatch):
    """Update mindfolio"""
    p = await pf_get(pid)
    if body.name is not None:
        p.name = body.name
    if body.status is not None:
        p.status = body.status
    await pf_put(p)
    return p


@router.delete("/{pid}")
async def delete_mindfolio(pid: str):
    """Permanently delete mindfolio from Redis + disk backup"""
    kv = await get_kv()
    
    # Delete the mindfolio data
    key = f"mindfolio:{pid}"
    if hasattr(kv, 'delete'):
        result = await kv.delete(key)
    else:
        result = kv.delete(key)
    
    # Remove from the index list
    list_key = key_mindfolio_list()
    current_list = await kv.get(list_key) or "[]"
    pf_list = json.loads(current_list)
    
    if pid in pf_list:
        pf_list.remove(pid)
        await kv.set(list_key, json.dumps(pf_list))
    
    # DELETE disk backup
    delete_mindfolio_backup(pid)
    
    return {"deleted": True, "id": pid, "result": result}


@router.post("/{pid}/funds", response_model=Mindfolio)
async def funds(pid: str, body: FundsOp):
    """Add/subtract funds from mindfolio"""
    p = await pf_get(pid)
    
    # Validate sufficient cash for withdrawals
    new_balance = p.cash_balance + float(body.delta)
    if new_balance < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient cash. Available: ${p.cash_balance:.2f}, Requested: ${abs(body.delta):.2f}"
        )
    
    p.cash_balance = round(new_balance, 2)
    await pf_put(p)
    return p


@router.post("/{pid}/allocate", response_model=Mindfolio)
async def allocate(pid: str, body: AllocOp):
    """Allocate budget to module"""
    p = await pf_get(pid)
    # Replace or append module allocation
    mods = [m for m in p.modules if m.module != body.module]
    mods.append(body.alloc)
    p.modules = mods
    await pf_put(p)
    return p


@router.post("/import-from-tradestation")
async def import_full_tradestation_mindfolio(
    body: dict,
    request: Request,
    x_user_id: str = Header(None, alias="X-User-ID")
):
    """
    Create a master TradeStation mindfolio with ALL positions and cash.
    
    Body: {
        "account_id": "11775499",
        "name": "TradeStation - Account 11775499" (optional)
    }
    
    Returns the created mindfolio with all positions imported as transactions.
    """
    import requests
    from app.services.tradestation import get_valid_token
    
    user_id = x_user_id or "default"
    
    # Get token from cache
    token_data = await get_valid_token(user_id)
    if not token_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = token_data.get("access_token")
    
    account_id = body.get("account_id")
    mindfolio_name = body.get("name", f"TradeStation - {account_id}")
    
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id required")
    
    # TradeStation API base URL
    TS_MODE = os.getenv("TRADESTATION_MODE", "SIMULATION")
    if TS_MODE == "LIVE":
        TS_API_BASE = "https://api.tradestation.com/v3"
    else:
        TS_API_BASE = "https://sim-api.tradestation.com/v3"
    
    try:
        # Get KV client for transaction storage
        cli = await get_kv()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        # Get account balance
        balance_url = f"{TS_API_BASE}/brokerage/accounts/{account_id}/balances"
        balance_response = requests.get(balance_url, headers=headers, timeout=10)
        
        if balance_response.status_code != 200:
            raise HTTPException(status_code=balance_response.status_code, detail="Failed to fetch balances")
        
        balance_data = balance_response.json()
        balances_list = balance_data.get("Balances", [])
        cash_balance = float(balances_list[0].get("CashBalance", 0)) if balances_list else 0.0
        
        # Get ALL positions
        positions_url = f"{TS_API_BASE}/brokerage/accounts/{account_id}/positions"
        positions_response = requests.get(positions_url, headers=headers, timeout=10)
        
        if positions_response.status_code != 200:
            raise HTTPException(status_code=positions_response.status_code, detail="Failed to fetch positions")
        
        positions_data = positions_response.json()
        positions_list = positions_data.get("Positions", [])
        
        # Create new mindfolio
        new_mindfolio = Mindfolio(
            id=f"mf_{secrets.token_hex(6)}",
            name=mindfolio_name,
            broker="TradeStation",
            environment=os.getenv("TRADESTATION_MODE", "SIMULATION"),
            account_type="Equity",
            account_id=account_id,
            cash_balance=cash_balance,
            starting_balance=cash_balance,
            status="ACTIVE",
            modules=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        
        await pf_put(new_mindfolio)
        
        # Import ALL positions as BUY transactions
        imported_positions = []
        for pos in positions_list:
            quantity = float(pos.get("Quantity", 0))
            if quantity == 0:
                continue
            
            symbol = pos.get("Symbol", "")
            asset_type = pos.get("AssetType", "")
            avg_price = float(pos.get("AveragePrice", 0))
            current_price = float(pos.get("Last", 0))
            market_value = float(pos.get("MarketValue", 0))
            unrealized_pnl = float(pos.get("UnrealizedProfitLoss", 0))
            
            # Create transaction
            now = datetime.utcnow().isoformat()
            tx = Transaction(
                id=f"tx_{secrets.token_hex(6)}",
                mindfolio_id=new_mindfolio.id,
                datetime=now,
                symbol=symbol,
                side="BUY",
                qty=quantity,
                price=avg_price,
                notes=f"Imported from TradeStation account {account_id}",
                created_at=now
            )
            
            # Save transaction to Redis
            await cli.set(key_transaction(tx.id), tx.json())
            
            # Update transaction list for mindfolio
            tx_list_raw = await cli.get(key_mindfolio_transactions(new_mindfolio.id)) or "[]"
            tx_ids = json.loads(tx_list_raw)
            tx_ids.append(tx.id)
            await cli.set(key_mindfolio_transactions(new_mindfolio.id), json.dumps(tx_ids))
            
            imported_positions.append({
                "symbol": symbol,
                "asset_type": asset_type,
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "market_value": market_value,
                "unrealized_pnl": unrealized_pnl
            })
        
        # Recalculate positions from transactions
        calculated_positions = await calculate_positions_fifo(new_mindfolio.id)
        
        # Save positions to Redis
        cli = await get_kv()
        positions_json = json.dumps([pos.dict() for pos in calculated_positions])
        await cli.set(key_mindfolio_positions(new_mindfolio.id), positions_json)
        
        # Refresh and save backup
        refreshed_mindfolio = await pf_get(new_mindfolio.id)
        if refreshed_mindfolio:
            await pf_put(refreshed_mindfolio)
        
        return {
            "status": "success",
            "mindfolio": refreshed_mindfolio.dict() if refreshed_mindfolio else new_mindfolio.dict(),
            "positions_imported": len(imported_positions),
            "positions": imported_positions,
            "cash_balance": cash_balance
        }
        
    except Exception as e:
        logger.error(f"TradeStation import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/{pid}/import-positions")
async def import_positions_from_tradestation(pid: str, body: dict):
    """
    Import selected positions from TradeStation to this mindfolio.
    
    Body: {
        "account_id": "11775499",
        "positions": [
            {"symbol": "TSLA", "quantity": 100, "avg_price": 250.00},
            {"symbol": "AAPL", "quantity": 50, "avg_price": 180.00}
        ],
        "cash_amount": 5000.00
    }
    
    Validates:
    - Cash amount doesn't exceed TS account balance
    - Positions exist in TS account
    - Creates transactions in mindfolio
    """
    from app.services.tradestation import get_valid_token
    import requests
    
    p = await pf_get(pid)
    account_id = body.get("account_id")
    positions_to_import = body.get("positions", [])
    cash_to_transfer = body.get("cash_amount", 0)
    
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id required")
    
    # Get TradeStation positions and balance
    try:
        token = await get_valid_token("default")  # TODO: use actual user_id
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get account balance
        ts_mode = os.getenv("TRADESTATION_MODE", "SIMULATION")
        ts_base = "https://api.tradestation.com/v3" if ts_mode == "LIVE" else "https://sim-api.tradestation.com/v3"
        
        balance_url = f"{ts_base}/brokerage/accounts/{account_id}/balances"
        balance_resp = requests.get(balance_url, headers=headers, timeout=10)
        balance_resp.raise_for_status()
        balance_data = balance_resp.json()
        
        available_cash = float(balance_data.get("Balances", [{}])[0].get("CashBalance", 0))
        
        # Validate cash transfer
        if cash_to_transfer > available_cash:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient cash in TradeStation. Available: ${available_cash:.2f}, Requested: ${cash_to_transfer:.2f}"
            )
        
        # Get TS positions
        pos_url = f"{ts_base}/brokerage/accounts/{account_id}/positions"
        pos_resp = requests.get(pos_url, headers=headers, timeout=10)
        pos_resp.raise_for_status()
        ts_positions = pos_resp.json().get("Positions", [])
        
        # Validate each position exists and has sufficient quantity
        ts_pos_map = {p["Symbol"]: p for p in ts_positions}
        
        for pos in positions_to_import:
            symbol = pos["symbol"]
            qty = pos["quantity"]
            
            if symbol not in ts_pos_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Position {symbol} not found in TradeStation account"
                )
            
            ts_qty = int(ts_pos_map[symbol]["Quantity"])
            if qty > ts_qty:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient quantity for {symbol}. Available: {ts_qty}, Requested: {qty}"
                )
        
        # All validations passed - create transactions
        transactions_created = []
        
        # Transfer cash
        if cash_to_transfer > 0:
            p.cash_balance += cash_to_transfer
            transactions_created.append({
                "type": "CASH_DEPOSIT",
                "amount": cash_to_transfer,
                "description": f"Transferred from TradeStation account {account_id}"
            })
        
        # Import positions as BUY transactions
        cli = await get_kv()
        for pos in positions_to_import:
            symbol = pos["symbol"]
            qty = pos["quantity"]
            avg_price = pos["avg_price"]
            
            # Create transaction using correct model
            now = datetime.utcnow().isoformat()
            tx = Transaction(
                id=f"tx_{secrets.token_hex(6)}",
                mindfolio_id=pid,
                account_id=account_id,
                datetime=now,
                symbol=symbol,
                side="BUY",
                qty=qty,
                price=avg_price,
                fee=0.0,
                notes=f"Imported from TradeStation account {account_id}",
                created_at=now
            )
            
            # Save transaction to Redis
            await cli.set(key_transaction(tx.id), tx.json())
            
            # Update transaction list for mindfolio
            tx_list_raw = await cli.get(key_mindfolio_transactions(pid)) or "[]"
            tx_ids = json.loads(tx_list_raw)
            tx_ids.append(tx.id)
            await cli.set(key_mindfolio_transactions(pid), json.dumps(tx_ids))
            
            # Deduct cost from cash
            cost = qty * avg_price
            p.cash_balance -= cost
            
            transactions_created.append({
                "symbol": symbol,
                "quantity": qty,
                "price": avg_price,
                "cost": cost
            })
        
        # Save updated mindfolio
        await pf_put(p)
        
        return {
            "status": "success",
            "mindfolio_id": pid,
            "cash_transferred": cash_to_transfer,
            "positions_imported": len(positions_to_import),
            "transactions": transactions_created,
            "new_cash_balance": p.cash_balance
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"TradeStation API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/{pid}/import-ytd")
async def import_ytd_transactions(pid: str, body: dict, user_id: str = Header("default", alias="X-User-ID")):
    """
    Import all filled orders from TradeStation starting from 2025-01-01.
    Creates BUY/SELL transactions in the mindfolio for complete P&L tracking.
    
    Body: {
        "account_id": "11775499"  # TradeStation account ID
    }
    
    Returns:
        - transactions_imported: number of new transactions created
        - date_range: earliest and latest transaction dates
        - symbols: list of unique symbols found
    """
    from app.services.tradestation import get_valid_token
    import requests
    from datetime import datetime, timezone
    
    p = await pf_get(pid)
    if not p:
        raise HTTPException(status_code=404, detail=f"Mindfolio {pid} not found")
    
    account_id = body.get("account_id")
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id required")
    
    try:
        # Get TradeStation token
        token_data = await get_valid_token(user_id)
        if not token_data:
            raise HTTPException(status_code=401, detail="Not authenticated with TradeStation. Please login first.")
        
        token = token_data.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Invalid token data")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Determine API base URL
        ts_mode = os.getenv("TRADESTATION_MODE", "SIMULATION")
        ts_base = "https://api.tradestation.com/v3" if ts_mode == "LIVE" else "https://sim-api.tradestation.com/v3"
        
        # Fetch all orders since 2025-01-01
        since_date = "2025-01-01T00:00:00Z"
        orders_url = f"{ts_base}/brokerage/accounts/{account_id}/orders"
        params = {"since": since_date}
        
        logger.info(f"Fetching orders from TradeStation for account {account_id} since {since_date}")
        
        orders_resp = requests.get(orders_url, headers=headers, params=params, timeout=15)
        orders_resp.raise_for_status()
        orders_data = orders_resp.json()
        
        all_orders = orders_data.get("Orders", [])
        logger.info(f"Retrieved {len(all_orders)} orders from TradeStation")
        logger.info(f"Response has pagination? NextToken: {orders_data.get('NextToken', 'None')}")
        
        # Check for pagination and fetch all pages
        while orders_data.get("NextToken"):
            params["pageToken"] = orders_data["NextToken"]
            logger.info(f"Fetching next page with token: {orders_data['NextToken']}")
            
            orders_resp = requests.get(orders_url, headers=headers, params=params, timeout=15)
            orders_resp.raise_for_status()
            orders_data = orders_resp.json()
            
            page_orders = orders_data.get("Orders", [])
            all_orders.extend(page_orders)
            logger.info(f"Retrieved {len(page_orders)} more orders. Total so far: {len(all_orders)}")
        
        logger.info(f"Total orders retrieved after pagination: {len(all_orders)}")
        
        # Filter only FILLED orders (status: FLL or Filled)
        filled_orders = [o for o in all_orders if o.get("Status", "").upper() in ["FLL", "FILLED"]]
        logger.info(f"Found {len(filled_orders)} filled orders")
        
        # Debug: Log first order structure
        if filled_orders:
            logger.info(f"Sample order structure: {json.dumps(filled_orders[0], indent=2)}")
        
        if not filled_orders:
            return {
                "status": "success",
                "transactions_imported": 0,
                "message": "No filled orders found since 2025-01-01"
            }
        
        # Create transactions from filled orders
        cli = await get_kv()
        transactions_created = []
        symbols_set = set()
        earliest_date = None
        latest_date = None
        
        for order in filled_orders:
            # Extract order details
            symbol = order.get("Symbol", "")
            filled_qty = float(order.get("FilledQuantity", 0) or 0)
            avg_price = float(order.get("FilledPrice", 0) or order.get("LimitPrice", 0) or 0)
            
            # Determine side: BUY or SELL
            action = order.get("TradeAction", "").upper()
            side = "BUY" if action in ["BUY", "BUYTOOPEN", "BUYTOCOVER"] else "SELL"
            
            # Parse timestamp
            timestamp_str = order.get("ClosedDateTime") or order.get("FilledTimestamp") or order.get("TimeStamp", "")
            if timestamp_str:
                # Handle different timestamp formats
                try:
                    if timestamp_str.endswith("Z"):
                        order_datetime = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    else:
                        order_datetime = datetime.fromisoformat(timestamp_str)
                except:
                    order_datetime = datetime.now(timezone.utc)
            else:
                order_datetime = datetime.now(timezone.utc)
            
            # Track date range
            if not earliest_date or order_datetime < earliest_date:
                earliest_date = order_datetime
            if not latest_date or order_datetime > latest_date:
                latest_date = order_datetime
            
            symbols_set.add(symbol)
            
            # Create transaction
            now = datetime.utcnow().isoformat()
            tx = Transaction(
                id=f"tx_{secrets.token_hex(6)}",
                mindfolio_id=pid,
                account_id=account_id,
                datetime=order_datetime.isoformat(),
                symbol=symbol,
                side=side,
                qty=filled_qty,
                price=avg_price,
                fee=0.0,  # TODO: extract commission if available
                notes=f"Imported from TradeStation order {order.get('OrderID', '')}",
                created_at=now
            )
            
            # Save transaction to Redis
            await cli.set(key_transaction(tx.id), tx.json())
            
            # Update transaction list for mindfolio
            tx_list_raw = await cli.get(key_mindfolio_transactions(pid)) or "[]"
            tx_ids = json.loads(tx_list_raw)
            tx_ids.append(tx.id)
            await cli.set(key_mindfolio_transactions(pid), json.dumps(tx_ids))
            
            transactions_created.append({
                "symbol": symbol,
                "side": side,
                "qty": filled_qty,
                "price": avg_price,
                "datetime": order_datetime.isoformat()
            })
        
        # Recalculate positions from all transactions
        calculated_positions = await calculate_positions_fifo(pid)
        
        # Save positions to Redis
        positions_json = json.dumps([pos.dict() for pos in calculated_positions])
        await cli.set(key_mindfolio_positions(pid), positions_json)
        
        # Update mindfolio updated_at timestamp
        p.updated_at = datetime.utcnow().isoformat()
        await pf_put(p)
        
        return {
            "status": "success",
            "transactions_imported": len(transactions_created),
            "date_range": {
                "earliest": earliest_date.isoformat() if earliest_date else None,
                "latest": latest_date.isoformat() if latest_date else None
            },
            "symbols": sorted(list(symbols_set)),
            "positions_recalculated": len(calculated_positions),
            "sample_transactions": transactions_created[:5]  # Show first 5 as preview
        }
        
    except requests.RequestException as e:
        logger.error(f"TradeStation API error during YTD import: {e}")
        raise HTTPException(status_code=503, detail=f"TradeStation API error: {str(e)}")
    except Exception as e:
        logger.error(f"YTD import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/{pid}/stats")
async def stats(pid: str):
    """Get mindfolio statistics with real P&L data"""
    try:
        # Calculate real statistics from transactions
        positions = await calculate_positions_fifo(pid)
        realized_pnl_data = await calculate_realized_pnl(pid)

        # Calculate totals
        total_realized = sum(pnl.realized for pnl in realized_pnl_data)
        total_trades = sum(pnl.trades for pnl in realized_pnl_data)

        # Mindfolio NAV
        mindfolio = await pf_get(pid)

        return {
            "mindfolio_id": pid,
            "nav": mindfolio.cash_balance,
            "pnl_realized": round2(total_realized),
            "pnl_unrealized": 0,  # Will be calculated with live market data integration
            "positions_count": len(positions),
            "total_trades": total_trades,
            "win_rate": None,  # Calculated when sufficient trade history available
            "expectancy": None,  # Calculated when sufficient trade history available
            "max_dd": None,  # Calculated when sufficient trade history available
            "realized_pnl_by_symbol": [pnl.dict() for pnl in realized_pnl_data],
        }
    except Exception as e:
        # Fallback to basic stats
        mindfolio = await pf_get(pid)
        return {
            "mindfolio_id": pid,
            "nav": mindfolio.cash_balance,
            "pnl_realized": 0,
            "pnl_unrealized": 0,
            "error": str(e),
        }


# ——— Transaction Endpoints ———
@router.get("/{pid}/transactions", response_model=List[Transaction])
async def get_transactions(pid: str, symbol: Optional[str] = None):
    """Get all transactions for mindfolio, optionally filtered by symbol"""
    transactions = await get_mindfolio_transactions(pid)

    if symbol:
        symbol = symbol.upper()
        transactions = [tx for tx in transactions if tx.symbol == symbol]

    return transactions


@router.post("/{pid}/transactions", response_model=Transaction)
async def create_transaction(pid: str, body: TransactionCreate):
    """Create new transaction"""
    # Verify mindfolio exists
    await pf_get(pid)

    transaction = Transaction(
        id=f"tx_{str(uuid.uuid4()).replace('-', '')[:8]}",
        mindfolio_id=pid,
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
    # Verify mindfolio exists
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
        "mindfolio_id": pid,
        "message": f"Successfully imported {imported_count} transactions",
    }


# ——— Transaction CRUD Functions ———
async def tx_create(tx: Transaction) -> Transaction:
    """Save transaction"""
    cli = await get_kv()
    await cli.set(key_transaction(tx.id), json.dumps(tx.dict()))

    # Update mindfolio transaction list
    current_list = await cli.get(key_mindfolio_transactions(tx.mindfolio_id)) or "[]"
    tx_list = json.loads(current_list)
    if tx.id not in tx_list:
        tx_list.append(tx.id)
        await cli.set(key_mindfolio_transactions(tx.mindfolio_id), json.dumps(tx_list))

    return tx


async def tx_get(tid: str) -> Transaction:
    """Get transaction by ID"""
    cli = await get_kv()
    raw = await cli.get(key_transaction(tid))
    if not raw:
        raise HTTPException(404, f"Transaction {tid} not found")
    data = json.loads(raw)
    return Transaction(**data)


async def parse_csv_transactions(csv_data: str, mindfolio_id: str) -> List[Transaction]:
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
                mindfolio_id=mindfolio_id,
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


@router.get("/ts/oauth-callback")
async def tradestation_oauth_callback(code: str, state: str):
    """Handle OAuth2 callback from TradeStation"""
    try:
        from tradestation_auth_service import tradestation_auth_service as ts_auth

        result = ts_auth.handle_callback(code, state)
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
async def get_mindfolio_buckets(pid: str):
    """Get all buckets for a mindfolio"""
    try:
        # First verify mindfolio exists
        await pf_get(pid)

        # For now, return mock buckets data
        # TODO[OPS-002]: Implement actual database integration when available
        mindfolio_buckets = [
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
            "mindfolio_id": pid,
            "buckets": mindfolio_buckets,
            "total_buckets": len(mindfolio_buckets),
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to get mindfolio buckets: {str(e)}")


@router.post("/{pid}/buckets")
async def create_mindfolio_bucket(
    pid: str, name: str, start_value: float = 0, notes: Optional[str] = None
):
    """Create a new bucket for mindfolio"""
    try:
        # Verify mindfolio exists
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
            "mindfolio_id": pid,
        }

        return {
            "status": "success",
            "message": f"Bucket '{name}' created successfully",
            "bucket": bucket,
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to create bucket: {str(e)}")

    # ——— Analytics & Equity Charts Endpoint ———

    except Exception as e:
        raise HTTPException(500, f"Failed to create bucket: {str(e)}")


# ——— Analytics & Equity Charts Endpoint ———
@router.get("/{pid}/analytics/equity")
async def get_mindfolio_equity_chart(pid: str, timeframe: str = "1M"):
    """Get equity curve data for mindfolio analytics"""
    try:
        # Get mindfolio transactions
        transactions = await get_mindfolio_transactions(pid)
        realized_pnl = await calculate_realized_pnl(pid)
        positions = await calculate_positions_fifo(pid)

        # Calculate equity curve data points
        equity_data = []
        running_balance = 10000.0  # Starting balance

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
            current_equity += pos.cost_basis  # Simplified, needs current market value

        # Analytics metrics
        total_realized = sum(pnl.realized for pnl in realized_pnl)
        total_trades = sum(pnl.trades for pnl in realized_pnl)

        analytics = {
            "equity_curve": (
                equity_data[-50:] if len(equity_data) > 50 else equity_data
            ),  # Last 50 points
            "summary": {
                "current_equity": round(current_equity, 2),
                "total_realized_pnl": round(total_realized, 2),
                "total_trades": total_trades,
                "win_rate": None,  # TODO[OPS-004]: Calculate from profitable trades
                "sharpe_ratio": None,  # TODO[OPS-005]: Calculate from equity curve
                "max_drawdown": None,  # TODO[OPS-006]: Calculate from equity curve
                "positions_count": len(positions),
            },
            "buckets": [],  # TODO[OPS-007]: Implement bucket-level analytics
            "timeframe": timeframe,
            "generated_at": datetime.utcnow().isoformat(),
        }

        return {"status": "success", "mindfolio_id": pid, "analytics": analytics}

    except Exception as e:
        raise HTTPException(500, f"Failed to generate equity analytics: {str(e)}")


@router.get("/{pid}/analytics/equity.csv")
async def export_mindfolio_equity_csv(pid: str, timeframe: str = "1M"):
    """Export equity curve data as CSV file"""
    try:
        # Get equity data using existing endpoint
        equity_response = await get_mindfolio_equity_chart(pid, timeframe)
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
                )  # Simplified calculation

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
                "Content-Disposition": f"attachment; filename=mindfolio_{pid}_equity.csv"
            },
        )

    except Exception as e:
        raise HTTPException(500, f"Failed to export equity CSV: {str(e)}")


# ——— Budget check helper (pentru /trade/preview & /place) ———
async def mindfolio_budget_ok(
    pid: str, module: str, risk_cost: float
) -> tuple[bool, str]:
    """Check if mindfolio has budget for trade"""
    try:
        p = await pf_get(pid)

        if p.status != "ACTIVE":
            return False, "Mindfolio not active"

        # Find module allocation
        alloc = next((m for m in p.modules if m.module == module), None)
        if not alloc:
            return False, f"Module {module} not allocated"

        if risk_cost > alloc.max_risk_per_trade and alloc.max_risk_per_trade > 0:
            return False, "Exceeds max_risk_per_trade"

        if risk_cost > alloc.budget and alloc.budget > 0:
            return False, "Exceeds module budget"

        if risk_cost > p.cash_balance:
            return False, "Insufficient mindfolio cash"

        return True, "OK"

    except HTTPException:
        return False, "Mindfolio not found"
    except Exception as e:
        return False, f"Budget check failed: {str(e)}"


# ——— EOD (End-of-Day) Snapshots ———
class EODSnapshot(BaseModel):
    id: str
    mindfolio_id: str
    date: str  # YYYY-MM-DD in Europe/Bucharest timezone
    realized: float
    unrealized: float
    total: float  # realized + unrealized
    cash_balance: float
    positions_count: int
    timestamp: str  # ISO datetime of snapshot creation
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
        )  # 5% gain as fallback
        market_value = pos.qty * current_price
        unrealized += market_value - pos.cost_basis

    return unrealized


@router.post("/{pid}/analytics/eod/snapshot")
async def create_eod_snapshot(pid: str):
    """Create a new EOD snapshot for the mindfolio"""
    try:
        from datetime import datetime

        import pytz

        # Use Europe/Bucharest timezone as requested
        tz = pytz.timezone("Europe/Bucharest")
        now = datetime.now(tz)
        date_str = now.strftime("%Y-%m-%d")
        timestamp = now.isoformat()

        # Get mindfolio data
        mindfolio = await pf_get(pid)
        positions = await calculate_positions_fifo(pid)
        realized_pnl = await calculate_realized_pnl(pid)

        # Calculate realized P&L total
        total_realized = sum(pnl.realized for pnl in realized_pnl)

        # Calculate unrealized P&L from current positions
        total_unrealized = await _calculate_unrealized_pnl(positions)

        # Create snapshot
        snapshot = EODSnapshot(
            id=str(uuid.uuid4()),
            mindfolio_id=pid,
            date=date_str,
            realized=round(total_realized, 2),
            unrealized=round(total_unrealized, 2),
            total=round(total_realized + total_unrealized, 2),
            cash_balance=mindfolio.cash_balance,
            positions_count=len(positions),
            timestamp=timestamp,
            timezone="Europe/Bucharest",
        )

        # Store snapshot in Redis (optional cache)
        try:
            kv = await get_kv()
            snapshot_key = f"eod_snapshot:{pid}:{date_str}"
            await kv.set(snapshot_key, json.dumps(snapshot.dict()), ex=86400 * 90)  # 90 days
        except Exception:
            pass  # Redis cache is optional

        # Also add to series index (Redis cache)
        try:
            kv = await get_kv()
            series_key = f"eod_series:{pid}"
            existing_series = await kv.get(series_key)
            if existing_series:
                series = json.loads(existing_series)
            else:
                series = []

            # Update or add today's snapshot
            series = [
                s for s in series if s.get("date") != date_str
            ]  # Remove existing for today
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

            await kv.set(series_key, json.dumps(series), ex=86400 * 90)
        except Exception:
            pass  # Redis cache is optional

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
    """Get EOD snapshot series for the mindfolio"""
    try:
        # Try Redis cache first, fallback to sample data
        series = []
        try:
            kv = await get_kv()
            series_key = f"eod_series:{pid}"
            existing_series = await kv.get(series_key)
            if existing_series:
                series = json.loads(existing_series)
        except Exception:
            pass  # Redis cache is optional

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
                realized = base_realized + (i * 50) + (i * 25)  # Gradual increase
                unrealized = base_unrealized + (i * 30) - (i * 10)  # Some volatility

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
            "mindfolio_id": pid,
            "series": series,
            "count": len(series),
            "timezone": "Europe/Bucharest",
        }

    except Exception as e:
        logger.error(f"Failed to get EOD series for {pid}: {str(e)}")
        raise HTTPException(500, f"Failed to get EOD series: {str(e)}")


# ——— MODULE BUDGET TRACKING ———


async def get_module_budget_usage(pid: str, module_name: str) -> dict:
    """
    Calculate current budget usage for a specific module.
    Returns: {budget, used, available, positions_count, buying_power_used}
    """
    try:
        # Get mindfolio
        pf = await pf_get(pid)

        # Find module
        module = next((m for m in pf.modules if m.module == module_name), None)
        if not module:
            raise HTTPException(
                404, f"Module {module_name} not found in mindfolio {pid}"
            )

        # Get all transactions for this mindfolio
        await get_transactions(pid)

        # Filter transactions tagged with this module (we'll add module field to transactions)
        # For now, calculate based on all positions
        # TODO: Add module field to Transaction model

        # Get current positions
        positions = await get_positions(pid)

        # Calculate buying power used (simplified - would need real options Greeks)
        buying_power_used = 0
        positions_count = len(positions)

        for pos in positions:
            # Estimate buying power (for stocks: qty * avg_cost)
            buying_power_used += abs(pos.qty * pos.avg_cost)

            # TODO: More sophisticated calculation for options
            # Options buying power = max_loss of spread

        return {
            "module": module_name,
            "budget": module.budget,
            "used": buying_power_used,
            "available": module.budget - buying_power_used,
            "utilization_pct": (
                (buying_power_used / module.budget * 100) if module.budget > 0 else 0
            ),
            "positions_count": positions_count,
            "max_risk_per_trade": module.max_risk_per_trade,
            "daily_loss_limit": module.daily_loss_limit,
            "autotrade": module.autotrade,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get module budget usage: {str(e)}")
        raise HTTPException(500, f"Failed to get module budget usage: {str(e)}")


async def get_all_modules_budget_usage(pid: str) -> dict:
    """
    Get budget usage for all modules in a mindfolio.
    Returns aggregated stats across all modules.
    """
    try:
        pf = await pf_get(pid)

        modules_usage = []
        total_budget = 0
        total_used = 0

        for module in pf.modules:
            usage = await get_module_budget_usage(pid, module.module)
            modules_usage.append(usage)
            total_budget += module.budget
            total_used += usage["used"]

        # Calculate reserve (cash not allocated to modules)
        reserve = pf.cash_balance - total_budget

        return {
            "mindfolio_id": pid,
            "mindfolio_name": pf.name,
            "total_cash": pf.cash_balance,
            "total_budget_allocated": total_budget,
            "total_budget_used": total_used,
            "reserve_cash": reserve,
            "allocation_pct": (
                (total_budget / pf.cash_balance * 100) if pf.cash_balance > 0 else 0
            ),
            "utilization_pct": (
                (total_used / total_budget * 100) if total_budget > 0 else 0
            ),
            "modules": modules_usage,
            "module_count": len(pf.modules),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get all modules budget usage: {str(e)}")
        raise HTTPException(500, f"Failed to get all modules budget usage: {str(e)}")


def validate_module_budget_allocation(pf: Mindfolio) -> tuple[bool, str]:
    """
    Validate that module budgets don't exceed mindfolio cash.
    Returns: (is_valid, error_message)
    """
    total_allocated = sum(m.budget for m in pf.modules)

    if total_allocated > pf.cash_balance:
        return (
            False,
            f"Total module budgets (${total_allocated:,.2f}) exceed mindfolio cash (${pf.cash_balance:,.2f})",
        )

    # Check for duplicate modules
    module_names = [m.module for m in pf.modules]
    if len(module_names) != len(set(module_names)):
        return False, "Duplicate module names not allowed"

    # Validate individual module budgets
    for m in pf.modules:
        if m.budget < 0:
            return False, f"Module {m.module} has negative budget: ${m.budget}"

        if m.max_risk_per_trade < 0:
            return (
                False,
                f"Module {m.module} has negative max_risk_per_trade: ${m.max_risk_per_trade}",
            )

        if m.daily_loss_limit < 0:
            return (
                False,
                f"Module {m.module} has negative daily_loss_limit: ${m.daily_loss_limit}",
            )

        if m.max_risk_per_trade > m.budget:
            return (
                False,
                f"Module {m.module} max_risk_per_trade (${m.max_risk_per_trade}) exceeds budget (${m.budget})",
            )

    return True, ""


async def check_module_can_trade(
    pid: str, module_name: str, trade_risk: float
) -> tuple[bool, str]:
    """
    Check if a module has available budget and is within risk limits to execute a trade.
    Returns: (can_trade, reason)
    """
    try:
        # Get mindfolio
        pf = await pf_get(pid)

        # Check mindfolio status
        if pf.status != "ACTIVE":
            return False, f"Mindfolio status is {pf.status}, not ACTIVE"

        # Find module
        module = next((m for m in pf.modules if m.module == module_name), None)
        if not module:
            return False, f"Module {module_name} not found"

        # Check trade risk vs module limit
        if trade_risk > module.max_risk_per_trade:
            return (
                False,
                f"Trade risk ${trade_risk:,.2f} exceeds module max ${module.max_risk_per_trade:,.2f}",
            )

        # Check module budget usage
        usage = await get_module_budget_usage(pid, module_name)

        if usage["available"] < trade_risk:
            return (
                False,
                f"Insufficient budget: ${usage['available']:,.2f} available, ${trade_risk:,.2f} required",
            )

        # TODO: Check daily loss limit (requires tracking daily P&L per module)

        return True, "OK"

    except Exception as e:
        logger.error(f"Failed to check module can trade: {str(e)}")
        return False, f"Error checking module: {str(e)}"


# ——— API ENDPOINTS FOR MODULE BUDGET ———


@router.get("/{pid}/modules/budget")
async def get_modules_budget_endpoint(pid: str):
    """Get budget allocation and usage for all modules in a mindfolio"""
    return await get_all_modules_budget_usage(pid)


@router.get("/{pid}/modules/{module_name}/budget")
async def get_module_budget_endpoint(pid: str, module_name: str):
    """Get budget allocation and usage for a specific module"""
    return await get_module_budget_usage(pid, module_name)


@router.post("/{pid}/modules/{module_name}/check-trade")
async def check_module_trade_endpoint(pid: str, module_name: str, trade_risk: float):
    """Check if a module can execute a trade with given risk"""
    can_trade, reason = await check_module_can_trade(pid, module_name, trade_risk)

    if can_trade:
        return {"status": "success", "can_trade": True, "reason": reason}
    else:
        return {"status": "error", "can_trade": False, "reason": reason}
