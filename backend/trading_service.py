"""
Trading Service
Handles order placement, validation, risk management, and trading operations
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator

from tradestation_client import TradeStationClient

logger = logging.getLogger(__name__)


class OrderSide(str, Enum):
    BUY = "Buy"
    SELL = "Sell"
    BUY_TO_COVER = "BuyToCover"
    SELL_SHORT = "SellShort"


class OrderType(str, Enum):
    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "StopMarket"
    STOP_LIMIT = "StopLimit"
    TRAILING_STOP = "TrailingStop"


class TimeInForce(str, Enum):
    DAY = "DAY"
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


class OrderRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    quantity: int = Field(..., gt=0, description="Order quantity")
    side: OrderSide = Field(..., description="Order side (Buy/Sell)")
    order_type: OrderType = Field(OrderType.MARKET, description="Order type")
    price: Optional[float] = Field(None, description="Limit price for limit orders")
    stop_price: Optional[float] = Field(None, description="Stop price for stop orders")
    time_in_force: TimeInForce = Field(TimeInForce.DAY, description="Time in force")

    @validator("price")
    def validate_price(cls, v, values):
        order_type = values.get("order_type")
        if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and v is None:
            raise ValueError("Price is required for limit orders")
        if v is not None and v <= 0:
            raise ValueError("Price must be positive")
        return v

    @validator("stop_price")
    def validate_stop_price(cls, v, values):
        order_type = values.get("order_type")
        if (
            order_type
            in [OrderType.STOP, OrderType.STOP_LIMIT, OrderType.TRAILING_STOP]
            and v is None
        ):
            raise ValueError("Stop price is required for stop orders")
        if v is not None and v <= 0:
            raise ValueError("Stop price must be positive")
        return v


class OrderModification(BaseModel):
    quantity: Optional[int] = Field(None, gt=0, description="New quantity")
    price: Optional[float] = Field(None, gt=0, description="New price")
    stop_price: Optional[float] = Field(None, gt=0, description="New stop price")


class RiskLimits(BaseModel):
    """Risk management limits for order validation"""

    max_order_value: float = 100000  # Maximum single order value
    max_daily_trades: int = 100  # Maximum daily trade count
    max_position_size: float = 0.25  # Maximum position as % of mindfolio
    max_sector_concentration: float = 0.40  # Maximum sector concentration
    min_account_balance: float = 1000  # Minimum account balance to maintain


class TradingRiskManager:
    """Risk management and order validation"""

    def __init__(self, limits: RiskLimits = RiskLimits()):
        self.limits = limits

    async def validate_order(
        self, order: OrderRequest, account_id: str, client: TradeStationClient
    ) -> Dict[str, Any]:
        """Comprehensive order validation including risk checks"""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "estimated_cost": 0.0,
            "risk_assessment": "LOW",
        }

        try:
            # Get current quote for price validation
            quotes = await client.get_quote(order.symbol)
            if not quotes:
                validation_result["errors"].append(
                    f"Unable to get quote for {order.symbol}"
                )
                validation_result["valid"] = False
                return validation_result

            current_quote = quotes[0]

            # Estimate order cost
            estimated_price = order.price if order.price else current_quote.last
            estimated_cost = estimated_price * order.quantity
            validation_result["estimated_cost"] = estimated_cost

            # Check maximum order value
            if estimated_cost > self.limits.max_order_value:
                validation_result["errors"].append(
                    f"Order value ${estimated_cost:.2f} exceeds maximum ${self.limits.max_order_value:.2f}"
                )
                validation_result["valid"] = False

            # Check account balances
            balances = await client.get_account_balances(account_id)
            buying_power = balances.get("DayTradingBuyingPower", 0)
            total_equity = balances.get("TotalEquity", 0)

            # Check buying power for buy orders
            if order.side in [OrderSide.BUY, OrderSide.BUY_TO_COVER]:
                if estimated_cost > buying_power:
                    validation_result["errors"].append(
                        f"Insufficient buying power. Required: ${estimated_cost:.2f}, Available: ${buying_power:.2f}"
                    )
                    validation_result["valid"] = False
                elif estimated_cost > buying_power * 0.8:
                    validation_result["warnings"].append(
                        f"Order uses {(estimated_cost / buying_power) * 100:.1f}% of available buying power"
                    )
                    validation_result["risk_assessment"] = "MEDIUM"

            # Check minimum account balance
            if total_equity < self.limits.min_account_balance:
                validation_result["warnings"].append(
                    f"Account balance ${total_equity:.2f} is below recommended minimum ${self.limits.min_account_balance:.2f}"
                )

            # Check price reasonableness (within 10% of current market)
            if order.price:
                price_deviation = (
                    abs(order.price - current_quote.last) / current_quote.last
                )
                if price_deviation > 0.15:  # 15% deviation
                    validation_result["errors"].append(
                        f"Order price ${order.price:.2f} deviates {price_deviation * 100:.1f}% from market ${current_quote.last:.2f}"
                    )
                    validation_result["valid"] = False
                elif price_deviation > 0.10:  # 10% deviation warning
                    validation_result["warnings"].append(
                        f"Order price ${order.price:.2f} is {price_deviation * 100:.1f}% from market ${current_quote.last:.2f}"
                    )
                    validation_result["risk_assessment"] = "MEDIUM"

            # Check position size limits
            positions = await client.get_positions(account_id)
            current_position = next(
                (pos for pos in positions if pos.symbol == order.symbol), None
            )

            mindfolio_value = sum(abs(pos.market_value) for pos in positions)
            if mindfolio_value > 0:
                new_position_value = estimated_cost
                if current_position:
                    new_position_value += abs(current_position.market_value)

                position_percentage = new_position_value / mindfolio_value
                if position_percentage > self.limits.max_position_size:
                    validation_result["warnings"].append(
                        f"Position would be {position_percentage * 100:.1f}% of mindfolio "
                        f"(limit: {self.limits.max_position_size * 100:.1f}%)"
                    )
                    validation_result["risk_assessment"] = "HIGH"

            # Market hours check
            market_hours = self._check_market_hours()
            if not market_hours["is_open"]:
                validation_result["warnings"].append(
                    f"Market is currently {market_hours['status']}. Order will be queued."
                )

            # Volatility check
            if current_quote.change_percent and abs(current_quote.change_percent) > 5:
                validation_result["warnings"].append(
                    f"{order.symbol} is experiencing high volatility ({current_quote.change_percent:.1f}% daily change)"
                )
                validation_result["risk_assessment"] = "MEDIUM"

            # Set final risk assessment
            if validation_result["errors"]:
                validation_result["risk_assessment"] = "INVALID"
            elif len(validation_result["warnings"]) >= 3:
                validation_result["risk_assessment"] = "HIGH"
            elif len(validation_result["warnings"]) >= 1:
                validation_result["risk_assessment"] = "MEDIUM"

        except Exception as e:
            logger.error(f"Order validation error: {str(e)}")
            validation_result["errors"].append(f"Validation error: {str(e)}")
            validation_result["valid"] = False
            validation_result["risk_assessment"] = "INVALID"

        return validation_result

    def _check_market_hours(self) -> Dict[str, Any]:
        """Check if market is currently open (simplified implementation)"""
        now = datetime.now()

        # Simple market hours check (EST: 9:30 AM - 4:00 PM, Monday-Friday)
        if now.weekday() >= 5:  # Weekend
            return {"is_open": False, "status": "closed (weekend)"}

        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

        if market_open <= now <= market_close:
            return {"is_open": True, "status": "open"}
        elif now < market_open:
            return {"is_open": False, "status": "pre-market"}
        else:
            return {"is_open": False, "status": "after-hours"}


class TradingService:
    """Main trading service orchestrating all trading operations"""

    def __init__(self, client: TradeStationClient):
        self.client = client
        self.risk_manager = TradingRiskManager()

    def update_risk_limits(self, new_limits: RiskLimits):
        """Update risk management limits"""
        self.risk_manager.limits = new_limits
        logger.info("Risk limits updated")

    async def validate_order(
        self, account_id: str, order: OrderRequest
    ) -> Dict[str, Any]:
        """Validate order without placing it"""
        return await self.risk_manager.validate_order(order, account_id, self.client)

    async def place_order(
        self, account_id: str, order: OrderRequest, force: bool = False
    ) -> Dict[str, Any]:
        """Place a new trading order with validation"""
        try:
            # Validate order
            validation = await self.risk_manager.validate_order(
                order, account_id, self.client
            )

            if not validation["valid"]:
                return {
                    "success": False,
                    "message": "Order validation failed",
                    "validation": validation,
                    "timestamp": datetime.now().isoformat(),
                }

            # Check warnings
            if validation["warnings"] and not force:
                return {
                    "success": False,
                    "message": "Order has warnings. Use force=true to override",
                    "validation": validation,
                    "requires_confirmation": True,
                    "timestamp": datetime.now().isoformat(),
                }

            # Place the order
            response = await self.client.place_order(
                account_id=account_id,
                symbol=order.symbol,
                quantity=(
                    order.quantity
                    if order.side in [OrderSide.BUY, OrderSide.BUY_TO_COVER]
                    else -order.quantity
                ),
                order_type=order.order_type.value,
                price=order.price,
                time_in_force=order.time_in_force.value,
            )

            # Log the order placement
            logger.info(
                f"Order placed: Account {account_id}, Symbol {order.symbol}, Quantity {order.quantity}, Type {order.order_type}"
            )

            return {
                "success": True,
                "message": "Order placed successfully",
                "order_response": response,
                "validation": validation,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to place order: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def cancel_order(self, account_id: str, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            # Verify order exists and can be cancelled
            orders = await self.client.get_orders(account_id)
            order_to_cancel = next(
                (order for order in orders if order.order_id == order_id), None
            )

            if not order_to_cancel:
                return {
                    "success": False,
                    "message": "Order not found",
                    "timestamp": datetime.now().isoformat(),
                }

            if order_to_cancel.status not in ["PND", "PFL"]:
                return {
                    "success": False,
                    "message": f"Order cannot be cancelled in status: {order_to_cancel.status}",
                    "timestamp": datetime.now().isoformat(),
                }

            # Cancel the order
            response = await self.client.cancel_order(account_id, order_id)

            logger.info(f"Order cancelled: Account {account_id}, Order ID {order_id}")

            return {
                "success": True,
                "message": "Order cancelled successfully",
                "order_id": order_id,
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to cancel order: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to cancel order: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def get_order_status(self, account_id: str, order_id: str) -> Dict[str, Any]:
        """Get detailed status of a specific order"""
        try:
            orders = await self.client.get_orders(account_id)
            order = next(
                (order for order in orders if order.order_id == order_id), None
            )

            if not order:
                return {
                    "success": False,
                    "message": "Order not found",
                    "timestamp": datetime.now().isoformat(),
                }

            # Get current quote for comparison
            quotes = await self.client.get_quote(order.symbol)
            current_quote = quotes[0] if quotes else None

            order_status = {
                "success": True,
                "order": {
                    "order_id": order.order_id,
                    "symbol": order.symbol,
                    "quantity": order.quantity,
                    "order_type": order.order_type,
                    "price": order.price,
                    "status": order.status,
                    "filled_quantity": order.filled_quantity,
                    "remaining_quantity": order.remaining_quantity,
                    "timestamp": order.timestamp.isoformat(),
                },
                "current_quote": (
                    {
                        "symbol": current_quote.symbol,
                        "last": current_quote.last,
                        "bid": current_quote.bid,
                        "ask": current_quote.ask,
                        "change_percent": current_quote.change_percent,
                    }
                    if current_quote
                    else None
                ),
                "execution_analysis": {
                    "fill_percentage": (
                        (order.filled_quantity / order.quantity * 100)
                        if order.quantity > 0
                        else 0
                    ),
                    "remaining_quantity": order.remaining_quantity,
                    "is_active": order.status in ["PND", "PFL"],
                    "can_modify": order.status in ["PND", "PFL"],
                    "can_cancel": order.status in ["PND", "PFL"],
                },
                "timestamp": datetime.now().isoformat(),
            }

            return order_status

        except Exception as e:
            logger.error(f"Failed to get order status: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get order status: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def get_trading_summary(
        self, account_id: str, days_back: int = 7
    ) -> Dict[str, Any]:
        """Get comprehensive trading activity summary"""
        try:
            # Get recent orders
            since_date = datetime.now() - timedelta(days=days_back)
            orders = await self.client.get_orders(account_id, since_date)

            # Analyze trading activity
            total_orders = len(orders)
            filled_orders = [
                order for order in orders if order.status in ["FLL", "PFL"]
            ]
            pending_orders = [order for order in orders if order.status == "PND"]
            cancelled_orders = [order for order in orders if order.status == "CAN"]

            # Calculate volumes
            total_volume = sum(abs(order.quantity) for order in filled_orders)
            total_value = 0

            # Estimate total value (would need additional quote data for accuracy)
            for order in filled_orders:
                estimated_value = abs(order.quantity) * (
                    order.price or 100
                )  # Rough estimate
                total_value += estimated_value

            # Symbol analysis
            symbol_counts = {}
            for order in orders:
                symbol_counts[order.symbol] = symbol_counts.get(order.symbol, 0) + 1

            most_traded_symbols = sorted(
                symbol_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]

            return {
                "account_id": account_id,
                "analysis_period": {
                    "days_back": days_back,
                    "start_date": since_date.isoformat(),
                    "end_date": datetime.now().isoformat(),
                },
                "order_summary": {
                    "total_orders": total_orders,
                    "filled_orders": len(filled_orders),
                    "pending_orders": len(pending_orders),
                    "cancelled_orders": len(cancelled_orders),
                    "success_rate": (
                        (len(filled_orders) / total_orders * 100)
                        if total_orders > 0
                        else 0
                    ),
                },
                "volume_analysis": {
                    "total_volume": total_volume,
                    "estimated_total_value": total_value,
                    "avg_order_size": (
                        total_volume / len(filled_orders) if filled_orders else 0
                    ),
                },
                "symbol_analysis": {
                    "unique_symbols": len(symbol_counts),
                    "most_traded": most_traded_symbols,
                },
                "risk_status": {
                    "current_limits": self.risk_manager.limits.dict(),
                    "recent_warnings": 0,  # Would track from validation history
                    "risk_level": "NORMAL",  # Would calculate based on recent activity
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get trading summary: {str(e)}")
            raise
