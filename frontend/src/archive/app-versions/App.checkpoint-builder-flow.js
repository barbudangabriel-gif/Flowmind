// App.js - Step 4: Add Header with Logo + Sidebar Toggle
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Menu } from 'lucide-react';
import SidebarSimple from './components/SidebarSimple';
import BuilderPage from './pages/BuilderPage';
import FlowPage from './pages/FlowPage';

function HomePage() {
 return (
 <div className="p-8">
 <h2 className="text-3xl font-medium text-[rgb(252, 251, 255)] mb-4">Dashboard</h2>
 <p className="text-slate-300">Welcome to FlowMind Options Analytics</p>
 <div className="mt-6 grid grid-cols-3 gap-4">
 <div className="bg-slate-800 p-6 rounded-lg">
 <p className="text-slate-400 text-xl">Total P&L</p>
 <p className="text-2xl font-medium text-emerald-400">+$12,450</p>
 </div>
 <div className="bg-slate-800 p-6 rounded-lg">
 <p className="text-slate-400 text-xl">Open Positions</p>
 <p className="text-2xl font-medium text-[rgb(252, 251, 255)]">8</p>
 </div>
 <div className="bg-slate-800 p-6 rounded-lg">
 <p className="text-slate-400 text-xl">Win Rate</p>
 <p className="text-2xl font-medium text-blue-400">68%</p>
 </div>
 </div>
 </div>
 );
}

function ComingSoonPage() {
 const location = window.location.pathname;
 return (
 <div className="p-8">
 <h2 className="text-3xl font-medium text-[rgb(252, 251, 255)] mb-4">Coming Soon</h2>
 <div className="bg-slate-800 p-6 rounded-lg">
 <p className="text-slate-300 mb-2">This feature is under development.</p>
 <p className="text-lg text-slate-500">Route: {location}</p>
 </div>
 </div>
 );
}

function App() {
 const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
 
 // Simple context for sidebar
 const ctx = {
 role: "user",
 flags: {},
 metrics: {},
 mindfolios: []
 };

 return (
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
 <div className="flex items-center gap-3 text-[rgb(252, 251, 255)] transform translate-y-1">
 <img 
 src="/assets/logos/flowmind_horizontal_white.svg" 
 alt="FlowMind Analytics" 
 className="h-14 w-auto"
 />
 </div>

 {/* Spacer */}
 <div className="flex-1"></div>

 {/* Right side */}
 <div className="flex items-center gap-4">
 <span className="text-xl text-[#94a3b8]">Welcome back</span>
 </div>
 </header>

 {/* Main Content */}
 <main className="flex-1 overflow-y-auto bg-[#0a0e1a]">
 <Routes>
 <Route path="/" element={<HomePage />} />
 <Route path="/dashboard" element={<HomePage />} />
 <Route path="/builder" element={<BuilderPage />} />
 <Route path="/builder/:strategySlug" element={<BuilderPage />} />
 <Route path="/flow" element={<FlowPage />} />
 <Route path="/flow/live" element={<FlowPage />} />
 {/* Catch-all for all other routes */}
 <Route path="*" element={<ComingSoonPage />} />
 </Routes>
 </main>
 </div>
 </div>
 </BrowserRouter>
 );
}

export default App;
