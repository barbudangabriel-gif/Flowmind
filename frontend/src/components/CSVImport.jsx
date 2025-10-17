import React, { useState } from 'react';
import { pfClient } from '../services/portfolioClient';

export default function CSVImport({ portfolioId, onImportComplete }) {
 const [csvData, setCsvData] = useState('');
 const [importing, setImporting] = useState(false);
 const [result, setResult] = useState(null);
 const [error, setError] = useState(null);

 const exampleCSV = `datetime,symbol,side,qty,price,fee,currency,notes
2024-01-15T09:30:00Z,AAPL,BUY,100,185.50,1.50,USD,Opening position
2024-01-20T14:15:00Z,AAPL,SELL,50,190.25,0.75,USD,Taking partial profit
2024-02-01T10:00:00Z,MSFT,BUY,75,410.80,2.25,USD,Tech diversification`;

 const handleImport = async () => {
 if (!csvData.trim()) {
 setError('Please enter CSV data');
 return;
 }

 setImporting(true);
 setError(null);
 setResult(null);

 try {
 const response = await pfClient.importCSV(portfolioId, csvData.trim());
 setResult(response);
 setCsvData('');
 
 // Notify parent component to refresh data
 if (onImportComplete) {
 onImportComplete(response);
 }
 } catch (e) {
 setError(e.message);
 } finally {
 setImporting(false);
 }
 };

 const loadExample = () => {
 setCsvData(exampleCSV);
 setError(null);
 setResult(null);
 };

 return (
 <div className="bg-white rounded-lg shadow-sm p-6">
 <div className="mb-4">
 <h3 className="text-3xl font-medium text-gray-900 mb-2">Import Transactions from CSV</h3>
 <p className="text-xl text-gray-600 mb-4">
 Upload transaction data in CSV format. Required columns: datetime, symbol, side, qty, price
 </p>
 </div>

 {/* CSV Input */}
 <div className="mb-4">
 <label className="block text-xl font-medium text-gray-700 mb-2">
 CSV Data
 </label>
 <textarea
 className="w-full h-40 p-3 border border-gray-300 rounded-md font-mono text-xl"
 placeholder="Paste your CSV data here or click 'Load Example' to see the format..."
 value={csvData}
 onChange={(e) => setCsvData(e.target.value)}
 />
 </div>

 {/* Controls */}
 <div className="flex items-center gap-3 mb-4">
 <button
 onClick={handleImport}
 disabled={importing || !csvData.trim()}
 className="px-4 py-2 bg-blue-600 text-[rgb(252, 251, 255)] rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
 >
 {importing ? 'Importing...' : 'Import Transactions'}
 </button>
 
 <button
 onClick={loadExample}
 className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
 >
 Load Example
 </button>
 
 <button
 onClick={() => {
 setCsvData('');
 setError(null);
 setResult(null);
 }}
 className="px-4 py-2 text-gray-600 hover:text-gray-800"
 >
 Clear
 </button>
 </div>

 {/* Results */}
 {result && (
 <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
 <div className="text-green-800 font-medium">Import Successful!</div>
 <div className="text-green-700 text-xl mt-1">
 {result.message} ({result.imported} transactions)
 </div>
 </div>
 )}

 {error && (
 <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
 <div className="text-red-800 font-medium">Import Failed</div>
 <div className="text-red-700 text-xl mt-1">{error}</div>
 </div>
 )}

 {/* CSV Format Help */}
 <div className="border-t border-gray-200 pt-4">
 <h4 className="text-xl font-medium text-gray-700 mb-2">CSV Format Requirements:</h4>
 <div className="text-xl text-gray-600 space-y-1">
 <div><strong>Required columns:</strong></div>
 <ul className="ml-4 space-y-1 text-lg">
 <li>• <code className="bg-gray-100 px-1 rounded">datetime</code> - ISO format (YYYY-MM-DDTHH:MM:SSZ)</li>
 <li>• <code className="bg-gray-100 px-1 rounded">symbol</code> - Stock/asset symbol (e.g., AAPL, MSFT)</li>
 <li>• <code className="bg-gray-100 px-1 rounded">side</code> - BUY or SELL</li>
 <li>• <code className="bg-gray-100 px-1 rounded">qty</code> - Quantity (number of shares)</li>
 <li>• <code className="bg-gray-100 px-1 rounded">price</code> - Price per share</li>
 </ul>
 <div className="mt-2"><strong>Optional columns:</strong></div>
 <ul className="ml-4 space-y-1 text-lg">
 <li>• <code className="bg-gray-100 px-1 rounded">fee</code> - Transaction fee (default: 0)</li>
 <li>• <code className="bg-gray-100 px-1 rounded">currency</code> - Currency code (default: USD)</li>
 <li>• <code className="bg-gray-100 px-1 rounded">notes</code> - Additional notes</li>
 <li>• <code className="bg-gray-100 px-1 rounded">account_id</code> - Account identifier</li>
 </ul>
 </div>
 </div>
 </div>
 );
}