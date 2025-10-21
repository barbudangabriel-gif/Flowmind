"""
Module for collecting and managing stock ticker data from S&P 500 and NASDAQ
"""

import asyncio
import logging
from typing import Any, Dict, List

import yfinance as yf

logger = logging.getLogger(__name__)

# S&P 500 tickers list (top 100 most liquid ones to avoid API limits)
SP500_TICKERS = [
    # Technology
    "AAPL",
    "MSFT",
    "GOOGL",
    "GOOG",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "NFLX",
    "ADBE",
    "CRM",
    "ORCL",
    "INTC",
    "AMD",
    "CSCO",
    "AVGO",
    "QCOM",
    "IBM",
    "NOW",
    "INTU",
    "MU",
    "AMAT",
    "LRCX",
    "ADI",
    "KLAC",
    "MCHP",
    "CDNS",
    "SNPS",
    "FTNT",
    "PANW",
    # Healthcare & Biotech
    "UNH",
    "JNJ",
    "PFE",
    "ABBV",
    "MRK",
    "LLY",
    "TMO",
    "ABT",
    "DHR",
    "BMY",
    "AMGN",
    "GILD",
    "VRTX",
    "CVS",
    "CI",
    "HUM",
    "ANTM",
    "ZTS",
    "REGN",
    "BIIB",
    # Financial Services
    "BRK-B",
    "JPM",
    "BAC",
    "WFC",
    "GS",
    "MS",
    "C",
    "AXP",
    "USB",
    "PNC",
    "TFC",
    "COF",
    "SCHW",
    "CME",
    "ICE",
    "SPGI",
    "MCO",
    "BLK",
    "CB",
    "AIG",
    # Consumer & Retail
    "AMZN",
    "WMT",
    "HD",
    "PG",
    "KO",
    "PEP",
    "COST",
    "MCD",
    "NKE",
    "SBUX",
    "TGT",
    "LOW",
    "TJX",
    "DIS",
    "CMCSA",
    "VZ",
    "T",
    "NFLX",
    "CL",
    "KMB",
    # Industrial & Energy
    "BA",
    "CAT",
    "MMM",
    "GE",
    "HON",
    "UNP",
    "LMT",
    "RTX",
    "UPS",
    "FDX",
    "XOM",
    "CVX",
    "COP",
    "EOG",
    "SLB",
    "PSX",
    "VLO",
    "MPC",
    "OXY",
    "DVN",
]

# NASDAQ 100 tickers (most important ones)
NASDAQ_TICKERS = [
    # Technology Leaders
    "AAPL",
    "MSFT",
    "GOOGL",
    "GOOG",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "NFLX",
    "ADBE",
    "PYPL",
    "INTC",
    "CSCO",
    "CMCSA",
    "AVGO",
    "TXN",
    "QCOM",
    "INTU",
    "AMD",
    "MU",
    "ISRG",
    "AMAT",
    "LRCX",
    "KLAC",
    "ADI",
    "MCHP",
    "CDNS",
    "SNPS",
    "MRVL",
    "NXPI",
    # Biotech & Healthcare
    "AMGN",
    "GILD",
    "VRTX",
    "BIIB",
    "REGN",
    "CELG",
    "ILMN",
    "ALXN",
    "BMRN",
    "INCY",
    # Consumer & Services
    "COST",
    "SBUX",
    "MAR",
    "BKNG",
    "EBAY",
    "FAST",
    "PAYX",
    "FISV",
    "ADP",
    "ROST",
    # Other Important
    "CHTR",
    "ATVI",
    "EA",
    "WBA",
    "MDLZ",
    "DLTR",
    "VRSK",
    "CTSH",
    "VRSN",
    "XLNX",
]

# Popular crypto and forex tickers for additional coverage
ADDITIONAL_TICKERS = [
    "BTC-USD",
    "ETH-USD",
    "SPY",
    "QQQ",
    "IWM",
    "VTI",
    "VTV",
    "VUG",
    "IVV",
    "VOO",
]


