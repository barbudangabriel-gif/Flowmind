import { useEffect, useRef, useState } from "react";
import { withRetry } from "../utils/withRetry";

function timeout(promise, ms = 3500) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("quality-timeout")), ms);
    promise.then(
      value => { clearTimeout(timer); resolve(value); },
      error => { clearTimeout(timer); reject(error); }
    );
  });
}

async function fetchQuality({ legs, spot, ivMult, rangePct, dte, symbol }) {
  const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";
  const payload = { 
    symbol: symbol || 'TSLA',
    expiry: new Date(Date.now() + dte * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    dte,
    legs, 
    spot, 
    iv_mult: ivMult, 
    range_pct: rangePct, 
    qty: 1,
    mode: 'pl_usd',
    strategyId: 'custom'
  };
  
  const res = await fetch(`${API}/api/builder/price`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  if (!res.ok) throw new Error(`quality ${res.status}`);
  const data = await res.json();
  return data?.quality?.score ?? 50;
}

// Patch D - Live, debounced quality hook
export function useQuality({ legs, spot, ivMult, rangePct, dte, symbol }, opts = {}) {
  const enabled = opts.enabled !== false;
  
  const [score, setScore] = useState(null);
  const [mode, setMode] = useState("idle"); // idle | loading | ok | degraded
  const tRef = useRef(0);

  useEffect(() => {
    if (!enabled || !Array.isArray(legs) || !legs.length) {
      setMode("idle");
      return;
    }
    
    // Clear previous debounce
    window.clearTimeout(tRef.current);
    setMode("loading");

    // Debounce 200ms
    tRef.current = window.setTimeout(async () => {
      try {
        const res = await withRetry(() => 
          fetchQuality({ legs, spot, ivMult, rangePct, dte, symbol }),
          { retries: 1, backoffMs: 300 }
        );
        setScore(Math.round(res));
        setMode("ok");
      } catch (error) {
        console.warn('Quality fetch failed:', error);
        // Fallback heuristic calculation
        const spreadPenalty = Math.max(0, 1 - (Math.abs(ivMult - 1) * 0.35 + rangePct * 0.4));
        const legsPenalty = Math.max(0, 1 - (legs.length - 1) * 0.08);
        setScore(Math.round(60 * spreadPenalty * legsPenalty));
        setMode("degraded");
      }
    }, 200);

    return () => window.clearTimeout(tRef.current);
  }, [enabled, JSON.stringify(legs), spot, ivMult, rangePct, dte, symbol]);

  return { score, mode };
}