from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class OptionsProvider(ABC):
    """Abstract base class for options data providers"""

    @abstractmethod
    def get_spot(self, symbol: str) -> float:
        """Get current spot price for symbol"""
        pass

    @abstractmethod
    def get_chain(
        self, symbol: str, expiry: Optional[str] = None, dte: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get options chain data for symbol

        Returns normalized structure:
        {
            "OptionChains": [
                {
                    "Expiration": "2025-02-21",
                    "Strikes": [
                        {
                            "StrikePrice": 200.0,
                            "Calls": [{"IV": 0.25, "Gamma": 0.01, "OpenInterest": 100}],
                            "Puts": [{"IV": 0.28, "Gamma": 0.012, "OpenInterest": 150}]
                        }
                    ]
                }
            ]
        }
        """
        pass
