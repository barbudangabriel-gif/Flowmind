import React, { useState } from "react";
import { mfClient } from "../services/mindfolioClient";
import { useNavigate, Link } from "react-router-dom";

export default function MindfolioCreate() {
 const navigate = useNavigate();
 const [name, setName] = useState("");
 const [balance, setBalance] = useState(10000);
 const [err, setErr] = useState("");
 const [creating, setCreating] = useState(false);

 const onSubmit = async (e) => {
 e.preventDefault();
 if (!name.trim() || creating) return;

 setCreating(true);
 setErr("");
 
 try {
 console.log('Creating mindfolio with:', { name: name.trim(), starting_balance: Number(balance), modules: [] });
 const mindfolio = await mfClient.create({
 name: name.trim(),
 starting_balance: Number(balance),
 modules: []
 });
 console.log('Created mindfolio:', mindfolio);
 // Navigate to mindfolio list instead of detail page
 navigate('/mindfolio');
 } catch (ex) {
 console.error('Creation error:', ex);
 setErr(String(ex));
 } finally {
 setCreating(false);
 }
 };

 return (
 <div className="min-h-screen bg-gray-950 p-8">
 <div className="max-w-2xl mx-auto">
 <div className="mb-8">
 <div className="flex items-center gap-3 mb-4">
 <Link 
 to="/mindfolio" 
 className="text-blue-400 hover:text-blue-300 transition-colors font-semibold"
 >
 ← Back to Mindfolios
 </Link>
 </div>
 <h1 className="text-3xl font-bold text-white mb-2">Create New Mindfolio</h1>
 <p className="text-gray-400">
 Set up a new mindfolio to track your trading strategies and performance
 </p>
 </div>

 {err && (
 <div className="mb-6 bg-red-900/20 border border-red-700/40 rounded-lg p-4">
 <div className="flex items-start gap-3">
 <span className="text-xl"></span>
 <div>
 <div className="font-semibold text-red-400 mb-1">Creation Failed</div>
 <div className="text-sm text-gray-400">{err}</div>
 </div>
 </div>
 </div>
 )}

 <form onSubmit={onSubmit} className="space-y-4 bg-gray-900 border border-gray-800 rounded-lg p-6 shadow-xl">
 <div>
 <label className="text-sm font-medium text-gray-300 mb-1 block">
 Mindfolio Name
 </label>
 <input
 type="text"
 value={name}
 onChange={e => setName(e.target.value)}
 placeholder="e.g. My Options Strategy"
 className="w-full border border-gray-700 bg-gray-800 text-white rounded-md px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
 required
 />
 </div>

 <div>
 <label className="text-sm font-medium text-gray-300 mb-1 block">
 Starting Balance (USD)
 </label>
 <input
 type="number"
 step="0.01"
 min="0"
 value={balance}
 onChange={e => setBalance(Number(e.target.value))}
 className="w-full border border-gray-700 bg-gray-800 text-white rounded-md px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
 />
 <div className="text-xs text-gray-500 mt-1">
 This will be your initial cash balance for trading
 </div>
 </div>

 <div className="pt-4 space-y-3">
 <button
 type="submit"
 disabled={!name.trim() || creating}
 className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors"
 >
 {creating ? "Creating..." : "Create Mindfolio"}
 </button>
 
 <Link
 to="/mindfolio"
 className="w-full px-4 py-2 border border-gray-700 text-gray-300 rounded-md hover:bg-gray-800 transition-colors text-center block"
 >
 Cancel
 </Link>
 </div>
 </form>
 </div>
 </div>
 );
}