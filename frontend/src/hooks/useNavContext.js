import { useState, useEffect } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export function useNavContext() {
 const [ctx, setCtx] = useState({
 role: "user", // sau "admin" pe baza auth
 flags: { TS_LIVE: false, ORDERS_LIVE: false },
 metrics: { ivOnline: false, verifiedRatio: 0 },
 mindfolios: [
 { id: 'ts-main', name: 'TS Main', nav: 969473 },
 { id: 'long-term', name: 'Long Term', nav: 45000 },
 { id: 'medium-term', name: 'Medium Term', nav: 23000 },
 ]
 });

 const [loading, setLoading] = useState(true);

 useEffect(() => {
 async function fetchNavContext() {
 try {
 // Fetch metrics în paralel
 const [redisRes, emergentRes, tsRes] = await Promise.allSettled([
 fetch(`${BACKEND_URL}/_redis/diag`),
 fetch(`${BACKEND_URL}/_emergent/status?module=sell_puts`),
 fetch(`${BACKEND_URL}/api/tradestation/connection/test`)
 ]);

 const newCtx = { ...ctx };

 // Redis + IV status
 if (redisRes.status === 'fulfilled' && redisRes.value.ok) {
 const redisData = await redisRes.value.json();
 newCtx.metrics.ivOnline = redisData.ok && redisData.impl === 'Redis';
 }

 // Emergent status pentru verified ratio
 if (emergentRes.status === 'fulfilled' && emergentRes.value.ok) {
 const emergentData = await emergentRes.value.json();
 if (emergentData.cache) {
 const { keys_total, keys_verified } = emergentData.cache;
 newCtx.metrics.verifiedRatio = keys_total > 0 ? keys_verified / keys_total : 0;
 }
 }

 // TradeStation connectivity
 if (tsRes.status === 'fulfilled' && tsRes.value.ok) {
 const tsData = await tsRes.value.json();
 newCtx.flags.TS_LIVE = tsData.status === 'success';
 }

 // Check admin role (simple check pe env sau auth)
 newCtx.role = window.location.hostname.includes('localhost') ? 'admin' : 'user';

 // Orders LIVE din env
 newCtx.flags.ORDERS_LIVE = process.env.NODE_ENV === 'development' || 
 window.location.search.includes('orders_live=1');

 setCtx(newCtx);
 } catch (error) {
 console.error('Failed to fetch nav context:', error);
 } finally {
 setLoading(false);
 }
 }

 fetchNavContext();
 
 // Refresh context every 30s
 const interval = setInterval(fetchNavContext, 30000);
 return () => clearInterval(interval);
 }, []);

 return { ctx, loading };
}