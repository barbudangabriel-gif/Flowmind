from pydantic import BaseModel
from typing import List, Optional, Literal, Tuple

class Summary(BaseModel):
 symbol: str
 spot: float
 iv: float
 em_usd: float
 em_pct: float
 front_dte: int
 back_dte: int

class Term(BaseModel):
 date: str # YYYY-MM-DD
 dte: int

class Strikes(BaseModel):
 symbol: str
 front: dict
 back: dict

Rule = Literal["calendar", "condor"]

class BatchRequest(BaseModel):
 watchlist: str = "WL_MAIN"
 rule: Rule = "calendar"
 mult: float = 0.5
 limit: int = 50

class BatchRow(BaseModel):
 symbol: str
 spot: float
 iv: float
 em_usd: float
 em_pct: float
 front_dte: int
 back_dte: int
 dc_low: Optional[int] = None
 dc_high: Optional[int] = None
 ic_shorts: Optional[Tuple[int, int]] = None
 ic_wings: Optional[Tuple[int, int]] = None
 error: Optional[str] = None

class BatchResponse(BaseModel):
 meta: dict
 rows: List[BatchRow]
