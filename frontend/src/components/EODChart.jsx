import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;
  const byKey = {};
  payload.forEach((p) => { byKey[p.dataKey] = p.value; });
  const prev = (payload[0].payload.__prev || {});
  const dTotal = byKey.total - (prev.total ?? byKey.total);
  const dReal = byKey.realized - (prev.realized ?? byKey.realized);
  const dUnr = byKey.unrealized - (prev.unrealized ?? byKey.unrealized);
  return (
    <div className="bg-white/95 border rounded p-2 text-xs">
      <div className="font-semibold">{label}</div>
      <div>Total: {byKey.total?.toFixed(2)} ({dTotal >= 0 ? '+' : ''}{dTotal.toFixed(2)})</div>
      <div>Realized: {byKey.realized?.toFixed(2)} ({dReal >= 0 ? '+' : ''}{dReal.toFixed(2)})</div>
      <div>Unrealized: {byKey.unrealized?.toFixed(2)} ({dUnr >= 0 ? '+' : ''}{dUnr.toFixed(2)})</div>
    </div>
  );
};

export default function EODChart({ data, title }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow p-4">
        {title && <div className="font-semibold mb-2">{title}</div>}
        <div className="h-64 flex items-center justify-center text-gray-500">
          No EOD data available
        </div>
      </div>
    );
  }

  // Format data for Recharts - EOD has realized, unrealized, total
  // Pregătește prev day pentru tooltip Δ
  const chartData = data.map((item, index) => ({
    date: item.date || `Day ${index + 1}`,
    total: item.total || 0,
    realized: item.realized || 0,
    unrealized: item.unrealized || 0,
    __prev: index > 0 ? data[index - 1] : {}
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
      {title && <div className="font-semibold mb-2">{title}</div>}
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
                name === 'total' ? 'Total (R+UR)' : 
                name === 'realized' ? 'Realized' :
                name === 'unrealized' ? 'Unrealized' : name
              ]}
            />
            
            {/* Total (R+UR) - Main line */}
            <Line 
              type="monotone" 
              dataKey="total" 
              stroke="#1e40af" 
              strokeWidth={3}
              dot={false} 
              name="total"
            />
            
            {/* Realized - Secondary line */}
            <Line 
              type="monotone" 
              dataKey="realized" 
              stroke="#10b981" 
              strokeWidth={2}
              dot={false} 
              name="realized"
              strokeDasharray="5 5"
            />
            
            {/* Unrealized - Tertiary line */}
            <Line 
              type="monotone" 
              dataKey="unrealized" 
              stroke="#f59e0b" 
              strokeWidth={2}
              dot={false} 
              name="unrealized"
              strokeDasharray="2 2"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Legend */}
      <div className="mt-2 flex items-center justify-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-blue-700"></div>
          <span>Total (R+UR)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-green-600 border-dashed border-t"></div>
          <span>Realized</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-yellow-600"></div>
          <span>Unrealized</span>
        </div>
      </div>
    </div>
  );
}