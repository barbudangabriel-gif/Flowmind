import math, time
import requests
from typing import Dict, Any
from backend.app.config import TS_KEY, UW_KEY, TIMEOUT_MS

S = requests.Session()

def _get(url, headers=None, params=None, timeout_ms=TIMEOUT_MS):
    r = S.get(url, headers=headers or {}, params=params or {}, timeout=timeout_ms/1000)
    r.raise_for_status()
    return r.json()

def get_tech_snapshot(symbol: str) -> Dict[str, Any]:
    try:
        ohlc = _get(f"https://api.tradestation/ohlc/daily/{symbol}", headers={"Authorization": f"Bearer {TS_KEY}"}, params={"lookback":"365"})
        px = [bar["close"] for bar in ohlc]
        if len(px) < 60: raise ValueError("not enough bars")

        def sma(arr, n): return sum(arr[-n:]) / n
        def rsi14(prices):
            gains, losses = [], []
            for i in range(1, 15):
                ch = prices[-i] - prices[-i-1]
                gains.append(max(ch,0)); losses.append(max(-ch,0))
            ag, al = (sum(gains)/14), (sum(losses)/14)
            rs = ag/(al or 1e-9)
            return 100 - 100/(1+rs)

        rsi = rsi14(px)
        ma20 = sma(px, 20); ma50 = sma(px, 50)
        curr = px[-1]; hi, lo = max(px), min(px)
        pct_52w = 0 if hi==lo else (curr - lo)/(hi - lo)

        return {"rsi14": rsi, "ma20_gt_ma50": ma20 > ma50, "pct_52w": pct_52w}
    except Exception:
        return {"rsi14": 50, "ma20_gt_ma50": False, "pct_52w": 0.5}

def get_vol_surface(symbol: str) -> Dict[str, Any]:
    try:
        chain = _get(f"https://api.tradestation/options/chain/{symbol}", headers={"Authorization": f"Bearer {TS_KEY}"}, params={"scope":"ATM±10","targetDTE":30})
        ivx30 = chain["iv_atm_30d"]
        iv_rank = chain.get("iv_rank", 50)
        skew25d = chain.get("skew25d", 0.0)
        return {"ivx30": ivx30, "iv_rank": iv_rank, "skew25d": skew25d}
    except Exception:
        return {"ivx30": 0.30, "iv_rank": 50, "skew25d": 0.0}

def get_flow_uw(symbol: str) -> Dict[str, Any]:
    try:
        uw = _get("https://api.unusualwhales/flow", headers={"Authorization": f"Bearer {UW_KEY}"}, params={"symbol":symbol,"lookback":"5d"})
        buys = sum(t["notional"] for t in uw if t["side"]=="B")
        sells = sum(t["notional"] for t in uw if t["side"]=="S")
        total = buys + sells or 1.0
        buy_ratio = buys/total
        urgency = sum(1 for t in uw if t.get("swept")) / max(1,len(uw))
        net = buys - sells
        return {"buy_ratio": buy_ratio, "urgency": urgency, "net_sweeps": net}
    except Exception:
        return {"buy_ratio": 0.5, "urgency": 0.5, "net_sweeps": 0.0}
