declare global {
  interface ImportMeta {
    env: Record<string, string | undefined>;
  }
}

const API_BASE = import.meta.env.VITE_FIS_API_BASE || "http://localhost:5174";
export type FISScore = { symbol:string; score:number; components?:Record<string,unknown> };
export type IVX = { symbol:string; ivx:string; rank:string; percentile:string };
export type GEX = { symbol:string; expiry:string; walls:{call:number; put:number}; strikes:number[]; gex:number[] };
export type Flow = { symbol:string; sweeps:number; blocks:number; bias:"bullish"|"bearish" };

export async function getFISScore(symbol:string):Promise<FISScore> {
  const r = await fetch(`${API_BASE}/fis/score?symbol=${symbol}`); if(!r.ok) throw new Error("fis/score");
  return r.json();
}
export async function getIVX(symbol:string):Promise<IVX> {
  const r = await fetch(`${API_BASE}/analytics/ivx?symbol=${symbol}`); if(!r.ok) throw new Error("analytics/ivx");
  return r.json();
}
export async function getGEX(symbol:string):Promise<GEX> {
  const r = await fetch(`${API_BASE}/options/gex?symbol=${symbol}`); if(!r.ok) throw new Error("options/gex");
  return r.json();
}
export async function getFlow(symbol:string):Promise<Flow> {
  const r = await fetch(`${API_BASE}/flow/bias?symbol=${symbol}`); if(!r.ok) throw new Error("flow/bias");
  return r.json();
}
