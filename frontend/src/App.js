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
import StrategyLibraryPage from './pages/StrategyLibraryPage';
import BuilderV2Page from './pages/BuilderV2Page';
import StrategyChartTestPage from './pages/StrategyChartTestPage';
import UniversalStrategyCardTestPage from './pages/UniversalStrategyCardTestPage';
import LongPutTestPage from './pages/LongPutTestPage';
import SimulatorPage from './pages/SimulatorPage';
import FlowPage from './pages/FlowPage';
import MindfolioList from './pages/MindfolioList';
import MindfolioDetail from './pages/MindfolioDetail';
import MindfolioDetailNew from './pages/MindfolioDetailNew';
import MindfolioDetailNewV2 from './pages/MindfolioDetailNewV2';
import MindfolioCreate from './pages/MindfolioCreate';
import MindfolioPage from './pages/MindfolioPage';
import ImportFromTradeStation from './pages/ImportFromTradeStation';
import TradeStationConnectPage from './pages/TradeStationConnectPage';
import AccountDetailPage from './pages/AccountDetailPage';
import AggregateAccountPage from './pages/AggregateAccountPage';
import TradeStationLogin from './pages/TradeStationLogin';
import MarketMoversPage from './pages/MarketMoversPage';
import CongressTradesPage from './pages/CongressTradesPage';
import DarkPoolPage from './pages/DarkPoolPage';
import InstitutionalPage from './pages/InstitutionalPage';
import LogosPage from './pages/LogosPage';
import ScreensaverSettings from './pages/ScreensaverSettings';
import CardTestPage from './pages/CardTestPage';

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
function InactivityMonitor({ timeout = 0 }) {
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
      // Don't redirect if already on homepage or test pages
      if (location.pathname === '/' || location.pathname === '/card-test' || location.pathname.startsWith('/builder')) return;
      
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
 
 console.log('[App.js] Fetching mindfolios from:', `${process.env.REACT_APP_BACKEND_URL}/api/mindfolio`);
 
 mfClient.list()
 .then(data => {
 if (!mounted) return;
 console.log('[App.js] Mindfolios received:', data);
 // Filter out deleted mindfolios
 const active = (data || []).filter(m => m.status !== 'DELETED');
 setMindfolios(active);
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
 console.log('[App.js] Auto-refreshing mindfolios...');
 mfClient.list()
 .then(data => {
 console.log('[App.js] Auto-refresh received:', data);
 // Filter out deleted mindfolios
 const active = (data || []).filter(m => m.status !== 'DELETED');
 setMindfolios(active);
 })
 .catch(e => console.error('Mindfolio refresh failed:', e));
 }, 30000);
 return () => clearInterval(interval);
 }, []);
 
 // Simple context for sidebar
 const ctx = {
      role: "user",
      flags: {},
      metrics: {},
      mindfolios: mindfolios
    };
    
    console.log('[App.js] Context mindfolios:', mindfolios);
    
    return (
 <WebSocketProvider>
 <BrowserRouter>
 {/* Inactivity monitor - returns to homepage after 5 minutes of inactivity */}
 {/* DISABLED FOR TESTING: <InactivityMonitor timeout={5 * 60 * 1000} /> */}
 
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
 <Route path="/builder" element={<BuilderV2Page />} />
 <Route path="/simulator" element={<SimulatorPage />} />
 <Route path="/strategy-chart-test" element={<StrategyChartTestPage />} />
 <Route path="/strategy-card-test" element={<UniversalStrategyCardTestPage />} />
 <Route path="/long-put-test" element={<LongPutTestPage />} />
 <Route path="/strategies" element={<StrategyLibraryPage />} />
 <Route path="/card-test" element={<CardTestPage />} />
 <Route path="/flow" element={<FlowPage />} />
 <Route path="/flow/live" element={<FlowPage />} />
 <Route path="/dark-pool" element={<DarkPoolPage />} />
 <Route path="/market-movers" element={<MarketMoversPage />} />
 <Route path="/congress-trades" element={<CongressTradesPage />} />
 <Route path="/institutional" element={<InstitutionalPage />} />
 <Route path="/tradestation/connect" element={<TradeStationConnectPage />} />
 
 {/* Aggregate Account View */}
 <Route path="/account/aggregate" element={<AggregateAccountPage />} />
 
 {/* Account Detail Pages - Dynamic Routes */}
 <Route path="/account/:broker/:accountType" element={<AccountDetailPage />} />
 
 <Route path="/tradestation/login" element={<TradeStationLogin />} />
 <Route path="/mindfolio" element={<MindfolioList />} />
 <Route path="/mindfolio/new" element={<MindfolioCreate />} />
 <Route path="/mindfolio/import" element={<ImportFromTradeStation />} />
 <Route path="/mindfolio/page/:id" element={<MindfolioPage />} />
 <Route path="/mindfolio/:id/old" element={<MindfolioDetail />} />
 <Route path="/mindfolio/:id/legacy" element={<MindfolioDetailNew />} />
 <Route path="/mindfolio/:id" element={<MindfolioDetailNewV2 />} />
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
