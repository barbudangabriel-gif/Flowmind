import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, Search, Plus, Check } from 'lucide-react';

const AddSymbolsToPortfolio = () => {
 const navigate = useNavigate();
 const [searchTerm, setSearchTerm] = useState('');
 const [searchResults, setSearchResults] = useState([]);
 const [selectedSymbols, setSelectedSymbols] = useState([]);
 const [bulkSymbols, setBulkSymbols] = useState('');
 const [isSearching, setIsSearching] = useState(false);
 const [showBulkEntry, setShowBulkEntry] = useState(false);

 // Mock symbol data - în realitate ar veni de la API
 const mockSymbolData = {
 'tsl': [
 { symbol: 'TSL', name: 'GraniteShares 1.25x Long Tesla Daily ETF', type: 'ETF' },
 { symbol: 'TSLA', name: 'Tesla, Inc.', type: 'Stock' },
 { symbol: 'TSLY', name: 'YieldMax TSLA Option Income Strategy ETF', type: 'ETF' },
 { symbol: 'TSLX', name: 'Sixth Street Specialty Lending, Inc.', type: 'Stock' },
 { symbol: 'TSLL', name: 'Direxion Daily TSLA Bull 2X Shares ETF', type: 'ETF' },
 { symbol: 'TSLQ', name: 'Tradr 2X Short TSLA Daily ETF', type: 'ETF' },
 { symbol: 'TSLS', name: 'Direxion Daily TSLA Bear 1X Shares ETF', type: 'ETF' },
 { symbol: 'TSLA:CA', name: 'Tesla, Inc.', type: 'Stock' },
 { symbol: 'TSLP', name: 'Kurv Yield Premium Strategy Tesla ETF', type: 'ETF' },
 { symbol: 'TSLT', name: 'T-Rex 2X Long Tesla Daily Target ETF', type: 'ETF' },
 { symbol: 'TSLAX', name: 'Transamerica Small Cap Value A', type: 'Fund' },
 { symbol: 'TSLR', name: 'GraniteShares 2x Long TSLA Daily ETF', type: 'ETF' }
 ],
 'aapl': [
 { symbol: 'AAPL', name: 'Apple Inc.', type: 'Stock' },
 { symbol: 'AAPL:CA', name: 'Apple Inc.', type: 'Stock' },
 { symbol: 'APLY', name: 'YieldMax AAPL Option Income Strategy ETF', type: 'ETF' },
 { symbol: 'AAPU', name: 'Direxion Daily AAPL Bull 2X Shares ETF', type: 'ETF' },
 { symbol: 'AAPB', name: 'GraniteShares 2x Long AAPL Daily ETF', type: 'ETF' },
 { symbol: 'AAPD', name: 'Direxion Daily AAPL Bear 1X Shares ETF', type: 'ETF' },
 { symbol: 'AAPW', name: 'Roundhill AAPL WeeklyPay ETF', type: 'ETF' },
 { symbol: 'APLY:CA', name: 'Apple (AAPL) Yield Shares Purpose ETF', type: 'ETF' },
 { symbol: 'AAPD.E', name: 'Direxion Daily AAPL Bear 1X Shares ETF Estimated', type: 'ETF' },
 { symbol: 'AAPU.IV', name: 'Direxion Daily AAPL Bull 1.5X Shares ETF Intraday', type: 'ETF' },
 { symbol: 'AAPD.IV', name: 'Direxion Daily AAPL Bear 1X Shares ETF Intraday', type: 'ETF' },
 { symbol: 'AAPD.N', name: 'Direxion Daily AAPL Bear 1X Shares ETF NAV', type: 'ETF' }
 ],
 'msft': [
 { symbol: 'MSFT', name: 'Microsoft Corporation', type: 'Stock' },
 { symbol: 'MSFT:CA', name: 'Microsoft Corporation', type: 'Stock' },
 ],
 'googl': [
 { symbol: 'GOOGL', name: 'Alphabet Inc. Class A', type: 'Stock' },
 { symbol: 'GOOG', name: 'Alphabet Inc. Class C', type: 'Stock' },
 ]
 };

 // Search pentru simboluri
 const handleSearch = (term) => {
 setSearchTerm(term);
 if (term.length >= 2) {
 setIsSearching(true);
 
 // Simulăm API call cu timeout
 setTimeout(() => {
 const searchKey = term.toLowerCase();
 const results = mockSymbolData[searchKey] || [];
 setSearchResults(results);
 setIsSearching(false);
 }, 300);
 } else {
 setSearchResults([]);
 }
 };

 const handleSymbolClick = (symbol) => {
 if (!selectedSymbols.find(s => s.symbol === symbol.symbol)) {
 setSelectedSymbols(prev => [...prev, symbol]);
 }
 setSearchTerm('');
 setSearchResults([]);
 };

 const removeSymbol = (symbolToRemove) => {
 setSelectedSymbols(prev => prev.filter(s => s.symbol !== symbolToRemove.symbol));
 };

 const handleBulkEntry = () => {
 setShowBulkEntry(true);
 };

 const handleNext = () => {
 // Process bulk symbols
 if (bulkSymbols.trim()) {
 const symbols = bulkSymbols.split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
 const newSymbols = symbols.map(symbol => ({
 symbol,
 name: `${symbol} Company`,
 type: 'Stock'
 }));
 setSelectedSymbols(prev => [...prev, ...newSymbols]);
 }
 
 // Navigate to next step with selected symbols
 navigate('/portfolios/create/manual/quantities', { 
 state: { symbols: selectedSymbols } 
 });
 };

 if (showBulkEntry) {
 return (
 <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
 <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl relative">
 
 {/* Header */}
 <div className="flex items-center justify-between p-8 pb-4">
 <h1 className="text-2xl font-medium text-gray-800">Add Symbols to Follow</h1>
 <button
 onClick={() => navigate('/portfolios/create')}
 className="text-2xl font-medium text-gray-600 hover:text-gray-800 transition-colors"
 >
 Cancel
 </button>
 </div>

 {/* Content */}
 <div className="px-8 pb-8">
 
 {/* Bulk Entry Input */}
 <div className="mb-6">
 <div className="relative">
 <input
 type="text"
 value={bulkSymbols}
 onChange={(e) => setBulkSymbols(e.target.value)}
 placeholder="Add symbols (e.g AAPL, GOOGL, etc...)"
 className="w-full px-6 py-4 text-3xl border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none pr-12"
 />
 <Search className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
 </div>
 </div>

 <p className="text-gray-600 mb-8">
 Enter symbols separated by commas to add to your portfolio.
 </p>

 {/* Selected Symbols Display */}
 {selectedSymbols.length > 0 && (
 <div className="mb-6">
 <h3 className="text-3xl font-medium text-gray-800 mb-3">Selected Symbols ({selectedSymbols.length})</h3>
 <div className="flex flex-wrap gap-2">
 {selectedSymbols.map((symbol, index) => (
 <div key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full flex items-center">
 <span className="font-medium">{symbol.symbol}</span>
 <button
 onClick={() => removeSymbol(symbol)}
 className="ml-2 hover:text-red-600"
 >
 <X size={14} />
 </button>
 </div>
 ))}
 </div>
 </div>
 )}

 {/* Action Buttons */}
 <div className="flex space-x-4">
 <button
 onClick={() => setShowBulkEntry(false)}
 className="flex-1 py-3 px-6 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
 >
 Back to Search
 </button>
 <button
 onClick={handleNext}
 className="flex-1 py-4 px-6 bg-gray-600 text-[rgb(252, 251, 255)] rounded-xl hover:bg-gray-700 transition-colors font-medium"
 >
 Next
 </button>
 </div>
 </div>
 </div>

 <div className="fixed inset-0 bg-black bg-opacity-50 -z-10"></div>
 </div>
 );
 }

 return (
 <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
 {/* Modal Container */}
 <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl relative max-h-[90vh] flex flex-col">
 
 {/* Header */}
 <div className="flex items-center justify-between p-8 pb-4 flex-shrink-0">
 <h1 className="text-2xl font-medium text-gray-800">Add Symbols to Follow</h1>
 <button
 onClick={() => navigate('/portfolios/create')}
 className="text-2xl font-medium text-gray-600 hover:text-gray-800 transition-colors"
 >
 Cancel
 </button>
 </div>

 {/* Content */}
 <div className="px-8 pb-8 flex-1 flex flex-col">
 
 {/* Search Input */}
 <div className="mb-6 flex-shrink-0">
 <div className="relative">
 <input
 type="text"
 value={searchTerm}
 onChange={(e) => handleSearch(e.target.value)}
 placeholder="Enter symbol to search..."
 className="w-full px-6 py-4 text-3xl border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none pr-12"
 />
 <button className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400">
 <X size={20} />
 </button>
 </div>
 </div>

 {/* Results Section */}
 <div className="flex-1 overflow-hidden flex flex-col">
 {searchResults.length > 0 && (
 <>
 <h3 className="text-3xl font-medium text-gray-700 mb-4 flex-shrink-0">Results:</h3>
 
 <div className="flex-1 overflow-y-auto border border-gray-200 rounded-xl">
 {searchResults.map((result, index) => (
 <button
 key={index}
 onClick={() => handleSymbolClick(result)}
 className="w-full px-6 py-4 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition-colors text-left flex items-center justify-between"
 >
 <div>
 <div className="font-medium text-gray-800 text-3xl">{result.symbol}</div>
 <div className="text-gray-600 text-xl">{result.name}</div>
 </div>
 {selectedSymbols.find(s => s.symbol === result.symbol) && (
 <Check className="text-green-500" size={20} />
 )}
 </button>
 ))}
 </div>
 </>
 )}

 {/* Selected Symbols */}
 {selectedSymbols.length > 0 && (
 <div className="mt-6 flex-shrink-0">
 <h3 className="text-3xl font-medium text-gray-800 mb-3">Selected Symbols ({selectedSymbols.length})</h3>
 <div className="flex flex-wrap gap-2 mb-4">
 {selectedSymbols.map((symbol, index) => (
 <div key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full flex items-center">
 <span className="font-medium">{symbol.symbol}</span>
 <button
 onClick={() => removeSymbol(symbol)}
 className="ml-2 hover:text-red-600"
 >
 <X size={14} />
 </button>
 </div>
 ))}
 </div>
 </div>
 )}
 </div>

 {/* Action Buttons */}
 <div className="flex-shrink-0 mt-6">
 <div className="flex space-x-4">
 <button
 onClick={handleBulkEntry}
 className="flex-1 py-3 px-6 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
 >
 Bulk Entry
 </button>
 <button
 onClick={handleNext}
 disabled={selectedSymbols.length === 0}
 className="flex-1 py-3 px-6 bg-blue-600 text-[rgb(252, 251, 255)] rounded-xl hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
 >
 Next ({selectedSymbols.length})
 </button>
 </div>
 </div>
 </div>
 </div>

 {/* Background Overlay */}
 <div className="fixed inset-0 bg-black bg-opacity-50 -z-10"></div>
 </div>
 );
};

export default AddSymbolsToPortfolio;