// Client-side helper for fetching TradeStation OHLCV data

export async function fetchOHLCV(symbol, tf, limit = 500) {
 const q = new URLSearchParams({ 
 symbol, 
 tf, 
 limit: String(limit) 
 });
 
 console.log(` Fetching OHLCV: ${symbol} ${tf} (${limit} bars)`);
 
 const res = await fetch(`/api/ohlcv?${q.toString()}`, { 
 cache: "no-store" 
 });
 
 if (!res.ok) {
 const errorData = await res.json().catch(() => ({}));
 throw new Error(`OHLCV ${res.status}: ${errorData.message || 'Unknown error'}`);
 }
 
 const json = await res.json();
 
 if (json.error) {
 throw new Error(`TS Error: ${json.message}`);
 }
 
 console.log(` OHLCV data: ${json.count} bars for ${symbol}`);
 return json.data;
}

// TradeStation-specific fetcher function for useOHLCV hook
export async function tsOHLCVFetcher({ symbol, timeframe, limit }) {
 try {
 return await fetchOHLCV(symbol, timeframe, limit);
 } catch (error) {
 console.error('TS OHLCV fetch failed:', error);
 throw error;
 }
}