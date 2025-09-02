import { useEffect, useMemo, useState } from 'react';

export function useChain({ symbol, expiry, dev }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState(null);
  const [demo, setDemo] = useState(false);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true); setErr(null); setDemo(false);
        const API = process.env.REACT_APP_BACKEND_URL || "";
        const url = `${API}/api/options/chain?symbol=${encodeURIComponent(symbol)}&expiry=${encodeURIComponent(expiry)}${dev ? '&dev=1' : ''}`;
        const r = await fetch(url);
        if (!r.ok) throw new Error(`Chain ${r.status}`);
        const j = await r.json();
        if (!alive) return;
        
        if (Array.isArray(j) && j.length >= 6) {
          setData(j);
          // Check if this is demo data by looking for consistent patterns
          const isDemoData = j.length === 13 && j.every((row, i) => 
            i === 0 || Math.abs(row.strike - j[i-1].strike) === 5
          );
          setDemo(isDemoData && !dev); // Only set demo flag if not explicitly requested
        } else {
          // auto-retry cu mock
          const r2 = await fetch(`${API}/api/options/chain?symbol=${encodeURIComponent(symbol)}&expiry=${encodeURIComponent(expiry)}&dev=1`);
          const j2 = r2.ok ? await r2.json() : [];
          setData(Array.isArray(j2) ? j2 : []);
          setDemo(true);
        }
      } catch (e) {
        if (!alive) return;
        setErr(e.message || 'Chain error');
        // Try demo data as final fallback
        try {
          const API = process.env.REACT_APP_BACKEND_URL || "";
          const r3 = await fetch(`${API}/api/options/chain?symbol=${encodeURIComponent(symbol)}&expiry=${encodeURIComponent(expiry)}&dev=1`);
          const j3 = r3.ok ? await r3.json() : [];
          setData(Array.isArray(j3) ? j3 : []);
          setDemo(true);
          setErr(null); // Clear error if demo works
        } catch {
          setData([]);
        }
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, [symbol, expiry, dev]);

  const byStrike = useMemo(() => new Map(data.map(r => [r.strike, r])), [data]);
  return { data, byStrike, loading, err, demo };
}