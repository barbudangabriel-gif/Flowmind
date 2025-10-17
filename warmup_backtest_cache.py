#!/usr/bin/env python3
"""
FlowMind - Warmup Backtest Cache
Populează Redis cu backtest data pentru top signals
"""

# --- import shim: find project root for cron ---
from pathlib import Path
import sys
import os

# setează FM_PROJECT_ROOT dacă vrei root explicit; altfel urcă 1-2 directoare din locația scriptului
ROOT = Path(os.getenv("FM_PROJECT_ROOT", Path(__file__).resolve().parents[0]))
if str(ROOT) not in sys.path:
 sys.path.insert(0, str(ROOT))
# -----------------------------------------------

import json
import asyncio

async def warmup_cache():
 """Demo warmup - populate cache with common signals"""
 sys.path.insert(0, "/app/backend") # Add backend to path
 from bt_cache_integration import attach_backtest

 # Demo signals pentru warmup
 signals = [
 {
 "symbol": "TSLA",
 "strategy": "IRON_CONDOR",
 "dte": 21,
 "ivr": 37,
 "width_ratio_em": 1.0,
 },
 {
 "symbol": "AAPL",
 "strategy": "IRON_CONDOR",
 "dte": 14,
 "ivr": 42,
 "width_ratio_em": 0.9,
 },
 {
 "symbol": "NVDA",
 "strategy": "IRON_CONDOR",
 "dte": 28,
 "ivr": 45,
 "width_ratio_em": 1.2,
 },
 {
 "symbol": "MSFT",
 "strategy": "IRON_CONDOR",
 "dte": 35,
 "ivr": 30,
 "width_ratio_em": 0.8,
 },
 {
 "symbol": "SPY",
 "strategy": "IRON_CONDOR",
 "dte": 21,
 "ivr": 25,
 "width_ratio_em": 1.0,
 },
 ]

 hits = misses = errors = 0

 for sig in signals:
 try:
 result = await attach_backtest(sig)
 if result.get("backtest", {}).get("cache") == "HIT":
 hits += 1
 else:
 misses += 1
 except Exception as e:
 print(f"Error processing {sig.get('symbol', 'unknown')}: {e}")
 errors += 1

 return {"hits": hits, "misses": misses, "errors": errors}

if __name__ == "__main__":
 print(f"[warmup] PWD={os.getcwd()} PYTHON={sys.executable}")
 print(f"[warmup] PYTHONPATH={sys.path[:3]}")

 result = asyncio.run(warmup_cache())
 print(f"Warmup complete: {json.dumps(result, indent=2)}")
