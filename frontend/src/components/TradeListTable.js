import React from 'react';

const TradeListTable = ({ activeFilter }) => {
 // Mock trade data based on filter
 const getTrades = () => {
 const allTrades = [
 {
 id: 1,
 symbol: 'AAPL',
 type: 'Stock',
 status: 'Open',
 quantity: 100,
 entryPrice: 185.50,
 currentPrice: 189.25,
 pnl: 375.00,
 pnlPercent: 2.02,
 date: '2024-12-20',
 typeColor: 'green',
 statusColor: 'blue'
 },
 {
 id: 2,
 symbol: 'TSLA',
 type: 'Call',
 status: 'Open', 
 quantity: 10,
 entryPrice: 12.50,
 currentPrice: 8.75,
 pnl: -3750.00,
 pnlPercent: -30.00,
 date: '2024-12-15',
 typeColor: 'blue',
 statusColor: 'blue'
 },
 {
 id: 3,
 symbol: 'MSFT',
 type: 'Stock',
 status: 'Closed',
 quantity: 50,
 entryPrice: 385.20,
 currentPrice: 392.45,
 pnl: 362.50,
 pnlPercent: 1.88,
 date: '2024-12-18',
 typeColor: 'green',
 statusColor: 'gray'
 },
 {
 id: 4,
 symbol: 'SPY',
 type: 'Put',
 status: 'Open',
 quantity: 5,
 entryPrice: 4.25,
 currentPrice: 2.10,
 pnl: -1075.00,
 pnlPercent: -50.59,
 date: '2024-12-10',
 typeColor: 'orange',
 statusColor: 'blue'
 },
 {
 id: 5,
 symbol: 'NVDA',
 type: 'Stock',
 status: 'Closed',
 quantity: 25,
 entryPrice: 495.80,
 currentPrice: 512.30,
 pnl: 412.50,
 pnlPercent: 3.33,
 date: '2024-12-12',
 typeColor: 'green',
 statusColor: 'gray'
 }
 ];

 // Filter based on activeFilter
 if (activeFilter === 'open') {
 return allTrades.filter(trade => trade.status === 'Open');
 } else if (activeFilter === 'closed') {
 return allTrades.filter(trade => trade.status === 'Closed');
 } else {
 return allTrades; // all/combined
 }
 };

 const trades = getTrades();

 const getTypeColor = (color) => {
 const colors = {
 green: 'bg-green-100 text-green-800',
 blue: 'bg-blue-100 text-blue-800', 
 orange: 'bg-orange-100 text-orange-800'
 };
 return colors[color] || 'bg-gray-100 text-gray-800';
 };

 const getStatusColor = (color) => {
 const colors = {
 blue: 'bg-blue-100 text-blue-800',
 gray: 'bg-gray-100 text-gray-800'
 };
 return colors[color] || 'bg-gray-100 text-gray-800';
 };

 return (
 <div className="bg-white rounded-xl p-6 shadow-sm">
 <div className="flex items-center justify-between mb-6">
 <h2 className="text-xl font-medium text-gray-900">Trade List</h2>
 <div className="text-xl text-gray-600">
 {activeFilter === 'open' ? 'Open Positions' : 
 activeFilter === 'closed' ? 'Closed Positions' : 
 'All Trades'} ({trades.length} {trades.length === 1 ? 'trade' : 'trades'})
 </div>
 </div>
 
 {/* Trade List Table */}
 <div className="overflow-x-auto">
 <table className="w-full">
 <thead>
 <tr className="border-b border-gray-200">
 <th className="text-left py-3 px-4 font-medium text-gray-700">Symbol</th>
 <th className="text-left py-3 px-4 font-medium text-gray-700">Type</th>
 <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
 <th className="text-right py-3 px-4 font-medium text-gray-700">Quantity</th>
 <th className="text-right py-3 px-4 font-medium text-gray-700">Entry Price</th>
 <th className="text-right py-3 px-4 font-medium text-gray-700">Current Price</th>
 <th className="text-right py-3 px-4 font-medium text-gray-700">P&L</th>
 <th className="text-right py-3 px-4 font-medium text-gray-700">P&L %</th>
 <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
 </tr>
 </thead>
 <tbody>
 {trades.map((trade) => (
 <tr key={trade.id} className="border-b border-gray-100 hover:bg-gray-50">
 <td className="py-3 px-4 font-medium">{trade.symbol}</td>
 <td className="py-3 px-4">
 <span className={`inline-block text-lg px-2 py-1 rounded ${getTypeColor(trade.typeColor)}`}>
 {trade.type}
 </span>
 </td>
 <td className="py-3 px-4">
 <span className={`inline-block text-lg px-2 py-1 rounded ${getStatusColor(trade.statusColor)}`}>
 {trade.status}
 </span>
 </td>
 <td className="py-3 px-4 text-right">{trade.quantity}</td>
 <td className="py-3 px-4 text-right">${trade.entryPrice.toFixed(2)}</td>
 <td className="py-3 px-4 text-right">${trade.currentPrice.toFixed(2)}</td>
 <td className={`py-3 px-4 text-right ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
 {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
 </td>
 <td className={`py-3 px-4 text-right ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
 {trade.pnlPercent >= 0 ? '+' : ''}{trade.pnlPercent.toFixed(2)}%
 </td>
 <td className="py-3 px-4">{trade.date}</td>
 </tr>
 ))}
 </tbody>
 </table>
 
 {trades.length === 0 && (
 <div className="text-center py-8 text-gray-500">
 <p>No trades found for the selected filter.</p>
 </div>
 )}
 </div>

 {/* Summary Stats */}
 <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
 <div className="bg-green-50 p-4 rounded-lg">
 <div className="text-xl text-green-700 font-medium">Total Profit</div>
 <div className="text-3xl font-medium text-green-900">
 +${trades.filter(t => t.pnl > 0).reduce((sum, t) => sum + t.pnl, 0).toFixed(2)}
 </div>
 </div>
 
 <div className="bg-red-50 p-4 rounded-lg">
 <div className="text-xl text-red-700 font-medium">Total Loss</div>
 <div className="text-3xl font-medium text-red-900">
 ${trades.filter(t => t.pnl < 0).reduce((sum, t) => sum + Math.abs(t.pnl), 0).toFixed(2)}
 </div>
 </div>
 
 <div className="bg-blue-50 p-4 rounded-lg">
 <div className="text-xl text-blue-700 font-medium">Net P&L</div>
 <div className={`text-3xl font-medium ${trades.reduce((sum, t) => sum + t.pnl, 0) >= 0 ? 'text-green-900' : 'text-red-900'}`}>
 {trades.reduce((sum, t) => sum + t.pnl, 0) >= 0 ? '+' : ''}${trades.reduce((sum, t) => sum + t.pnl, 0).toFixed(2)}
 </div>
 </div>
 </div>
 </div>
 );
};

export default TradeListTable;