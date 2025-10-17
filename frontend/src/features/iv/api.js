const BASE = "/api";

export const ivAPI = {
 async fetchSummary(symbol) {
 const res = await fetch(`${BASE}/iv/summary?symbol=${symbol}`);
 const data = await res.json();
 
 // Fallback calculation dacă em lipsește
 if (!data.em && data.iv) {
 const front_dte = data.front_dte || 7;
 const em_pct = data.iv * Math.sqrt(front_dte / 365);
 const em_usd = data.spot * em_pct;
 data.em = { pct: em_pct, usd: em_usd };
 }
 
 return data;
 },
 
 async fetchStrikes(body) {
 const res = await fetch(`${BASE}/iv/strikes`, {
 method: 'POST',
 headers: { 'Content-Type': 'application/json' },
 body: JSON.stringify(body)
 });
 const data = await res.json();
 
 // Ensure strikes arrays exist
 if (data.front && !data.front.strikes) {
 data.front.strikes = [172, 191]; // fallback
 }
 if (data.back && !data.back.strikes) {
 data.back.strikes = [172, 191]; // fallback
 }
 
 return data;
 }
};