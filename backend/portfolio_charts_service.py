"""
Portfolio Charts Service
Provides data and analysis for portfolio performance charts and allocation visualizations
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class PortfolioChartsService:
    def __init__(self):
        self.logger = logger

    async def get_portfolio_performance_data(
        self,
        portfolio_id: str,
        filter_type: str = "closed",  # 'closed' or 'all'
        asset_type: str = "combined",  # 'stocks', 'options', 'combined'
        timeframe: str = "all",  # 'daily', 'weekly', 'monthly', 'all', 'custom'
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get portfolio performance data for charting
        """
        try:
            self.logger.info(f"Fetching performance data for portfolio {portfolio_id}")

            # Generate performance data based on filters
            performance_data = await self._generate_performance_data(
                portfolio_id, filter_type, asset_type, timeframe, start_date, end_date
            )

            # Calculate portfolio summary
            portfolio_summary = await self._calculate_portfolio_summary(
                portfolio_id, performance_data
            )

            return {
                "status": "success",
                "portfolio_id": portfolio_id,
                "filters": {
                    "filter_type": filter_type,
                    "asset_type": asset_type,
                    "timeframe": timeframe,
                },
                "performance_data": performance_data,
                "portfolio_summary": portfolio_summary,
            }

        except Exception as e:
            self.logger.error(f"Error getting portfolio performance data: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to fetch performance data: {str(e)}",
            }

    async def get_portfolio_allocation_data(
        self,
        portfolio_id: str,
        filter_type: str = "closed",
        asset_type: str = "combined",
        timeframe: str = "all",
    ) -> Dict[str, Any]:
        """
        Get portfolio allocation data for pie charts and distribution analysis
        """
        try:
            self.logger.info(f"Fetching allocation data for portfolio {portfolio_id}")

            # Generate allocation data
            allocation_data = await self._generate_allocation_data(
                portfolio_id, filter_type, asset_type
            )

            return {
                "status": "success",
                "portfolio_id": portfolio_id,
                "allocation_data": allocation_data,
                "total_positions": len(allocation_data),
                "filters": {"filter_type": filter_type, "asset_type": asset_type},
            }

        except Exception as e:
            self.logger.error(f"Error getting portfolio allocation data: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to fetch allocation data: {str(e)}",
            }

    async def _generate_performance_data(
        self,
        portfolio_id: str,
        filter_type: str,
        asset_type: str,
        timeframe: str,
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        Generate mock performance data for development
        In production, this would fetch real trading data
        """
        # Determine date range
        end_dt = datetime.now()
        if timeframe == "daily":
            start_dt = end_dt - timedelta(days=30)
            interval_days = 1
        elif timeframe == "weekly":
            start_dt = end_dt - timedelta(weeks=12)
            interval_days = 7
        elif timeframe == "monthly":
            start_dt = end_dt - timedelta(days=365)
            interval_days = 30
        elif timeframe == "custom" and start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            interval_days = 1
        else:  # 'all'
            start_dt = end_dt - timedelta(days=90)
            interval_days = 1

        performance_data = []
        current_dt = start_dt

        # Base values for different asset types
        base_stocks = 1000
        base_options = 300
        stocks_trend = 0
        options_trend = 0

        while current_dt <= end_dt:
            # Add some realistic volatility and trends
            stocks_noise = -50 + secrets.randbelow(10000) / 100  # -50 to 50
            options_noise = -30 + secrets.randbelow(6000) / 100  # -30 to 30

            # Slight upward trend with volatility
            stocks_trend += -5 + secrets.randbelow(1500) / 100  # -5 to 10
            options_trend += -8 + secrets.randbelow(2000) / 100  # -8 to 12

            stocks_pnl = base_stocks + stocks_trend + stocks_noise
            options_pnl = base_options + options_trend + options_noise
            combined_pnl = stocks_pnl + options_pnl

            # Apply filters
            if filter_type == "closed":
                # Reduce values slightly to simulate only closed positions
                stocks_pnl *= 0.8
                options_pnl *= 0.7
                combined_pnl *= 0.75

            performance_data.append(
                {
                    "date": current_dt.strftime("%Y-%m-%d"),
                    "stocks_pnl": round(stocks_pnl, 2),
                    "options_pnl": round(options_pnl, 2),
                    "combined_pnl": round(combined_pnl, 2),
                    "cumulative_stocks": round(base_stocks + stocks_trend, 2),
                    "cumulative_options": round(base_options + options_trend, 2),
                    "cumulative_combined": round(
                        base_stocks + base_options + stocks_trend + options_trend, 2
                    ),
                }
            )

            current_dt += timedelta(days=interval_days)

        return performance_data

    async def _generate_allocation_data(
        self, portfolio_id: str, filter_type: str, asset_type: str
    ) -> List[Dict[str, Any]]:
        """
        Generate mock allocation data for development
        In production, this would fetch real position data
        """
        # Mock positions data with cash and margin
        all_positions = [
            {
                "name": "AAPL",
                "value": 25000,
                "type": "stocks",
                "count": 5,
                "sector": "Technology",
            },
            {
                "name": "MSFT",
                "value": 20000,
                "type": "stocks",
                "count": 3,
                "sector": "Technology",
            },
            {
                "name": "GOOGL",
                "value": 15000,
                "type": "stocks",
                "count": 2,
                "sector": "Technology",
            },
            {
                "name": "NVDA",
                "value": 12000,
                "type": "stocks",
                "count": 4,
                "sector": "Technology",
            },
            {
                "name": "JPM",
                "value": 18000,
                "type": "stocks",
                "count": 3,
                "sector": "Finance",
            },
            {
                "name": "JNJ",
                "value": 14000,
                "type": "stocks",
                "count": 2,
                "sector": "Healthcare",
            },
            {
                "name": "TSLA Calls",
                "value": 8000,
                "type": "options",
                "count": 10,
                "expiry": "2024-12-20",
            },
            {
                "name": "SPY Puts",
                "value": 5000,
                "type": "options",
                "count": 5,
                "expiry": "2024-11-15",
            },
            {
                "name": "AAPL Calls",
                "value": 6000,
                "type": "options",
                "count": 8,
                "expiry": "2024-12-15",
            },
            {
                "name": "QQQ Calls",
                "value": 4000,
                "type": "options",
                "count": 6,
                "expiry": "2025-01-17",
            },
            {
                "name": "Cash",
                "value": 100000,
                "type": "cash",
                "count": 1,
                "sector": "Cash",
            },
            {
                "name": "Margin Available",
                "value": 25000,
                "type": "margin",
                "count": 1,
                "sector": "Margin",
            },
        ]

        # Apply asset type filter
        if asset_type == "stocks":
            filtered_positions = [
                pos for pos in all_positions if pos["type"] == "stocks"
            ]
        elif asset_type == "options":
            filtered_positions = [
                pos for pos in all_positions if pos["type"] == "options"
            ]
        else:  # combined
            filtered_positions = all_positions

        # Apply closed/all filter
        if filter_type == "closed":
            # Simulate some positions being closed (70% probability to keep)
            filtered_positions = [
                pos for pos in filtered_positions if secrets.randbelow(100) > 30
            ]

        # Add some variance to values
        for pos in filtered_positions:
            variance = 0.9 + secrets.randbelow(20) / 100  # 0.9-1.1
            pos["value"] = round(pos["value"] * variance, 2)

        return filtered_positions

    async def _calculate_portfolio_summary(
        self, portfolio_id: str, performance_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate portfolio summary statistics
        """
        if not performance_data:
            return {"total_value": 0, "total_pnl": 0, "cash_balance": 0}

        latest_data = performance_data[-1]
        first_data = performance_data[0]

        # Portfolio values based on portfolio_id
        portfolio_values = {"htech-15t": {"total_value": 139902.60, "cash": 100000.00}}

        portfolio_info = portfolio_values.get(
            portfolio_id, portfolio_values["htech-15t"]
        )

        total_pnl = latest_data["combined_pnl"] - first_data["combined_pnl"]

        return {
            "total_value": portfolio_info["total_value"],
            "total_pnl": round(total_pnl, 2),
            "cash_balance": portfolio_info["cash"],
            "pnl_percentage": (
                round((total_pnl / portfolio_info["total_value"]) * 100, 2)
                if portfolio_info["total_value"] > 0
                else 0
            ),
        }
