// App.js - Step 4: Add Header with Logo + Sidebar Toggle
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { WebSocketProvider } from './context/WebSocketContext';
import { ConnectionStatusBar } from './components/ConnectionStatus';
import SidebarSimple from './components/SidebarSimple';
import { mfClient } from './services/mindfolioClient';
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
import BuilderPage from './pages/BuilderPage';
import SimulatorPage from './pages/SimulatorPage';
import FlowPage from './pages/FlowPage';
import MindfolioList from './pages/MindfolioList';
import MindfolioDetail from './pages/MindfolioDetail';
import MindfolioDetailNew from './pages/MindfolioDetailNew';
import MindfolioCreate from './pages/MindfolioCreate';
import MindfolioPage from './pages/MindfolioPage';
import AccountBalancePage from './pages/AccountBalancePage';
import TradeStationLogin from './pages/TradeStationLogin';
import MarketMoversPage from './pages/MarketMoversPage';
import CongressTradesPage from './pages/CongressTradesPage';
import DarkPoolPage from './pages/DarkPoolPage';
import InstitutionalPage from './pages/InstitutionalPage';
import LogosPage from './pages/LogosPage';
import ScreensaverSettings from './pages/ScreensaverSettings';

function ComingSoonPage() {
 const location = window.location.pathname;
 return (
 <div className="p-8">
 <h2 className="text-xl font-bold text-white mb-4">Coming Soon</h2>
 <div className="bg-slate-800 p-6 rounded-lg">
 <p className="text-slate-300 mb-2">This feature is under development.</p>
 <p className="text-xs text-slate-500">Route: {location}</p>
 </div>
 </div>
 );
}

// Inactivity monitor component
function InactivityMonitor({ timeout = 5 * 60 * 1000 }) {
 const navigate = useNavigate();
 const location = useLocation();
 const [currentTimeout, setCurrentTimeout] = useState(timeout);
 
 // Listen for settings changes
 useEffect(() => {
 const handleSettingsChange = (e) => {
 setCurrentTimeout(e.detail.timeout);
 };
 
 window.addEventListener('screensaverSettingsChanged', handleSettingsChange);
 
 // Load initial timeout from localStorage
 const saved = localStorage.getItem('screensaverTimeout');
 if (saved) {
 setCurrentTimeout(parseInt(saved) * 60 * 1000);
 }
 
 return () => {
 window.removeEventListener('screensaverSettingsChanged', handleSettingsChange);
 };
 }, []);
 
    useEffect(() => {
      // Don't redirect if already on homepage
      if (location.pathname === '/') return;
      
      // Don't set timer if timeout is 0 (disabled)
      if (currentTimeout === 0) return;
      
      let timer;
      
      const resetTimer = () => {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => {
          console.log('User inactive - returning to homepage');
          navigate('/', { replace: true });
        }, currentTimeout);
      };
      
<Route path="/simulator" element={<SimulatorPage />} />
      // Track user activity
      const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
      events.forEach(event => {
        document.addEventListener(event, resetTimer);
      });
      
      // Start the timer
      resetTimer();
      
      // Cleanup
      return () => {
        if (timer) clearTimeout(timer);
        events.forEach(event => {
          document.removeEventListener(event, resetTimer);
        });
      };
    }, [navigate, location.pathname, currentTimeout]); return null;
}

function App() {
 const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
 const [mindfolios, setMindfolios] = useState([]);
 
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
 
 // Fetch mindfolios for sidebar navigation
 useEffect(() => {
 let mounted = true;
 
 mfClient.list()
 .then(data => {
 if (!mounted) return;
 setMindfolios(data || []);
 })
 .catch(e => {
 console.error('Failed to load mindfolios for sidebar:', e);
 });
 
 return () => { mounted = false; };
 }, []);
 
 // Update market status every minute
 React.useEffect(() => {
 const interval = setInterval(() => {
 setMarketOpen(isMarketOpen());
 }, 60000);
 return () => clearInterval(interval);
 }, []);
 
 // Auto-refresh mindfolios every 30 seconds
 useEffect(() => {
 const interval = setInterval(() => {
 mfClient.list()
 .then(data => setMindfolios(data || []))
 .catch(e => console.error('Mindfolio refresh failed:', e));
 }, 30000);
 return () => clearInterval(interval);
 }, []);
 
 // Simple context for sidebar
 const ctx = {
 role: "user",
 flags: {},
 metrics: {},
 mindfolios: mindfolios,
 portfolios: mindfolios // Alias for backwards compatibility
 };

 return (
 <WebSocketProvider>
 <BrowserRouter>
 {/* Inactivity monitor - returns to homepage after 5 minutes of inactivity */}
 <InactivityMonitor timeout={5 * 60 * 1000} />
 
 <div className="flex h-screen bg-[#0a0e1a]">
 {/* Sidebar with toggle button */}
 <div className={`relative transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-[212px]'}`}>
 <SidebarSimple ctx={ctx} collapsed={sidebarCollapsed} />
 
 {/* Toggle button - positioned on left side of sidebar at header height */}
 <button
 onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
 className="absolute top-[12px] left-1 h-[50px] w-10 flex items-center justify-center bg-gradient-to-r from-[#0f1419] to-[#0a0e1a] hover:bg-slate-800 transition-all duration-200 z-10 group"
 title={sidebarCollapsed ? "Show sidebar" : "Hide sidebar"}
 >
            <div className="flex flex-col gap-0.5">
              <div className="w-4 h-px bg-slate-300 group-hover:bg-white rounded-full transition-colors duration-200"></div>
              <div className="w-4 h-px bg-slate-300 group-hover:bg-white rounded-full transition-colors duration-200"></div>
              <div className="w-4 h-px bg-slate-300 group-hover:bg-white rounded-full transition-colors duration-200"></div>
            </div>
 </button>
 </div>
 
 {/* Main content area */}
 <div className="flex-1 flex flex-col overflow-hidden">
 {/* Header */}
 <header className="bg-gradient-to-r from-[#0f1419] to-[#0a0e1a] border-b border-[#1e293b] h-16 flex items-center px-6 gap-4">
 {/* Logo */}
 <div className="flex items-center gap-3 text-white transform translate-y-1 ml-[-22px]">
 <img 
 src="/assets/logos/flowmind_analytics_horizontal.png" 
 alt="FlowMind Analytics" 
 className="h-[114px] w-auto"
 />
 </div>

 {/* Spacer */}
 <div className="flex-1"></div>

 {/* Right side - Market Status */}
 <div className="flex items-center gap-4">
 {/* Market Status - Clean text without card */}
 <div className="flex items-center gap-2 text-[8.4px] font-medium text-slate-400">
 <div className={`w-2 h-2 rounded-full ${marketOpen ? 'bg-emerald-400' : 'bg-slate-500'}`}></div>
 <span>{marketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}</span>
 </div>
 </div>
 </header>

 {/* WebSocket Status Bar */}
 <ConnectionStatusBar />
 
 {/* Main Content */}
 <main className="flex-1 overflow-y-auto bg-[#0f1419]">
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
 <Route path="/tradestation/login" element={<TradeStationLogin />} />
 <Route path="/mindfolio" element={<MindfolioList />} />
 <Route path="/mindfolio/new" element={<MindfolioCreate />} />
 <Route path="/mindfolio/page/:id" element={<MindfolioPage />} />
 <Route path="/mindfolio/:id/old" element={<MindfolioDetail />} />
                <Route path="/mindfolio/:id" element={<MindfolioDetailNew />} />
                <Route path="/logos" element={<LogosPage />} />
                <Route path="/settings/screensaver" element={<ScreensaverSettings />} />
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
