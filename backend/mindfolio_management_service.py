"""
Mindfolio Management Service
Advanced mindfolio management system with position movement capabilities
Integrated with TradeStation API for real-time data
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio

# Import TradeStation client for real data
from tradestation_client import TradeStationClient

logger = logging.getLogger(__name__)


@dataclass
class Position:
    id: str
    symbol: str
    quantity: float
    avg_cost: float
    current_price: float
    position_type: str  # 'stock', 'option', 'crypto'
    market_value: float
    unrealized_pnl: float
    mindfolio_id: str
    added_date: datetime
    last_updated: datetime
    metadata: Dict[str, Any]  # Extra info like expiry for options


@dataclass
class Mindfolio:
    id: str
    name: str
    description: str
    category: str  # 'long_term', 'medium_term', 'short_term', 'custom'
    created_date: datetime
    last_updated: datetime
    total_value: float
    total_pnl: float
    positions_count: int
    settings: Dict[str, Any]


@dataclass
class PositionMove:
    id: str
    position_id: str
    from_mindfolio_id: str
    to_mindfolio_id: str
    move_date: datetime
    quantity_moved: float
    reason: str
    metadata: Dict[str, Any]


class MindfolioManagementService:
    def __init__(self, ts_auth=None):
        self.logger = logger
        # In-memory storage for MVP (will be replaced with MongoDB)
        self.mindfolios: Dict[str, Mindfolio] = {}
        self.positions: Dict[str, Position] = {}
        self.position_moves: List[PositionMove] = []

        # TradeStation client for real data (optional)
        self.ts_client = None
        if ts_auth:
            try:
                from tradestation_client import TradeStationClient

                self.ts_client = TradeStationClient(ts_auth)
            except Exception as e:
                logger.warning(f"Failed to initialize TradeStation client: {e}")

        self._initialized = False

        self._initialize_default_mindfolios()
        # Note: We'll load real positions from TradeStation via initialize() method

    async def initialize(self):
        """Initialize the service with real TradeStation data"""
        if not self._initialized:
            try:
                await self._load_tradestation_positions()
                self._initialized = True
                logger.info(
                    "Mindfolio management service initialized with TradeStation data"
                )
            except Exception as e:
                logger.error(f"Failed to initialize with TradeStation data: {str(e)}")
                await self._initialize_mock_positions_fallback()
                self._initialized = True

    def _initialize_default_mindfolios(self):
        """Initialize default mindfolio structure"""
        default_mindfolios = [
            {
                "id": "tradestation-main",
                "name": "TradeStation Main",
                "description": "Main TradeStation account with live positions",
                "category": "main",
                "settings": {
                    "is_main": True,
                    "sync_with_broker": True,
                    "auto_refresh": True,
                },
            },
            {
                "id": "long-term-mindfolio",
                "name": "Long Term Holdings",
                "description": "Long-term stocks and LEAPS (1+ years)",
                "category": "long_term",
                "settings": {
                    "target_allocation": {"stocks": 70, "leaps": 30},
                    "rebalance_threshold": 0.05,
                },
            },
            {
                "id": "medium-term-mindfolio",
                "name": "Medium Term Trading",
                "description": "Medium-term trades (3-12 months)",
                "category": "medium_term",
                "settings": {
                    "target_allocation": {"stocks": 50, "options": 50},
                    "max_position_size": 0.10,
                },
            },
            {
                "id": "short-term-mindfolio",
                "name": "Short Term Trading",
                "description": "Short-term trades and scalping",
                "category": "short_term",
                "settings": {
                    "target_allocation": {"options": 80, "stocks": 20},
                    "max_holding_period": 30,
                },
            },
        ]

        for mindfolio_data in default_mindfolios:
            mindfolio = Mindfolio(
                id=mindfolio_data["id"],
                name=mindfolio_data["name"],
                description=mindfolio_data["description"],
                category=mindfolio_data["category"],
                created_date=datetime.now(),
                last_updated=datetime.now(),
                total_value=0.0,
                total_pnl=0.0,
                positions_count=0,
                settings=mindfolio_data["settings"],
            )
            self.mindfolios[mindfolio.id] = mindfolio

    async def _load_tradestation_positions(self, account_id: str = None):
        """Load real positions from TradeStation API - NO MOCK DATA ALLOWED"""
        try:
            logger.info("🔄 Loading REAL TradeStation positions (NO MOCK DATA)")

            # Use the existing TradeStation client instance from server.py
            import requests
            import os

            # Get accounts using direct API call (same pattern as IndividualMindfolio component)
            base_url = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")

            # Try direct API call first
            accounts_response = requests.get(
                f"{base_url}/api/tradestation/accounts", timeout=30
            )
            if accounts_response.status_code != 200:
                logger.error(
                    f" TradeStation accounts API failed: {accounts_response.status_code}"
                )
                raise Exception("TradeStation accounts API not accessible")

            accounts_data = accounts_response.json()
            if not accounts_data.get("accounts"):
                logger.error(" No TradeStation accounts found")
                raise Exception("No TradeStation accounts available")

            if not account_id:
                # Use first margin account or first available
                target_account = None
                for acc in accounts_data["accounts"]:
                    if acc.get("Type") == "Margin":
                        target_account = acc
                        break
                if not target_account:
                    target_account = accounts_data["accounts"][0]
                account_id = target_account["AccountID"]

            logger.info(f" Using TradeStation account: {account_id}")

            # Get positions from TradeStation - DIRECT API CALL
            positions_response = requests.get(
                f"{base_url}/api/tradestation/accounts/{account_id}/positions",
                timeout=30,
            )
            if positions_response.status_code != 200:
                logger.error(
                    f" TradeStation positions API failed: {positions_response.status_code}"
                )
                raise Exception("TradeStation positions API not accessible")

            ts_positions_response = positions_response.json()

            # Extract positions from response structure
            ts_positions = ts_positions_response.get("positions", [])
            logger.info(
                f" Retrieved {len(ts_positions)} REAL positions from TradeStation API"
            )

            # Clear existing positions in TradeStation Main mindfolio
            existing_ts_positions = [
                pos_id
                for pos_id, pos in self.positions.items()
                if pos.mindfolio_id == "tradestation-main"
            ]
            for pos_id in existing_ts_positions:
                del self.positions[pos_id]

            # Convert TradeStation positions to our format - REAL DATA ONLY
            total_value = 0
            total_pnl = 0

            for ts_pos in ts_positions:
                position_id = str(uuid.uuid4())

                # Use real TradeStation data fields (dictionary format from API)
                quantity = ts_pos.get("quantity", 0)
                current_price = ts_pos.get("mark_price", ts_pos.get("current_price", 0))
                avg_cost = ts_pos.get("average_price", ts_pos.get("avg_cost", 0))
                market_value = (
                    ts_pos.get("market_value", abs(quantity * current_price))
                    if ts_pos.get("market_value")
                    else abs(quantity * current_price)
                )
                unrealized_pnl = ts_pos.get("unrealized_pnl", 0)

                # Determine position type from TradeStation data
                asset_type = ts_pos.get("asset_type", "UNKNOWN")
                position_type = (
                    "stock"
                    if asset_type == "STOCK"
                    else (
                        "option"
                        if asset_type in ["STOCKOPTION", "OPTION"]
                        else "unknown"
                    )
                )

                # Create metadata with REAL TradeStation source
                metadata = {
                    "asset_type": asset_type,
                    "account_id": account_id,
                    "source": "tradestation_live_api",  # MARK AS REAL DATA
                    "last_sync": datetime.now().isoformat(),
                }

                # Add option-specific metadata if available
                if position_type == "option":
                    metadata.update(
                        {
                            "option_type": ts_pos.get("option_type", "Unknown"),
                            "strike_price": ts_pos.get("strike_price", None),
                            "expiration_date": ts_pos.get("expiration_date", None),
                            "underlying_symbol": ts_pos.get("underlying_symbol", None),
                        }
                    )

                # Create Position object with REAL TradeStation data
                position = Position(
                    id=position_id,
                    symbol=ts_pos.get("symbol", "UNKNOWN"),
                    quantity=quantity,
                    avg_cost=avg_cost,
                    current_price=current_price,
                    position_type=position_type,
                    market_value=market_value,
                    unrealized_pnl=unrealized_pnl,
                    mindfolio_id="tradestation-main",
                    added_date=datetime.now(),
                    last_updated=datetime.now(),
                    metadata=metadata,
                )

                self.positions[position_id] = position
                total_value += market_value
                total_pnl += unrealized_pnl
                logger.debug(
                    f" Added REAL position: {position.symbol} ({position.quantity} {position.position_type})"
                )

            # Update TradeStation mindfolio totals with REAL data
            if "tradestation-main" in self.mindfolios:
                self.mindfolios["tradestation-main"].total_value = total_value
                self.mindfolios["tradestation-main"].total_pnl = total_pnl
                self.mindfolios["tradestation-main"].positions_count = len(ts_positions)
                self.mindfolios["tradestation-main"].last_updated = datetime.now()

            logger.info(
                f" Successfully loaded {len(ts_positions)} REAL TradeStation positions - NO MOCK DATA USED"
            )
            logger.info(
                f" Mindfolio totals: ${total_value:,.2f} value, ${total_pnl:,.2f} P&L"
            )

        except Exception as e:
            logger.error(f" CRITICAL ERROR loading TradeStation positions: {str(e)}")
            # DO NOT FALL BACK TO MOCK DATA - RAISE ERROR INSTEAD
            raise Exception(
                f"Failed to load real TradeStation positions: {str(e)}. Mock data is disabled."
            )

    async def _initialize_mock_positions_fallback(self):
        """Initialize mock positions in TradeStation Main mindfolio as fallback"""
        logger.info(
            "Using mock positions as fallback - simulating 84 positions (19 stocks, 65 options)"
        )

        # Clear existing positions first
        existing_ts_positions = [
            pos_id
            for pos_id, pos in self.positions.items()
            if pos.mindfolio_id == "tradestation-main"
        ]
        for pos_id in existing_ts_positions:
            del self.positions[pos_id]

        # Mock stock positions (19 stocks)
        stock_positions = [
            {
                "symbol": "AAPL",
                "quantity": 100,
                "avg_cost": 185.50,
                "current_price": 189.25,
            },
            {
                "symbol": "MSFT",
                "quantity": 50,
                "avg_cost": 385.20,
                "current_price": 392.45,
            },
            {
                "symbol": "GOOGL",
                "quantity": 25,
                "avg_cost": 2750.00,
                "current_price": 2820.30,
            },
            {
                "symbol": "AMZN",
                "quantity": 30,
                "avg_cost": 3200.00,
                "current_price": 3350.75,
            },
            {
                "symbol": "TSLA",
                "quantity": 40,
                "avg_cost": 235.60,
                "current_price": 248.45,
            },
            {
                "symbol": "NVDA",
                "quantity": 20,
                "avg_cost": 875.30,
                "current_price": 925.65,
            },
            {
                "symbol": "META",
                "quantity": 35,
                "avg_cost": 485.20,
                "current_price": 502.80,
            },
            {
                "symbol": "NFLX",
                "quantity": 15,
                "avg_cost": 625.40,
                "current_price": 645.90,
            },
            {
                "symbol": "QQQ",
                "quantity": 200,
                "avg_cost": 365.75,
                "current_price": 372.80,
            },
            {
                "symbol": "SPY",
                "quantity": 150,
                "avg_cost": 435.20,
                "current_price": 442.15,
            },
            {
                "symbol": "IWM",
                "quantity": 100,
                "avg_cost": 218.30,
                "current_price": 224.75,
            },
            {
                "symbol": "DIA",
                "quantity": 75,
                "avg_cost": 445.60,
                "current_price": 448.90,
            },
            {
                "symbol": "VTI",
                "quantity": 80,
                "avg_cost": 245.80,
                "current_price": 251.20,
            },
            {
                "symbol": "ARKK",
                "quantity": 60,
                "avg_cost": 68.90,
                "current_price": 72.45,
            },
            {
                "symbol": "XLK",
                "quantity": 45,
                "avg_cost": 185.30,
                "current_price": 192.80,
            },
            {
                "symbol": "JPM",
                "quantity": 25,
                "avg_cost": 165.40,
                "current_price": 172.90,
            },
            {
                "symbol": "JNJ",
                "quantity": 30,
                "avg_cost": 158.70,
                "current_price": 162.45,
            },
            {
                "symbol": "PG",
                "quantity": 40,
                "avg_cost": 145.20,
                "current_price": 148.90,
            },
            {"symbol": "KO", "quantity": 50, "avg_cost": 58.30, "current_price": 61.75},
        ]

        # Mock option positions (65 options)
        option_positions = []
        option_symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "NVDA",
            "META",
            "NFLX",
            "QQQ",
            "SPY",
        ]
        option_types = ["CALL", "PUT"]

        for i in range(65):
            symbol = option_symbols[i % len(option_symbols)]
            option_type = option_types[i % 2]
            strike_base = {
                "AAPL": 190,
                "MSFT": 390,
                "GOOGL": 2800,
                "AMZN": 3300,
                "TSLA": 250,
                "NVDA": 900,
                "META": 500,
                "NFLX": 640,
                "QQQ": 370,
                "SPY": 440,
            }

            strike = strike_base.get(symbol, 100) + (i % 10 - 5) * 5  # Vary strikes
            expiry_months = [
                "2024-12-20",
                "2025-01-17",
                "2025-02-21",
                "2025-03-21",
                "2025-06-20",
                "2026-01-15",
            ]

            option_positions.append(
                {
                    "symbol": f"{symbol}_{expiry_months[i % len(expiry_months)]}_{strike}_{option_type}",
                    "underlying": symbol,
                    "quantity": 1 + (i % 5),  # 1-5 contracts
                    "avg_cost": 5.50 + (i % 20),  # $5.50 - $24.50 per contract
                    "current_price": 6.25 + (i % 18),  # Current option price
                    "option_type": option_type,
                    "strike": strike,
                    "expiry": expiry_months[i % len(expiry_months)],
                }
            )

        # Add stock positions
        for pos_data in stock_positions:
            position_id = str(uuid.uuid4())
            market_value = abs(pos_data["quantity"]) * pos_data["current_price"]
            cost_basis = abs(pos_data["quantity"]) * pos_data["avg_cost"]
            unrealized_pnl = market_value - cost_basis

            position = Position(
                id=position_id,
                symbol=pos_data["symbol"],
                quantity=pos_data["quantity"],
                avg_cost=pos_data["avg_cost"],
                current_price=pos_data["current_price"],
                position_type="stock",
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                mindfolio_id="tradestation-main",
                added_date=datetime.now(),
                last_updated=datetime.now(),
                metadata={
                    "sector": "Various",
                    "source": "mock_fallback",
                    "asset_type": "STOCK",
                },
            )

            self.positions[position_id] = position

        # Add option positions
        for pos_data in option_positions:
            position_id = str(uuid.uuid4())
            market_value = (
                abs(pos_data["quantity"]) * pos_data["current_price"] * 100
            )  # Options are per 100 shares
            cost_basis = abs(pos_data["quantity"]) * pos_data["avg_cost"] * 100
            unrealized_pnl = market_value - cost_basis

            position = Position(
                id=position_id,
                symbol=pos_data["symbol"],
                quantity=pos_data["quantity"],
                avg_cost=pos_data["avg_cost"],
                current_price=pos_data["current_price"],
                position_type="option",
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                mindfolio_id="tradestation-main",
                added_date=datetime.now(),
                last_updated=datetime.now(),
                metadata={
                    "underlying_symbol": pos_data["underlying"],
                    "option_type": pos_data["option_type"],
                    "strike_price": pos_data["strike"],
                    "expiration_date": pos_data["expiry"],
                    "source": "mock_fallback",
                    "asset_type": "OPTION",
                },
            )

            self.positions[position_id] = position

        logger.info(
            f"Initialized {len(stock_positions)} stock positions and {len(option_positions)} option positions"
        )

        # Update mindfolio totals
        await self._update_mindfolio_totals("tradestation-main")

    async def _update_mindfolio_totals(self, mindfolio_id: str):
        """Update mindfolio total value and P&L based on positions"""
        if mindfolio_id not in self.mindfolios:
            return

        mindfolio_positions = [
            pos for pos in self.positions.values() if pos.mindfolio_id == mindfolio_id
        ]

        total_value = sum(pos.market_value for pos in mindfolio_positions)
        total_pnl = sum(pos.unrealized_pnl for pos in mindfolio_positions)
        positions_count = len(mindfolio_positions)

        self.mindfolios[mindfolio_id].total_value = total_value
        self.mindfolios[mindfolio_id].total_pnl = total_pnl
        self.mindfolios[mindfolio_id].positions_count = positions_count
        self.mindfolios[mindfolio_id].last_updated = datetime.now()

        logger.info(
            f"Updated mindfolio {mindfolio_id}: ${total_value:.2f} value, {positions_count} positions"
        )

    async def get_all_mindfolios(self) -> List[Mindfolio]:
        """Get all mindfolios with their current totals"""
        mindfolios = list(self.mindfolios.values())

        # Update totals for each mindfolio
        for mindfolio in mindfolios:
            await self._update_mindfolio_totals(mindfolio.id)

        return mindfolios

    async def get_mindfolio_positions(self, mindfolio_id: str) -> List[Position]:
        """Get all positions for a specific mindfolio"""
        # If requesting TradeStation main mindfolio, try to load fresh data
        if mindfolio_id == "tradestation-main":
            try:
                await self._load_tradestation_positions()
                logger.info("Refreshed TradeStation positions")
            except Exception as e:
                logger.error(f"Failed to refresh TradeStation positions: {str(e)}")
                # Continue with existing/cached data

        positions = [
            pos for pos in self.positions.values() if pos.mindfolio_id == mindfolio_id
        ]
        return sorted(positions, key=lambda x: x.market_value, reverse=True)

    async def create_custom_mindfolio(
        self, name: str, description: str, category: str = "custom"
    ) -> Mindfolio:
        """Create a new custom mindfolio"""
        mindfolio_id = str(uuid.uuid4())

        mindfolio = Mindfolio(
            id=mindfolio_id,
            name=name,
            description=description,
            category=category,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            total_value=0.0,
            total_pnl=0.0,
            positions_count=0,
            settings={},
        )

        self.mindfolios[mindfolio_id] = mindfolio
        return mindfolio

    async def move_position(
        self,
        position_id: str,
        to_mindfolio_id: str,
        quantity_to_move: Optional[float] = None,
        reason: str = "Manual move",
    ) -> Dict[str, Any]:
        """Move a position or partial position to another mindfolio"""
        try:
            if position_id not in self.positions:
                raise ValueError(f"Position {position_id} not found")

            if to_mindfolio_id not in self.mindfolios:
                raise ValueError(f"Target mindfolio {to_mindfolio_id} not found")

            position = self.positions[position_id]
            from_mindfolio_id = position.mindfolio_id

            # If no specific quantity, move entire position
            if quantity_to_move is None:
                quantity_to_move = position.quantity

            if quantity_to_move > position.quantity:
                raise ValueError("Cannot move more than available quantity")

            # Create move record
            move_record = PositionMove(
                id=str(uuid.uuid4()),
                position_id=position_id,
                from_mindfolio_id=from_mindfolio_id,
                to_mindfolio_id=to_mindfolio_id,
                move_date=datetime.now(),
                quantity_moved=quantity_to_move,
                reason=reason,
                metadata={},
            )
            self.position_moves.append(move_record)

            if quantity_to_move == position.quantity:
                # Move entire position
                position.mindfolio_id = to_mindfolio_id
                position.last_updated = datetime.now()
            else:
                # Partial move - split position
                remaining_quantity = position.quantity - quantity_to_move

                # Update original position
                position.quantity = remaining_quantity
                position.market_value = remaining_quantity * position.current_price
                position.unrealized_pnl = (
                    remaining_quantity * position.current_price
                ) - (remaining_quantity * position.avg_cost)

                # Create new position in target mindfolio
                new_position = Position(
                    id=str(uuid.uuid4()),
                    symbol=position.symbol,
                    quantity=quantity_to_move,
                    avg_cost=position.avg_cost,
                    current_price=position.current_price,
                    position_type=position.position_type,
                    market_value=quantity_to_move * position.current_price,
                    unrealized_pnl=(quantity_to_move * position.current_price)
                    - (quantity_to_move * position.avg_cost),
                    mindfolio_id=to_mindfolio_id,
                    added_date=datetime.now(),
                    last_updated=datetime.now(),
                    metadata=position.metadata.copy(),
                )
                self.positions[new_position.id] = new_position

            # Update mindfolio totals
            await self._update_mindfolio_totals(from_mindfolio_id)
            await self._update_mindfolio_totals(to_mindfolio_id)

            return {
                "success": True,
                "move_id": move_record.id,
                "message": f"Moved {quantity_to_move} shares of {position.symbol} to {self.mindfolios[to_mindfolio_id].name}",
            }

        except Exception as e:
            self.logger.error(f"Error moving position: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_aggregate_view(self) -> Dict[str, Any]:
        """Get aggregated view of all mindfolios"""
        all_positions = list(self.positions.values())

        total_value = sum(pos.market_value for pos in all_positions)
        total_pnl = sum(pos.unrealized_pnl for pos in all_positions)

        # Mindfolio breakdown
        mindfolio_breakdown = {}
        for mindfolio in self.mindfolios.values():
            mindfolio_positions = [
                pos for pos in all_positions if pos.mindfolio_id == mindfolio.id
            ]
            mindfolio_value = sum(pos.market_value for pos in mindfolio_positions)

            mindfolio_breakdown[mindfolio.id] = {
                "name": mindfolio.name,
                "value": mindfolio_value,
                "positions_count": len(mindfolio_positions),
                "percentage": (
                    (mindfolio_value / total_value * 100) if total_value > 0 else 0
                ),
            }

        # Asset type breakdown
        asset_breakdown = {}
        for pos in all_positions:
            asset_type = pos.position_type
            if asset_type not in asset_breakdown:
                asset_breakdown[asset_type] = {"value": 0, "count": 0}
            asset_breakdown[asset_type]["value"] += pos.market_value
            asset_breakdown[asset_type]["count"] += 1

        return {
            "total_value": total_value,
            "total_pnl": total_pnl,
            "total_positions": len(all_positions),
            "mindfolio_breakdown": mindfolio_breakdown,
            "asset_breakdown": asset_breakdown,
            "last_updated": datetime.now().isoformat(),
        }

    async def get_move_history(
        self, mindfolio_id: Optional[str] = None
    ) -> List[PositionMove]:
        """Get move history, optionally filtered by mindfolio"""
        moves = self.position_moves

        if mindfolio_id:
            moves = [
                move
                for move in moves
                if move.from_mindfolio_id == mindfolio_id
                or move.to_mindfolio_id == mindfolio_id
            ]

        return sorted(moves, key=lambda x: x.move_date, reverse=True)

    async def get_available_mindfolios_for_move(
        self, current_mindfolio_id: str
    ) -> List[Mindfolio]:
        """Get list of mindfolios available for moving positions to"""
        available = [
            mindfolio
            for mindfolio in self.mindfolios.values()
            if mindfolio.id != current_mindfolio_id
        ]
        return available
