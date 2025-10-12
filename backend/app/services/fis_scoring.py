from typing import Dict
from .fis_adapters import get_tech_snapshot, get_vol_surface, get_flow_uw

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def score_tech(snap: Dict) -> int:
    rsi = snap["rsi14"]
    rsi_score = 1.0 - abs((rsi - 60.0) / 40.0)
    rsi_score = clamp01(rsi_score)
    trend_bonus = 0.15 if snap["ma20_gt_ma50"] else -0.05
    p = snap["pct_52w"]
    pos_score = 1.0 - abs((p - 0.65) / 0.65)
    pos_score = clamp01(pos_score)
    s = clamp01(0.6*rsi_score + 0.3*pos_score + trend_bonus)
    return round(s * 100)

def score_vol(surf: Dict) -> int:
    ivr = surf["iv_rank"] / 100.0
    ivr_pref = 1.0 - abs((ivr - 0.4) / 0.4)
    ivr_pref = clamp01(ivr_pref)
    skew = surf["skew25d"]
    skew_adj = 1.0 - max(0.0, (0.05 - skew)) * 6.0
    skew_adj = clamp01(skew_adj)
    ivx = surf["ivx30"]
    ivx_pref = 1.0 - max(0.0, (ivx - 0.35)) * 4.0
    ivx_pref = clamp01(ivx_pref)
    s = clamp01(0.5*ivr_pref + 0.3*ivx_pref + 0.2*skew_adj)
    return round(s * 100)

def score_flow(flow: Dict) -> int:
    br = clamp01(flow["buy_ratio"])
    urg = clamp01(flow["urgency"])
    ns = max(-1.0, min(1.0, flow["net_sweeps"] / 1_000_000.0))
    ns_pref = (ns + 1.0) / 2.0
    s = clamp01(0.5*br + 0.3*urg + 0.2*ns_pref)
    return round(s * 100)

def calc_fis(symbol: str) -> Dict:
    tech = score_tech(get_tech_snapshot(symbol))
    vol  = score_vol(get_vol_surface(symbol))
    flow = score_flow(get_flow_uw(symbol))
    score = round(0.4*tech + 0.4*vol + 0.2*flow)
    return {
        "symbol": symbol.upper(),
        "score": score,
        "factors": {
            "tech": tech,
            "vol_surface": vol,
            "flow": flow
        }
    }
