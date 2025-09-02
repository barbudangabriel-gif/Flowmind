// Frontend Flow API with TypeScript-like JSDoc
const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";

/**
 * @typedef {Object} FlowSummaryResponse
 * @property {'LIVE'|'DEMO'} mode
 * @property {Array} items
 * @property {string} ts
 */

/**
 * @typedef {Object} FlowLiveResponse  
 * @property {'LIVE'|'DEMO'} mode
 * @property {Array} items
 * @property {string|null} next
 * @property {string} ts
 */

/**
 * Get flow summary data
 * @param {Object} params
 * @param {number} [params.limit=24]
 * @param {number} [params.minPremium=25000]  
 * @returns {Promise<FlowSummaryResponse>}
 */
export async function getFlowSummary(params = {}) {
  const q = new URLSearchParams({
    limit: String(params.limit ?? 24),
    minPremium: String(params.minPremium ?? 25000),
  });
  
  const res = await fetch(`${API}/api/flow/summary?${q.toString()}`, { 
    credentials: 'same-origin' 
  });
  
  if (!res.ok) throw new Error(`flow/summary ${res.status}`);
  return res.json();
}

/**
 * Get live flow data for specific symbol
 * @param {Object} params
 * @param {string} params.symbol
 * @param {number} [params.minPremium=25000]
 * @param {string|null} [params.cursor=null]
 * @returns {Promise<FlowLiveResponse>}
 */
export async function getFlowLive(params) {
  const q = new URLSearchParams({
    symbol: params.symbol,
    minPremium: String(params.minPremium ?? 25000),
    ...(params.cursor ? { cursor: params.cursor } : {})
  });
  
  const res = await fetch(`${API}/api/flow/live?${q.toString()}`, { 
    credentials: 'same-origin' 
  });
  
  if (!res.ok) throw new Error(`flow/live ${res.status}`);
  return res.json();
}

/**
 * Get historical flow data
 * @param {Object} params
 * @param {string} params.symbol
 * @param {number} [params.days=7]
 * @param {number} [params.minPremium=25000]
 * @returns {Promise<FlowLiveResponse>}
 */
export async function getFlowHistorical(params) {
  const q = new URLSearchParams({
    symbol: params.symbol,
    days: String(params.days ?? 7),
    minPremium: String(params.minPremium ?? 25000),
  });
  
  const res = await fetch(`${API}/api/flow/historical?${q.toString()}`, { 
    credentials: 'same-origin' 
  });
  
  if (!res.ok) throw new Error(`flow/historical ${res.status}`);
  return res.json();
}

/**
 * Get news flow data
 * @param {string[]} [tickers=[]]
 * @returns {Promise<FlowLiveResponse>}
 */
export async function getFlowNews(tickers = []) {
  const q = new URLSearchParams();
  if (tickers.length) {
    q.append('tickers', tickers.join(','));
  }
  
  const res = await fetch(`${API}/api/flow/news?${q.toString()}`, { 
    credentials: 'same-origin' 
  });
  
  if (!res.ok) throw new Error(`flow/news ${res.status}`);
  return res.json();
}

/**
 * Get congress flow data
 * @param {string[]} [tickers=[]]
 * @returns {Promise<FlowLiveResponse>}
 */
export async function getFlowCongress(tickers = []) {
  const q = new URLSearchParams();
  if (tickers.length) {
    q.append('tickers', tickers.join(','));
  }
  
  const res = await fetch(`${API}/api/flow/congress?${q.toString()}`, { 
    credentials: 'same-origin' 
  });
  
  if (!res.ok) throw new Error(`flow/congress ${res.status}`);
  return res.json();
}

/**
 * Get insiders flow data
 * @param {string[]} [tickers=[]]
 * @returns {Promise<FlowLiveResponse>}
 */
export async function getFlowInsiders(tickers = []) {
  const q = new URLSearchParams();
  if (tickers.length) {
    q.append('tickers', tickers.join(','));
  }
  
  const res = await fetch(`${API}/api/flow/insiders?${q.toString()}`, { 
    credentials: 'same-origin' 
  });
  
  if (!res.ok) throw new Error(`flow/insiders ${res.status}`);
  return res.json();
}