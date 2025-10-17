// frontend/src/lib/builderApi.js
const API = import.meta.env?.VITE_API || '';

async function json(url, opts = {}) {
  const r = await fetch(API + url, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!r.ok) {
    const txt = await r.text().catch(() => '');
    throw new Error(txt || r.statusText || 'Request failed');
  }
  return r.json();
}

// Pricing pentru configurația curentă (symbol, expiry, legs, etc)
export function priceStrategy(payload) {
  return json('/api/builder/price', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// Date istorice pentru snapshot/backtest (opțional, în Sprint 2)
export function getHistorical(payload) {
  return json('/api/builder/historical', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
