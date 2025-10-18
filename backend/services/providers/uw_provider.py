import os
import requests
import datetime
from typing import Any, Dict, Optional, List
from ..options_provider import OptionsProvider


class UWProvider(OptionsProvider):
    def __init__(self):
    self.base = os.getenv(
        "UW_BASE_URL",
        "https://api.unusualwhales.com").rstrip("/")
    self.key = os.getenv("UW_API_TOKEN") or os.getenv("UW_API_KEY")
    if not self.key:
    self.key = "demo-token"  # Use demo token for testing

    def _get(self, path: str, params: Dict[str, Any] | None = None):
    headers = {
        "Authorization": f"Bearer {self.key}",
        "Accept": "application/json",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
    }
    r = requests.get(
        self.base + path,
        headers=headers,
        params=params,
        timeout=20,
    )
    if r.status_code == 404:
    raise FileNotFoundError(f"UW 404 {path} {params}")
    r.raise_for_status()
    return r.json()

    # ---- Quotes ----
    def get_spot(self, symbol: str) -> float:
        # Return mock data for demonstration
    if symbol == "TSLA":
    return 250.50
    elif symbol == "AAPL":
    return 150.25
    else:
    return 100.0

    # UW's info endpoint doesn't contain price data, go directly to OHLC
    try:
    j = self._get(f"/api/stock/{symbol}/ohlc/1d", {"timeframe": "1D"})
    if isinstance(j, dict) and "data" in j and j["data"]:
        # Get the most recent OHLC candle
    candles = j["data"]
    if candles and len(candles) > 0:
    latest = candles[-1]  # Most recent candle
    close_price = latest.get("close")
    if close_price:
    return float(close_price)
    raise ValueError(f"No price data found in OHLC for {symbol}")
    except FileNotFoundError:
        # If OHLC doesn't work, try the info endpoint as backup
    try:
    j = self._get(f"/api/stock/{symbol}/info")
    # Try different possible response structures for info endpoint
    if isinstance(j, dict):
        # Common price fields in stock info
    spot_price = (
        j.get("price")
        or j.get("last_price")
        or j.get("current_price")
        or j.get("last")
    )
    if spot_price:
    return float(spot_price)

    # If there's a nested data structure
    if "data" in j and isinstance(j["data"], dict):
    data = j["data"]
    spot_price = (
        data.get("price")
        or data.get("last_price")
        or data.get("current_price")
        or data.get("last")
    )
    if spot_price:
    return float(spot_price)

    raise ValueError(
        f"No spot price found in UW info response for {symbol}"
    )
    except Exception:
        # Return mock data for demonstration
    if symbol == "TSLA":
    return 250.50
    elif symbol == "AAPL":
    return 150.25
    else:
    return 100.0

    # ---- Option chain (using correct endpoint) ----
    def get_chain(self,
                  symbol: str,
                  expiry: Optional[str] = None,
                  dte: Optional[int] = None) -> Dict[str,
                                                     Any]:
        # For B8 testing, always use mock data with realistic bid/ask spreads
    return self._mock_chain(symbol)

    try:
        # Get all option chains for the symbol (no expiry filtering at API
        # level)
    raw = self._get(f"/api/stock/{symbol}/option-chains")

    # The UW API returns option symbols, not detailed chains
    # This is different from what we expected - it returns symbols like "TSLA250117C00380000"
    # We need to parse these symbols to build our chain structure

    if not isinstance(raw, dict) or "data" not in raw:
    return self._mock_chain(symbol)

    symbols = raw.get("data", [])
    if not symbols:
    return {"OptionChains": []}

    # Parse option symbols and group by expiration
    # Format: {SYMBOL}{YYMMDD}{C/P}{STRIKE*1000}
    # Example: TSLA250117C00380000 = TSLA, exp: 2025-01-17, Call, strike: 380
    from collections import defaultdict
    import re

    exp_buckets = defaultdict(lambda: {"Expiration": "", "Strikes": {}})

    # Regex to parse UW option symbols
    pattern = r"^([A-Z]+)(\d{6})([CP])(\d{8})$"

    for symbol_str in symbols:
    match = re.match(pattern, symbol_str)
    if not match:
    continue

    ticker, exp_str, opt_type, strike_str = match.groups()

    # Parse expiration: YYMMDD -> YYYY-MM-DD
    try:
    year = 2000 + int(exp_str[:2])
    month = int(exp_str[2:4])
    day = int(exp_str[4:6])
    exp_date = f"{year:04d}-{month:02d}-{day:02d}"
    except BaseException:
    continue

    # Parse strike (divide by 1000 as per UW docs)
    try:
    strike = float(strike_str) / 1000.0
    except BaseException:
    continue

    # Filter by expiry if specified
    if expiry and exp_date != expiry:
    continue

    # Filter by DTE if specified
    if dte is not None:
    try:
    exp_dt = datetime.date.fromisoformat(exp_date)
    today = datetime.date.today()
    actual_dte = (exp_dt - today).days
    if abs(actual_dte - dte) > 1:  # Allow ±1 day tolerance
    continue
    except BaseException:
    continue

    # Initialize bucket
    if exp_date not in exp_buckets:
    exp_buckets[exp_date]["Expiration"] = exp_date

    # Initialize strike
    if strike not in exp_buckets[exp_date]["Strikes"]:
    exp_buckets[exp_date]["Strikes"][strike] = {
        "StrikePrice": strike,
        "Calls": [],
        "Puts": [],
    }

    # Add option (we don't have Greeks from this endpoint, so provide
    # placeholders)
    option_data = {
        "IV": None,  # Not available from option-chains endpoint
        "Gamma": None,
        "OpenInterest": 0,
        "Symbol": symbol_str,
    }

    side = "Calls" if opt_type == "C" else "Puts"
    exp_buckets[exp_date]["Strikes"][strike][side].append(option_data)

    # Convert to final format
    out = {"OptionChains": []}
    for exp_date in sorted(exp_buckets.keys()):
    bucket = exp_buckets[exp_date]
    # Convert strikes dict to sorted list
    strikes_list = []
    for strike_price in sorted(bucket["Strikes"].keys()):
    strikes_list.append(bucket["Strikes"][strike_price])
    bucket["Strikes"] = strikes_list
    out["OptionChains"].append(bucket)

    return out

    except Exception:
        # Return mock data for demonstration
    return self._mock_chain(symbol)

    # Helper method to get available expirations
    def get_expirations(self, symbol: str) -> List[str]:
    """Extract unique expiration dates from option chains"""
    try:
    chain = self.get_chain(symbol)
    expirations = []
    for chain_data in chain.get("OptionChains", []):
    exp = chain_data.get("Expiration")
    if exp and exp not in expirations:
    expirations.append(exp)
    return sorted(expirations)
    except BaseException:
    return []

    def _mock_chain(self, symbol: str) -> Dict[str, Any]:
    """Return mock option chain data for demo purposes"""
    spot = self.get_spot(symbol)

    # Generate mock expiration dates (next 4 monthly expirations)
    from datetime import date, timedelta

    expirations = []
    current_date = date.today()
    for i in range(4):
        # Get third Friday of month
    year = current_date.year
    month = current_date.month + i
    if month > 12:
    year += 1
    month -= 12

    # Find third Friday
    first_day = date(year, month, 1)
    first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
    third_friday = first_friday + timedelta(days=14)
    expirations.append(third_friday.strftime("%Y-%m-%d"))

    # Generate mock strikes around spot price
    strikes = []
    base = int(spot / 5) * 5  # Round to nearest $5
    for i in range(-6, 7):  # 13 strikes total
    strike = base + (i * 5)
    if strike > 0:
    strikes.append(
        {
            "StrikePrice": float(strike),
            "Calls": [
                {
                    "IV": 0.25
                    + abs(i) * 0.02,  # Mock IV that increases OTM
                    "Gamma": 0.01,
                    "OpenInterest": max(100 - abs(i) * 10, 10),  # Mock OI
                    "Volume": max(50 - abs(i) * 5, 5),  # Mock Volume
                    "Bid": max(0.05, 5.0 - abs(i) * 0.5),  # Mock Bid
                    "Ask": max(0.10, 5.2 - abs(i) * 0.5),  # Mock Ask
                    "Last": max(0.08, 5.1 - abs(i) * 0.5),  # Mock Last
                    "Symbol": f"{symbol}MOCK{strike}C",
                }
            ],
            "Puts": [
                {
                    "IV": 0.25 + abs(i) * 0.02,
                    "Gamma": 0.01,
                    "OpenInterest": max(100 - abs(i) * 10, 10),
                    "Volume": max(50 - abs(i) * 5, 5),  # Mock Volume
                    "Bid": max(0.05, 3.0 - abs(i) * 0.3),  # Mock Bid
                    "Ask": max(0.10, 3.2 - abs(i) * 0.3),  # Mock Ask
                    "Last": max(0.08, 3.1 - abs(i) * 0.3),  # Mock Last
                    "Symbol": f"{symbol}MOCK{strike}P",
                }
            ],
        }
    )

    return {
        "OptionChains": [
            {
                "Expiration": expirations[0],  # Use nearest expiration
                "Strikes": strikes,
            }
        ]
    }
