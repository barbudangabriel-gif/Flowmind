import math
import os
from typing import Dict, Any, List, Optional
from services.providers import get_provider
from services.bs import norm_cdf, call_price, put_price
from utils.deeplink import builder_link

# B8 - Market Analysis Functions for Spread Quality
def _leg_market_snapshot(
    chain: Dict[str, Any], opt_type: str, strike: float
) -> Dict[str, Any]:
    """Get market data for a specific option leg"""
    for ch in chain.get("OptionChains", []):
    for row in ch.get("Strikes", []):
    if abs(float(row["StrikePrice"]) - strike) < 1e-6:
    opt_data = (
        row.get("Calls", [{}])[0]
        if opt_type.upper().startswith("C")
        else row.get("Puts", [{}])[0]
    )
    bid = float(opt_data.get("Bid", 0))
    ask = float(opt_data.get("Ask", 0))
    mid = (
        (bid + ask) / 2
        if bid > 0 and ask > 0
        else float(opt_data.get("Last", 0))
    )
    oi = float(opt_data.get("OpenInterest", 0))
    vol = float(opt_data.get("Volume", 0))
    spr = max(0, ask - bid)
    rel = spr / max(0.05, mid) if mid > 0 else 1.0
    return {
        "bid": bid,
        "ask": ask,
        "mid": mid,
        "oi": oi,
        "vol": vol,
        "spr": spr,
        "rel": rel,
    }
    return {"bid": 0, "ask": 0, "mid": 0, "oi": 0, "vol": 0, "spr": 0, "rel": 1.0}

def _spread_score(rel: float) -> float:
    """Calculate spread quality score (0-1) based on relative spread"""
    if rel <= 0:
    return 1.0
    if rel >= 0.2:
    return 0.0
    if rel <= 0.05:
    return 1.0 - 0.25 * (rel / 0.05)
    if rel <= 0.10:
    return 0.75 - 0.25 * ((rel - 0.05) / 0.05)
    return 0.5 - 0.5 * ((rel - 0.10) / 0.10)

def _compute_spread_quality(
    legs: List[Dict[str, Any]], chain: Dict[str, Any]
) -> Dict[str, Any]:
    """Compute spread quality metrics for a strategy"""
    w_sum = 0
    q_sum = 0
    slippage = 0
    nbbo_ok = True
    market_data = []

    for leg in legs:
    mm = _leg_market_snapshot(chain, leg["type"], float(leg["strike"]))
    q = 0.65 * _spread_score(mm["rel"]) + 0.35 * math.tanh(
        (mm["oi"] + mm["vol"]) / 1500
    )
    w = max(1, abs(mm["mid"]))

    w_sum += w
    q_sum += q * w
    slippage += 0.5 * mm["spr"] * 100 # Half spread in dollars
    market_data.append(mm)

    # Check NBBO criteria
    if not (mm["rel"] <= 0.12 or mm["spr"] <= 0.10):
    nbbo_ok = False

    quality = (q_sum / w_sum) if w_sum > 0 else 0

    return {
        "quality": round(quality * 100),
        "slippage_est": round(slippage * 100) / 100,
        "nbbo_ok": nbbo_ok,
        "market": market_data,
    }

def _pick_iv(chain: Dict[str, Any], spot: float) -> float:
    best = None
    best_d = 1e9
    for ch in chain.get("OptionChains", []):
    for row in ch.get("Strikes", []):
    k = float(row["StrikePrice"])
    d = abs(k - spot)
    if d < best_d:
    ivc = row["Calls"][0].get("IV") if row["Calls"] else None
    ivp = row["Puts"][0].get("IV") if row["Puts"] else None
    iv = float(ivc) if ivc else float(ivp) if ivp else None
    if iv:
    best, best_d = iv, d
    return float(best) if best else 0.40

def _prob_above(spot: float, strike: float, iv: float, dte: int) -> float:
    T = max(dte, 1) / 365.0
    if T <= 0 or iv <= 0:
    return 0.5
    mu = math.log(spot) - 0.5 * (iv**2) * T
    sig = iv * math.sqrt(T)
    z = (math.log(strike) - mu) / sig
    return 1.0 - norm_cdf(z)

