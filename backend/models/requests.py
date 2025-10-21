"""
Pydantic Request Models for FlowMind API

Provides type-safe request validation with custom validators
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Literal
from datetime import datetime, date
from enum import Enum

# ============================================================================
# Enums
# ============================================================================


class OptionType(str, Enum):
    """Option contract type"""

    CALL = "CALL"
    PUT = "PUT"


class LegSide(str, Enum):
    """Position side"""

    BUY = "BUY"
    SELL = "SELL"


class Sentiment(str, Enum):
    """Market sentiment"""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


# ============================================================================
# Builder Models
# ============================================================================


class LegSchema(BaseModel):
    """Single leg of an options strategy"""

    type: OptionType = Field(..., description="CALL or PUT")
    strike: float = Field(..., gt=0, description="Strike price (must be positive)")
    side: LegSide = Field(..., description="BUY or SELL")
    qty: int = Field(1, ge=1, le=1000, description="Quantity (1-1000)")
    expiry: Optional[str] = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Expiration date (YYYY-MM-DD)"
    )

    class Config:
        schema_extra = {
            "example": {
                "type": "CALL",
                "strike": 250.0,
                "side": "BUY",
                "qty": 1,
                "expiry": "2025-11-15",
            }
        }


class BuilderPriceRequest(BaseModel):
    """Request for pricing an options strategy"""

    symbol: str = Field(
        ..., pattern=r"^[A-Z]{1,5}$", description="Stock ticker (1-5 uppercase letters)"
    )
    expiry: str = Field(
        ..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Expiration date (YYYY-MM-DD)"
    )
    legs: List[LegSchema] = Field(
        ..., min_items=1, max_items=4, description="Strategy legs (1-4)"
    )
    spot: Optional[float] = Field(None, gt=0, description="Current stock price")
    iv_mult: float = Field(1.0, ge=0.5, le=2.0, description="IV multiplier (0.5-2.0)")
    range_pct: float = Field(
        0.15, ge=0.05, le=0.5, description="Price range % (0.05-0.5)"
    )
    dte: Optional[int] = Field(
        None, ge=1, le=730, description="Days to expiration (1-730)"
    )

    @validator("expiry")
    def expiry_must_be_future(cls, v):
        """Validate expiry is in the future"""
        expiry_date = datetime.strptime(v, "%Y-%m-%d").date()
        if expiry_date < date.today():
            raise ValueError("Expiry must be in the future")
        return v

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        """Ensure symbol is uppercase"""
        return v.upper()

    @root_validator
    def validate_strategy(cls, values):
        """Validate strategy legs make sense"""
        legs = values.get("legs", [])

        # Check for duplicate legs
        leg_signatures = []
        for leg in legs:
            sig = f"{leg.type}_{leg.strike}_{leg.side}"
            if sig in leg_signatures:
                raise ValueError(f"Duplicate leg: {sig}")
            leg_signatures.append(sig)

        return values

    class Config:
        schema_extra = {
            "example": {
                "symbol": "TSLA",
                "expiry": "2025-11-15",
                "legs": [
                    {"type": "CALL", "strike": 250, "side": "BUY", "qty": 1},
                    {"type": "CALL", "strike": 270, "side": "SELL", "qty": 1},
                ],
                "spot": 250.5,
                "iv_mult": 1.0,
                "range_pct": 0.15,
                "dte": 30,
            }
        }


class BuilderHistoricalRequest(BaseModel):
    """Request for historical backtest"""

    legs: List[LegSchema] = Field(..., min_items=1, max_items=4)
    symbol: str = Field(..., pattern=r"^[A-Z]{1,5}$")
    days_back: int = Field(30, ge=1, le=730, description="Days to look back (1-730)")

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        return v.upper()


# ============================================================================
# Options Chain Models
# ============================================================================


class OptionsChainRequest(BaseModel):
    """Request for options chain data"""

    symbol: str = Field(..., pattern=r"^[A-Z]{1,5}$", description="Stock ticker")
    expiry: Optional[str] = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Specific expiration"
    )
    dte: Optional[int] = Field(None, ge=0, le=730, description="Days to expiration")
    dev: int = Field(0, ge=0, le=1, description="Force demo data (0 or 1)")

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        return v.upper()

    @root_validator
    def either_expiry_or_dte(cls, values):
        """Must provide either expiry or dte, not both"""
        expiry = values.get("expiry")
        dte = values.get("dte")

        if expiry and dte:
            raise ValueError("Provide either 'expiry' or 'dte', not both")

        return values


class GEXRequest(BaseModel):
    """Request for Gamma Exposure calculation"""

    symbol: str = Field(..., pattern=r"^[A-Z]{1,5}$")
    expiry: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    dte: Optional[int] = Field(None, ge=0, le=365)

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        return v.upper()


# ============================================================================
# Flow Models
# ============================================================================


class FlowSummaryRequest(BaseModel):
    """Request for options flow summary"""

    limit: int = Field(24, ge=1, le=100, description="Number of items (1-100)")
    min_premium: float = Field(25000, ge=0, description="Minimum premium filter")
    symbol: Optional[str] = Field(
        None, pattern=r"^[A-Z]{1,5}$", description="Filter by symbol"
    )

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        if v:
            return v.upper()
        return v


class FlowLiveRequest(BaseModel):
    """Request for live options flow"""

    symbol: Optional[str] = Field(None, pattern=r"^[A-Z]{1,5}$")
    min_premium: float = Field(25000, ge=0)
    limit: int = Field(50, ge=1, le=500)

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        if v:
            return v.upper()
        return v


class FlowHistoricalRequest(BaseModel):
    """Request for historical flow data"""

    symbol: str = Field(..., pattern=r"^[A-Z]{1,5}$")
    days: int = Field(7, ge=1, le=365, description="Days to look back")
    start_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        return v.upper()

    @root_validator
    def validate_date_range(cls, values):
        """Validate date range if provided"""
        start = values.get("start_date")
        end = values.get("end_date")

        if start and end:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")

            if start_dt > end_dt:
                raise ValueError("start_date must be before end_date")

        return values


# ============================================================================
# Optimizer Models
# ============================================================================


class OptimizerSuggestRequest(BaseModel):
    """Request for strategy recommendations"""

    symbol: str = Field(..., pattern=r"^[A-Z]{1,5}$")
    sentiment: Sentiment = Field(..., description="Market outlook")
    target_price: Optional[float] = Field(None, gt=0, description="Target price")
    budget: Optional[float] = Field(
        None, gt=0, le=100000, description="Max capital (USD)"
    )
    dte: int = Field(30, ge=1, le=180, description="Days to expiration")
    risk_bias: float = Field(
        0.0, ge=-1.0, le=1.0, description="Risk preference (-1 to 1)"
    )

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        return v.upper()

    class Config:
        schema_extra = {
            "example": {
                "symbol": "TSLA",
                "sentiment": "bullish",
                "target_price": 270.0,
                "budget": 5000.0,
                "dte": 30,
                "risk_bias": 0.0,
            }
        }


# ============================================================================
# Mindfolio Models
# ============================================================================


class MindfolioCreateRequest(BaseModel):
    """Request to create a new mindfolio"""

    name: str = Field(..., min_length=1, max_length=100)
    cash_balance: float = Field(10000.0, ge=0)
    description: Optional[str] = Field(None, max_length=500)

    class Config:
        schema_extra = {
            "example": {
                "name": "My Trading Mindfolio",
                "cash_balance": 10000.0,
                "description": "Options trading strategies",
            }
        }


class TransactionCreateRequest(BaseModel):
    """Request to add a transaction"""

    mindfolio_id: str = Field(..., min_length=1)
    symbol: str = Field(..., pattern=r"^[A-Z]{1,10}$")
    side: Literal["BUY", "SELL"] = Field(...)
    qty: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    fee: float = Field(0.0, ge=0)
    notes: Optional[str] = Field(None, max_length=500)

    @validator("symbol")
    def symbol_must_be_uppercase(cls, v):
        return v.upper()


# ============================================================================
# Health/Status Models
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: Literal["healthy", "unhealthy"]
    service: str
    version: str
    timestamp: str


class RedisHealthResponse(BaseModel):
    """Redis health check response"""

    status: Literal["connected", "fallback", "error"]
    mode: Literal["redis", "in-memory"]
    implementation: str
    connected: bool
    message: str


# ============================================================================
# Utility Functions
# ============================================================================


def validate_request(model_class: type[BaseModel], data: dict) -> BaseModel:
    """
    Validate request data against Pydantic model

    Args:
        model_class: Pydantic model class
        data: Request data dict

    Returns:
        Validated model instance

    Raises:
        ValueError: If validation fails
    """
    try:
        return model_class(**data)
    except Exception as e:
        raise ValueError(f"Request validation failed: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Test BuilderPriceRequest
    test_data = {
        "symbol": "tsla",  # Will be converted to uppercase
        "expiry": "2025-11-15",
        "legs": [
            {"type": "CALL", "strike": 250, "side": "BUY", "qty": 1},
            {"type": "CALL", "strike": 270, "side": "SELL", "qty": 1},
        ],
        "spot": 250.5,
        "iv_mult": 1.0,
        "range_pct": 0.15,
    }

    try:
        validated = BuilderPriceRequest(**test_data)
        print(" Validation passed!")
        print(f"Symbol: {validated.symbol}")
        print(f"Legs: {len(validated.legs)}")
    except ValueError as e:
        print(f" Validation failed: {e}")
