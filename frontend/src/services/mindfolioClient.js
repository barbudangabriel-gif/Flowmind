const BASE = process.env.REACT_APP_BACKEND_URL || "";

async function j(path, init = {}) {
 // Add timeout to prevent hanging
 const controller = new AbortController();
 const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
 
 try {
 const response = await fetch(`${BASE}${path}`, {
 headers: { 
   "Content-Type": "application/json",
   "X-User-ID": "default"
 },
 ...init,
 signal: controller.signal,
 });
 
 clearTimeout(timeoutId);
 
 if (!response.ok) {
 throw new Error(`${response.status} ${response.statusText}`);
 }
 
 const json = await response.json();
 // Extract data from {status: "success", data: ...} wrapper
 return json.data !== undefined ? json.data : json;
 } catch (error) {
 clearTimeout(timeoutId);
 if (error.name === 'AbortError') {
 throw new Error('Request timeout - backend not responding');
 }
 throw error;
 }
}

export const mfClient = {
 // Mindfolio operations
 list: () => j(`/api/mindfolio`),
 get: (pid) => j(`/api/mindfolio/${pid}`),
 create: (body) => j(`/api/mindfolio`, { 
 method: "POST", 
 body: JSON.stringify(body) 
 }),
 patch: (pid, body) => j(`/api/mindfolio/${pid}`, {
 method: "PATCH",
 body: JSON.stringify(body)
 }),
 update: (pid, body) => j(`/api/mindfolio/${pid}`, {
 method: "PATCH",
 body: JSON.stringify(body)
 }),
 delete: (pid) => j(`/api/mindfolio/${pid}`, {
 method: "DELETE"
 }),
 funds: (pid, delta) => j(`/api/mindfolio/${pid}/funds`, { 
 method: "POST", 
 body: JSON.stringify({ delta }) 
 }),
 allocate: (pid, module, alloc) => j(`/api/mindfolio/${pid}/allocate`, { 
 method: "POST", 
 body: JSON.stringify({ module, alloc }) 
 }),
 stats: (pid) => j(`/api/mindfolio/${pid}/stats`),
 
 // TradeStation import
 importFromTradeStation: (account_id, name) => j(`/api/mindfolio/import-from-tradestation`, {
 method: "POST",
 body: JSON.stringify({ account_id, name })
 }),
 
 // Import YTD transactions from TradeStation
 importYTD: (pid, account_id) => j(`/api/mindfolio/${pid}/import-ytd`, {
 method: "POST",
 body: JSON.stringify({ account_id })
 }),
 
 // Transaction operations
 getTransactions: (pid, symbol = null) => {
 const params = new URLSearchParams();
 if (symbol) params.set('symbol', symbol);
 const query = params.toString() ? `?${params.toString()}` : '';
 return j(`/api/mindfolio/${pid}/transactions${query}`);
 },
 
 createTransaction: (pid, transaction) => j(`/api/mindfolio/${pid}/transactions`, {
 method: "POST",
 body: JSON.stringify(transaction)
 }),
 
 getPositions: (pid) => j(`/api/mindfolio/${pid}/positions`),
 
 getRealizedPnL: (pid) => j(`/api/mindfolio/${pid}/realized-pnl`),
 
 importCSV: (pid, csvData) => j(`/api/mindfolio/${pid}/import-csv`, {
 method: "POST",
 body: JSON.stringify({ csv_data: csvData })
 })
};