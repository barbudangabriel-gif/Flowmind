import React from 'react';
import { toBuilderLink } from '../lib/flowApi';

export default function FlowTable({ items }) {
 if (!items || items.length === 0) {
 return (
 <div className="bg-white rounded-2xl shadow p-8">
 <div className="text-center text-gray-500">
 No flow data available
 </div>
 </div>
 );
 }

 return (
 <div className="bg-white rounded-2xl shadow overflow-hidden">
 <div className="overflow-x-auto">
 <table className="min-w-full divide-y divide-gray-200">
 <thead className="bg-gray-50">
 <tr>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Side</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Kind</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Strike</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Expiry</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Premium</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">IV</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">DTE</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Type</th>
 <th className="px-3 py-3 text-left text-lg font-medium text-gray-500 uppercase tracking-wider">Actions</th>
 </tr>
 </thead>
 <tbody className="bg-white divide-y divide-gray-200">
 {items.map((row, index) => (
 <tr key={index} className="hover:bg-gray-50">
 <td className="px-3 py-4 whitespace-nowrap text-xl font-medium text-gray-900">
 {row.symbol}
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-500">
 <span className={`px-2 py-1 rounded text-lg font-medium ${
 row.side === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
 }`}>
 {row.side}
 </span>
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-500">
 {row.kind}
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-500">
 ${row.strike}
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-500">
 {row.expiry}
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-900">
 ${(row.premium || 0).toLocaleString()}
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-500">
 {row.iv ? `${(row.iv * 100).toFixed(1)}%` : '-'}
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-500">
 {row.dte || '-'}
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-500">
 <div className="flex gap-1">
 {row.is_sweep && (
 <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-lg rounded">
 Sweep
 </span>
 )}
 {row.is_block && (
 <span className="px-2 py-0.5 bg-purple-100 text-purple-800 text-lg rounded">
 Block
 </span>
 )}
 </div>
 </td>
 <td className="px-3 py-4 whitespace-nowrap text-xl text-gray-500">
 <a 
 href={toBuilderLink(row)} 
 className="text-indigo-600 hover:text-indigo-900 hover:underline font-medium"
 target="_blank"
 rel="noopener noreferrer"
 >
 Open in Builder
 </a>
 </td>
 </tr>
 ))}
 </tbody>
 </table>
 </div>
 </div>
 );
}
