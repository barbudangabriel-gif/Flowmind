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

export const mfClient = {
  // Portfolio operations
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
  funds: (pid, delta) => j(`/api/mindfolio/${pid}/funds`, { 
    method: "POST", 
    body: JSON.stringify({ delta }) 
  }),
  allocate: (pid, module, alloc) => j(`/api/mindfolio/${pid}/allocate`, { 
    method: "POST", 
    body: JSON.stringify({ module, alloc }) 
  }),
  stats: (pid) => j(`/api/mindfolio/${pid}/stats`),
  
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