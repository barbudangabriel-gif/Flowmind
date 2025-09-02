import api from './api.js';

// Portfolio-specific API wrapper that works with existing token management
export const portfolioAPI = {
  // Portfolios
  listPortfolios: async () => {
    const response = await api.get('/portfolios');
    return response.data;
  },

  createPortfolio: async (name, base_currency = 'USD') => {
    const response = await api.post('/portfolios', { name, base_currency });
    return response.data;
  },

  // Summary 
  summary: async (pid) => {
    const response = await api.get(`/portfolios/${pid}/stats`);
    return response.data;
  },

  // Positions (FIFO generic)
  positions: async (pid) => {
    const response = await api.get(`/portfolios/${pid}/positions`);
    return response.data;
  },

  // TS Positions grid
  positionsTS: async (pid) => {
    try {
      const response = await api.get(`/portfolios/positions-ts`, { params: { portfolioId: pid } });
      return response.data;
    } catch (error) {
      // Fallback to regular positions
      return await portfolioAPI.positions(pid);
    }
  },

  // Transactions
  listTx: async (pid, filters = {}) => {
    const params = { portfolioId: pid, ...filters };
    // Remove undefined/empty values
    Object.keys(params).forEach(key => {
      if (params[key] == null || params[key] === '') {
        delete params[key];
      }
    });
    
    const response = await api.get(`/portfolios/${pid}/transactions`, { params });
    return response.data;
  },
  
  createTx: async (pid, body) => {
    const response = await api.post(`/portfolios/${pid}/transactions`, body);
    return response.data;
  },

  // Import CSV
  importCSV: async (pid, csv_data) => {
    const response = await api.post(`/portfolios/${pid}/import-csv`, { csv_data });
    return response.data;
  },

  // Buckets
  listBuckets: async (pid) => {
    try {
      const response = await api.get(`/portfolios/${pid}/buckets`);
      return response.data;
    } catch (error) {
      console.warn('Buckets not available:', error);
      return { buckets: [] };
    }
  },

  createBucket: async (pid, body) => {
    const response = await api.post(`/portfolios/${pid}/buckets`, body);
    return response.data;
  },

  // Analytics & Equity
  equity: async (pid, params = {}) => {
    try {
      const queryParams = { ...params };
      const response = await api.get(`/portfolios/${pid}/analytics/equity`, { params: queryParams });
      return response.data;
    } catch (error) {
      console.warn('Equity analytics not available:', error);
      // Return mock data structure for development
      return {
        analytics: {
          equity_curve: [],
          summary: {
            current_equity: 0,
            total_realized_pnl: 0,
            total_trades: 0
          }
        }
      };
    }
  },

  // EOD Analytics (End of Day snapshots)
  eod: async (pid) => {
    try {
      const response = await api.get(`/portfolios/${pid}/analytics/eod`);
      return response.data;
    } catch (error) {
      console.warn('EOD analytics not available:', error);
      return {
        series: []
      };
    }
  },

  // EOD Snapshot (trigger manual snapshot)
  eodSnapshot: async (pid) => {
    try {
      const response = await api.post(`/portfolios/${pid}/analytics/eod/snapshot`);
      return response.data;
    } catch (error) {
      console.error('EOD snapshot failed:', error);
      throw error;
    }
  }
};