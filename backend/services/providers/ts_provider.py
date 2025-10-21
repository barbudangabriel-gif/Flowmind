import logging
import os
from typing import Any, Dict, Optional

from ..options_provider import OptionsProvider

logger = logging.getLogger(__name__)


class TSProvider(OptionsProvider):
    def __init__(self):
        self.base = os.getenv("TS_BASE_URL", "https://api.tradestation.com")

    def get_spot(self, symbol: str) -> float:
        """Get current spot price from TradeStation"""
        try:
            # Import here to avoid circular imports
            from database import DatabaseManager
            from services.ts_oauth import authorized_get

            # Try to get from database first (fallback to existing system)
            try:
                db_manager = DatabaseManager()
                with db_manager.get_connection() as conn:
                    row = conn.execute(
                        "SELECT last FROM marks WHERE symbol = ?", (symbol,)
                    ).fetchone()
                    if row and row["last"]:
                        return float(row["last"])
            except Exception:
                pass  # Fallback to TS API

            # Get from TradeStation API
            r = authorized_get(
                None, f"{self.base}/v3/marketdata/quotes", params={"symbols": symbol}
            )
            r.raise_for_status()
            j = r.json()

            # Handle different TS response formats
            quotes = j.get("Quotes", j.get("quotes", []))
            if quotes:
                last_price = quotes[0].get("Last") or quotes[0].get("last")
                if last_price:
                    return float(last_price)

            raise ValueError(f"No spot price found in TS response for {symbol}")

        except Exception as e:
            logger.error(f"Failed to get spot price for {symbol} from TS: {e}")
            raise

    def get_chain(
        self, symbol: str, expiry: Optional[str] = None, dte: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get options chain from TradeStation - already in correct format"""
        try:
            # Import here to avoid circular imports
            from services.ts_oauth import authorized_get

            params = {"symbol": symbol}
            if expiry:
                params["expiry"] = expiry
            if dte is not None:
                params["dte"] = dte

            r = authorized_get(
                None, f"{self.base}/v3/marketdata/optionchains", params=params
            )
            r.raise_for_status()

            # TradeStation already returns data in the format we expect
            # {"OptionChains": [{"Expiration": "...", "Strikes": [...]}]}
            chain_data = r.json()

            # Ensure we have the expected structure
            if "OptionChains" not in chain_data:
                chain_data = {"OptionChains": chain_data.get("optionChains", [])}

            return chain_data

        except Exception as e:
            logger.error(f"Failed to get options chain for {symbol} from TS: {e}")
            # For testing/development, return empty structure
            return {"OptionChains": []}