class TickerDataManager:
    def __init__(self):
        self.sp500_data = {}
        self.nasdaq_data = {}
        self.last_updated = None

    async def get_sp500_tickers(self) -> List[str]:
        """Get S&P 500 ticker list"""
        return SP500_TICKERS

    async def get_nasdaq_tickers(self) -> List[str]:
        """Get NASDAQ ticker list"""
        return NASDAQ_TICKERS

    async def get_all_tickers(self) -> List[str]:
        """Get combined ticker list"""
        all_tickers = list(set(SP500_TICKERS + NASDAQ_TICKERS + ADDITIONAL_TICKERS))
        return sorted(all_tickers)

    async def get_ticker_info_batch(
        self, tickers: List[str], max_batch_size: int = 20
    ) -> List[Dict[str, Any]]:
        """Get ticker information in batches to avoid API limits"""
        results = []

        # Process in smaller batches to avoid overwhelming the API
        for i in range(0, len(tickers), max_batch_size):
            batch = tickers[i : i + max_batch_size]
            batch_results = await self._process_ticker_batch(batch)
            results.extend(batch_results)

            # Small delay between batches
            await asyncio.sleep(1)

        return results

    async def _process_ticker_batch(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Process a single batch of tickers"""
        results = []

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                history = stock.history(period="1d")

                if not history.empty:
                    latest = history.iloc[-1]
                    previous = history.iloc[-2] if len(history) > 1 else latest

                    ticker_data = {
                        "symbol": ticker,
                        "name": info.get("longName", ticker),
                        "sector": info.get("sector", "Unknown"),
                        "industry": info.get("industry", "Unknown"),
                        "price": float(latest["Close"]),
                        "change": float(latest["Close"] - previous["Close"]),
                        "change_percent": float(
                            ((latest["Close"] - previous["Close"]) / previous["Close"])
                            * 100
                        ),
                        "volume": int(latest["Volume"]),
                        "market_cap": info.get("marketCap"),
                        "pe_ratio": info.get("forwardPE"),
                        "dividend_yield": info.get("dividendYield"),
                        "52_week_high": info.get("fiftyTwoWeekHigh"),
                        "52_week_low": info.get("fiftyTwoWeekLow"),
                        "beta": info.get("beta"),
                        "avg_volume": info.get("averageVolume"),
                        "exchange": info.get("exchange", "Unknown"),
                    }
                    results.append(ticker_data)

            except Exception as e:
                logger.warning(f"Failed to get data for {ticker}: {str(e)}")
                # Add basic data even if detailed fetch fails
                results.append(
                    {
                        "symbol": ticker,
                        "name": ticker,
                        "sector": "Unknown",
                        "industry": "Unknown",
                        "price": 0.0,
                        "change": 0.0,
                        "change_percent": 0.0,
                        "volume": 0,
                        "market_cap": None,
                        "pe_ratio": None,
                        "dividend_yield": None,
                        "52_week_high": None,
                        "52_week_low": None,
                        "beta": None,
                        "avg_volume": None,
                        "exchange": "Unknown",
                    }
                )
                continue

        return results

    async def screen_stocks(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Screen stocks based on criteria"""
        tickers = await self.get_all_tickers()

        # Limit to a reasonable number for performance
        tickers = tickers[:50]  # First 50 most liquid stocks

        stock_data = await self.get_ticker_info_batch(tickers)

        filtered_stocks = []
        for stock in stock_data:
            if self._meets_criteria(stock, criteria):
                filtered_stocks.append(stock)

        return filtered_stocks

    def _meets_criteria(self, stock: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if stock meets screening criteria"""
        try:
            # Price range
            if "min_price" in criteria and criteria["min_price"]:
                if stock["price"] < float(criteria["min_price"]):
                    return False

            if "max_price" in criteria and criteria["max_price"]:
                if stock["price"] > float(criteria["max_price"]):
                    return False

            # Market cap range
            if (
                "min_market_cap" in criteria
                and criteria["min_market_cap"]
                and stock["market_cap"]
            ):
                if (
                    stock["market_cap"] < float(criteria["min_market_cap"]) * 1000000
                ):  # Convert to millions
                    return False

            if (
                "max_market_cap" in criteria
                and criteria["max_market_cap"]
                and stock["market_cap"]
            ):
                if stock["market_cap"] > float(criteria["max_market_cap"]) * 1000000:
                    return False

            # P/E ratio range
            if "min_pe" in criteria and criteria["min_pe"] and stock["pe_ratio"]:
                if stock["pe_ratio"] < float(criteria["min_pe"]):
                    return False

            if "max_pe" in criteria and criteria["max_pe"] and stock["pe_ratio"]:
                if stock["pe_ratio"] > float(criteria["max_pe"]):
                    return False

            # Volume filter
            if "min_volume" in criteria and criteria["min_volume"]:
                if stock["volume"] < int(criteria["min_volume"]):
                    return False

            # Sector filter
            if (
                "sector" in criteria
                and criteria["sector"]
                and criteria["sector"] != "All"
            ):
                if stock["sector"] != criteria["sector"]:
                    return False

            # Change percent range
            if "min_change" in criteria and criteria["min_change"]:
                if stock["change_percent"] < float(criteria["min_change"]):
                    return False

            if "max_change" in criteria and criteria["max_change"]:
                if stock["change_percent"] > float(criteria["max_change"]):
                    return False

            return True

        except (TypeError, ValueError):
            return False  # Global instance


ticker_manager = TickerDataManager()
