"""
TradeStation API Client
Handles all interactions with TradeStation API for portfolio data and trading functionality
"""

import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from fastapi import HTTPException

from tradestation_auth import TradeStationAuth

logger = logging.getLogger(__name__)

class TradingEnvironment(Enum):
    SIMULATION = "sim-api.tradestation.com"
    LIVE = "api.tradestation.com"

class OrderStatus(Enum):
    PENDING = "PND"
    FILLED = "FLL"
    CANCELLED = "CAN"
    REJECTED = "REJ"
    PARTIALLY_FILLED = "PFL"

class AssetType(Enum):
    STOCK = "EQ"
    OPTION = "OP"
    FUTURE = "FU"

@dataclass
class Quote:
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int
    timestamp: datetime
    change: float
    change_percent: float

@dataclass
class Position:
    account_id: str
    symbol: str
    asset_type: str
    quantity: int
    average_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float

@dataclass
class Order:
    order_id: str
    account_id: str
    symbol: str
    asset_type: str
    quantity: int
    order_type: str
    price: Optional[float]
    status: str
    filled_quantity: int
    remaining_quantity: int
    timestamp: datetime

class TradeStationClient:
    """Main client for TradeStation API interactions"""
    
    def __init__(self, auth_handler: TradeStationAuth):
        self.auth = auth_handler
        self.base_url = auth_handler.api_base
        self.session = None
        
        logger.info(f"TradeStation client initialized for {auth_handler.environment} environment")
        logger.info(f"Base URL: {self.base_url}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to TradeStation API"""
        try:
            # Ensure valid token
            await self.auth.ensure_valid_token()
            
            # Construct URL
            url = f"{self.base_url}{endpoint}"
            
            # Get headers with auto-refresh
            headers = await self.auth.get_auth_headers()
            
            # Initialize session if needed
            if self.session is None:
                self.session = httpx.AsyncClient(timeout=30.0)
            
            logger.debug(f"Making {method} request to {url}")
            
            # Make request
            response = await self.session.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json() if response.content else {}
                logger.debug(f"Request successful: {method} {endpoint}")
                return result
            elif response.status_code == 429:
                logger.warning(f"Rate limit exceeded for {endpoint}")
                raise HTTPException(
                    status_code=429, 
                    detail="TradeStation API rate limit exceeded. Please wait before retrying."
                )
            elif response.status_code == 401:
                logger.error(f"Authentication failed for {endpoint}")
                raise HTTPException(
                    status_code=401, 
                    detail="TradeStation authentication failed. Please re-authenticate."
                )
            elif response.status_code == 403:
                logger.error(f"Access forbidden for {endpoint}")
                raise HTTPException(
                    status_code=403, 
                    detail="Access forbidden. Check account permissions or subscription status."
                )
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"TradeStation API request failed: {response.text}"
                )
                
        except httpx.RequestError as e:
            logger.error(f"Network error in API request: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Network error communicating with TradeStation: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in API request: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Unexpected error in TradeStation API request: {str(e)}"
            )
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test API connection and authentication"""
        try:
            # Try to get user info or accounts
            response = await self._make_request("GET", "/brokerage/accounts")
            
            return {
                "status": "success",
                "message": "Successfully connected to TradeStation API",
                "environment": self.auth.environment,
                "accounts_found": len(response.get("Accounts", [])),
                "timestamp": datetime.now().isoformat()
            }
            
        except HTTPException as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {e.detail}",
                "environment": self.auth.environment,
                "timestamp": datetime.now().isoformat()
            }
    
    # === ACCOUNT METHODS ===
    
    async def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts accessible to the user"""
        response = await self._make_request("GET", "/brokerage/accounts")
        accounts = response.get("Accounts", [])
        
        logger.info(f"Retrieved {len(accounts)} accounts")
        return accounts
    
    async def get_account_balances(self, account_id: str) -> Dict[str, Any]:
        """Get account balance information"""
        response = await self._make_request("GET", f"/brokerage/accounts/{account_id}/balances")
        logger.debug(f"Retrieved balances for account {account_id}")
        return response
    
    # === POSITIONS METHODS ===
    
    async def get_positions(self, account_id: str) -> List[Position]:
        """Get current positions for an account"""
        response = await self._make_request("GET", f"/brokerage/accounts/{account_id}/positions")
        positions = []
        
        for pos_data in response.get("Positions", []):
            try:
                position = Position(
                    account_id=account_id,
                    symbol=pos_data.get("Symbol", ""),
                    asset_type=pos_data.get("AssetType", ""),
                    quantity=int(pos_data.get("Quantity", 0)),
                    average_price=float(pos_data.get("AveragePrice", 0.0)),
                    current_price=float(pos_data.get("Last", 0.0)),
                    market_value=float(pos_data.get("MarketValue", 0.0)),
                    unrealized_pnl=float(pos_data.get("UnrealizedProfitLoss", 0.0)),
                    unrealized_pnl_percent=float(pos_data.get("UnrealizedProfitLossPercent", 0.0))
                )
                positions.append(position)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing position data for {pos_data.get('Symbol', 'unknown')}: {e}")
                continue
        
        logger.info(f"Retrieved {len(positions)} positions for account {account_id}")
        return positions
    
    # === ORDERS METHODS ===
    
    async def get_orders(self, account_id: str, since_date: Optional[datetime] = None) -> List[Order]:
        """Get orders for an account"""
        params = {}
        if since_date:
            params["since"] = since_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            
        response = await self._make_request("GET", f"/brokerage/accounts/{account_id}/orders", params=params)
        orders = []
        
        for order_data in response.get("Orders", []):
            try:
                # Parse timestamp
                timestamp_str = order_data.get("TimeStamp", "")
                if timestamp_str:
                    # Handle different timestamp formats
                    if timestamp_str.endswith('Z'):
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    timestamp = datetime.now()
                
                order = Order(
                    order_id=order_data.get("OrderID", ""),
                    account_id=account_id,
                    symbol=order_data.get("Symbol", ""),
                    asset_type=order_data.get("AssetType", ""),
                    quantity=int(order_data.get("Quantity", 0)),
                    order_type=order_data.get("OrderType", ""),
                    price=float(order_data.get("LimitPrice")) if order_data.get("LimitPrice") else None,
                    status=order_data.get("Status", ""),
                    filled_quantity=int(order_data.get("FilledQuantity", 0)),
                    remaining_quantity=int(order_data.get("RemainingQuantity", 0)),
                    timestamp=timestamp
                )
                orders.append(order)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing order data for {order_data.get('OrderID', 'unknown')}: {e}")
                continue
        
        logger.info(f"Retrieved {len(orders)} orders for account {account_id}")
        return orders
    
    # === MARKET DATA METHODS ===
    
    async def get_quote(self, symbols: Union[str, List[str]]) -> List[Quote]:
        """Get current quotes for symbols"""
        if isinstance(symbols, str):
            symbols = [symbols]
            
        symbol_param = ",".join(symbols)
        response = await self._make_request("GET", f"/marketdata/quotes/{symbol_param}")
        quotes = []
        
        for quote_data in response.get("Quotes", []):
            try:
                # Parse timestamp
                timestamp_str = quote_data.get("TimeStamp", "")
                if timestamp_str:
                    if timestamp_str.endswith('Z'):
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    timestamp = datetime.now()
                
                quote = Quote(
                    symbol=quote_data.get("Symbol", ""),
                    bid=float(quote_data.get("Bid", 0.0)),
                    ask=float(quote_data.get("Ask", 0.0)),
                    last=float(quote_data.get("Last", 0.0)),
                    volume=int(quote_data.get("Volume", 0)),
                    timestamp=timestamp,
                    change=float(quote_data.get("NetChange", 0.0)),
                    change_percent=float(quote_data.get("NetChangePercent", 0.0))
                )
                quotes.append(quote)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing quote data for {quote_data.get('Symbol', 'unknown')}: {e}")
                continue
        
        logger.debug(f"Retrieved quotes for {len(quotes)} symbols")
        return quotes
    
    async def get_historical_bars(
        self, 
        symbol: str, 
        interval: int, 
        unit: str, 
        bars_back: int = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """Get historical bar data for a symbol"""
        params = {
            "interval": interval,
            "unit": unit
        }
        
        if bars_back:
            params["barsback"] = bars_back
        if start_date:
            params["firstdate"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["lastdate"] = end_date.strftime("%Y-%m-%d")
            
        response = await self._make_request("GET", f"/marketdata/barcharts/{symbol}", params=params)
        bars = response.get("Bars", [])
        
        logger.debug(f"Retrieved {len(bars)} historical bars for {symbol}")
        return bars
    
    # === TRADING METHODS ===
    
    async def place_order(
        self,
        account_id: str,
        symbol: str,
        quantity: int,
        order_type: str = "Market",
        price: Optional[float] = None,
        time_in_force: str = "DAY"
    ) -> Dict[str, Any]:
        """Place a trading order"""
        order_data = {
            "AccountID": account_id,
            "Symbol": symbol,
            "Quantity": str(quantity),  # TradeStation expects string
            "OrderType": order_type,
            "TimeInForce": time_in_force
        }
        
        if price and order_type.upper() == "LIMIT":
            order_data["LimitPrice"] = str(price)
        
        logger.info(f"Placing {order_type} order: {quantity} shares of {symbol}")
        
        response = await self._make_request("POST", f"/brokerage/accounts/{account_id}/orders", json=order_data)
        
        logger.info(f"Order placed successfully for {symbol}")
        return response
    
    async def cancel_order(self, account_id: str, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        logger.info(f"Cancelling order {order_id}")
        
        response = await self._make_request("DELETE", f"/brokerage/accounts/{account_id}/orders/{order_id}")
        
        logger.info(f"Order {order_id} cancelled successfully")
        return response
    
    # === COMBINED METHODS ===
    
    async def get_account_summary(self, account_id: str) -> Dict[str, Any]:
        """Get comprehensive account summary including positions, balances, and recent orders"""
        try:
            # Execute multiple requests concurrently
            balances_task = self.get_account_balances(account_id)
            positions_task = self.get_positions(account_id)
            recent_orders_task = self.get_orders(account_id, datetime.now() - timedelta(days=7))
            
            balances, positions, recent_orders = await asyncio.gather(
                balances_task, 
                positions_task, 
                recent_orders_task,
                return_exceptions=True
            )
            
            # Handle potential errors
            if isinstance(balances, Exception):
                logger.error(f"Error fetching balances: {balances}")
                balances = {}
            else:
                logger.info(f"Balances retrieved successfully: {type(balances)}")
            
            if isinstance(positions, Exception):
                logger.error(f"Error fetching positions: {positions}")
                positions = []
            else:
                logger.info(f"Positions retrieved successfully: {len(positions)} positions")
            
            if isinstance(recent_orders, Exception):
                logger.error(f"Error fetching orders: {recent_orders}")
                recent_orders = []
            else:
                logger.info(f"Orders retrieved successfully: {len(recent_orders)} orders")
            
            # Check for authentication issues
            if not positions and not balances:
                logger.warning("No positions or balances retrieved - possible authentication issue")
                logger.warning(f"Auth status: {self.auth.is_authenticated()}")
                logger.warning(f"Token expires: {self.auth.token_expires}")
                logger.warning(f"Current time: {datetime.now()}")
            
            # Convert positions to dict format
            positions_data = []
            for pos in positions:
                if isinstance(pos, Position):
                    positions_data.append({
                        "account_id": pos.account_id,
                        "symbol": pos.symbol,
                        "asset_type": pos.asset_type,
                        "quantity": pos.quantity,
                        "average_price": pos.average_price,
                        "current_price": pos.current_price,
                        "market_value": pos.market_value,
                        "unrealized_pnl": pos.unrealized_pnl,
                        "unrealized_pnl_percent": pos.unrealized_pnl_percent
                    })
            
            # Convert orders to dict format
            orders_data = []
            for order in recent_orders:
                if isinstance(order, Order):
                    orders_data.append({
                        "order_id": order.order_id,
                        "account_id": order.account_id,
                        "symbol": order.symbol,
                        "asset_type": order.asset_type,
                        "quantity": order.quantity,
                        "order_type": order.order_type,
                        "price": order.price,
                        "status": order.status,
                        "filled_quantity": order.filled_quantity,
                        "remaining_quantity": order.remaining_quantity,
                        "timestamp": order.timestamp.isoformat()
                    })
            
            summary = {
                "account_id": account_id,
                "balances": balances,
                "positions": positions_data,
                "recent_orders": orders_data,
                "summary_timestamp": datetime.now().isoformat(),
                "totals": {
                    "position_count": len(positions_data),
                    "recent_order_count": len(orders_data),
                    "total_market_value": sum(pos.get("market_value", 0) for pos in positions_data),
                    "total_unrealized_pnl": sum(pos.get("unrealized_pnl", 0) for pos in positions_data)
                }
            }
            
            logger.info(f"Generated account summary for {account_id}: {len(positions_data)} positions, {len(orders_data)} recent orders")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get account summary for {account_id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to retrieve account summary: {str(e)}"
            )