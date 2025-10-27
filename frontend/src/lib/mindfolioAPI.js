import api from './api.js';

// Mindfolio-specific API wrapper that works with existing token management
export const mindfolioAPI = {
 // Mindfolios
 listMindfolios: async () => {
 const response = await api.get('/mindfolio');
 return response.data;
 },

 createMindfolio: async (name, base_currency = 'USD') => {
 const response = await api.post('/mindfolio', { name, base_currency });
 return response.data;
 },

 // Summary 
 summary: async (pid) => {
 const response = await api.get(`/mindfolio/${pid}/stats`);
 return response.data;
 },

 // Positions (FIFO generic)
 positions: async (pid) => {
 const response = await api.get(`/mindfolio/${pid}/positions`);
 return response.data;
 },

 // TS Positions grid
 positionsTS: async (pid) => {
 try {
 const response = await api.get(`/mindfolio/positions-ts`, { params: { mindfolioId: pid } });
 return response.data;
 } catch (error) {
 // Fallback to regular positions
 return await mindfolioAPI.positions(pid);
 }
 },

 // Transactions
 listTx: async (pid, filters = {}) => {
 const params = { mindfolioId: pid, ...filters };
 // Remove undefined/empty values
 Object.keys(params).forEach(key => {
 if (params[key] == null || params[key] === '') {
 delete params[key];
 }
 });
 
 const response = await api.get(`/mindfolio/${pid}/transactions`, { params });
 return response.data;
 },
 
 createTx: async (pid, body) => {
 const response = await api.post(`/mindfolio/${pid}/transactions`, body);
 return response.data;
 },

 // Import CSV
 importCSV: async (pid, csv_data) => {
 const response = await api.post(`/mindfolio/${pid}/import-csv`, { csv_data });
 return response.data;
 },

 // Buckets
 listBuckets: async (pid) => {
 try {
 const response = await api.get(`/mindfolio/${pid}/buckets`);
 return response.data;
 } catch (error) {
 console.warn('Buckets not available:', error);
 return { buckets: [] };
 }
 },

 createBucket: async (pid, body) => {
 const response = await api.post(`/mindfolio/${pid}/buckets`, body);
 return response.data;
 },

 // Analytics & Equity
 equity: async (pid, params = {}) => {
 try {
 const queryParams = { ...params };
 const response = await api.get(`/mindfolio/${pid}/analytics/equity`, { params: queryParams });
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
 const response = await api.get(`/mindfolio/${pid}/analytics/eod`);
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
 const response = await api.post(`/mindfolio/${pid}/analytics/eod/snapshot`);
 return response.data;
 } catch (error) {
 console.error('EOD snapshot failed:', error);
 throw error;
 }
 }
};