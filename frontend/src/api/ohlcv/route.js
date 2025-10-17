// TradeStation OHLCV REST API Route
// Snapshot data fetching for initial chart load

const TS_BASE_URL = process.env.TS_BASE_URL || "https://sim-api.tradestation.com";
const TS_CLIENT_ID = process.env.TS_CLIENT_ID || "";
const TS_CLIENT_SECRET = process.env.TS_CLIENT_SECRET || "";
const TS_REFRESH_TOKEN = process.env.TS_REFRESH_TOKEN || "";

// TradeStation timeframe mapping
function mapTf(tf) {
 const map = {
 "1": { interval: 1, unit: "Minute" },
 "5": { interval: 5, unit: "Minute" },
 "15": { interval: 15, unit: "Minute" },
 "30": { interval: 30, unit: "Minute" },
 "60": { interval: 60, unit: "Minute" },
 "1h": { interval: 60, unit: "Minute" },
 "4h": { interval: 240, unit: "Minute" },
 "D": { interval: 1, unit: "Daily" },
 "W": { interval: 1, unit: "Weekly" }
 };
 return map[tf] || { interval: 1, unit: "Daily" };
}

// Get access token using refresh token
async function getAccessToken() {
 if (!TS_REFRESH_TOKEN) {
 throw new Error("TS_REFRESH_TOKEN not configured");
 }

 const tokenUrl = `${TS_BASE_URL}/oauth/token`;
 const body = new URLSearchParams({
 grant_type: "refresh_token", 
 refresh_token: TS_REFRESH_TOKEN,
 client_id: TS_CLIENT_ID,
 });

 if (TS_CLIENT_SECRET) {
 body.set("client_secret", TS_CLIENT_SECRET);
 }

 const response = await fetch(tokenUrl, {
 method: "POST",
 headers: { "Content-Type": "application/x-www-form-urlencoded" },
 body: body.toString(),
 });

 if (!response.ok) {
 const error = await response.text();
 throw new Error(`Token refresh failed: ${response.status} ${error}`);
 }

 const data = await response.json();
 return data.access_token;
}

export async function GET(request) {
 const { searchParams } = new URL(request.url);
 const symbol = searchParams.get("symbol") || "AAPL";
 const tf = searchParams.get("tf") || "D";
 const limit = Math.min(Number(searchParams.get("limit") || "500"), 57600);

 console.log(` TS OHLCV request: ${symbol} ${tf} (${limit} bars)`);

 try {
 const token = await getAccessToken();
 const { interval, unit } = mapTf(tf);

 const url = new URL(`${TS_BASE_URL}/v3/marketdata/barcharts/${encodeURIComponent(symbol)}`);
 url.searchParams.set("interval", String(interval));
 url.searchParams.set("unit", unit);
 url.searchParams.set("barsback", String(limit));

 console.log(`🔗 Fetching: ${url.toString()}`);

 const r = await fetch(url.toString(), { 
 headers: { Authorization: `Bearer ${token}` }, 
 cache: "no-store" 
 });
 
 if (!r.ok) {
 const m = await r.text();
 return new Response(JSON.stringify({ 
 error: "TS_ERROR", 
 status: r.status, 
 message: m 
 }), { status: 502 });
 }
 
 const js = await r.json();
 const bars = Array.isArray(js.Bars) ? js.Bars : [];

 const data = bars
 .map((b) => ({
 time: Math.floor(((b.Epoch ?? Date.parse(b.TimeStamp)) / 1000)),
 open: Number(b.Open),
 high: Number(b.High),
 low: Number(b.Low),
 close: Number(b.Close),
 volume: Number(b.TotalVolume ?? b.Volume ?? 0),
 }))
 .filter((x) => Number.isFinite(x.time) && Number.isFinite(x.open))
 .sort((a, b) => a.time - b.time);

 console.log(` TS data: ${data.length} bars for ${symbol}`);

 return new Response(JSON.stringify({ 
 symbol, 
 tf: { interval, unit }, 
 count: data.length, 
 data 
 }), {
 headers: { "Content-Type": "application/json" }
 });
 
 } catch (e) {
 console.error('TS OHLCV error:', e);
 return new Response(JSON.stringify({ 
 error: "ADAPTER_FAIL", 
 message: e?.message || String(e) 
 }), { status: 500 });
 }
}