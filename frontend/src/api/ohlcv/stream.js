// TradeStation OHLCV Streaming API Route (SSE Proxy)
// Converts TradeStation HTTP streaming to Server-Sent Events

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
 const limit = Math.min(Number(searchParams.get("barsBack") || "500"), 57600);

 console.log(`📡 Starting TS stream: ${symbol} ${tf} (${limit} bars)`);

 try {
 const token = await getAccessToken();
 const { interval, unit } = mapTf(tf);

 // TradeStation streaming endpoint
 const streamUrl = new URL(`${TS_BASE_URL}/v3/marketdata/stream/barcharts/${encodeURIComponent(symbol)}`);
 streamUrl.searchParams.set("interval", String(interval));
 streamUrl.searchParams.set("unit", unit);
 streamUrl.searchParams.set("barsback", String(limit));

 console.log(`🔗 Connecting to TS stream: ${streamUrl.toString()}`);

 // Create SSE response
 const encoder = new TextEncoder();
 const stream = new ReadableStream({
 async start(controller) {
 try {
 // Connect to TradeStation streaming endpoint
 const tsResponse = await fetch(streamUrl.toString(), {
 headers: { 
 Authorization: `Bearer ${token}`,
 Accept: "application/json"
 },
 signal: request.signal
 });

 if (!tsResponse.ok) {
 const error = await tsResponse.text();
 controller.enqueue(encoder.encode(`event: error\ndata: ${JSON.stringify({ 
 error: "TS_STREAM_ERROR", 
 status: tsResponse.status, 
 message: error 
 })}\n\n`));
 controller.close();
 return;
 }

 const reader = tsResponse.body?.getReader();
 if (!reader) {
 controller.enqueue(encoder.encode(`event: error\ndata: ${JSON.stringify({ 
 error: "NO_READER", 
 message: "Failed to get stream reader" 
 })}\n\n`));
 controller.close();
 return;
 }

 // Send initial status
 controller.enqueue(encoder.encode(`event: status\ndata: ${JSON.stringify({ 
 status: "connected", 
 symbol, 
 tf: { interval, unit },
 timestamp: Date.now()
 })}\n\n`));

 let buffer = "";
 while (true) {
 const { done, value } = await reader.read();
 if (done) break;

 // Process incoming chunks
 buffer += new TextDecoder().decode(value);
 const lines = buffer.split('\n');
 buffer = lines.pop() || ""; // Keep incomplete line in buffer

 for (const line of lines) {
 if (line.trim()) {
 try {
 const barData = JSON.parse(line);
 
 // Check for stream status messages
 if (barData.StreamStatus) {
 controller.enqueue(encoder.encode(`event: status\ndata: ${JSON.stringify({ 
 status: "stream_update", 
 streamStatus: barData.StreamStatus,
 timestamp: Date.now()
 })}\n\n`));
 continue;
 }

 // Process bar data
 if (barData.Open !== undefined && barData.Close !== undefined) {
 const normalizedBar = {
 time: Math.floor(((barData.Epoch ?? Date.parse(barData.TimeStamp)) / 1000)),
 open: Number(barData.Open),
 high: Number(barData.High),
 low: Number(barData.Low),
 close: Number(barData.Close),
 volume: Number(barData.TotalVolume ?? barData.Volume ?? 0),
 isEndOfHistory: barData.IsEndOfHistory === true
 };

 // Validate data
 if (Number.isFinite(normalizedBar.time) && Number.isFinite(normalizedBar.open)) {
 controller.enqueue(encoder.encode(`event: bar\ndata: ${JSON.stringify(normalizedBar)}\n\n`));
 }
 }
 } catch (parseError) {
 console.warn('Failed to parse TS stream line:', line, parseError);
 }
 }
 }
 }

 controller.close();
 } catch (streamError) {
 console.error('TS Stream error:', streamError);
 controller.enqueue(encoder.encode(`event: error\ndata: ${JSON.stringify({ 
 error: "STREAM_ERROR", 
 message: streamError.message 
 })}\n\n`));
 controller.close();
 }
 },

 cancel() {
 console.log('📡 TS stream cancelled by client');
 }
 });

 return new Response(stream, {
 headers: {
 "Content-Type": "text/event-stream",
 "Cache-Control": "no-cache",
 "Connection": "keep-alive",
 "Access-Control-Allow-Origin": "*",
 "Access-Control-Allow-Headers": "Cache-Control"
 },
 });

 } catch (error) {
 console.error('TS Streaming setup error:', error);
 return new Response(JSON.stringify({ 
 error: "ADAPTER_FAIL", 
 message: error.message || String(error) 
 }), { 
 status: 500,
 headers: { "Content-Type": "application/json" }
 });
 }
}