def _liq_score(chain: Dict[str, Any], *strikes: float, kind: str = "CALL") -> float:
    """scor simplu 0..1 din OI total pe strikes implicate"""
    kind_key = "Calls" if kind.upper().startswith("C") else "Puts"
    want = {round(float(k), 2) for k in strikes}
    tot = 0
    acc = 0
    for ch in chain.get("OptionChains", []):
    for row in ch.get("Strikes", []):
    k = round(float(row["StrikePrice"]), 2)
    if k in want:
    arr = row.get(kind_key) or []
    oi = 0
    if arr:
    oi = int(arr[0].get("OpenInterest") or 0)
    acc += min(oi, 5000) # plafon pentru scor
    # total pentru normalizare
    for arr in (row.get("Calls") or []) + (row.get("Puts") or []):
    tot += min(int(arr.get("OpenInterest") or 0), 5000)
    if tot <= 0:
    return 0.3 # fallback slab
    return max(0.05, min(1.0, acc / (0.02 * tot))) # dacă strikes sunt populare -> ~1

def _format_card(
    id_: str,
    label: str,
    legs,
    roi,
    chance,
    profit_max,
    risk_capital,
    collateral,
    breakevens,
    mini,
    deeplink,
) -> Dict[str, Any]:
    return {
        "id": id_,
        "label": label,
        "roi": roi,
        "chance": chance,
        "profit_max": profit_max,
        "risk_capital": risk_capital,
        "collateral": collateral,
        "breakevens": breakevens,
        "legs": legs,
        "mini": mini,
        "open_in_builder": deeplink,
    }

