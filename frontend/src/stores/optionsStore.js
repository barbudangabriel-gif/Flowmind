// src/stores/optionsStore.js
import { create } from 'zustand';
import { getMarketOverview, getFlowSummary } from '../services/optionsApi';
import React from 'react';

export const useOptionsStore = create((set) => ({
  loading: false,
  error: null,
  overview: null,
  flow: null,
  previewItem: null,
  
  fetchAnalytics: async (symbol = 'ALL') => {
    set({ loading: true, error: null });
    try {
      const [overview, flow] = await Promise.all([
        getMarketOverview(symbol),
        getFlowSummary(symbol),
      ]);
      set({ overview, flow, loading: false });
    } catch (e) {
      set({ error: e?.message ?? 'Load failed', loading: false });
    }
  },
  
  setPreviewItem: (p) => set({ previewItem: p })
}));

// Hook for polling market overview data every 60 seconds
export function useOptionsOverviewPolling(symbol = 'ALL') {
  const { fetchAnalytics } = useOptionsStore();
  
  React.useEffect(() => {
    let active = true;
    
    // Initial fetch
    if (active) {
      fetchAnalytics(symbol);
    }
    
    // Set up polling interval (60 seconds)
    const intervalId = setInterval(() => {
      if (active) {
        fetchAnalytics(symbol);
      }
    }, 60_000);
    
    // Cleanup function
    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, [symbol, fetchAnalytics]);
}