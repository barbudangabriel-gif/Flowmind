import React, { Suspense } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import FlowMindSidebar from './FlowMindSidebar';
import { useNavContext } from '../hooks/useNavContext';

// Import existing components for routes
const ChartProTSLive = React.lazy(() => import("./ChartProTSLive"));
const ScreenerV2 = React.lazy(() => import("../features/iv/ScreenerV2"));
const OptionsModule = React.lazy(() => import("./OptionsModule"));
const SmartRebalancingAgent = React.lazy(() => import("./SmartRebalancingAgent"));

// Import Portfolio components
const PortfoliosList = React.lazy(() => import("../pages/PortfoliosList"));
const PortfolioDetail = React.lazy(() => import("../pages/PortfolioDetail"));
const PortfolioCreate = React.lazy(() => import("../pages/PortfolioCreate"));

// Loading fallback
const LoadingFallback = ({ componentName }) => (
 <div className="flex items-center justify-center h-64">
 <div className="text-center">
 <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
 <p className="mt-2 text-xl text-gray-600">Loading {componentName}...</p>
 </div>
 </div>
);

// Route mapping for compatibility with new nav structure
const RouteMapping = () => {
 return (
 <Routes>
 {/* Overview */}
 <Route path="/dashboard" element={
 <Suspense fallback={<LoadingFallback componentName="Dashboard" />}>
 <ChartProTSLive />
 </Suspense>
 } />
 <Route path="/" element={
 <Suspense fallback={<LoadingFallback componentName="Dashboard" />}>
 <ChartProTSLive />
 </Suspense>
 } />

 {/* Account & Portfolios */}
 <Route path="/account/balance" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Account Balance</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Account balance interface coming soon...</p>
 </div>
 </div>
 } />
 
 {/* Portfolios Routes */}
 <Route path="/portfolios" element={
 <Suspense fallback={<LoadingFallback componentName="Portfolios List" />}>
 <PortfoliosList />
 </Suspense>
 } />
 
 <Route path="/portfolios/new" element={
 <Suspense fallback={<LoadingFallback componentName="Create Portfolio" />}>
 <PortfolioCreate />
 </Suspense>
 } />
 
 <Route path="/portfolios/:id" element={
 <Suspense fallback={<LoadingFallback componentName="Portfolio Details" />}>
 <PortfolioDetail />
 </Suspense>
 } />
 
 {/* Legacy portfolio route */}
 <Route path="/portfolios/ts-main" element={
 <Suspense fallback={<LoadingFallback componentName="TS Main Portfolio" />}>
 <ChartProTSLive />
 </Suspense>
 } />

 {/* Stocks */}
 <Route path="/stocks/scoring" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Investment Scoring</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Investment scoring interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/stocks/scanner" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Scoring Scanner</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Stock scanner interface coming soon...</p>
 </div>
 </div>
 } />

 {/* Options */}
 <Route path="/screener/iv" element={
 <Suspense fallback={<LoadingFallback componentName="IV Screener" />}>
 <ScreenerV2 />
 </Suspense>
 } />
 
 <Route path="/screener/sell-puts" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Sell Puts (Auto)</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Redirecting to existing sell puts interface...</p>
 <button 
 onClick={() => window.location.href = '/options/selling'}
 className="mt-4 px-4 py-2 bg-blue-600 text-[rgb(252, 251, 255)] rounded hover:bg-blue-700"
 >
 Go to Sell Puts Interface
 </button>
 </div>
 </div>
 } />
 
 <Route path="/builder/new" element={
 <Suspense fallback={<LoadingFallback componentName="Options Builder" />}>
 <OptionsModule />
 </Suspense>
 } />

 {/* Trades */}
 <Route path="/trades/preview" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Preview Queue</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Trade preview queue coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/trades/orders/sim" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Orders (SIM)</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Simulation orders interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/trades/orders/live" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Orders (Live)</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Live orders interface coming soon...</p>
 </div>
 </div>
 } />

 {/* Analytics */}
 <Route path="/analytics/backtests" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Backtests</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Backtests interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/analytics/verified" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Verified Chains</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Verified chains interface coming soon...</p>
 </div>
 </div>
 } />

 {/* Data Providers */}
 <Route path="/providers/ts" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">TradeStation</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>TradeStation provider interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/md/quotes" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Market Quotes</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Real-time quotes interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/md/chain" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Option Chain</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Option chain interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/providers/uw" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Unusual Whales</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Unusual Whales provider interface coming soon...</p>
 </div>
 </div>
 } />

 {/* Ops / Diagnostics */}
 <Route path="/ops/redis" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Redis Diagnostics</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Redis diagnostics interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/ops/bt" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Backtest Ops</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Backtest operations interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/ops/emergent" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Emergent Status</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Emergent status interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/ops/warmup" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Cache Warm-up</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Cache warm-up interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/ops/ratelimits" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Rate Limits</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Rate limits interface coming soon...</p>
 </div>
 </div>
 } />

 {/* Settings */}
 <Route path="/settings/gates" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Risk & Gates</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Risk gates configuration coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/settings/accounts" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Account Settings</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Account settings interface coming soon...</p>
 </div>
 </div>
 } />
 
 <Route path="/settings/keys" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">API Keys</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>API keys management coming soon...</p>
 </div>
 </div>
 } />

 {/* Help */}
 <Route path="/help/docs" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Documentation</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>Documentation coming soon...</p>
 </div>
 </div>
 } />

 {/* Legacy routes for compatibility */}
 <Route path="/options/selling" element={
 <div className="p-6">
 <h2 className="text-2xl font-medium mb-4">Legacy: Options Selling</h2>
 <div className="bg-white rounded-lg p-6 shadow-sm">
 <p>This route exists in the legacy system. Please use the new navigation.</p>
 </div>
 </div>
 } />
 
 <Route path="/iv/screener" element={
 <Suspense fallback={<LoadingFallback componentName="IV Screener" />}>
 <ScreenerV2 />
 </Suspense>
 } />

 {/* Catch all - redirect to dashboard */}
 <Route path="*" element={
 <Suspense fallback={<LoadingFallback componentName="Dashboard" />}>
 <ChartProTSLive />
 </Suspense>
 } />
 </Routes>
 );
};

export default function AppWithFlowMindSidebar() {
 const { ctx, loading } = useNavContext();

 if (loading) {
 return (
 <div className="flex items-center justify-center h-screen">
 <div className="text-center">
 <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
 <p className="mt-4 text-gray-600">Loading FlowMind...</p>
 </div>
 </div>
 );
 }

 return (
 <div className="flex h-screen bg-gray-50">
 <FlowMindSidebar ctx={ctx} />
 <main className="flex-1 overflow-y-auto">
 <div className="container mx-auto p-6">
 <RouteMapping />
 </div>
 </main>
 </div>
 );
}