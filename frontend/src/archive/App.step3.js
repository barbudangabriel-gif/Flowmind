// App.js - Step 3: Add Sidebar
import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import SidebarSimple from './components/SidebarSimple';

function HomePage() {
  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold text-white mb-4">Dashboard</h2>
      <p className="text-slate-300">Welcome to FlowMind Options Analytics</p>
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-slate-400 text-sm">Total P&L</p>
          <p className="text-2xl font-bold text-emerald-400">+$12,450</p>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-slate-400 text-sm">Open Positions</p>
          <p className="text-2xl font-bold text-white">8</p>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-slate-400 text-sm">Win Rate</p>
          <p className="text-2xl font-bold text-blue-400">68%</p>
        </div>
      </div>
    </div>
  );
}

function BuilderPage() {
  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold text-white mb-4">Options Builder</h2>
      <div className="bg-slate-800 p-6 rounded-lg">
        <p className="text-slate-300">Strategy builder interface coming soon...</p>
      </div>
    </div>
  );
}

function App() {
  // Simple context for sidebar
  const ctx = {
    role: "user",
    flags: {},
    metrics: {},
    portfolios: []
  };

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-slate-900">
        {/* Sidebar */}
        <SidebarSimple ctx={ctx} />
        
        {/* Main content */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<HomePage />} />
            <Route path="/builder" element={<BuilderPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
