import math
import os
from typing import Any, Dict, Tuple
from services.bs import (
    call_price,
    put_price,
    call_delta,
    put_delta,
    bs_gamma,
    bs_vega,
    call_theta,
    put_theta,
)
from services.providers import get_provider

LEG_MULT = 100.0  # opțiuni US

# ---- helpers payoff la expirare ----


def leg_payoff_expiry(
    kind: str, strike: float, qty: int, side: str, S_T: float
) -> float:
    kind = kind.upper()
    side = side.upper()
    # BUY = long position (positive payoff when ITM)
    sign = 1 if side == "BUY" else -1
    if kind.startswith("C"):
    intrinsic = max(0.0, S_T - strike)
    else:
    intrinsic = max(0.0, strike - S_T)
    return sign * intrinsic * qty * LEG_MULT

# ---- pricing inițial (t=0) pentru debit/credit ----


def leg_price_now(
    kind: str,
    strike: float,
    qty: int,
    side: str,
    S: float,
    T: float,
    iv: float,
    r: float,
) -> float:
    kind = kind.upper()
    side = side.upper()
    px = (
        call_price(S, strike, T, iv, r)
        if kind.startswith("C")
        else put_price(S, strike, T, iv, r)
    )
    sign = 1 if side == "BUY" else -1
    return sign * px * qty * LEG_MULT  # >0 = debit, <0 = credit

# ---- PoP/lognormal pdf ----


def logn_params(S: float, iv: float, T: float) -> Tuple[float, float]:
    # S_T = lognormal(mu, sigma); mu = ln(S) - 0.5σ²T; sigma = σ√T
    return math.log(S) - 0.5 * (iv**2) * T, iv * math.sqrt(T)


def logn_pdf(x: float, mu: float, sig: float) -> float:
    if x <= 0:
    return 0.0
    return (1.0 / (x * sig * math.sqrt(2 * math.pi))) * math.exp(
        -0.5 * ((math.log(x) - mu) / sig) ** 2
    )

# ---- engine principal ----


