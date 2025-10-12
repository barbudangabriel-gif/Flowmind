
import { useEffect, useState, useCallback } from "react";
import { fetchFIS, fetchFISHistory } from "../api/fis";
import { histCache } from "./fisCache";

const TTL_MS = 60 * 1000; // 60s cache
const hasLS = typeof window !== "undefined" && "localStorage" in window;

function getCacheKey(symbol){ return `FIS:${symbol?.toUpperCase()}`; }
function readCache(symbol){ if(!hasLS) return null;
  try {
    const raw = localStorage.getItem(getCacheKey(symbol));
    if(!raw) return null;
    const obj = JSON.parse(raw);
    if(Date.now() - obj.t > TTL_MS) return null;
    return obj.d;
  } catch { return null; }
}
function writeCache(symbol, data){ if(!hasLS) return;
  try { localStorage.setItem(getCacheKey(symbol), JSON.stringify({t: Date.now(), d: data})); } catch {}
}

export function useFIS(symbol) {
  const [data, setData] = useState(() => readCache(symbol));
  const [loading, setLoading] = useState(!readCache(symbol) && Boolean(symbol));
  const [error, setError] = useState(null);

  const [history, setHistory] = useState([]);
  const [histLoading, setHistLoading] = useState(!!symbol);
  const [histError, setHistError] = useState(null);

  const refresh = useCallback(async (force=false) => {
    if(!symbol) return;
    try {
      setError(null); setLoading(true);
      if(!force){ const cache=readCache(symbol); if(cache) setData(cache); }
      const fresh = await fetchFIS(symbol);
      setData(fresh); writeCache(symbol, fresh);
    } catch(e){ setError(e); } finally { setLoading(false); }
  }, [symbol]);


  const refreshHistory = useCallback(async (days=30) => {
    if(!symbol) return;
    try {
      setHistError(null); setHistLoading(true);
      // Check global cache first
      const cacheKey = symbol.toUpperCase();
      const cached = histCache.get(cacheKey);
      if (cached && Date.now() - cached.t < TTL_MS) {
        setHistory(cached.data || []);
        setHistLoading(false);
        return;
      }
      const h = await fetchFISHistory(symbol, days);
      setHistory(h || []);
      histCache.set(cacheKey, { t: Date.now(), data: h || [] });
    } catch(e){ setHistError(e); } finally { setHistLoading(false); }
  }, [symbol]);

  useEffect(() => { if(symbol){ refresh(); refreshHistory(30); } }, [symbol, refresh, refreshHistory]);

  return { data, loading, error, history, histLoading, histError, refresh, refreshHistory };
}
