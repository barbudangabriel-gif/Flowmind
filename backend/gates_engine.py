import hashlib
import json
import time
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class Mode(str, Enum):
    SIM = "SIM"
    REAL = "REAL"


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OptionType(str, Enum):
    CALL = "CALL"
    PUT = "PUT"


class Severity(str, Enum):
    BLOCK = "BLOCK"
    WARN = "WARN"


class Quote(BaseModel):
    bid: float = 0.0
    ask: float = 0.0
    last: float = 0.0
    tsMs: int = 0


class LegRequest(BaseModel):
    side: Side
    type: OptionType
    expiry: str
    strike: float
    qty: int


class Leg(BaseModel):
    side: Side
    type: OptionType
    expiry: str
    strike: float
    qty: int
    quote: Quote


class PortfolioGreeks(BaseModel):
    delta: float = 0
    gamma: float = 0
    theta: float = 0
    vega: float = 0
    notional: float = 100000
    equity: float = 200000


class AccountState(BaseModel):
    tradeable: bool = True
    buyingPower: float = 100000


class MarketMetrics(BaseModel):
    ivRank: float = 35
    emAbs: float = 12
    atr14: float = 10


class SessionInfo(BaseModel):
    isOpen: bool = True
    minutesSinceOpen: int = 30
    minutesToClose: int = 120


class Events(BaseModel):
    hasEarnings: bool = False
    hasDividend: bool = False


class TradeContext(BaseModel):
    mode: Mode
    strategy: str
    underlying: str
    underlyingQuote: Quote
    legs: List[Leg]
    portfolio: PortfolioGreeks
    account: AccountState
    market: MarketMetrics
    session: SessionInfo
    events: Events
    openPositionsBySymbol: Dict[str, int] = {}
    estMaxLoss: float = 0


class GateConfig(BaseModel):
    maxPositionsPerSymbol: int = 5
    maxPortfolioNotional: float = 1000000
    minBuyingPowerRatio: float = 0.2
    maxQuoteAgeMs: int = 30000
    minLiquidity: int = 100
    maxBidAskSpread: float = 0.20
    ivRankMin: float = 20
    ivRankMax: float = 80
    emThreshold: float = 5.0
    maxDelta: float = 0.50
    # New config pentru term structure
    minAbsFrontBackIVpp: float = 0.03  # 3pp
    termSlopeMode: str = "any"  # "any" | "front_gt_back" | "back_gt_front"


class GateResult(BaseModel):
    gateName: str
    passed: bool
    severity: Severity
    reason: str
    details: Optional[Dict[str, Any]] = None


class GateDecision(BaseModel):
    decision: str  # ALLOW, ALLOW_WITH_WARNINGS, REJECT
    results: List[GateResult]


DEFAULT_CONFIG = GateConfig()


