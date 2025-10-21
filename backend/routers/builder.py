from typing import Any, Dict

from fastapi import APIRouter

from services.builder_engine import price_structure
from services.historical_engine import historical_series

router = APIRouter(prefix="/builder", tags=["builder"])


@router.post("/price")
def builder_price(payload: Dict[str, Any]):
    return price_structure(payload)


@router.post("/historical")
def builder_historical(payload: Dict[str, Any]):
    return historical_series(payload)
