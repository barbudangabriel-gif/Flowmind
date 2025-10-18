# backend/services/quality.py

def clamp(x, a=0, b=1):
    return max(a, min(b, x))


def norm_spread(bid, ask):
    if not bid or not ask:
    return 1.0
    mid = (bid + ask) / 2
    if mid <= 0:
    return 1.0
    return (ask - bid) / mid  # 0.05 = 5%


def liquidity_score(oi_pct, vol_oi, spread_pct):
    s_spread = clamp(1 - (spread_pct / 0.20))  # 20% spread = 0 score
    s_oi = clamp(oi_pct)  # 0..1 percentile OI
    s_vo = clamp(vol_oi / 1.5)  # 1.5x is full score
    return 0.6 * s_oi + 0.25 * s_vo + 0.15 * s_spread


def pricing_score(theo, mid, is_credit, iv_rank_z):
    if mid <= 0 or theo <= 0:
    edge = 0
    else:
    edge = (mid - theo) / mid if is_credit else (theo - mid) / theo
    s_edge = clamp(0.5 + edge * 3)  # ~±17% edge → ±0.5 shift
    s_iv = clamp(
        0.5 + (-iv_rank_z) * 0.25
    )  # credit wants high IV, debit wants lower IV
    return clamp(0.6 * s_edge + 0.4 * s_iv)


def structure_score(
        target_delta,
        net_delta,
        dte,
        dte_lo=20,
        dte_hi=60,
        be_pct=None):
    d_delta = clamp(1 - abs((net_delta - target_delta)) / 0.25)
    d_dte = clamp(
        1 - abs(((dte - (dte_lo + dte_hi) / 2) / ((dte_hi - dte_lo) / 2))))
    # breakeven dist % vs expected move
    d_be = clamp(1 - abs(be_pct or 0) / 0.25)
    return clamp(0.5 * d_delta + 0.3 * d_dte + 0.2 * d_be)


def risk_score(max_loss, max_gain, assignment_risk):
    rr = clamp(max_gain / (max_loss + 1e-9) / 3.0)  # 3:1 → full
    asg = clamp(1 - assignment_risk)  # 0..1 (lower risk → higher score)
    return clamp(0.7 * rr + 0.3 * asg)


def stability_score(gamma, vega, iv_swing=0.1, notional=1_000):
    # penalize excessive sensitivity
    g = clamp(1 - abs(gamma) * 50)  # heuristic
    v = clamp(1 - abs(vega) * iv_swing / notional)  # relative to notional
    return clamp(0.5 * g + 0.5 * v)


TARGET_DELTA = {
    "long-call": 0.40,
    "short-put": 0.25,
    "bull-call-spread": 0.25,
    "cash-secured-put": 0.20,
    "bear-put-spread": -0.25,
    "bear-call-spread": -0.25,
    "iron-condor": 0.0,
    "iron-butterfly": 0.0,
    "long-straddle": 0.0,
    "long-strangle": 0.0,
    "covered-call": 0.15,
    "protective-put": -0.15,
}


def compute_quality(payload, chain_snapshot, context):
                """
                Compute spread quality score
                payload: legs [], dte, strategyId, be_pct etc.
                chain_snapshot: {strike: {bid, ask, oi, vol, iv, oi_pct}} for used strikes
                context: {theo, mid, is_credit, iv_rank_z, gamma, vega, delta, max_loss, max_gain, assignment_risk}
    """
    # Liquidity (per leg average)
    spreads, oi_pcts, vol_ois = [], [], []
    for leg in payload.get("legs", []):
    strike_key = str(leg.get("strike", 0))
    row = chain_snapshot.get(strike_key)
    if not row:
    continue

    bid = row.get("bid", 0)
    ask = row.get("ask", 0)
    s = norm_spread(bid, ask)
    spreads.append(s)

    oi_pct = row.get("oi_pct", 0)
    oi_pcts.append(clamp(oi_pct))

    volume = row.get("volume", 0)
    oi = row.get("oi", 1)
    vol_ois.append(volume / oi if oi > 0 else 0)

    # Calculate component scores
    L = liquidity_score(
        oi_pct=sum(oi_pcts) / max(len(oi_pcts), 1),
        vol_oi=sum(vol_ois) / max(len(vol_ois), 1),
        spread_pct=sum(spreads) / max(len(spreads), 1),
    )

    P = pricing_score(
        context.get("theo", 0),
        context.get("mid", 0),
        context.get("is_credit", False),
        context.get("iv_rank_z", 0),
    )

    strategy_id = payload.get("strategyId", "")
    S = structure_score(
        TARGET_DELTA.get(strategy_id, 0.0),
        context.get("delta", 0),
        payload.get("dte", 30),
        be_pct=payload.get("be_pct"),
    )

    R = risk_score(
        context.get("max_loss", 1000),
        context.get("max_gain", 300),
        context.get("assignment_risk", 0.15),
    )

    T = stability_score(context.get("gamma", 0), context.get("vega", 0))

    # Weighted final score
    score = round(100 * (0.30 * L + 0.20 * P + 0.20 * S + 0.20 * R + 0.10 * T))

    # Quality flags
    flags = []
    avg_spread = sum(spreads) / max(len(spreads), 1)
    if avg_spread > 0.10:
    flags.append("Wide spread >10%")
    if payload.get("dte", 30) < 7:
    flags.append("DTE under 7")
    if context.get("earnings_soon"):
    flags.append("Earnings <7d")

    return {
        "score": max(0, min(100, score)),  # Clamp to 0-100
        "buckets": {
            "liquidity": round(L, 2),
            "pricing": round(P, 2),
            "structure": round(S, 2),
            "risk": round(R, 2),
            "stability": round(T, 2),
        },
        "flags": flags,
    }
