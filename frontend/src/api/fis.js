const API = process.env.REACT_APP_API || "http://localhost:4100";

export async function fetchFIS(symbol) {
  const url = `${API}/investment-scoring/advanced/${encodeURIComponent(symbol)}`;
  const r = await fetch(url, { headers: { "Accept": "application/json" } });
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`FIS ${r.status}: ${text || r.statusText}`);
  }
  return r.json();
}

export async function fetchFISHistory(symbol, days = 30) {
  const r = await fetch(
    `${API}/analytics/fis/history/${encodeURIComponent(symbol)}?days=${days}`
  );
  if (!r.ok) throw new Error(`FIS history ${r.status}`);
  return r.json(); // [{t, score, tech, vol_surface, flow}, ...] asc
}
