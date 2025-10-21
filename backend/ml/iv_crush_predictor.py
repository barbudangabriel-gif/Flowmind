"""
IV Crush Predictor - Machine Learning Model

Predicts implied volatility crush percentage after earnings announcements
using historical patterns, sector data, and market conditions.

Model: RandomForest / XGBoost (ensemble)
Features: Historical IV rank, sector, market cap, past crush patterns, market regime
Target: IV crush percentage (0.0 to 1.0)

Author: FlowMind AI Team
Date: October 15, 2025
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class IVCrushPredictor:
    """
    Machine Learning model for predicting IV crush after earnings

    This is a demo/prototype version using rule-based logic.
    Production version would use scikit-learn RandomForest or XGBoost
    trained on historical earnings data.
    """

    def __init__(self):
        """Initialize IV Crush Predictor"""
        self.model_version = "1.0.0-demo"
        self.is_trained = False

        # Historical crush patterns (demo data)
        # In production, this would be learned from data
        self.sector_crush_patterns = {
            "Technology": {"avg": 0.48, "std": 0.12, "min": 0.25, "max": 0.75},
            "Automotive": {"avg": 0.52, "std": 0.15, "min": 0.30, "max": 0.80},
            "Consumer Cyclical": {"avg": 0.45, "std": 0.10, "min": 0.28, "max": 0.65},
            "Healthcare": {"avg": 0.42, "std": 0.14, "min": 0.20, "max": 0.70},
            "Financial": {"avg": 0.38, "std": 0.08, "min": 0.22, "max": 0.55},
            "Energy": {"avg": 0.50, "std": 0.16, "min": 0.25, "max": 0.85},
        }

        # Symbol-specific historical crush data
        self.symbol_history = {
            "TSLA": {
                "last_8_quarters": [0.52, 0.48, 0.55, 0.45, 0.50, 0.47, 0.53, 0.49],
                "avg": 0.499,
                "std": 0.032,
                "trend": "stable",
            },
            "NVDA": {
                "last_8_quarters": [0.58, 0.55, 0.52, 0.60, 0.48, 0.54, 0.57, 0.53],
                "avg": 0.546,
                "std": 0.039,
                "trend": "increasing",
            },
            "AAPL": {
                "last_8_quarters": [0.35, 0.32, 0.38, 0.34, 0.36, 0.33, 0.37, 0.35],
                "avg": 0.350,
                "std": 0.019,
                "trend": "stable",
            },
            "META": {
                "last_8_quarters": [0.48, 0.45, 0.42, 0.50, 0.44, 0.46, 0.47, 0.43],
                "avg": 0.456,
                "std": 0.026,
                "trend": "stable",
            },
            "AMZN": {
                "last_8_quarters": [0.42, 0.40, 0.45, 0.38, 0.44, 0.41, 0.43, 0.39],
                "avg": 0.415,
                "std": 0.024,
                "trend": "stable",
            },
        }

        logger.info(f"IVCrushPredictor initialized (version {self.model_version})")

    async def predict_iv_crush(
        self,
        symbol: str,
        current_iv: float,
        sector: str = "Unknown",
        market_cap: float = 0,
        iv_rank: Optional[float] = None,
        market_regime: str = "normal",
    ) -> Optional[float]:
        """
        Predict IV crush percentage for upcoming earnings

        Args:
            symbol: Stock ticker
            current_iv: Current implied volatility (e.g., 0.82 for 82%)
            sector: Company sector
            market_cap: Market capitalization
            iv_rank: IV rank (0-100, percentile vs 1-year range)
            market_regime: Market condition (bull/normal/bear/high_vol)

        Returns:
            Predicted IV crush percentage (0.0 to 1.0)
            Returns None if prediction not confident enough
        """
        logger.info(f"Predicting IV crush for {symbol}")

        # Feature 1: Symbol-specific historical pattern
        symbol_data = self.symbol_history.get(symbol)

        if symbol_data:
            # Use historical average as base prediction
            base_crush = symbol_data["avg"]
            confidence = 0.85  # High confidence with historical data
        else:
            # Fall back to sector average
            sector_data = self.sector_crush_patterns.get(
                sector, {"avg": 0.45, "std": 0.12}
            )
            base_crush = sector_data["avg"]
            confidence = 0.65  # Medium confidence with sector data only

        # Feature 2: Current IV level adjustment
        # Higher current IV → potentially larger crush
        iv_adjustment = 0.0

        if current_iv > 0.80:  # Very high IV
            iv_adjustment = 0.05
        elif current_iv > 0.60:  # High IV
            iv_adjustment = 0.02
        elif current_iv < 0.30:  # Low IV
            iv_adjustment = -0.05

        # Feature 3: IV Rank adjustment
        if iv_rank is not None:
            if iv_rank > 80:  # IV in top 20% of 1-year range
                iv_adjustment += 0.03
            elif iv_rank < 20:  # IV in bottom 20%
                iv_adjustment -= 0.03

        # Feature 4: Market regime adjustment
        regime_adjustment = 0.0

        if market_regime == "high_vol":
            # High vol markets see larger crushes
            regime_adjustment = 0.05
        elif market_regime == "low_vol":
            # Low vol markets see smaller crushes
            regime_adjustment = -0.03
        elif market_regime == "bear":
            # Bear markets maintain elevated IV longer
            regime_adjustment = -0.02

        # Feature 5: Market cap adjustment
        # Larger cap = more analyst coverage = less surprise = smaller crush
        cap_adjustment = 0.0

        if market_cap > 1_000_000_000_000:  # > $1T
            cap_adjustment = -0.03
        elif market_cap > 500_000_000_000:  # > $500B
            cap_adjustment = -0.01
        elif market_cap < 50_000_000_000:  # < $50B
            cap_adjustment = 0.02

        # Combine all features
        predicted_crush = (
            base_crush + iv_adjustment + regime_adjustment + cap_adjustment
        )

        # Clamp to realistic bounds [0.15, 0.85]
        predicted_crush = max(0.15, min(0.85, predicted_crush))

        # Calculate prediction confidence
        # Lower confidence if we're far from historical patterns
        if symbol_data:
            deviation = abs(predicted_crush - base_crush)
            std = symbol_data["std"]

            if deviation > 2 * std:
                confidence *= 0.70  # Low confidence if 2+ std devs away
            elif deviation > std:
                confidence *= 0.85  # Medium confidence if 1+ std devs away

        logger.info(
            f"{symbol} IV crush prediction: {predicted_crush:.2%} "
            f"(confidence: {confidence:.2%})"
        )

        # Only return prediction if confidence is high enough
        if confidence < 0.60:
            logger.warning(
                f"Low confidence ({confidence:.2%}), not returning prediction"
            )
            return None

        return predicted_crush

    async def get_prediction_with_metadata(
        self, symbol: str, current_iv: float, **kwargs
    ) -> Dict:
        """
        Get prediction with full metadata and explanation

        Returns:
            Dictionary with prediction, confidence, features used, explanation
        """
        # Get base prediction
        predicted_crush = await self.predict_iv_crush(
            symbol=symbol, current_iv=current_iv, **kwargs
        )

        if predicted_crush is None:
            return {
                "symbol": symbol,
                "prediction": None,
                "confidence": 0.0,
                "reason": "Insufficient data or low confidence",
            }

        # Get historical context
        symbol_data = self.symbol_history.get(symbol)
        sector_data = self.sector_crush_patterns.get(
            kwargs.get("sector", "Unknown"), {"avg": 0.45}
        )

        # Build explanation
        explanation_parts = []

        if symbol_data:
            explanation_parts.append(
                f"Historical avg: {symbol_data['avg']:.2%} "
                f"(last 8 quarters, trend: {symbol_data['trend']})"
            )
        else:
            explanation_parts.append(
                f"Sector avg ({kwargs.get('sector', 'Unknown')}): "
                f"{sector_data['avg']:.2%}"
            )

        if current_iv > 0.80:
            explanation_parts.append("Current IV very high → larger crush expected")
        elif current_iv < 0.30:
            explanation_parts.append("Current IV low → smaller crush expected")

        if kwargs.get("market_regime") == "high_vol":
            explanation_parts.append("High volatility regime → larger crush")

        market_cap = kwargs.get("market_cap", 0)
        if market_cap > 1_000_000_000_000:
            explanation_parts.append("Mega cap → well-covered → smaller crush")

        return {
            "symbol": symbol,
            "prediction": predicted_crush,
            "confidence": 0.85 if symbol_data else 0.65,
            "historical_range": {
                "min": (
                    symbol_data["last_8_quarters"][0]
                    if symbol_data
                    else sector_data.get("min", 0.20)
                ),
                "max": (
                    symbol_data["last_8_quarters"][-1]
                    if symbol_data
                    else sector_data.get("max", 0.70)
                ),
                "avg": symbol_data["avg"] if symbol_data else sector_data["avg"],
            },
            "explanation": " | ".join(explanation_parts),
            "model_version": self.model_version,
            "timestamp": datetime.now().isoformat(),
        }

    def train_model(self, historical_data: List[Dict]):
        """
        Train ML model on historical earnings data

        In production, this would:
        1. Load historical earnings + IV data
        2. Extract features (IV rank, sector, market regime, etc.)
        3. Train RandomForest or XGBoost
        4. Validate on held-out test set
        5. Save model to disk

        For demo, this is a placeholder.
        """
        logger.info(f"Training model on {len(historical_data)} historical earnings")

        # Placeholder: In production, use scikit-learn
        # from sklearn.ensemble import RandomForestRegressor
        # model = RandomForestRegressor(n_estimators=100, max_depth=10)
        # model.fit(X_train, y_train)

        self.is_trained = True
        logger.info("Model training complete")

    def get_model_info(self) -> Dict:
        """Get model metadata"""
        return {
            "version": self.model_version,
            "is_trained": self.is_trained,
            "symbols_in_history": len(self.symbol_history),
            "sectors_covered": len(self.sector_crush_patterns),
            "model_type": "Rule-based (demo) - Production will use RandomForest/XGBoost",
        }
