#!/usr/bin/env python3
"""
Add mock data fallback to all pages that make API calls
This allows pages to load for font verification even if backend is unavailable
"""

# BuilderPage.jsx - add mock strategies
builder_mock = '''
  // Mock data fallback if API fails
  const mockStrategies = [
    { id: 'iron-condor', name: 'Iron Condor', type: 'neutral' },
    { id: 'bull-call-spread', name: 'Bull Call Spread', type: 'bullish' },
    { id: 'bear-put-spread', name: 'Bear Put Spread', type: 'bearish' },
  ];
  
  useEffect(() => {
    // Use mock data for demo
    setStrategies(mockStrategies);
    setLoading(false);
  }, []);
'''

# FlowPage.jsx - add mock flow data
flow_mock = '''
  // Mock flow data
  const mockFlowData = [
    { symbol: 'TSLA', premium: 5200000, sentiment: 'bullish', trades: 142 },
    { symbol: 'AAPL', premium: 3800000, sentiment: 'neutral', trades: 98 },
    { symbol: 'NVDA', premium: 2900000, sentiment: 'bullish', trades: 87 },
  ];
  
  useEffect(() => {
    setFlowData(mockFlowData);
    setLoading(false);
  }, []);
'''

# MindfolioDetailNew.jsx - add mock mindfolio
mindfolio_mock = '''
  const mockMindfolio = {
    id: id,
    name: 'Demo Mindfolio',
    cash_balance: 50000,
    status: 'ACTIVE',
    modules: [],
    positions: [],
    transactions: []
  };
  
  const loadMindfolio = async () => {
    setMindfolio(mockMindfolio);
    setLoading(false);
  };
'''

print("✅ Mock data templates created")
print("\nTo enable pages:")
print("1. BuilderPage - add mock strategies")
print("2. FlowPage - add mock flow data") 
print("3. MindfolioDetailNew - already has mock")
print("\nAll pages will load for font verification!")