def price_structure(payload: Dict[str, Any], provider=None) -> Dict[str, Any]:
    symbol = payload.get("symbol")
    expiry = payload.get("expiry")
    legs = payload.get("legs") or []
    qty_all = int(payload.get("qty") or 1)
    range_pct = float(payload.get("range_pct") or 0.12)
    iv_mult = float(payload.get("iv_mult") or 1.0)
    spot_override = payload.get("spot_override")

    provider = provider or get_provider()
    S = float(spot_override if spot_override else provider.get_spot(symbol))
    # dacă payload nu dă dte, aproximăm la 30
    dte = int(payload.get("dte") or 30)
    T = max(dte, 1) / 365.0
    iv_atm = float(payload.get("iv_atm") or 0.0) or 0.40
    if iv_atm == 0.40:
    try:
    ch = provider.get_chain(symbol)
    # ia IV ATM (cea mai apropiată de S)
    best = None
    bd = 1e9
    for oc in ch.get("OptionChains", []):
    for row in oc.get("Strikes", []):
    k = float(row["StrikePrice"])
    d = abs(k - S)
    if d < bd:
    ivc = row["Calls"][0].get("IV") if row["Calls"] else None
    ivp = row["Puts"][0].get("IV") if row["Puts"] else None
    best = float(ivc or ivp or 0) or best
    bd = d
    if best:
    iv_atm = best
    except Exception:
    pass

    iv_eff = max(0.05, min(2.0, iv_atm * iv_mult))
    r = float(os.getenv("RF_RATE", "0.045"))

    # debit/credit inițial
    net0 = 0.0
    for L in legs:
    net0 += leg_price_now(
        L["type"],
        float(L["strike"]),
        int(L.get("qty", 1)) * qty_all,
        L["side"],
        S,
        T,
        iv_eff,
        r,
    )
    net_debit = max(0.0, net0)
    net_credit = max(0.0, -net0)

    # grid pentru P/L la expirare și PoP
    x_min = S * (1.0 - range_pct)
    x_max = S * (1.0 + range_pct)
    N = 241
    xs = [x_min + (x_max - x_min) * i / (N - 1) for i in range(N)]

    pl = []
    for X in xs:
    payoff = 0.0
    for L in legs:
    payoff += leg_payoff_expiry(
        L["type"],
        float(L["strike"]),
        int(L.get("qty", 1)) * qty_all,
        L["side"],
        X,
    )
    # adaugă costul inițial (debit negativ / credit pozitiv)
    payoff -= net_debit
    payoff += net_credit
    pl.append(payoff)

    # breakeven(s): locuri unde se schimbă semnul
    bes = []
    for i in range(1, len(xs)):
    if pl[i - 1] == 0:
    bes.append(xs[i - 1])
    continue
    if (pl[i - 1] < 0 and pl[i] > 0) or (pl[i - 1] > 0 and pl[i] < 0):
        # interpolare liniară
    x0, y0 = xs[i - 1], pl[i - 1]
    x1, y1 = xs[i], pl[i]
    if y1 != y0:
    t = -y0 / (y1 - y0)
    bes.append(x0 + t * (x1 - x0))

    # max/min P/L aproximativ pe fereastră
    max_profit = max(pl)
    max_loss = -min(pl)

    # Chance of Profit ≈ ∫ I(pl>0)*pdf(x) dx
    mu, sig = logn_params(S, iv_eff, T)
    prob = 0.0
    for i in range(1, len(xs)):
    mid = 0.5 * (xs[i - 1] + xs[i])
    w = xs[i] - xs[i - 1]
    if 0.5 * (pl[i - 1] + pl[i]) > 0:
    prob += logn_pdf(mid, mu, sig) * w
    # pdf lognormal integrată pe [0,∞) = 1; discretizarea pe [x_min,x_max] e
    # ok pentru range 10–30%

    # serie probabilitate pentru overlay (CDF approx)
    cdf = []
    acc = 0.0
    for i in range(1, len(xs)):
    mid = 0.5 * (xs[i - 1] + xs[i])
    w = xs[i] - xs[i - 1]
    acc += logn_pdf(mid, mu, sig) * w
    cdf.append({"x": xs[i], "y": min(1.0, acc)})

    # greeks (aggregate) – per 1 contract, scalate la qty și 100 multiplier
    # unde e cazul
    delta = gamma = vega = theta = 0.0
    for L in legs:
    K = float(L["strike"])
    q = int(L.get("qty", 1)) * qty_all
    sign = 1 if L["side"].upper() == "BUY" else -1
    if L["type"].upper().startswith("C"):
    d = call_delta(S, K, T, iv_eff, r)
    th = call_theta(S, K, T, iv_eff, r)
    else:
    d = put_delta(S, K, T, iv_eff, r)
    th = put_theta(S, K, T, iv_eff, r)
    g = bs_gamma(S, K, T, iv_eff, r)
    v = bs_vega(S, K, T, iv_eff, r)

    # delta e pe unitate subiect; vega e pe 1.0 (nu %); theta e per an →
    # zilnic ca /365
    delta += sign * d * q / 100.0
    gamma += sign * g * q / 100.0
    vega += sign * v * q / 100.0
    theta += sign * (th / 365.0) * q / 100.0

    result = {
        "meta": {
            "symbol": symbol,
            "spot": S,
            "expiry": expiry,
            "dte": dte,
            "iv_atm": iv_atm,
            "iv_eff": iv_eff,
            "rf": r,
        },
        "pricing": {
            "net_debit": round(net_debit, 2),
            "net_credit": round(net_credit, 2),
            "max_loss": round(max_loss, 2),
            "max_profit": None if max_profit > 1e8 else round(max_profit, 2),
            "chance_profit": round(prob, 4),
            "breakevens": [round(b, 2) for b in bes],
        },
        "chart": {
            "x_min": round(x_min, 2),
            "x_max": round(x_max, 2),
            "series": [
                {
                    "label": "Expiration",
                    "xy": [[round(x, 2), round(y, 2)] for x, y in zip(xs, pl)],
                }
            ],
            "prob": cdf,
        },
        "greeks": {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 4),
            "vega": round(vega, 4),
        },
    }

    # Add quality scoring
    try:
    from services.quality import compute_quality

    # Get strategy ID from payload
    strategy_id = payload.get("strategyId", "unknown")

    # Create chain snapshot for quality calculation
    chain_snapshot = {}
    for leg in legs:
    strike = leg.get("strike", 0)
    strike_key = str(strike)

    # Mock chain data for quality calc (in real implementation, get from
    # provider)
    chain_snapshot[strike_key] = {
        "bid": leg.get("bid", strike * 0.02),  # mock bid
        "ask": leg.get("ask", strike * 0.025),  # mock ask
        "oi": leg.get("oi", 1000),
        "volume": leg.get("volume", 100),
        "iv": iv_eff,
        "oi_pct": 0.1,  # mock OI percentage
    }

    # Quality context
    quality_context = {
        "theo": abs(net_debit) if net_debit != 0 else abs(net_credit),
        "mid": abs(net_debit) if net_debit != 0 else abs(net_credit),
        "is_credit": net_credit > 0,
        "iv_rank_z": 0.0,  # mock IV rank
        "delta": delta,
        "gamma": gamma,
        "vega": vega,
        "max_loss": max_loss,
        "max_gain": max_profit if max_profit and max_profit < 1e8 else 0,
        "assignment_risk": 0.15,
        "earnings_soon": False,
    }

    quality_payload = {
        "legs": legs,
        "dte": dte,
        "strategyId": strategy_id,
        "be_pct": 0.05,  # mock breakeven percentage
    }

    quality_result = compute_quality(
        quality_payload, chain_snapshot, quality_context
    )
    result["quality"] = quality_result

    except Exception:
        # Fallback quality score if calculation fails
    result["quality"] = {
        "score": 50,
        "buckets": {
            "liquidity": 0.5,
            "pricing": 0.5,
            "structure": 0.5,
            "risk": 0.5,
            "stability": 0.5,
        },
        "flags": ["Quality calculation unavailable"],
    }

    return result