def suggest(
    symbol: str,
    sentiment: str = "bullish",
    target_price: Optional[float] = None,
    budget: Optional[float] = None,
    dte: int = 30,
    risk_bias: int = 0,
) -> Dict[str, Any]:
    provider = get_provider()
    spot = float(provider.get_spot(symbol))
    chain = provider.get_chain(symbol) # adaptorul ia o expirare apropiată
    expiry = chain["OptionChains"][0]["Expiration"]
    iv = _pick_iv(chain, spot)
    T = max(dte, 1) / 365.0
    rf = float(os.getenv("RF_RATE", "0.045"))

    items: List[Dict[str, Any]] = []
    rb = max(-2, min(2, int(risk_bias)))

    # Heuristici strikes
    bias_up = 0.03 + 0.02 * rb # long call
    bias_dn = 0.08 - 0.02 * rb # CSP
    width_pct = 0.10 - 0.02 * rb # spread width

    # === 1) Long Call
    k1 = round(spot * (1 + bias_up) / 5) * 5
    price_call = call_price(spot, k1, T, iv, rf)
    debit = max(0.01, price_call * 100.0)
    be = k1 + debit / 100.0
    chance = _prob_above(spot, be, iv, dte)
    # EV aproximativ (două nivele): câștig mediu la target vs pierdere medie
    tgt = target_price or (spot * (1 + 0.07))
    win = max(0.0, (tgt - k1) * 100.0) - debit
    loss = debit
    ev = chance * max(win, 0.0) - (1 - chance) * loss
    roi_ev = ev / debit
    liq = _liq_score(chain, k1, kind="CALL")
    link = builder_link(
        "long-call",
        symbol,
        expiry,
        [{"side": "BUY", "type": "CALL", "qty": 1, "strike": k1}],
        1,
    )
    if budget is None or debit <= budget:
    items.append(
        _format_card(
            "long-call",
            f"Buy {int(k1)}C",
            [{"side": "BUY", "type": "CALL", "qty": 1, "strike": k1}],
            roi_ev,
            chance,
            None,
            debit,
            0.0,
            [be],
            {"x": [spot * 0.8, spot * 1.2], "breakevens": [be]},
            link,
        )
    )
    items[-1]["_score"] = 0.35 * roi_ev + 0.45 * chance + 0.20 * liq

    # B8 - Add spread quality metrics for Long Call
    legs_lc = [{"side": "BUY", "type": "CALL", "strike": k1}]
    quality_lc = _compute_spread_quality(legs_lc, chain)
    items[-1].update(quality_lc)

    # === 2) Bull Call Spread
    buy = round(spot / 5) * 5
    sell = round((spot * (1 + width_pct)) / 5) * 5
    c_buy = call_price(spot, buy, T, iv, rf)
    c_sell = call_price(spot, sell, T, iv, rf)
    debit2 = max(0.01, (c_buy - c_sell) * 100.0)
    width = max(0.01, (sell - buy) * 100.0)
    max_profit = max(0.0, width - debit2)
    be2 = buy + debit2 / 100.0
    chance2 = _prob_above(spot, be2, iv, dte)
    ev2 = chance2 * max_profit - (1 - chance2) * debit2
    roi2 = ev2 / debit2
    liq2 = min(
        1.0,
        0.5 * _liq_score(chain, buy, kind="CALL")
        + 0.5 * _liq_score(chain, sell, kind="CALL"),
    )
    link2 = builder_link(
        "bull-call-spread",
        symbol,
        expiry,
        [
            {"side": "BUY", "type": "CALL", "qty": 1, "strike": buy},
            {"side": "SELL", "type": "CALL", "qty": 1, "strike": sell},
        ],
        1,
    )
    if (budget is None or debit2 <= budget) and width > 0:
    items.append(
        _format_card(
            "bull-call-spread",
            f"Buy {int(buy)}C, Sell {int(sell)}C",
            [
                {"side": "BUY", "type": "CALL", "qty": 1, "strike": buy},
                {"side": "SELL", "type": "CALL", "qty": 1, "strike": sell},
            ],
            roi2,
            chance2,
            max_profit,
            debit2,
            0.0,
            [be2],
            {"x": [spot * 0.8, spot * 1.2], "breakevens": [be2]},
            link2,
        )
    )
    items[-1]["_score"] = 0.4 * roi2 + 0.4 * chance2 + 0.2 * liq2

    # B8 - Add spread quality metrics for Bull Call Spread
    legs_bcs = [
        {"side": "BUY", "type": "CALL", "strike": buy},
        {"side": "SELL", "type": "CALL", "strike": sell},
    ]
    quality_bcs = _compute_spread_quality(legs_bcs, chain)
    items[-1].update(quality_bcs)

    # === 3) Cash-Secured Put
    put_k = round(spot * (1 - bias_dn) / 5) * 5
    p_price = put_price(spot, put_k, T, iv, rf)
    credit = max(0.0, p_price * 100.0)
    collateral = max(0.0, put_k * 100.0 - credit)
    be3 = put_k - credit / 100.0
    # probabilitatea ca S_T >= K (assignment evitat) ~ profit = credit
    chance3 = _prob_above(spot, put_k, iv, dte)
    ev3 = chance3 * credit - (1 - chance3) * (collateral) # foarte conservator
    # ROI pe risc: credit/collateral; ROI_EV: EV/collateral
    roi3 = ev3 / (collateral if collateral > 0 else 1)
    liq3 = _liq_score(chain, put_k, kind="PUT")
    link3 = builder_link(
        "cash-secured-put",
        symbol,
        expiry,
        [{"side": "SELL", "type": "PUT", "qty": 1, "strike": put_k}],
        1,
    )
    if budget is None or collateral <= budget:
    items.append(
        _format_card(
            "cash-secured-put",
            f"Sell {int(put_k)}P",
            [{"side": "SELL", "type": "PUT", "qty": 1, "strike": put_k}],
            roi3,
            chance3,
            credit,
            collateral,
            collateral,
            [be3],
            {"x": [spot * 0.8, spot * 1.2], "breakevens": [be3]},
            link3,
        )
    )
    items[-1]["_score"] = 0.35 * roi3 + 0.4 * chance3 + 0.25 * liq3

    # B8 - Add spread quality metrics for Cash-Secured Put
    legs_csp = [{"side": "SELL", "type": "PUT", "strike": put_k}]
    quality_csp = _compute_spread_quality(legs_csp, chain)
    items[-1].update(quality_csp)

    # ordonare + curățare
    items.sort(key=lambda z: z.get("_score", 0), reverse=True)
    for x in items:
    x.pop("_score", None)

    return {
        "meta": {
            "symbol": symbol,
            "spot": spot,
            "dte": dte,
            "expiry": expiry,
            "iv": iv,
            "rf": os.getenv("RF_RATE", "0.045"),
        },
        "strategies": items[:9],
    }
