const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || "";

const j = async (r) => {
 if (!r.ok) throw new Error(`API Error ${r.status}: ${await r.text()}`);
 return r.json();
};

const toQ = (f) => {
 const q = new URLSearchParams();
 const set = (k, v) => {
 if (v !== undefined && v !== null && v !== '') q.set(k, String(v));
 };
 
 if (f.tickers?.length) set('tickers', f.tickers.join(','));
 ['side', 'kinds', 'opt_types'].forEach(k => {
 const v = f[k];
 if (v?.length) set(k, v.join(','));
 });
 ['otm', 'vol_gt_oi', 'above_ask_below_bid'].forEach(k => {
 if (f[k]) set(k, 'true');
 });
 if (f.price_op) set('price_op', f.price_op), set('price_val', f.price_val);
 if (f.chance_op) set('chance_op', f.chance_op), set('chance_val', f.chance_val);
 if (f.min_dte != null) set('min_dte', f.min_dte);
 if (f.max_dte != null) set('max_dte', f.max_dte);
 if (f.date_from) set('date_from', f.date_from);
 if (f.date_to) set('date_to', f.date_to);
 
 return q.toString();
};

export const flowApi = {
 summary: (params = {}) => {
 const { limit = 24, minPremium = 25000 } = params;
 const q = new URLSearchParams({ limit: String(limit), minPremium: String(minPremium) });
 return fetch(`${API}/api/flow/summary?${q.toString()}`).then(j);
 },
 live: (f = {}) => {
 const symbol = f.symbol || f.tickers?.[0] || "TSLA";
 const params = { ...f, symbol };
 return fetch(`${API}/api/flow/live?${toQ(params)}`).then(j);
 },
 historical: (f = {}) => fetch(`${API}/api/flow/historical?${toQ(f)}`).then(j),
 news: (tickers) => fetch(`${API}/api/flow/news?tickers=${encodeURIComponent((tickers || []).join(','))}`).then(j),
 congress: (tickers) => fetch(`${API}/api/flow/congress?tickers=${encodeURIComponent((tickers || []).join(','))}`).then(j),
 insiders: (tickers) => fetch(`${API}/api/flow/insiders?tickers=${encodeURIComponent((tickers || []).join(','))}`).then(j)
};

export function toBuilderLink(row) {
 // Map BUY/SELL CALL/PUT to simple one-leg strategy in Builder
 const strategyMap = {
 "BUY_CALL": "long_call",
 "BUY_PUT": "long_put", 
 "SELL_CALL": "short_call",
 "SELL_PUT": "short_put"
 };
 
 const strategyKey = `${row.side}_${row.kind}`;
 const strategyId = strategyMap[strategyKey] || "long_call";
 
 const legs = [{
 side: row.side === "BUY" ? "BUY" : "SELL",
 kind: row.kind,
 strike: row.strike,
 qty: Math.max(1, Math.round((row.qty || 100) / 100))
 }];
 
 const params = {
 strategyId,
 symbol: row.symbol,
 expiry: row.expiry,
 legs,
 qty: 1
 };
 
 try {
 const s = btoa(unescape(encodeURIComponent(JSON.stringify(params))));
 return `/build/${strategyId}?s=${s}`;
 } catch (error) {
 console.error("Error encoding builder params:", error);
 return `/build/${strategyId}`;
 }
}