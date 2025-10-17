const BASE = process.env.REACT_APP_BACKEND_URL || "";

async function j(path, init = {}) {
 // Add timeout to prevent hanging
 const controller = new AbortController();
 const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
 
 try {
 const response = await fetch(`${BASE}${path}`, {
 headers: { "Content-Type": "application/json" },
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
 // Portfolio operations
 list: () => j(`/api/mindfolios`),
 get: (pid) => j(`/api/mindfolios/${pid}`),
 create: (body) => j(`/api/mindfolios`, { 
 method: "POST", 
 body: JSON.stringify(body) 
 }),
 patch: (pid, body) => j(`/api/mindfolios/${pid}`, {
 method: "PATCH",
 body: JSON.stringify(body)
 }),
 funds: (pid, delta) => j(`/api/mindfolios/${pid}/funds`, { 
 method: "POST", 
 body: JSON.stringify({ delta }) 
 }),
 allocate: (pid, module, alloc) => j(`/api/mindfolios/${pid}/allocate`, { 
 method: "POST", 
 body: JSON.stringify({ module, alloc }) 
 }),
 stats: (pid) => j(`/api/mindfolios/${pid}/stats`),
 
 // Transaction operations
 getTransactions: (pid, symbol = null) => {
 const params = new URLSearchParams();
 if (symbol) params.set('symbol', symbol);
 const query = params.toString() ? `?${params.toString()}` : '';
 return j(`/api/mindfolios/${pid}/transactions${query}`);
 },
 
 createTransaction: (pid, transaction) => j(`/api/mindfolios/${pid}/transactions`, {
 method: "POST",
 body: JSON.stringify(transaction)
 }),
 
 getPositions: (pid) => j(`/api/mindfolios/${pid}/positions`),
 
 getRealizedPnL: (pid) => j(`/api/mindfolios/${pid}/realized-pnl`),
 
 importCSV: (pid, csvData) => j(`/api/mindfolios/${pid}/import-csv`, {
 method: "POST",
 body: JSON.stringify({ csv_data: csvData })
 })
};