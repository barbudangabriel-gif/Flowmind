// utils/withRetry.js
export async function withRetry(
 fn,
 { retries = 2, backoff = 300 } = {}
) {
 let lastErr;
 for (let i = 0; i <= retries; i++) {
 try { 
 return await fn(); 
 } catch (e) {
 lastErr = e;
 if (i === retries) break;
 await new Promise(r => setTimeout(r, backoff * (i + 1))); // 300ms, 600ms
 }
 }
 throw lastErr;
}