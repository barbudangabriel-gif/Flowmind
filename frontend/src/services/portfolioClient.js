const BASE = process.env.REACT_APP_BACKEND_URL || "";

async function j(path, init = {}) {
 const response = await fetch(`${BASE}${path}`, {
 headers: { "Content-Type": "application/json" },
 ...init,
 });
 
 if (!response.ok) {
 throw new Error(`${response.status} ${response.statusText}`);
 }
 
 return response.json();
}

export const pfClient = {
 // Portfolio operations
 list: () => j(`/api/portfolios`),
 get: (pid) => j(`/api/portfolios/${pid}`),
 create: (body) => j(`/api/portfolios`, { 
 method: "POST", 
 body: JSON.stringify(body) 
 }),
 patch: (pid, body) => j(`/api/portfolios/${pid}`, {
 method: "PATCH",
 body: JSON.stringify(body)
 }),
 funds: (pid, delta) => j(`/api/portfolios/${pid}/funds`, { 
 method: "POST", 
 body: JSON.stringify({ delta }) 
 }),
 allocate: (pid, module, alloc) => j(`/api/portfolios/${pid}/allocate`, { 
 method: "POST", 
 body: JSON.stringify({ module, alloc }) 
 }),
 stats: (pid) => j(`/api/portfolios/${pid}/stats`),
 
 // Transaction operations
 getTransactions: (pid, symbol = null) => {
 const params = new URLSearchParams();
 if (symbol) params.set('symbol', symbol);
 const query = params.toString() ? `?${params.toString()}` : '';
 return j(`/api/portfolios/${pid}/transactions${query}`);
 },
 
 createTransaction: (pid, transaction) => j(`/api/portfolios/${pid}/transactions`, {
 method: "POST",
 body: JSON.stringify(transaction)
 }),
 
 getPositions: (pid) => j(`/api/portfolios/${pid}/positions`),
 
 getRealizedPnL: (pid) => j(`/api/portfolios/${pid}/realized-pnl`),
 
 importCSV: (pid, csvData) => j(`/api/portfolios/${pid}/import-csv`, {
 method: "POST",
 body: JSON.stringify({ csv_data: csvData })
 })
};