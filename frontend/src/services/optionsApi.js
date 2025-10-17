// src/services/optionsApi.js

export async function getMarketOverview(symbol = 'ALL') {
 const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
 const res = await fetch(`${backendUrl}/api/options/overview?symbol=${encodeURIComponent(symbol)}`, { 
 credentials: 'include',
 headers: {
 'Content-Type': 'application/json'
 }
 });
 
 if (!res.ok) {
 throw new Error(`Options overview API error: ${res.status}`);
 }
 
 const json = await res.json();
 return {
 activeStrategies: json.activeStrategies ?? 0,
 expirationDates: json.expirationDates ?? 0,
 dailyVolumeUsd: json.dailyVolumeUsd ?? 0,
 avgIvPct: json.avgIvPct ?? null
 };
}

// Real flow summary from UW trades data
export async function getFlowSummary(symbol = 'ALL', days = 7) {
 const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
 const res = await fetch(`${backendUrl}/api/options/flow/summary?symbol=${encodeURIComponent(symbol)}&days=${days}`, { 
 credentials: 'include',
 headers: {
 'Content-Type': 'application/json'
 }
 });
 
 if (!res.ok) {
 throw new Error(`Flow summary API error: ${res.status}`);
 }
 
 const json = await res.json();
 return {
 live: json.live ?? 0,
 historical: json.historical ?? 0,
 news: json.news ?? 0,
 congress: json.congress ?? 0,
 insiders: json.insiders ?? 0
 };
}

export async function getExpirationsCount() {
 return 12; // Mock for now
}