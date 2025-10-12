declare global {
  interface ImportMeta {
    env: Record<string, string | undefined>;
  }
}

const API_BASE = import.meta.env.VITE_FIS_API_BASE || "http://localhost:5174";

export type FISScore = { symbol:string; score:number; components?:Record<string,unknown> };
export type IVX = { symbol:string; ivx:string; rank:string; percentile?:string };
export type GEX = { symbol:string; expiry:string; walls:{call:number; put:number}; strikes:number[]; gex:number[] };
export type Flow = { symbol:string; sweeps:number; blocks:number; bias:"bullish"|"bearish"|"neutral" };

function withTimeout(ms:number, signal?:AbortSignal) {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(), ms);
  return {
    signal: signal ? mergeAbortSignals(signal, ctrl.signal) : ctrl.signal,
    cancel: () => clearTimeout(id),
  };
}

// Helper to merge two AbortSignals (minimal, not a full polyfill)
function mergeAbortSignals(a: AbortSignal, b: AbortSignal): AbortSignal {
  if (a.aborted) return a;
  if (b.aborted) return b;
  const ctrl = new AbortController();
  const onAbort = () => ctrl.abort();
  a.addEventListener("abort", onAbort);
  b.addEventListener("abort", onAbort);
  return ctrl.signal;
}

async function getJSON<T>(path:string, {timeout=5000}:{timeout?:number} = {}): Promise<T> {
  const ctrl = new AbortController();
  const { signal } = withTimeout(timeout, ctrl.signal);
  const r = await fetch(`${API_BASE}${path}`, { signal: signal as AbortSignal, headers:{ "Accept": "application/json" }});
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} @ ${path}`);
  return r.json();
}

export const api = {
  score: (symbol:string) => getJSON<FISScore>(`/fis/score?symbol=${encodeURIComponent(symbol)}`),
  ivx:   (symbol:string) => getJSON<IVX>(`/analytics/ivx?symbol=${encodeURIComponent(symbol)}`),
  gex:   (symbol:string) => getJSON<GEX>(`/options/gex?symbol=${encodeURIComponent(symbol)}`),
  flow:  (symbol:string) => getJSON<Flow>(`/flow/bias?symbol=${encodeURIComponent(symbol)}`),
};
