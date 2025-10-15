// App.js - Step 4: Add Header with Logo + Sidebar Toggle
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { WebSocketProvider } from './context/WebSocketContext';
import { ConnectionStatusBar } from './components/ConnectionStatus';
import SidebarSimple from './components/SidebarSimple';
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
import BuilderPage from './pages/BuilderPage';
import FlowPage from './pages/FlowPage';
import MindfolioList from './pages/MindfolioList';
import MindfolioDetail from './pages/MindfolioDetail';
import MindfolioCreate from './pages/MindfolioCreate';
import AccountBalancePage from './pages/AccountBalancePage';
import MarketMoversPage from './pages/MarketMoversPage';
import CongressTradesPage from './pages/CongressTradesPage';
import DarkPoolPage from './pages/DarkPoolPage';
import InstitutionalPage from './pages/InstitutionalPage';

function ComingSoonPage() {
  const location = window.location.pathname;
  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold text-white mb-4">Coming Soon</h2>
      <div className="bg-slate-800 p-6 rounded-lg">
        <p className="text-slate-300 mb-2">This feature is under development.</p>
        <p className="text-xs text-slate-500">Route: {location}</p>
      </div>
    </div>
  );
}

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Market hours check (9:30 AM - 4:00 PM EST)
  const isMarketOpen = () => {
    const now = new Date();
    const hours = now.getUTCHours() - 5; // EST (simplified, doesn't account for DST)
    const day = now.getUTCDay();
    const isWeekday = day >= 1 && day <= 5;
    const isMarketHours = hours >= 9.5 && hours < 16;
    return isWeekday && isMarketHours;
  };
  
  const [marketOpen, setMarketOpen] = useState(isMarketOpen());
  
  // Update market status every minute
  React.useEffect(() => {
    const interval = setInterval(() => {
      setMarketOpen(isMarketOpen());
    }, 60000);
    return () => clearInterval(interval);
  }, []);
  
  // Simple context for sidebar
  const ctx = {
    role: "user",
    flags: {},
    metrics: {},
    portfolios: []
  };

  return (
    <WebSocketProvider>
      <BrowserRouter>
        <div className="flex h-screen bg-[#0a0e1a]">
          {/* Sidebar with toggle button */}
          <div className={`relative transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-64'}`}>
            <SidebarSimple ctx={ctx} collapsed={sidebarCollapsed} />
            
            {/* Toggle button - positioned on left side of sidebar at header height */}
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="absolute top-0 left-0 h-16 w-12 flex items-center justify-center bg-gradient-to-r from-[#0f1419] to-[#0a0e1a] hover:bg-slate-800 transition-colors z-10"
              title={sidebarCollapsed ? "Show sidebar" : "Hide sidebar"}
            >
              <div className="flex flex-col gap-1">
                <div className="w-5 h-0.5 bg-slate-300 rounded-full"></div>
                <div className="w-5 h-0.5 bg-slate-300 rounded-full"></div>
                <div className="w-5 h-0.5 bg-slate-300 rounded-full"></div>
              </div>
            </button>
          </div>
        
          {/* Main content area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <header className="bg-gradient-to-r from-[#0f1419] to-[#0a0e1a] border-b border-[#1e293b] h-16 flex items-center px-6 gap-4">
              {/* Logo */}
              <div className="flex items-center gap-3 text-white transform translate-y-1">
                <img 
                  src="/assets/logos/flowmind_horizontal_white.svg" 
                  alt="FlowMind Analytics" 
                  className="h-14 w-auto"
                />
              </div>

              {/* Spacer */}
              <div className="flex-1"></div>

              {/* Right side - Market Status + Welcome */}
              <div className="flex items-center gap-4">
                {/* Market Status Badge */}
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold ${
                  marketOpen 
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                    : 'bg-slate-700 text-slate-400 border border-slate-600'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${marketOpen ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`}></div>
                  <span>{marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}</span>
                </div>
                
                <span className="text-sm text-[#94a3b8]">Welcome back</span>
              </div>
            </header>

            {/* WebSocket Status Bar */}
            <ConnectionStatusBar />
            
            {/* Main Content */}
            <main className="flex-1 overflow-y-auto bg-[#0a0e1a]">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/builder" element={<BuilderPage />} />
                <Route path="/builder/:strategySlug" element={<BuilderPage />} />
                <Route path="/flow" element={<FlowPage />} />
                <Route path="/flow/live" element={<FlowPage />} />
                <Route path="/dark-pool" element={<DarkPoolPage />} />
                <Route path="/market-movers" element={<MarketMoversPage />} />
                <Route path="/congress-trades" element={<CongressTradesPage />} />
                <Route path="/institutional" element={<InstitutionalPage />} />
                <Route path="/account/balance" element={<AccountBalancePage />} />
                <Route path="/mindfolio" element={<MindfolioList />} />
                <Route path="/mindfolio/new" element={<MindfolioCreate />} />
                <Route path="/mindfolio/:id" element={<MindfolioDetail />} />
                {/* Catch-all for all other routes */}
                <Route path="*" element={<ComingSoonPage />} />
              </Routes>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </WebSocketProvider>
  );
}

export default App;
