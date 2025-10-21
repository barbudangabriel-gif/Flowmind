from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class WatchlistIn(BaseModel):
    name: str
    description: Optional[str] = None
    symbols: List[str]


class WatchlistOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    symbols: List[str]
    created_at: datetime
    updated_at: datetime


class WatchlistImport(BaseModel):
    name: str
    description: Optional[str] = None
    symbols_text: str
    delimiter: str = "auto"
    mode: str = "merge"


class ImportResponse(BaseModel):
    name: str
    inserted: int
    updated: int
    symbols: List[str]
