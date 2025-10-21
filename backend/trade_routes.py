from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from typing import Optional, List
import time
from gates_engine import *

router = APIRouter(prefix="/trade", tags=["trade"])

# Idempotency store (in-memory)
_IDEM: Dict[str, Any] = {}


class PreviewRequest(BaseModel):
    mode: Optional[Mode] = Mode.SIM
    strategy: str
    underlying: str
    legs: List[LegRequest]


class PlaceRequest(BaseModel):
    mode: Optional[Mode] = Mode.SIM
    strategy: str
    underlying: str
    legs: List[LegRequest]
    previewAuditHash: Optional[str] = None


# Market data service (stub)
class MarketDataService:
    async def get_underlying(self, symbol: str) -> Quote:
        return Quote(bid=250.0, ask=250.2, last=250.1, tsMs=int(time.time() * 1000))

    async def get_option(self, leg: LegRequest, underlying: str) -> Quote:
        return Quote(bid=2.5, ask=2.7, last=2.6, tsMs=int(time.time() * 1000))

    async def get_market(self, symbol: str) -> MarketMetrics:
        return MarketMetrics(ivRank=35, emAbs=12, atr14=10)

    async def get_session(self, symbol: str) -> SessionInfo:
        return SessionInfo(isOpen=True, minutesSinceOpen=30, minutesToClose=120)

    async def get_events(self, symbol: str) -> Events:
        return Events(hasEarnings=False, hasDividend=False)


# Trading service (stub)
class TradingService:
    async def place(
        self, underlying: str, strategy: str, legs: List[Leg], mode: Mode
    ) -> Dict[str, Any]:
        order_id = f"ORD_{int(time.time())}"
        return {"orderId": order_id, "status": "SUBMITTED"}


market = MarketDataService()
trader = TradingService()


@router.post("/preview")
async def trade_preview(body: PreviewRequest):
    # Build context
    u = await market.get_underlying(body.underlying)
    legs: List[Leg] = []

    for l in body.legs:
        q = await market.get_option(l, body.underlying)
        legs.append(
            Leg(
                side=l.side,
                type=l.type,
                expiry=l.expiry,
                strike=l.strike,
                qty=l.qty,
                quote=q,
            )
        )

    market_metrics = await market.get_market(body.underlying)
    session = await market.get_session(body.underlying)
    events = await market.get_events(body.underlying)

    # Estimate max loss (simplified)
    est_max_loss = (
        sum(leg.strike * leg.qty for leg in legs if leg.side == Side.SELL) * 100
    )

    mindfolio = MindfolioGreeks(
        delta=0, gamma=0, theta=0, vega=0, notional=est_max_loss, equity=200000
    )
    account = AccountState(tradeable=True, buyingPower=100000)

    ctx = TradeContext(
        mode=body.mode or Mode.SIM,
        strategy=body.strategy,
        underlying=body.underlying,
        underlyingQuote=u,
        legs=legs,
        mindfolio=mindfolio,
        account=account,
        market=market_metrics,
        session=session,
        events=events,
        openPositionsBySymbol={body.underlying: 0},
        estMaxLoss=est_max_loss,
    )

    # Evaluate gates
    gate_result = evaluate_gates(ctx, DEFAULT_CONFIG)

    # Create audit payload
    audit_payload = {
        "mode": body.mode,
        "strategy": body.strategy,
        "underlying": body.underlying,
        "legs": [l.dict() for l in body.legs],
        "u": {"bid": u.bid, "ask": u.ask, "last": u.last, "tsMs": u.tsMs},
        "frozenTs": int(time.time() * 1000),
    }
    ah = audit_hash(audit_payload)

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "decision": gate_result.decision,
            "results": [r.dict() for r in gate_result.results],
            "estMaxLoss": est_max_loss,
            "auditHash": ah,
            "frozenTs": audit_payload["frozenTs"],
        },
    )


@router.post("/place")
async def trade_place(
    body: PlaceRequest,
    x_mode: Optional[Mode] = Header(default=None, alias="X-Mode"),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    # Idempotency check
    if idempotency_key and idempotency_key in _IDEM:
        resp = _IDEM[idempotency_key]
        resp["reused"] = True
        return JSONResponse(status_code=200, content=resp)

    mode = x_mode or body.mode or Mode.SIM

    # Build context (similar to preview)
    u = await market.get_underlying(body.underlying)
    legs: List[Leg] = []

    for l in body.legs:
        q = await market.get_option(l, body.underlying)
        legs.append(
            Leg(
                side=l.side,
                type=l.type,
                expiry=l.expiry,
                strike=l.strike,
                qty=l.qty,
                quote=q,
            )
        )

    mindfolio = MindfolioGreeks(
        delta=0, gamma=0, theta=0, vega=0, notional=100000, equity=200000
    )
    account = AccountState(tradeable=True, buyingPower=100000)

    ctx = TradeContext(
        mode=mode,
        strategy=body.strategy,
        underlying=body.underlying,
        underlyingQuote=u,
        legs=legs,
        mindfolio=mindfolio,
        account=account,
        market=MarketMetrics(),
        session=SessionInfo(),
        events=Events(),
        openPositionsBySymbol={body.underlying: 0},
        estMaxLoss=1000,
    )

    # Run subset of gates for final sanity check
    subset_results = [gate(ctx, DEFAULT_CONFIG) for gate in SUBSET_PLACE]
    blocks = [
        r for r in subset_results if r.severity == Severity.BLOCK and not r.passed
    ]
    decision = "REJECT" if blocks else "ALLOW"

    # Create audit hash
    audit_payload = {
        "mode": mode.value,
        "strategy": body.strategy,
        "underlying": body.underlying,
        "legs": [l.dict() for l in body.legs],
        "subset": ["data.freshness", "pricing.sanity", "risk.buyingpower"],
    }
    ah = audit_hash(audit_payload)

    if decision == "REJECT":
        resp = {
            "ok": False,
            "decision": decision,
            "results": [r.dict() for r in subset_results],
            "auditHash": ah,
        }
        if idempotency_key:
            _IDEM[idempotency_key] = resp
        return JSONResponse(status_code=409, content=resp)

    # Place order
    order = await trader.place(body.underlying, body.strategy, legs, mode)

    resp = {
        "ok": True,
        "decision": decision,
        "results": [r.dict() for r in subset_results],
        "orderId": order["orderId"],
        "auditHash": ah,
    }

    if idempotency_key:
        _IDEM[idempotency_key] = resp

    return JSONResponse(status_code=200, content=resp)
