"""
Smart Money Concepts & Price Action Analysis
Comprehensive implementation for institutional trading analysis
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif pd.isna(obj):
        return None
    return obj


@dataclass
class OrderBlock:
    """Order Block structure"""

    start_time: str
    end_time: str
    high: float
    low: float
    volume: float
    type: str  # 'bullish' or 'bearish'
    strength: str  # 'weak', 'medium', 'strong'
    tested: bool = False


@dataclass
class FairValueGap:
    """Fair Value Gap structure"""

    start_time: str
    end_time: str
    gap_high: float
    gap_low: float
    gap_size: float
    type: str  # 'bullish' or 'bearish'
    filled: bool = False
    fill_percentage: float = 0.0


@dataclass
class LiquiditySweep:
    """Liquidity Sweep structure"""

    time: str
    price: float
    type: str  # 'high_sweep' or 'low_sweep'
    volume: float
    significance: str  # 'minor', 'major'


@dataclass
class MarketStructurePoint:
    """Market Structure Point"""

    time: str
    price: float
    type: str  # 'HH', 'HL', 'LH', 'LL'
    volume: float
    confirmed: bool = False


class SmartMoneyAnalyzer:
    """Advanced Smart Money Concepts and Price Action Analyzer"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def analyze_smart_money_concepts(
        self, symbol: str, period: str = "3mo"
    ) -> Dict[str, Any]:
        """Comprehensive Smart Money analysis for a symbol"""
        try:
            # Get detailed price data
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                period=period, interval="1h"
            )  # Hourly data for better precision

            if df.empty:
                raise ValueError(f"No data available for {symbol}")

            # Perform all Smart Money analyses
            order_blocks = self._identify_order_blocks(df)
            fair_value_gaps = self._identify_fair_value_gaps(df)
            liquidity_sweeps = self._identify_liquidity_sweeps(df)
            market_structure = self._analyze_market_structure(df)
            premium_discount = self._calculate_premium_discount_zones(df)
            bos_choch = self._identify_bos_choch(df)
            imbalances = self._identify_imbalances(df)

            # Price Action Analysis
            support_resistance = self._identify_support_resistance(df)
            candlestick_patterns = self._identify_candlestick_patterns(df)
            supply_demand_zones = self._identify_supply_demand_zones(df)
            volume_analysis = self._analyze_volume_profile(df)

            current_price = float(df["Close"].iloc[-1])

            # Generate Smart Money verdict
            smart_money_verdict = self._generate_smart_money_verdict(
                order_blocks,
                fair_value_gaps,
                liquidity_sweeps,
                market_structure,
                bos_choch,
                current_price,
            )

            result = {
                "symbol": symbol.upper(),
                "analysis_timestamp": datetime.now().isoformat(),
                "current_price": float(current_price),
                "timeframe": period,
                # Smart Money Concepts
                "smart_money_verdict": smart_money_verdict,
                "order_blocks": [
                    self._order_block_to_dict(ob) for ob in order_blocks[-10:]
                ],  # Last 10
                "fair_value_gaps": [
                    self._fvg_to_dict(fvg) for fvg in fair_value_gaps if not fvg.filled
                ],
                "liquidity_sweeps": [
                    self._liquidity_sweep_to_dict(ls) for ls in liquidity_sweeps[-5:]
                ],
                "market_structure": {
                    "current_trend": market_structure["trend"],
                    "structure_points": [
                        self._structure_point_to_dict(sp)
                        for sp in market_structure["points"][-10:]
                    ],
                    "break_of_structure": bos_choch["bos"],
                    "change_of_character": bos_choch["choch"],
                },
                "premium_discount": premium_discount,
                "imbalances": imbalances[-5:],  # Last 5 imbalances
                # Price Action
                "price_action": {
                    "support_resistance": support_resistance,
                    "candlestick_patterns": candlestick_patterns[
                        -10:
                    ],  # Recent patterns
                    "supply_demand_zones": supply_demand_zones,
                    "volume_analysis": volume_analysis,
                },
                # Trading Signals
                "trading_signals": self._generate_trading_signals(
                    order_blocks,
                    fair_value_gaps,
                    support_resistance,
                    market_structure,
                    current_price,
                ),
            }

            # Convert all numpy types to native Python types
            return convert_numpy_types(result)

        except Exception as e:
            self.logger.error(f"Error in Smart Money analysis for {symbol}: {str(e)}")
            raise

    def _identify_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """Identify Order Blocks - zones where institutions placed large orders"""
        order_blocks = []

        # Look for significant price movements with high volume
        df["price_change"] = df["Close"].pct_change()
        df["volume_sma"] = df["Volume"].rolling(20).mean()
        df["high_volume"] = df["Volume"] > df["volume_sma"] * 1.5

        # Identify potential order blocks
        for i in range(10, len(df) - 5):
            current_candle = df.iloc[i]

            # Bullish Order Block criteria
            if (
                current_candle["price_change"] > 0.02  # 2%+ move
                and current_candle["high_volume"]
                and current_candle["Close"] > current_candle["Open"]
            ):
                # Find the origin candle (last bearish before the move)
                origin_idx = i
                for j in range(i - 1, max(0, i - 10), -1):
                    if df.iloc[j]["Close"] < df.iloc[j]["Open"]:
                        origin_idx = j
                        break

                origin_candle = df.iloc[origin_idx]
                strength = self._calculate_ob_strength(df, i, origin_idx)

                order_blocks.append(
                    OrderBlock(
                        start_time=origin_candle.name.isoformat(),
                        end_time=current_candle.name.isoformat(),
                        high=float(origin_candle["High"]),
                        low=float(origin_candle["Low"]),
                        volume=float(current_candle["Volume"]),
                        type="bullish",
                        strength=strength,
                    )
                )

            # Bearish Order Block criteria
            elif (
                current_candle["price_change"] < -0.02  # 2%+ drop
                and current_candle["high_volume"]
                and current_candle["Close"] < current_candle["Open"]
            ):
                # Find the origin candle (last bullish before the move)
                origin_idx = i
                for j in range(i - 1, max(0, i - 10), -1):
                    if df.iloc[j]["Close"] > df.iloc[j]["Open"]:
                        origin_idx = j
                        break

                origin_candle = df.iloc[origin_idx]
                strength = self._calculate_ob_strength(df, i, origin_idx)

                order_blocks.append(
                    OrderBlock(
                        start_time=origin_candle.name.isoformat(),
                        end_time=current_candle.name.isoformat(),
                        high=float(origin_candle["High"]),
                        low=float(origin_candle["Low"]),
                        volume=float(current_candle["Volume"]),
                        type="bearish",
                        strength=strength,
                    )
                )

        return order_blocks

    def _identify_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """Identify Fair Value Gaps - price gaps that need to be filled"""
        fvgs = []

        for i in range(2, len(df)):
            prev_candle = df.iloc[i - 2]
            df.iloc[i - 1]
            next_candle = df.iloc[i]

            # Bullish FVG: prev_high < next_low
            if prev_candle["High"] < next_candle["Low"]:
                gap_size = next_candle["Low"] - prev_candle["High"]
                if gap_size > 0:  # Valid gap
                    # Check if gap has been filled
                    filled = False
                    fill_percentage = 0.0

                    # Check subsequent candles for gap fill
                    for j in range(
                        i + 1, min(len(df), i + 50)
                    ):  # Check next 50 candles
                        if df.iloc[j]["Low"] <= prev_candle["High"]:
                            filled = True
                            fill_percentage = 100.0
                            break
                        elif df.iloc[j]["Low"] < next_candle["Low"]:
                            fill_percentage = (
                                (next_candle["Low"] - df.iloc[j]["Low"]) / gap_size
                            ) * 100

                    fvgs.append(
                        FairValueGap(
                            start_time=prev_candle.name.isoformat(),
                            end_time=next_candle.name.isoformat(),
                            gap_high=float(next_candle["Low"]),
                            gap_low=float(prev_candle["High"]),
                            gap_size=float(gap_size),
                            type="bullish",
                            filled=filled,
                            fill_percentage=fill_percentage,
                        )
                    )

            # Bearish FVG: prev_low > next_high
            elif prev_candle["Low"] > next_candle["High"]:
                gap_size = prev_candle["Low"] - next_candle["High"]
                if gap_size > 0:  # Valid gap
                    # Check if gap has been filled
                    filled = False
                    fill_percentage = 0.0

                    # Check subsequent candles for gap fill
                    for j in range(
                        i + 1, min(len(df), i + 50)
                    ):  # Check next 50 candles
                        if df.iloc[j]["High"] >= prev_candle["Low"]:
                            filled = True
                            fill_percentage = 100.0
                            break
                        elif df.iloc[j]["High"] > next_candle["High"]:
                            fill_percentage = (
                                (df.iloc[j]["High"] - next_candle["High"]) / gap_size
                            ) * 100

                    fvgs.append(
                        FairValueGap(
                            start_time=prev_candle.name.isoformat(),
                            end_time=next_candle.name.isoformat(),
                            gap_high=float(prev_candle["Low"]),
                            gap_low=float(next_candle["High"]),
                            gap_size=float(gap_size),
                            type="bearish",
                            filled=filled,
                            fill_percentage=fill_percentage,
                        )
                    )

        return fvgs

    def _identify_liquidity_sweeps(self, df: pd.DataFrame) -> List[LiquiditySweep]:
        """Identify Liquidity Sweeps - when price sweeps above/below key levels to grab liquidity"""
        sweeps = []

        # Calculate recent highs and lows
        df["recent_high"] = df["High"].rolling(20).max()
        df["recent_low"] = df["Low"].rolling(20).min()

        for i in range(20, len(df)):
            current = df.iloc[i]
            prev_recent_high = df.iloc[i - 1]["recent_high"]
            prev_recent_low = df.iloc[i - 1]["recent_low"]

            # High liquidity sweep
            if (
                current["High"] > prev_recent_high
                and current["Close"] < current["High"] * 0.995
            ):  # Price retreated after sweep
                # Calculate significance based on volume and price action
                volume_ratio = (
                    current["Volume"] / df["Volume"].rolling(20).mean().iloc[i]
                )
                significance = "major" if volume_ratio > 2.0 else "minor"

                sweeps.append(
                    LiquiditySweep(
                        time=current.name.isoformat(),
                        price=float(current["High"]),
                        type="high_sweep",
                        volume=float(current["Volume"]),
                        significance=significance,
                    )
                )

            # Low liquidity sweep
            elif (
                current["Low"] < prev_recent_low
                and current["Close"] > current["Low"] * 1.005
            ):  # Price recovered after sweep
                # Calculate significance based on volume and price action
                volume_ratio = (
                    current["Volume"] / df["Volume"].rolling(20).mean().iloc[i]
                )
                significance = "major" if volume_ratio > 2.0 else "minor"

                sweeps.append(
                    LiquiditySweep(
                        time=current.name.isoformat(),
                        price=float(current["Low"]),
                        type="low_sweep",
                        volume=float(current["Volume"]),
                        significance=significance,
                    )
                )

        return sweeps

    def _analyze_market_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market structure - Higher Highs, Higher Lows, etc."""
        structure_points = []

        # Find swing highs and lows
        for i in range(5, len(df) - 5):
            current_high = df.iloc[i]["High"]
            current_low = df.iloc[i]["Low"]

            # Check if it's a swing high
            is_swing_high = True
            for j in range(i - 5, i + 6):
                if j != i and df.iloc[j]["High"] >= current_high:
                    is_swing_high = False
                    break

            if is_swing_high:
                structure_points.append(
                    MarketStructurePoint(
                        time=df.index[i].isoformat(),
                        price=float(current_high),
                        type="swing_high",
                        volume=float(df.iloc[i]["Volume"]),
                        confirmed=True,
                    )
                )

            # Check if it's a swing low
            is_swing_low = True
            for j in range(i - 5, i + 6):
                if j != i and df.iloc[j]["Low"] <= current_low:
                    is_swing_low = False
                    break

            if is_swing_low:
                structure_points.append(
                    MarketStructurePoint(
                        time=df.index[i].isoformat(),
                        price=float(current_low),
                        volume=float(df.iloc[i]["Volume"]),
                        type="swing_low",
                        confirmed=True,
                    )
                )

        # Determine overall trend
        swing_highs = [sp for sp in structure_points if sp.type == "swing_high"]
        swing_lows = [sp for sp in structure_points if sp.type == "swing_low"]

        trend = "sideways"
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            recent_highs = swing_highs[-2:]
            recent_lows = swing_lows[-2:]

            if (
                recent_highs[-1].price > recent_highs[-2].price
                and recent_lows[-1].price > recent_lows[-2].price
            ):
                trend = "bullish"  # Higher Highs, Higher Lows
            elif (
                recent_highs[-1].price < recent_highs[-2].price
                and recent_lows[-1].price < recent_lows[-2].price
            ):
                trend = "bearish"  # Lower Highs, Lower Lows

        return {"trend": trend, "points": structure_points}

    def _identify_bos_choch(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify Break of Structure and Change of Character"""
        # This is a simplified implementation
        # In practice, this would be more complex

        bos_events = []
        choch_events = []

        # Calculate recent support and resistance levels
        df["resistance"] = df["High"].rolling(20).max()
        df["support"] = df["Low"].rolling(20).min()

        for i in range(20, len(df)):
            current = df.iloc[i]
            prev_resistance = df.iloc[i - 1]["resistance"]
            prev_support = df.iloc[i - 1]["support"]

            # Break of Structure (BOS) - break above resistance or below support
            if current["Close"] > prev_resistance:
                bos_events.append(
                    {
                        "time": current.name.isoformat(),
                        "price": float(current["Close"]),
                        "type": "bullish_bos",
                        "level_broken": float(prev_resistance),
                    }
                )
            elif current["Close"] < prev_support:
                bos_events.append(
                    {
                        "time": current.name.isoformat(),
                        "price": float(current["Close"]),
                        "type": "bearish_bos",
                        "level_broken": float(prev_support),
                    }
                )

        return {
            "bos": bos_events[-5:],  # Last 5 BOS events
            "choch": choch_events,  # Would implement CHoCH logic here
        }

    def _calculate_premium_discount_zones(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Premium and Discount zones based on recent range"""
        if len(df) < 50:
            return {
                "premium": 0,
                "discount": 0,
                "equilibrium": 0,
                "current_zone": "equilibrium",
            }

        # Use last 50 periods for range calculation
        recent_high = df["High"].tail(50).max()
        recent_low = df["Low"].tail(50).min()
        range_size = recent_high - recent_low

        # Standard Fibonacci levels
        equilibrium = recent_low + (range_size * 0.5)
        premium_start = recent_low + (range_size * 0.618)  # 61.8%
        discount_end = recent_low + (range_size * 0.382)  # 38.2%

        current_price = float(df["Close"].iloc[-1])

        # Determine current zone
        if current_price > premium_start:
            current_zone = "premium"
        elif current_price < discount_end:
            current_zone = "discount"
        else:
            current_zone = "equilibrium"

        return {
            "range_high": float(recent_high),
            "range_low": float(recent_low),
            "equilibrium": float(equilibrium),
            "premium_zone": float(premium_start),
            "discount_zone": float(discount_end),
            "current_price": current_price,
            "current_zone": current_zone,
            "premium_percentage": (
                ((current_price - recent_low) / range_size) * 100
                if range_size > 0
                else 50
            ),
        }

    def _identify_imbalances(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify price imbalances (similar to FVGs but broader concept)"""
        imbalances = []

        for i in range(1, len(df) - 1):
            current = df.iloc[i]
            next_candle = df.iloc[i + 1]

            # Bullish imbalance
            if current["High"] < next_candle["Low"]:
                imbalance_size = next_candle["Low"] - current["High"]
                imbalances.append(
                    {
                        "time": current.name.isoformat(),
                        "high": float(next_candle["Low"]),
                        "low": float(current["High"]),
                        "size": float(imbalance_size),
                        "type": "bullish",
                        "filled": False,
                    }
                )

            # Bearish imbalance
            elif current["Low"] > next_candle["High"]:
                imbalance_size = current["Low"] - next_candle["High"]
                imbalances.append(
                    {
                        "time": current.name.isoformat(),
                        "high": float(current["Low"]),
                        "low": float(next_candle["High"]),
                        "size": float(imbalance_size),
                        "type": "bearish",
                        "filled": False,
                    }
                )

        return imbalances

    def _identify_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify key support and resistance levels"""
        # Find significant price levels
        levels = []

        # Method 1: Swing highs and lows
        for i in range(10, len(df) - 10):
            current_high = df.iloc[i]["High"]
            current_low = df.iloc[i]["Low"]

            # Check for swing high
            if all(
                df.iloc[j]["High"] <= current_high
                for j in range(i - 10, i + 11)
                if j != i
            ):
                levels.append(
                    {"price": float(current_high), "type": "resistance", "strength": 1}
                )

            # Check for swing low
            if all(
                df.iloc[j]["Low"] >= current_low
                for j in range(i - 10, i + 11)
                if j != i
            ):
                levels.append(
                    {"price": float(current_low), "type": "support", "strength": 1}
                )

        # Remove duplicates and sort
        levels = sorted(levels, key=lambda x: x["price"])

        # Find current nearest support and resistance
        current_price = float(df["Close"].iloc[-1])

        resistance_levels = [
            l
            for l in levels
            if l["price"] > current_price and l["type"] == "resistance"
        ]
        support_levels = [
            l for l in levels if l["price"] < current_price and l["type"] == "support"
        ]

        return {
            "nearest_support": support_levels[-1]["price"] if support_levels else None,
            "nearest_resistance": (
                resistance_levels[0]["price"] if resistance_levels else None
            ),
            "all_support_levels": [l["price"] for l in support_levels[-5:]],
            "all_resistance_levels": [l["price"] for l in resistance_levels[:5]],
            "key_levels": levels[-20:],  # Last 20 significant levels
        }

    def _identify_candlestick_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify candlestick patterns"""
        patterns = []

        for i in range(2, len(df)):
            current = df.iloc[i]
            prev = df.iloc[i - 1]
            df.iloc[i - 2]

            # Calculate body and shadow sizes
            body_size = abs(current["Close"] - current["Open"])
            upper_shadow = current["High"] - max(current["Open"], current["Close"])
            lower_shadow = min(current["Open"], current["Close"]) - current["Low"]
            total_range = current["High"] - current["Low"]

            pattern_found = None

            # Doji pattern
            if body_size < total_range * 0.1:  # Body is less than 10% of total range
                pattern_found = {
                    "name": "Doji",
                    "type": "reversal",
                    "reliability": "medium",
                    "signal": "indecision",
                }

            # Hammer pattern
            elif (
                lower_shadow > body_size * 2
                and upper_shadow < body_size * 0.5
                and current["Close"] > current["Open"]
            ):
                pattern_found = {
                    "name": "Hammer",
                    "type": "reversal",
                    "reliability": "high",
                    "signal": "bullish",
                }

            # Shooting Star pattern
            elif (
                upper_shadow > body_size * 2
                and lower_shadow < body_size * 0.5
                and current["Close"] < current["Open"]
            ):
                pattern_found = {
                    "name": "Shooting Star",
                    "type": "reversal",
                    "reliability": "high",
                    "signal": "bearish",
                }

            # Engulfing patterns
            elif (
                current["Open"] < prev["Close"]
                and current["Close"] > prev["Open"]
                and current["Close"] > current["Open"]
                and prev["Close"] < prev["Open"]
            ):
                pattern_found = {
                    "name": "Bullish Engulfing",
                    "type": "reversal",
                    "reliability": "high",
                    "signal": "bullish",
                }

            elif (
                current["Open"] > prev["Close"]
                and current["Close"] < prev["Open"]
                and current["Close"] < current["Open"]
                and prev["Close"] > prev["Open"]
            ):
                pattern_found = {
                    "name": "Bearish Engulfing",
                    "type": "reversal",
                    "reliability": "high",
                    "signal": "bearish",
                }

            if pattern_found:
                pattern_found.update(
                    {
                        "time": current.name.isoformat(),
                        "price": float(current["Close"]),
                        "volume": float(current["Volume"]),
                    }
                )
                patterns.append(pattern_found)

        return patterns

    def _identify_supply_demand_zones(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify Supply and Demand zones"""
        supply_zones = []
        demand_zones = []

        # Look for strong moves away from consolidation areas
        for i in range(20, len(df) - 5):
            # Check for demand zone (strong move up from consolidation)
            consolidation_low = df.iloc[i - 20 : i]["Low"].min()
            consolidation_high = df.iloc[i - 20 : i]["High"].max()
            consolidation_size = consolidation_high - consolidation_low

            # Strong bullish move after consolidation
            if (
                df.iloc[i + 1]["Close"] > df.iloc[i]["Close"] * 1.02  # 2% move
                and df.iloc[i + 1]["Volume"]
                > df.iloc[i - 20 : i]["Volume"].mean() * 1.5
            ):
                demand_zones.append(
                    {
                        "high": float(consolidation_high),
                        "low": float(consolidation_low),
                        "time": df.index[i].isoformat(),
                        "strength": "strong" if consolidation_size > 0 else "weak",
                        "tested": False,
                    }
                )

            # Strong bearish move after consolidation
            elif (
                df.iloc[i + 1]["Close"] < df.iloc[i]["Close"] * 0.98  # 2% drop
                and df.iloc[i + 1]["Volume"]
                > df.iloc[i - 20 : i]["Volume"].mean() * 1.5
            ):
                supply_zones.append(
                    {
                        "high": float(consolidation_high),
                        "low": float(consolidation_low),
                        "time": df.index[i].isoformat(),
                        "strength": "strong" if consolidation_size > 0 else "weak",
                        "tested": False,
                    }
                )

        return {
            "supply_zones": supply_zones[-5:],  # Last 5 supply zones
            "demand_zones": demand_zones[-5:],  # Last 5 demand zones
        }

    def _analyze_volume_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume profile and volume patterns"""
        # Calculate volume-based indicators
        df_temp = df.copy()
        df_temp["volume_sma_20"] = df_temp["Volume"].rolling(20).mean()
        df_temp["volume_ratio"] = df_temp["Volume"] / df_temp["volume_sma_20"]
        df_temp["price_volume"] = df_temp["Close"] * df_temp["Volume"]

        # Volume profile levels (simplified)
        price_levels = np.linspace(df["Low"].min(), df["High"].max(), 20)
        volume_at_price = []

        for level in price_levels:
            level_volume = 0
            for i in range(len(df)):
                if df.iloc[i]["Low"] <= level <= df.iloc[i]["High"]:
                    level_volume += df.iloc[i]["Volume"]
            volume_at_price.append({"price": float(level), "volume": level_volume})

        # Find Point of Control (POC) - price level with highest volume
        poc = max(volume_at_price, key=lambda x: x["volume"])

        # Recent volume analysis
        recent_high_volume_bars = []
        for i in range(len(df_temp)):
            if df_temp.iloc[i]["volume_ratio"] > 2.0:  # Volume > 2x average
                recent_high_volume_bars.append(
                    {
                        "time": df_temp.index[i].isoformat(),
                        "price": float(df_temp.iloc[i]["Close"]),
                        "volume": float(df_temp.iloc[i]["Volume"]),
                        "volume_ratio": float(df_temp.iloc[i]["volume_ratio"]),
                    }
                )

        return {
            "point_of_control": poc,
            "volume_profile": volume_at_price,
            "high_volume_bars": recent_high_volume_bars[
                -10:
            ],  # Last 10 high volume bars
            "average_volume": float(df["Volume"].mean()),
            "current_volume_ratio": float(df_temp["volume_ratio"].iloc[-1]),
        }

    def _generate_smart_money_verdict(
        self,
        order_blocks,
        fair_value_gaps,
        liquidity_sweeps,
        market_structure,
        bos_choch,
        current_price,
    ) -> Dict[str, Any]:
        """Generate overall Smart Money verdict"""
        signals = []

        # Analyze Order Blocks
        recent_bullish_obs = [
            ob for ob in order_blocks if ob.type == "bullish" and not ob.tested
        ]
        recent_bearish_obs = [
            ob for ob in order_blocks if ob.type == "bearish" and not ob.tested
        ]

        if len(recent_bullish_obs) > len(recent_bearish_obs):
            signals.append(
                ("bullish", "order_blocks", "More untested bullish order blocks")
            )
        elif len(recent_bearish_obs) > len(recent_bullish_obs):
            signals.append(
                ("bearish", "order_blocks", "More untested bearish order blocks")
            )

        # Analyze Fair Value Gaps
        unfilled_bullish_fvgs = [
            fvg for fvg in fair_value_gaps if fvg.type == "bullish" and not fvg.filled
        ]
        unfilled_bearish_fvgs = [
            fvg for fvg in fair_value_gaps if fvg.type == "bearish" and not fvg.filled
        ]

        if len(unfilled_bullish_fvgs) > len(unfilled_bearish_fvgs):
            signals.append(("bullish", "fair_value_gaps", "More unfilled bullish FVGs"))
        elif len(unfilled_bearish_fvgs) > len(unfilled_bullish_fvgs):
            signals.append(("bearish", "fair_value_gaps", "More unfilled bearish FVGs"))

        # Analyze Market Structure
        if market_structure["trend"] == "bullish":
            signals.append(
                ("bullish", "market_structure", "Bullish market structure (HH, HL)")
            )
        elif market_structure["trend"] == "bearish":
            signals.append(
                ("bearish", "market_structure", "Bearish market structure (LH, LL)")
            )

        # Calculate overall verdict
        bullish_signals = len([s for s in signals if s[0] == "bullish"])
        bearish_signals = len([s for s in signals if s[0] == "bearish"])

        if bullish_signals > bearish_signals:
            overall_verdict = "BULLISH"
            confidence = min(90, 60 + (bullish_signals - bearish_signals) * 10)
        elif bearish_signals > bullish_signals:
            overall_verdict = "BEARISH"
            confidence = min(90, 60 + (bearish_signals - bullish_signals) * 10)
        else:
            overall_verdict = "NEUTRAL"
            confidence = 45

        return {
            "verdict": overall_verdict,
            "confidence": confidence,
            "supporting_signals": signals,
            "key_insight": self._get_key_insight(signals, overall_verdict),
        }

    def _generate_trading_signals(
        self,
        order_blocks,
        fair_value_gaps,
        support_resistance,
        market_structure,
        current_price,
    ) -> List[Dict[str, Any]]:
        """Generate actionable trading signals"""
        signals = []

        # Order Block signals
        for ob in order_blocks[-3:]:  # Check last 3 order blocks
            if not ob.tested and ob.type == "bullish" and current_price <= ob.high:
                signals.append(
                    {
                        "type": "buy",
                        "reason": f"Price approaching untested bullish order block at {ob.low:.2f}-{ob.high:.2f}",
                        "entry": ob.low,
                        "stop_loss": ob.low * 0.99,
                        "target": current_price * 1.05,
                        "confidence": "high" if ob.strength == "strong" else "medium",
                    }
                )

        # Support/Resistance signals
        if support_resistance["nearest_support"]:
            distance_to_support = (
                (current_price - support_resistance["nearest_support"]) / current_price
            ) * 100
            if distance_to_support < 2:  # Within 2% of support
                signals.append(
                    {
                        "type": "buy",
                        "reason": f"Price near key support level at {support_resistance['nearest_support']:.2f}",
                        "entry": support_resistance["nearest_support"],
                        "stop_loss": support_resistance["nearest_support"] * 0.98,
                        "target": current_price * 1.04,
                        "confidence": "medium",
                    }
                )

        return signals[:5]  # Return top 5 signals

    def _get_key_insight(self, signals, verdict) -> str:
        """Generate key insight based on analysis"""
        if verdict == "BULLISH":
            return "Smart money shows bullish positioning with institutional buying interest evident."
        elif verdict == "BEARISH":
            return "Smart money indicates bearish sentiment with institutional selling pressure."
        else:
            return "Mixed signals from smart money analysis suggest caution and wait for clearer direction."

    # Helper methods for data conversion
    def _order_block_to_dict(self, ob: OrderBlock) -> Dict[str, Any]:
        return {
            "start_time": ob.start_time,
            "end_time": ob.end_time,
            "high": ob.high,
            "low": ob.low,
            "volume": ob.volume,
            "type": ob.type,
            "strength": ob.strength,
            "tested": ob.tested,
        }

    def _fvg_to_dict(self, fvg: FairValueGap) -> Dict[str, Any]:
        return {
            "start_time": fvg.start_time,
            "end_time": fvg.end_time,
            "gap_high": fvg.gap_high,
            "gap_low": fvg.gap_low,
            "gap_size": fvg.gap_size,
            "type": fvg.type,
            "filled": fvg.filled,
            "fill_percentage": fvg.fill_percentage,
        }

    def _liquidity_sweep_to_dict(self, ls: LiquiditySweep) -> Dict[str, Any]:
        return {
            "time": ls.time,
            "price": ls.price,
            "type": ls.type,
            "volume": ls.volume,
            "significance": ls.significance,
        }

    def _structure_point_to_dict(self, sp: MarketStructurePoint) -> Dict[str, Any]:
        return {
            "time": sp.time,
            "price": sp.price,
            "type": sp.type,
            "volume": sp.volume,
            "confirmed": sp.confirmed,
        }

    def _calculate_ob_strength(
        self, df: pd.DataFrame, current_idx: int, origin_idx: int
    ) -> str:
        """Calculate Order Block strength based on various factors"""
        volume_ratio = (
            df.iloc[current_idx]["Volume"]
            / df["Volume"].rolling(20).mean().iloc[current_idx]
        )
        price_move = (
            abs(df.iloc[current_idx]["Close"] - df.iloc[origin_idx]["Close"])
            / df.iloc[origin_idx]["Close"]
        )

        if volume_ratio > 3 and price_move > 0.05:  # 5%+ move with 3x volume
            return "strong"
        elif volume_ratio > 2 and price_move > 0.03:  # 3%+ move with 2x volume
            return "medium"
        else:
            return "weak"


# Global instance
smart_money_analyzer = SmartMoneyAnalyzer()
