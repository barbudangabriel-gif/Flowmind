// App.js - Step 2: Add React Router
import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

function HomePage() {
  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold text-white mb-4">Home Page</h2>
      <p className="text-slate-300">Welcome to FlowMind Options Analytics</p>
    </div>
  );
}

function BuilderPage() {
  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold text-white mb-4">Builder</h2>
      <p className="text-slate-300">Options strategy builder will go here</p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-900">
        {/* Simple Nav */}
        <nav className="bg-slate-800 border-b border-slate-700 px-6 py-4">
          <div className="flex items-center gap-6">
            <h1 className="text-xl font-bold text-white">FlowMind</h1>
            <Link to="/" className="text-slate-300 hover:text-white px-3 py-2">Home</Link>
            <Link to="/builder" className="text-slate-300 hover:text-white px-3 py-2">Builder</Link>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/builder" element={<BuilderPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
