// --- types ---
export type GexSummaryItem = {
  expiry: string;
  net_gex: number;
  walls?: { call?: number; put?: number };
  ts?: string;
  source?: "real" | "cache" | "mock";
};

export type GexSummaryResponse = {
  symbol: string;
  items: GexSummaryItem[];
  meta?: { cacheHits?: number; misses?: number; p95_ms?: number };
};

// helper existent: API_BASE, API_TOKEN, SOURCE_DEFAULT, httpGet, query(...)
import { SOURCE_DEFAULT, httpGet } from "../utils";

// --- NEW: fetch summary ---
// NB: backend folosește `expiries` (CSV). Uneori param-ul pentru dealer e `dealer`,
// alteori `dealer_sign`. Trimitem ambele ca să fim compatibili.
export async function fetchGexSummary(p: {
  symbol: string;
  expiries: string[];          // ["2025-11-21", "2025-12-19"]
  dealer?: string;             // mm_short | mm_long
  normalize?: string;          // none | spot | iv
  source?: "real" | "mock";
}): Promise<GexSummaryResponse> {
  const src = p.source || SOURCE_DEFAULT;
  if (src === "mock") {
    // sintetizează rapid din mock ca fallback
    const mod = await import("../mocks/gex.mock");
    const items = await Promise.all(
      p.expiries.map(async (e) => {
        const d = await mod.getMockGex(p.symbol);
        return { expiry: e, net_gex: d.net_gex ?? 0, walls: d.walls, source: "mock" as const };
      })
    );
    return { symbol: p.symbol, items, meta: { cacheHits: 0, misses: items.length } };
  }
  const params: Record<string, any> = {
    symbol: p.symbol,
    expiries: p.expiries.join(","),
    normalize: p.normalize,
    dealer: p.dealer,
    dealer_sign: p.dealer,     // compat
  };
  try {
    return await httpGet<GexSummaryResponse>("/api/v1/analytics/gex/summary", params);
  } catch (e) {
    console.warn("GEX summary real failed, fallback to mock:", e);
    return fetchGexSummary({ ...p, source: "mock" });
  }
}
