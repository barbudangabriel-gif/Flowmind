import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function EquityChart({ data, title }) {
 if (!data || data.length === 0) {
 return (
 <div className="bg-white rounded-2xl shadow p-4">
 {title && <div className="font-medium mb-2">{title}</div>}
 <div className="h-64 flex items-center justify-center text-gray-500">
 No equity data available
 </div>
 </div>
 );
 }

 // Format data for Recharts
 const chartData = data.map((item, index) => ({
 date: item.date || `Day ${index + 1}`,
 equity: item.equity || item.current_equity || 0,
 realizedCum: item.realizedCum || item.realized_cum || item.total_realized_pnl || 0
 }));

 // Format date for display
 const formatDate = (dateStr) => {
 if (!dateStr || dateStr.startsWith('Day')) return dateStr;
 try {
 return new Date(dateStr).toLocaleDateString();
 } catch (e) {
 return dateStr;
 }
 };

 return (
 <div className="bg-white rounded-2xl shadow p-4">
 {title && <div className="font-medium mb-2">{title}</div>}
 <div className="h-64">
 <ResponsiveContainer width="100%" height="100%">
 <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
 <CartesianGrid strokeDasharray="3 3" />
 <XAxis 
 dataKey="date" 
 minTickGap={24}
 tickFormatter={formatDate}
 />
 <YAxis />
 <Tooltip 
 labelFormatter={formatDate}
 formatter={(value, name) => [
 typeof value === 'number' ? `$${value.toFixed(2)}` : value,
 name === 'equity' ? 'Total Equity' : 'Realized P&L'
 ]}
 />
 <Line 
 type="monotone" 
 dataKey="equity" 
 stroke="#0ea5e9" 
 dot={false} 
 strokeWidth={2}
 name="equity"
 />
 {chartData.some(d => d.realizedCum !== 0) && (
 <Line 
 type="monotone" 
 dataKey="realizedCum" 
 stroke="#10b981" 
 dot={false} 
 strokeWidth={2}
 name="realizedCum"
 />
 )}
 </LineChart>
 </ResponsiveContainer>
 </div>
 </div>
 );
}