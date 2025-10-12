// fallback mock for GEX summary
export const gexSummaryMock = {
  items: [
    {
      expiry: "2025-11-21",
      net_gex: 1234567,
      walls: { call: 420, put: 69 },
      source: "mock",
      ts: "2025-10-11T20:27:00Z"
    },
    {
      expiry: "2025-12-19",
      net_gex: 7654321,
      walls: { call: 111, put: 222 },
      source: "mock",
      ts: "2025-10-11T20:27:00Z"
    }
  ],
  meta: {
    p95_ms: 12,
    cacheHits: 0,
    misses: 1
  }
};

// Returns a mock GEX item for a given symbol (for summary fallback)
export function getMockGex(symbol: string) {
  // Just alternate between the two mock items for demo
  const idx = symbol.length % 2;
  return gexSummaryMock.items[idx];
}
