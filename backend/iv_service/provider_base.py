from typing import List, Dict, Any
from abc import ABC, abstractmethod

class IVProvider(ABC):
 @abstractmethod
 async def get_spot(self, symbol: str) -> float: ...
 @abstractmethod
 async def get_atm_iv(self, symbol: str, dte: int) -> float: ...
 @abstractmethod
 async def list_terms(self, symbol: str) -> List[Dict[str, Any]]: ...
 @abstractmethod
 async def list_strikes(self, symbol: str, dte: int) -> List[int]: ...

# util: step infer
def tick_step(spot: float) -> float:
 if spot < 25:
 return 0.5
 if spot < 200:
 return 1.0
 if spot < 1000:
 return 5.0
 return 10.0

def round_to_tick(x: float, spot: float) -> int:
 step = tick_step(spot)
 return int(round(x / step) * step)
