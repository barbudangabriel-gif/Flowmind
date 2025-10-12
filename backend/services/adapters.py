import math, time, random
from typing import Dict, Any, Optional

def get_tech_snapshot(symbol: str, timeout_ms: int = 300) -> Dict[str, Any]:
    """
    Returnează date minime pt. Tech: MA20, MA50, RSI14, pct_vs_52w (0..1).
    MOCK: generează valori plauzibile.
    """
    rsi = 40 + random.random() * 40
    ma20_above_ma50 = random.random() > 0.5
    pct_52w = random.random()  # 0..1 poziția în intervalul 52w
    return {"rsi14": rsi, "ma20_gt_ma50": ma20_above_ma50, "pct_52w": pct_52w}

def get_vol_surface(symbol: str, timeout_ms: int = 300) -> Dict[str, Any]:
    """
    Returnează IVx30D, IV Rank (0..100), Skew25Δ (-..+).
    MOCK: valori plauzibile.
    """
    ivx = 0.25 + random.random() * 0.25  # 25–50%
    iv_rank = random.random() * 100
    skew25d = -0.1 + random.random() * 0.2  # -10%..+10%
    return {"ivx30": ivx, "iv_rank": iv_rank, "skew25d": skew25d}

def get_flow_uw(symbol: str, timeout_ms: int = 300) -> Dict[str, Any]:
    """
    Returnează sumar flow: net_sweeps_$, buy_ratio (0..1), urgency (0..1).
    MOCK: valori plauzibile.
    """
    buy_ratio = random.random()
    urgency = random.random()
    net_sweeps = (-1 + 2*random.random()) * 1_000_000
    return {"buy_ratio": buy_ratio, "urgency": urgency, "net_sweeps": net_sweeps}
