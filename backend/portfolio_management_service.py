"""
Portfolio Management Service
Advanced portfolio management system with position movement capabilities
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
    portfolio_id: str
    added_date: datetime
    last_updated: datetime
    metadata: Dict[str, Any]  # Extra info like expiry for options

@dataclass
class Portfolio:
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
    from_portfolio_id: str
    to_portfolio_id: str
    move_date: datetime
    quantity_moved: float
    reason: str
    metadata: Dict[str, Any]

class PortfolioManagementService:
    def __init__(self):
        self.logger = logger
        # In-memory storage for MVP (will be replaced with MongoDB)
        self.portfolios: Dict[str, Portfolio] = {}
        self.positions: Dict[str, Position] = {}
        self.position_moves: List[PositionMove] = []
        
        # TradeStation client for real data
        self.ts_client = TradeStationClient()
        
        self._initialize_default_portfolios()
        # Note: We'll load real positions from TradeStation instead of mock data

    def _initialize_default_portfolios(self):
        """Initialize default portfolio structure"""
        default_portfolios = [
            {
                'id': 'tradestation-main',
                'name': 'TradeStation Main',
                'description': 'Main TradeStation account with live positions',
                'category': 'main',
                'settings': {
                    'is_main': True,
                    'sync_with_broker': True,
                    'auto_refresh': True
                }
            },
            {
                'id': 'long-term-portfolio',
                'name': 'Long Term Holdings',
                'description': 'Long-term stocks and LEAPS (1+ years)',
                'category': 'long_term',
                'settings': {
                    'target_allocation': {'stocks': 70, 'leaps': 30},
                    'rebalance_threshold': 0.05
                }
            },
            {
                'id': 'medium-term-portfolio',
                'name': 'Medium Term Trading',
                'description': 'Medium-term trades (3-12 months)',
                'category': 'medium_term',
                'settings': {
                    'target_allocation': {'stocks': 50, 'options': 50},
                    'max_position_size': 0.10
                }
            },
            {
                'id': 'short-term-portfolio',
                'name': 'Short Term Trading',
                'description': 'Short-term trades and scalping',
                'category': 'short_term',
                'settings': {
                    'target_allocation': {'options': 80, 'stocks': 20},
                    'max_holding_period': 30
                }
            }
        ]

        for portfolio_data in default_portfolios:
            portfolio = Portfolio(
                id=portfolio_data['id'],
                name=portfolio_data['name'],
                description=portfolio_data['description'],
                category=portfolio_data['category'],
                created_date=datetime.now(),
                last_updated=datetime.now(),
                total_value=0.0,
                total_pnl=0.0,
                positions_count=0,
                settings=portfolio_data['settings']
            )
            self.portfolios[portfolio.id] = portfolio

    async def _load_tradestation_positions(self, account_id: str = None):
        """Load real positions from TradeStation API"""
        try:
            if not account_id:
                # Get first available account
                accounts_response = await self.ts_client.get_accounts()
                if not accounts_response or not accounts_response.get('accounts'):
                    logger.warning("No TradeStation accounts found")
                    return
                account_id = accounts_response['accounts'][0]['AccountID']
                logger.info(f"Using TradeStation account: {account_id}")
            
            # Get positions from TradeStation
            ts_positions = await self.ts_client.get_positions(account_id)
            logger.info(f"Loaded {len(ts_positions)} positions from TradeStation")
            
            # Clear existing positions in TradeStation Main portfolio
            existing_ts_positions = [pos_id for pos_id, pos in self.positions.items() 
                                   if pos.portfolio_id == 'tradestation-main']
            for pos_id in existing_ts_positions:
                del self.positions[pos_id]
            
            # Convert TradeStation positions to our format
            for ts_pos in ts_positions:
                position_id = str(uuid.uuid4())
                
                # Calculate market value and P&L
                market_value = abs(ts_pos.quantity * ts_pos.mark_price)
                cost_basis = abs(ts_pos.quantity * ts_pos.average_price)
                unrealized_pnl = market_value - cost_basis
                
                # Determine position type
                position_type = 'stock' if ts_pos.asset_type == 'STOCK' else 'option'
                
                # Create metadata based on position type
                metadata = {
                    'asset_type': ts_pos.asset_type,
                    'account_id': account_id,
                    'ts_position_id': getattr(ts_pos, 'position_id', None)
                }
                
                if position_type == 'option':
                    # Add option-specific metadata if available
                    metadata.update({
                        'option_type': getattr(ts_pos, 'option_type', 'Unknown'),
                        'strike': getattr(ts_pos, 'strike_price', None),
                        'expiry': getattr(ts_pos, 'expiry_date', None)
                    })
                
                position = Position(
                    id=position_id,
                    symbol=ts_pos.symbol,
                    quantity=ts_pos.quantity,
                    avg_cost=ts_pos.average_price,
                    current_price=ts_pos.mark_price,
                    position_type=position_type,
                    market_value=market_value,
                    unrealized_pnl=unrealized_pnl,
                    portfolio_id='tradestation-main',
                    added_date=datetime.now(),
                    last_updated=datetime.now(),
                    metadata=metadata
                )
                
                self.positions[position_id] = position
            
            # Update TradeStation portfolio totals
            await self._update_portfolio_totals('tradestation-main')
            logger.info(f"Successfully loaded {len(ts_positions)} TradeStation positions")
            
        except Exception as e:
            logger.error(f"Error loading TradeStation positions: {str(e)}")
            # Fall back to mock data if TradeStation fails
            await self._initialize_mock_positions_fallback()

    async def _initialize_mock_positions_fallback(self):
        """Initialize mock positions in TradeStation Main portfolio as fallback"""
        logger.info("Using mock positions as fallback")
        mock_positions = [
            {
                'symbol': 'AAPL',
                'quantity': 100,
                'avg_cost': 185.50,
                'current_price': 189.25,
                'position_type': 'stock',
                'metadata': {'sector': 'Technology', 'source': 'mock'}
            },
            {
                'symbol': 'MSFT',
                'quantity': 50,
                'avg_cost': 385.20,
                'current_price': 392.45,
                'position_type': 'stock',
                'metadata': {'sector': 'Technology'}
            },
            {
                'symbol': 'TSLA',
                'quantity': 25,
                'avg_cost': 245.80,
                'current_price': 251.30,
                'position_type': 'stock',
                'metadata': {'sector': 'Automotive'}
            },
            {
                'symbol': 'NVDA Jan2026 LEAPS',
                'quantity': 5,
                'avg_cost': 45.20,
                'current_price': 52.80,
                'position_type': 'option',
                'metadata': {
                    'expiry': '2026-01-15',
                    'strike': 400,
                    'option_type': 'CALL',
                    'is_leap': True
                }
            },
            {
                'symbol': 'SPY Weekly Calls',
                'quantity': 10,
                'avg_cost': 3.20,
                'current_price': 2.95,
                'position_type': 'option',
                'metadata': {
                    'expiry': '2025-01-03',
                    'strike': 595,
                    'option_type': 'CALL',
                    'is_leap': False
                }
            },
            {
                'symbol': 'QQQ',
                'quantity': 75,
                'avg_cost': 485.60,
                'current_price': 491.20,
                'position_type': 'stock',
                'metadata': {'sector': 'ETF'}
            }
        ]

        for pos_data in mock_positions:
            market_value = pos_data['quantity'] * pos_data['current_price']
            cost_basis = pos_data['quantity'] * pos_data['avg_cost']
            unrealized_pnl = market_value - cost_basis

            position = Position(
                id=str(uuid.uuid4()),
                symbol=pos_data['symbol'],
                quantity=pos_data['quantity'],
                avg_cost=pos_data['avg_cost'],
                current_price=pos_data['current_price'],
                position_type=pos_data['position_type'],
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                portfolio_id='tradestation-main',
                added_date=datetime.now(),
                last_updated=datetime.now(),
                metadata=pos_data['metadata']
            )
            self.positions[position.id] = position

        # Update TradeStation portfolio totals
        self._update_portfolio_totals('tradestation-main')

    async def get_all_portfolios(self) -> List[Portfolio]:
        """Get all portfolios with their current totals"""
        portfolios = list(self.portfolios.values())
        
        # Update totals for each portfolio
        for portfolio in portfolios:
            self._update_portfolio_totals(portfolio.id)
        
        return portfolios

    async def get_portfolio_positions(self, portfolio_id: str) -> List[Position]:
        """Get all positions for a specific portfolio"""
        positions = [pos for pos in self.positions.values() if pos.portfolio_id == portfolio_id]
        return sorted(positions, key=lambda x: x.market_value, reverse=True)

    async def create_custom_portfolio(self, name: str, description: str, category: str = 'custom') -> Portfolio:
        """Create a new custom portfolio"""
        portfolio_id = str(uuid.uuid4())
        
        portfolio = Portfolio(
            id=portfolio_id,
            name=name,
            description=description,
            category=category,
            created_date=datetime.now(),
            last_updated=datetime.now(),
            total_value=0.0,
            total_pnl=0.0,
            positions_count=0,
            settings={}
        )
        
        self.portfolios[portfolio_id] = portfolio
        return portfolio

    async def move_position(
        self, 
        position_id: str, 
        to_portfolio_id: str, 
        quantity_to_move: Optional[float] = None,
        reason: str = "Manual move"
    ) -> Dict[str, Any]:
        """Move a position or partial position to another portfolio"""
        try:
            if position_id not in self.positions:
                raise ValueError(f"Position {position_id} not found")
            
            if to_portfolio_id not in self.portfolios:
                raise ValueError(f"Target portfolio {to_portfolio_id} not found")

            position = self.positions[position_id]
            from_portfolio_id = position.portfolio_id
            
            # If no specific quantity, move entire position
            if quantity_to_move is None:
                quantity_to_move = position.quantity

            if quantity_to_move > position.quantity:
                raise ValueError("Cannot move more than available quantity")

            # Create move record
            move_record = PositionMove(
                id=str(uuid.uuid4()),
                position_id=position_id,
                from_portfolio_id=from_portfolio_id,
                to_portfolio_id=to_portfolio_id,
                move_date=datetime.now(),
                quantity_moved=quantity_to_move,
                reason=reason,
                metadata={}
            )
            self.position_moves.append(move_record)

            if quantity_to_move == position.quantity:
                # Move entire position
                position.portfolio_id = to_portfolio_id
                position.last_updated = datetime.now()
            else:
                # Partial move - split position
                remaining_quantity = position.quantity - quantity_to_move
                
                # Update original position
                position.quantity = remaining_quantity
                position.market_value = remaining_quantity * position.current_price
                position.unrealized_pnl = (remaining_quantity * position.current_price) - (remaining_quantity * position.avg_cost)
                
                # Create new position in target portfolio
                new_position = Position(
                    id=str(uuid.uuid4()),
                    symbol=position.symbol,
                    quantity=quantity_to_move,
                    avg_cost=position.avg_cost,
                    current_price=position.current_price,
                    position_type=position.position_type,
                    market_value=quantity_to_move * position.current_price,
                    unrealized_pnl=(quantity_to_move * position.current_price) - (quantity_to_move * position.avg_cost),
                    portfolio_id=to_portfolio_id,
                    added_date=datetime.now(),
                    last_updated=datetime.now(),
                    metadata=position.metadata.copy()
                )
                self.positions[new_position.id] = new_position

            # Update portfolio totals
            self._update_portfolio_totals(from_portfolio_id)
            self._update_portfolio_totals(to_portfolio_id)

            return {
                'success': True,
                'move_id': move_record.id,
                'message': f'Moved {quantity_to_move} shares of {position.symbol} to {self.portfolios[to_portfolio_id].name}'
            }

        except Exception as e:
            self.logger.error(f"Error moving position: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_aggregate_view(self) -> Dict[str, Any]:
        """Get aggregated view of all portfolios"""
        all_positions = list(self.positions.values())
        
        total_value = sum(pos.market_value for pos in all_positions)
        total_pnl = sum(pos.unrealized_pnl for pos in all_positions)
        
        # Portfolio breakdown
        portfolio_breakdown = {}
        for portfolio in self.portfolios.values():
            portfolio_positions = [pos for pos in all_positions if pos.portfolio_id == portfolio.id]
            portfolio_value = sum(pos.market_value for pos in portfolio_positions)
            
            portfolio_breakdown[portfolio.id] = {
                'name': portfolio.name,
                'value': portfolio_value,
                'positions_count': len(portfolio_positions),
                'percentage': (portfolio_value / total_value * 100) if total_value > 0 else 0
            }
        
        # Asset type breakdown
        asset_breakdown = {}
        for pos in all_positions:
            asset_type = pos.position_type
            if asset_type not in asset_breakdown:
                asset_breakdown[asset_type] = {'value': 0, 'count': 0}
            asset_breakdown[asset_type]['value'] += pos.market_value
            asset_breakdown[asset_type]['count'] += 1

        return {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_positions': len(all_positions),
            'portfolio_breakdown': portfolio_breakdown,
            'asset_breakdown': asset_breakdown,
            'last_updated': datetime.now().isoformat()
        }

    async def get_move_history(self, portfolio_id: Optional[str] = None) -> List[PositionMove]:
        """Get move history, optionally filtered by portfolio"""
        moves = self.position_moves
        
        if portfolio_id:
            moves = [
                move for move in moves 
                if move.from_portfolio_id == portfolio_id or move.to_portfolio_id == portfolio_id
            ]
        
        return sorted(moves, key=lambda x: x.move_date, reverse=True)

    def _update_portfolio_totals(self, portfolio_id: str):
        """Update portfolio totals based on current positions"""
        if portfolio_id not in self.portfolios:
            return
        
        portfolio_positions = [pos for pos in self.positions.values() if pos.portfolio_id == portfolio_id]
        
        total_value = sum(pos.market_value for pos in portfolio_positions)
        total_pnl = sum(pos.unrealized_pnl for pos in portfolio_positions)
        
        self.portfolios[portfolio_id].total_value = total_value
        self.portfolios[portfolio_id].total_pnl = total_pnl
        self.portfolios[portfolio_id].positions_count = len(portfolio_positions)
        self.portfolios[portfolio_id].last_updated = datetime.now()

    async def get_available_portfolios_for_move(self, current_portfolio_id: str) -> List[Portfolio]:
        """Get list of portfolios available for moving positions to"""
        available = [
            portfolio for portfolio in self.portfolios.values() 
            if portfolio.id != current_portfolio_id
        ]
        return available