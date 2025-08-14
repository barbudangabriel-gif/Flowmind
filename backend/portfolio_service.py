"""
Portfolio Analysis Service
Provides portfolio analytics, performance metrics, and risk analysis
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from tradestation_client import TradeStationClient, Position

logger = logging.getLogger(__name__)

class PortfolioMetrics:
    """Calculate portfolio performance metrics"""
    
    @staticmethod
    def calculate_total_return(positions: List[Position]) -> Dict[str, float]:
        """Calculate total portfolio return metrics"""
        total_market_value = sum(pos.market_value for pos in positions)
        total_cost_basis = sum(pos.average_price * abs(pos.quantity) for pos in positions)
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        
        total_return_pct = (total_unrealized_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0
        
        return {
            "total_market_value": total_market_value,
            "total_cost_basis": total_cost_basis,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_return_percent": total_return_pct,
            "position_count": len(positions)
        }
    
    @staticmethod
    def analyze_sector_allocation(positions: List[Position]) -> Dict[str, Dict[str, float]]:
        """Analyze portfolio allocation by asset type and sector"""
        asset_allocation = defaultdict(lambda: {"count": 0, "value": 0.0})
        
        for position in positions:
            # Use asset type as a proxy for sector until we get more detailed data
            asset_type = position.asset_type
            asset_allocation[asset_type]["count"] += 1
            asset_allocation[asset_type]["value"] += abs(position.market_value)
        
        total_value = sum(data["value"] for data in asset_allocation.values())
        
        # Convert to percentages
        for asset_type in asset_allocation:
            if total_value > 0:
                asset_allocation[asset_type]["percentage"] = (
                    asset_allocation[asset_type]["value"] / total_value * 100
                )
            else:
                asset_allocation[asset_type]["percentage"] = 0
                
        return dict(asset_allocation)
    
    @staticmethod
    def calculate_position_metrics(positions: List[Position]) -> List[Dict[str, Any]]:
        """Calculate detailed metrics for each position"""
        enhanced_positions = []
        
        total_value = sum(abs(pos.market_value) for pos in positions)
        
        for position in positions:
            position_dict = asdict(position)
            
            # Add additional calculated fields
            position_dict["weight_percent"] = (
                abs(position.market_value) / total_value * 100 if total_value > 0 else 0
            )
            position_dict["risk_score"] = abs(position.unrealized_pnl_percent) * abs(position.market_value) / 10000
            position_dict["position_type"] = "Long" if position.quantity > 0 else "Short"
            
            enhanced_positions.append(position_dict)
        
        # Sort by market value descending
        enhanced_positions.sort(key=lambda x: abs(x["market_value"]), reverse=True)
        
        return enhanced_positions

class RiskAnalyzer:
    """Portfolio risk analysis and management"""
    
    @staticmethod
    def calculate_concentration_risk(positions: List[Position]) -> Dict[str, Any]:
        """Calculate position concentration risk metrics"""
        if not positions:
            return {
                "max_position_weight": 0,
                "top_5_concentration": 0,
                "concentration_score": "LOW",
                "diversification_rating": "INSUFFICIENT"
            }
        
        total_value = sum(abs(pos.market_value) for pos in positions)
        position_weights = []
        
        for pos in positions:
            if total_value > 0:
                weight = abs(pos.market_value) / total_value * 100
                position_weights.append({
                    "symbol": pos.symbol,
                    "weight_percent": weight,
                    "market_value": pos.market_value
                })
        
        # Sort by weight
        position_weights.sort(key=lambda x: x["weight_percent"], reverse=True)
        
        # Calculate metrics
        max_position_weight = position_weights[0]["weight_percent"] if position_weights else 0
        top_5_concentration = sum(pos["weight_percent"] for pos in position_weights[:5])
        
        # Determine concentration score
        if max_position_weight > 40:
            concentration_score = "VERY HIGH"
        elif max_position_weight > 25:
            concentration_score = "HIGH"
        elif max_position_weight > 15:
            concentration_score = "MEDIUM"
        else:
            concentration_score = "LOW"
        
        # Determine diversification rating
        if len(positions) < 5:
            diversification_rating = "INSUFFICIENT"
        elif len(positions) < 10:
            diversification_rating = "LIMITED"
        elif len(positions) < 20:
            diversification_rating = "MODERATE"
        else:
            diversification_rating = "WELL DIVERSIFIED"
        
        return {
            "max_position_weight": max_position_weight,
            "top_5_concentration": top_5_concentration,
            "concentration_score": concentration_score,
            "diversification_rating": diversification_rating,
            "position_count": len(positions),
            "largest_positions": position_weights[:10]
        }
    
    @staticmethod
    def calculate_risk_metrics(positions: List[Position], account_balance: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics"""
        total_equity = account_balance.get("TotalEquity", 0)
        total_market_value = sum(abs(pos.market_value) for pos in positions)
        
        # Position concentration analysis
        concentration_analysis = RiskAnalyzer.calculate_concentration_risk(positions)
        
        # Calculate additional risk metrics
        unrealized_pnl_volatility = 0
        if positions:
            pnl_values = [pos.unrealized_pnl_percent for pos in positions]
            avg_pnl = sum(pnl_values) / len(pnl_values)
            unrealized_pnl_volatility = sum((pnl - avg_pnl) ** 2 for pnl in pnl_values) / len(pnl_values)
            unrealized_pnl_volatility = unrealized_pnl_volatility ** 0.5  # Standard deviation
        
        # Risk flags
        risk_flags = {
            "high_concentration": concentration_analysis["max_position_weight"] > 25,
            "low_diversification": len(positions) < 5,
            "high_volatility": unrealized_pnl_volatility > 20,
            "over_leveraged": total_market_value > total_equity * 2 if total_equity > 0 else False,
            "significant_losses": any(pos.unrealized_pnl_percent < -20 for pos in positions)
        }
        
        # Overall risk score (0-100, higher is riskier)
        risk_score = 0
        if risk_flags["high_concentration"]:
            risk_score += 30
        if risk_flags["low_diversification"]:
            risk_score += 25
        if risk_flags["high_volatility"]:
            risk_score += 20
        if risk_flags["over_leveraged"]:
            risk_score += 15
        if risk_flags["significant_losses"]:
            risk_score += 10
        
        # Risk level classification
        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level,
            "concentration_analysis": concentration_analysis,
            "volatility_metrics": {
                "unrealized_pnl_volatility": unrealized_pnl_volatility,
                "total_market_value": total_market_value,
                "portfolio_leverage": total_market_value / total_equity if total_equity > 0 else 0
            },
            "risk_flags": risk_flags,
            "recommendations": RiskAnalyzer._generate_risk_recommendations(risk_flags, concentration_analysis)
        }
    
    @staticmethod
    def _generate_risk_recommendations(risk_flags: Dict[str, bool], concentration: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if risk_flags["high_concentration"]:
            recommendations.append(f"Consider reducing position in largest holding ({concentration['max_position_weight']:.1f}% of portfolio)")
        
        if risk_flags["low_diversification"]:
            recommendations.append("Increase diversification by adding positions in different sectors/asset classes")
        
        if risk_flags["high_volatility"]:
            recommendations.append("Consider reducing position sizes to lower portfolio volatility")
        
        if risk_flags["over_leveraged"]:
            recommendations.append("Reduce leverage by closing some positions or adding capital")
        
        if risk_flags["significant_losses"]:
            recommendations.append("Review positions with >20% losses and consider stop-loss strategies")
        
        if not any(risk_flags.values()):
            recommendations.append("Portfolio risk profile appears well-balanced")
        
        return recommendations

class PerformanceAnalyzer:
    """Portfolio performance analysis"""
    
    @staticmethod
    async def calculate_performance_metrics(
        positions: List[Position], 
        orders: List[Any], 
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        # Current portfolio metrics
        current_metrics = PortfolioMetrics.calculate_total_return(positions)
        
        # Trading activity analysis
        recent_orders = [
            order for order in orders 
            if hasattr(order, 'timestamp') and 
            (datetime.now() - order.timestamp).days <= days_back
        ]
        
        filled_orders = [order for order in recent_orders if order.status in ["FLL", "PFL"]]
        
        # Calculate win/loss metrics (simplified)
        total_trades = len(filled_orders)
        
        # Group orders by symbol for P&L calculation
        symbol_trades = defaultdict(list)
        for order in filled_orders:
            symbol_trades[order.symbol].append(order)
        
        # Calculate trading metrics
        total_volume = sum(abs(order.quantity) for order in filled_orders)
        most_active_symbols = sorted(
            symbol_trades.keys(),
            key=lambda x: len(symbol_trades[x]),
            reverse=True
        )[:10]
        
        # Performance summary
        performance_data = {
            "analysis_period_days": days_back,
            "current_portfolio": current_metrics,
            "trading_activity": {
                "total_trades": total_trades,
                "total_volume": total_volume,
                "avg_trade_size": total_volume / total_trades if total_trades > 0 else 0,
                "most_active_symbols": most_active_symbols,
                "unique_symbols_traded": len(symbol_trades)
            },
            "period_analysis": {
                "analysis_start": (datetime.now() - timedelta(days=days_back)).isoformat(),
                "analysis_end": datetime.now().isoformat()
            }
        }
        
        return performance_data

class PortfolioService:
    """Main portfolio service orchestrating all portfolio operations"""
    
    def __init__(self, ts_client: TradeStationClient):
        self.ts_client = ts_client
        self.metrics = PortfolioMetrics()
        self.risk_analyzer = RiskAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
    
    async def get_comprehensive_portfolio_analysis(self, account_id: str) -> Dict[str, Any]:
        """Get comprehensive portfolio analysis combining all metrics"""
        try:
            # Get account data
            account_summary = await self.ts_client.get_account_summary(account_id)
            
            # Parse positions
            positions = []
            for pos_data in account_summary.get("positions", []):
                if isinstance(pos_data, dict):
                    position = Position(
                        account_id=pos_data.get("account_id", account_id),
                        symbol=pos_data.get("symbol", ""),
                        asset_type=pos_data.get("asset_type", "EQ"),
                        quantity=pos_data.get("quantity", 0),
                        average_price=pos_data.get("average_price", 0.0),
                        current_price=pos_data.get("current_price", 0.0),
                        market_value=pos_data.get("market_value", 0.0),
                        unrealized_pnl=pos_data.get("unrealized_pnl", 0.0),
                        unrealized_pnl_percent=pos_data.get("unrealized_pnl_percent", 0.0)
                    )
                    positions.append(position)
            
            # Calculate all metrics
            portfolio_metrics = self.metrics.calculate_total_return(positions)
            sector_allocation = self.metrics.analyze_sector_allocation(positions)
            enhanced_positions = self.metrics.calculate_position_metrics(positions)
            
            # Risk analysis
            risk_analysis = self.risk_analyzer.calculate_risk_metrics(
                positions, 
                account_summary.get("balances", {})
            )
            
            # Performance analysis
            performance_metrics = await self.performance_analyzer.calculate_performance_metrics(
                positions,
                account_summary.get("recent_orders", [])
            )
            
            # Combine all analysis
            comprehensive_analysis = {
                "account_id": account_id,
                "account_summary": {
                    "balances": account_summary.get("balances", {}),
                    "totals": account_summary.get("totals", {})
                },
                "portfolio_metrics": portfolio_metrics,
                "sector_allocation": sector_allocation,
                "positions": enhanced_positions,
                "risk_analysis": risk_analysis,
                "performance_metrics": performance_metrics,
                "recent_orders": account_summary.get("recent_orders", []),
                "analysis_timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_positions": len(positions),
                    "total_value": portfolio_metrics["total_market_value"],
                    "total_pnl": portfolio_metrics["total_unrealized_pnl"],
                    "overall_return": portfolio_metrics["total_return_percent"],
                    "risk_level": risk_analysis["risk_level"],
                    "risk_score": risk_analysis["risk_score"]
                }
            }
            
            logger.info(f"Generated comprehensive portfolio analysis for {account_id}")
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive portfolio analysis: {str(e)}")
            raise