def gate_tradeability(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    """Gate 1: Account must be tradeable"""
    passed = ctx.account.tradeable
    return GateResult(
        gateName="tradeability",
        passed=passed,
        severity=Severity.BLOCK,
        reason="Account tradeable" if passed else "Account not tradeable",
    )


def gate_data_freshness(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    """Gate 2: Quote data must be fresh"""
    now = int(time.time() * 1000)
    max_age = cfg.maxQuoteAgeMs

    stale_quotes = []
    for leg in ctx.legs:
        age = now - leg.quote.tsMs
        if age > max_age:
            stale_quotes.append(f"{leg.type}{leg.strike}")

    if ctx.underlyingQuote.tsMs and (now - ctx.underlyingQuote.tsMs) > max_age:
        stale_quotes.append("underlying")

    passed = len(stale_quotes) == 0
    return GateResult(
        gateName="data.freshness",
        passed=passed,
        severity=Severity.BLOCK,
        reason="All quotes fresh"
        if passed
        else f"Stale quotes: {', '.join(stale_quotes)}",
    )


def gate_buying_power(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    """Gate 3: Sufficient buying power"""
    required = ctx.estMaxLoss
    available = ctx.account.buyingPower
    ratio = available / max(required, 1)

    passed = ratio >= cfg.minBuyingPowerRatio
    return GateResult(
        gateName="risk.buyingpower",
        passed=passed,
        severity=Severity.BLOCK,
        reason=f"BP ratio: {ratio:.2f}"
        if passed
        else f"Insufficient BP: {ratio:.2f} < {cfg.minBuyingPowerRatio}",
    )


def gate_liquidity(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    """Gate 4: Option liquidity check"""
    illiquid_legs = []
    for leg in ctx.legs:
        volume = getattr(leg.quote, "volume", 0)
        if volume < cfg.minLiquidity:
            illiquid_legs.append(f"{leg.type}{leg.strike}")

    passed = len(illiquid_legs) == 0
    return GateResult(
        gateName="liquidity",
        passed=passed,
        severity=Severity.WARN,
        reason="All legs liquid"
        if passed
        else f"Low liquidity: {', '.join(illiquid_legs)}",
    )


def gate_pricing_sanity(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    """Gate 5: Bid/ask spread sanity"""
    wide_spreads = []
    for leg in ctx.legs:
        if leg.quote.ask > 0 and leg.quote.bid > 0:
            spread = (leg.quote.ask - leg.quote.bid) / leg.quote.bid
            if spread > cfg.maxBidAskSpread:
                wide_spreads.append(f"{leg.type}{leg.strike}:{spread:.1%}")

    passed = len(wide_spreads) == 0
    return GateResult(
        gateName="pricing.sanity",
        passed=passed,
        severity=Severity.WARN,
        reason="Spreads OK" if passed else f"Wide spreads: {', '.join(wide_spreads)}",
    )


# Additional gates (simplified for v0.1)
# Additional gates pentru long-vega strategies
def gate_term_structure(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    """Term structure gate pentru CALENDAR/DIAGONAL/DOUBLE_DIAGONAL"""
    if ctx.strategy not in ("CALENDAR", "DIAGONAL", "DOUBLE_DIAGONAL"):
        return GateResult(
            gateName="term.structure",
            passed=True,
            severity=Severity.WARN,
            reason="N/A pentru strategy",
        )

    # Stub term structure data
    iv_front = 0.55
    iv_back = 0.50
    diff = iv_front - iv_back

    abs_ok = abs(diff) >= cfg.minAbsFrontBackIVpp
    slope_ok = (
        cfg.termSlopeMode == "any"
        or (cfg.termSlopeMode == "front_gt_back" and diff >= cfg.minAbsFrontBackIVpp)
        or (cfg.termSlopeMode == "back_gt_front" and -diff >= cfg.minAbsFrontBackIVpp)
    )

    passed = abs_ok and slope_ok
    return GateResult(
        gateName="term.structure",
        passed=passed,
        severity=Severity.BLOCK,
        reason=f"|Front-Back|={abs(diff)*100:.1f}pp OK"
        if passed
        else f"Slope nefavorabil: {diff*100:.1f}pp",
    )


def gate_iv_regime(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    iv_rank = ctx.market.ivRank
    passed = cfg.ivRankMin <= iv_rank <= cfg.ivRankMax
    return GateResult(
        gateName="iv.regime",
        passed=passed,
        severity=Severity.WARN,
        reason=f"IV rank: {iv_rank}"
        if passed
        else f"IV rank {iv_rank} outside [{cfg.ivRankMin}-{cfg.ivRankMax}]",
    )


def gate_portfolio_risk(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    delta = abs(ctx.portfolio.delta)
    passed = delta <= cfg.maxDelta
    return GateResult(
        gateName="portfolio.risk",
        passed=passed,
        severity=Severity.WARN,
        reason=f"Delta: {delta:.2f}" if passed else f"High delta: {delta:.2f}",
    )


def gate_max_positions(ctx: TradeContext, cfg: GateConfig) -> GateResult:
    current = ctx.openPositionsBySymbol.get(ctx.underlying, 0)
    passed = current < cfg.maxPositionsPerSymbol
    return GateResult(
        gateName="risk.maxpositions",
        passed=passed,
        severity=Severity.BLOCK,
        reason=f"Positions: {current}" if passed else f"Too many positions: {current}",
    )


# Stub gates pentru v0.1
STUB_GATES = [
    lambda ctx, cfg: GateResult(
        gateName="time.session",
        passed=True,
        severity=Severity.WARN,
        reason="Market open",
    ),
    lambda ctx, cfg: GateResult(
        gateName="events.earnings",
        passed=True,
        severity=Severity.WARN,
        reason="No earnings",
    ),
    lambda ctx, cfg: GateResult(
        gateName="em.atr", passed=True, severity=Severity.WARN, reason="EM/ATR OK"
    ),
    lambda ctx, cfg: GateResult(
        gateName="greeks.portfolio",
        passed=True,
        severity=Severity.WARN,
        reason="Greeks OK",
    ),
    lambda ctx, cfg: GateResult(
        gateName="risk.pertrade",
        passed=True,
        severity=Severity.WARN,
        reason="Per-trade OK",
    ),
    lambda ctx, cfg: GateResult(
        gateName="term.structure", passed=True, severity=Severity.WARN, reason="Term OK"
    ),
]

ALL_GATES = [
    gate_tradeability,
    gate_data_freshness,
    gate_buying_power,
    gate_liquidity,
    gate_pricing_sanity,
    gate_iv_regime,
    gate_portfolio_risk,
    gate_max_positions,
] + STUB_GATES

SUBSET_PLACE = [gate_data_freshness, gate_pricing_sanity, gate_buying_power]


def evaluate_gates(ctx: TradeContext, cfg: GateConfig = DEFAULT_CONFIG) -> GateDecision:
    results = [gate(ctx, cfg) for gate in ALL_GATES]
    blocking_fails = [
        r for r in results if r.severity == Severity.BLOCK and not r.passed
    ]
    warning_fails = [r for r in results if r.severity == Severity.WARN and not r.passed]

    if blocking_fails:
        decision = "REJECT"
    elif warning_fails:
        decision = "ALLOW_WITH_WARNINGS"
    else:
        decision = "ALLOW"

    return GateDecision(decision=decision, results=results)


def audit_hash(payload: Dict[str, Any]) -> str:
    """Generate stable audit hash"""
    json_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]
