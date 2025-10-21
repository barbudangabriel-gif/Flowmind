import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
 TrendingUp, 
 TrendingDown, 
 Plus, 
 Briefcase, 
 PieChart, 
 BarChart3,
 Target,
 DollarSign,
 Clock,
 Shield,
 RefreshCw,
 Activity
} from 'lucide-react';
import useMindfolioManagement from '../hooks/useMindfolioManagement';

const AllMindfolios = () => {
 const navigate = useNavigate();
 const [loading, setLoading] = useState(true);
 
 // Use real mindfolio management hook
 const {
 mindfolios,
 loading: apiLoading,
 error,
 fetchMindfolios,
 clearError
 } = useMindfolioManagement();

 // Load mindfolios on component mount
 useEffect(() => {
 const loadData = async () => {
 setLoading(true);
 try {
 await fetchMindfolios();
 } catch (err) {
 console.error('Error loading mindfolios:', err);
 } finally {
 setLoading(false);
 }
 };
 
 loadData();
 }, []);

 // Calculate aggregate stats from real data
 const aggregateStats = React.useMemo(() => {
 if (!mindfolios || mindfolios.length === 0) {
 return {
 totalValue: 0,
 totalPnl: 0,
 totalMindfolios: 0,
 activeMindfolio: 'No Mindfolios'
 };
 }
 
 const totalValue = mindfolios.reduce((sum, p) => sum + (p.total_value || 0), 0);
 const totalPnl = mindfolios.reduce((sum, p) => sum + (p.total_pnl || 0), 0);
 const mainMindfolio = mindfolios.find(p => p.id === 'tradestation-main');
 
 return {
 totalValue,
 totalPnl,
 totalMindfolios: mindfolios.length,
 activeMindfolio: mainMindfolio ? mainMindfolio.name : mindfolios[0]?.name || 'No Mindfolio'
 };
 }, [mindfolios]);

 const getTrendIcon = (change) => {
 return change >= 0 ? TrendingUp : TrendingDown;
 };

 const getChangeColor = (change) => {
 return change >= 0 ? 'text-green-500' : 'text-red-500';
 };

 const getBgChangeColor = (change) => {
 return change >= 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
 };

 const getRiskColor = (category) => {
 switch (category) {
 case 'main': return 'bg-blue-100 text-blue-800';
 case 'long-term': return 'bg-green-100 text-green-800'; 
 case 'medium-term': return 'bg-yellow-100 text-yellow-800';
 case 'short-term': return 'bg-red-100 text-red-800';
 case 'custom': return 'bg-purple-100 text-purple-800';
 default: return 'bg-gray-100 text-gray-800';
 }
 };

 const getCategoryLabel = (category) => {
 switch (category) {
 case 'main': return 'MAIN ACCOUNT';
 case 'long-term': return 'LONG TERM';
 case 'medium-term': return 'MEDIUM TERM';
 case 'short-term': return 'SHORT TERM';
 case 'custom': return 'CUSTOM';
 default: return 'MINDFOLIO';
 }
 };

 const handleRefresh = async () => {
 setLoading(true);
 try {
 await fetchMindfolios();
 } finally {
 setLoading(false);
 }
 };

 const formatValue = (value) => {
 return new Intl.NumberFormat('en-US', {
 style: 'currency',
 currency: 'USD',
 minimumFractionDigits: 0,
 maximumFractionDigits: 0,
 }).format(value);
 };

 if (loading || apiLoading) {
 return (
 <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
 <div className="text-center">
 <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
 <span className="text-xl text-gray-300">Loading mindfolios...</span>
 <p className="text-gray-500 mt-2">Fetching real TradeStation data</p>
 </div>
 </div>
 );
 }

 return (
 <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
 {/* Header */}
 <div className="bg-gray-800 shadow-sm border-b border-gray-700">
 <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
 <div className="flex items-center justify-between h-16">
 <div>
 <h1 className="text-2xl font-medium text-[rgb(252, 251, 255)] flex items-center">
 <Briefcase className="mr-3 text-blue-400" size={28} />
 All Mindfolios
 </h1>
 <p className="text-xl text-gray-400">
 Manage and monitor your TradeStation mindfolios
 </p>
 </div>
 
 <div className="flex space-x-3">
 <button 
 onClick={handleRefresh}
 className="bg-gray-700 text-[rgb(252, 251, 255)] px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2"
 disabled={loading}
 >
 <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
 <span>Refresh</span>
 </button>
 
 <button 
 onClick={() => navigate('/mindfolios/create')}
 className="bg-blue-600 text-[rgb(252, 251, 255)] px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
 >
 <Plus size={20} />
 <span>Create Mindfolio</span>
 </button>
 </div>
 </div>
 </div>
 </div>

 {/* Error Display */}
 {error && (
 <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
 <div className="bg-red-50 border border-red-200 rounded-lg p-4">
 <span className="text-red-700">Error: {error}</span>
 <button
 onClick={clearError}
 className="ml-2 text-red-600 hover:text-red-800"
 >
 Dismiss
 </button>
 </div>
 </div>
 )}

 {/* Main Content */}
 <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
 
 {/* Mindfolio Summary Stats */}
 <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
 <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
 <div className="flex items-center justify-between">
 <div>
 <p className="text-gray-400 text-xl">Total Value</p>
 <p className="text-2xl font-medium text-[rgb(252, 251, 255)]">
 {formatValue(aggregateStats.totalValue)}
 </p>
 </div>
 <DollarSign className="text-green-400" size={32} />
 </div>
 </div>
 
 <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
 <div className="flex items-center justify-between">
 <div>
 <p className="text-gray-400 text-xl">Total Mindfolios</p>
 <p className="text-2xl font-medium text-[rgb(252, 251, 255)]">{aggregateStats.totalMindfolios}</p>
 </div>
 <Briefcase className="text-blue-400" size={32} />
 </div>
 </div>
 
 <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
 <div className="flex items-center justify-between">
 <div>
 <p className="text-gray-400 text-xl">Unrealized P&L</p>
 <p className={`text-2xl font-medium ${getChangeColor(aggregateStats.totalPnl)}`}>
 {aggregateStats.totalPnl >= 0 ? '+' : ''}{formatValue(aggregateStats.totalPnl)}
 </p>
 </div>
 {aggregateStats.totalPnl >= 0 ? 
 <TrendingUp className="text-green-400" size={32} /> : 
 <TrendingDown className="text-red-400" size={32} />
 }
 </div>
 </div>
 
 <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
 <div className="flex items-center justify-between">
 <div>
 <p className="text-gray-400 text-xl">Main Mindfolio</p>
 <p className="text-3xl font-medium text-[rgb(252, 251, 255)]">{aggregateStats.activeMindfolio}</p>
 <p className="text-lg text-blue-400">Live TradeStation</p>
 </div>
 <Activity className="text-blue-400" size={32} />
 </div>
 </div>
 </div>

 {/* Mindfolio Cards */}
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
 {mindfolios && mindfolios.length > 0 ? (
 mindfolios.map((mindfolio) => {
 const changePercent = mindfolio.total_value > 0 
 ? (mindfolio.total_pnl / (mindfolio.total_value - mindfolio.total_pnl)) * 100 
 : 0;
 
 const TrendIcon = getTrendIcon(mindfolio.total_pnl);
 
 return (
 <div 
 key={mindfolio.id}
 className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 hover:border-blue-500 transition-colors cursor-pointer"
 onClick={() => navigate(`/mindfolios/${mindfolio.id}`)}
 >
 <div className="p-6">
 {/* Mindfolio Header */}
 <div className="flex items-center justify-between mb-4">
 <div>
 <h3 className="text-xl font-medium text-[rgb(252, 251, 255)]">{mindfolio.name}</h3>
 <p className="text-gray-400 text-xl">{mindfolio.positions_count} positions</p>
 </div>
 <div className={`px-3 py-1 rounded-full text-lg font-medium ${getRiskColor(mindfolio.category)}`}>
 {getCategoryLabel(mindfolio.category)}
 </div>
 </div>

 {/* Mindfolio Value */}
 <div className="mb-4">
 <div className="text-3xl font-medium text-[rgb(252, 251, 255)] mb-1">
 {formatValue(mindfolio.total_value)}
 </div>
 <div className={`flex items-center space-x-2 ${getChangeColor(mindfolio.total_pnl)}`}>
 <TrendIcon size={20} />
 <span className="text-3xl font-medium">
 {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
 </span>
 <span className="text-xl">
 ({mindfolio.total_pnl >= 0 ? '+' : ''}{formatValue(mindfolio.total_pnl)})
 </span>
 </div>
 </div>

 {/* Quick Stats */}
 <div className="grid grid-cols-2 gap-4 mb-4">
 <div className="text-center p-3 bg-gray-700 rounded-lg">
 <div className="text-xl text-gray-400">Positions</div>
 <div className="text-3xl font-medium text-[rgb(252, 251, 255)]">{mindfolio.positions_count}</div>
 </div>
 <div className="text-center p-3 bg-gray-700 rounded-lg">
 <div className="text-xl text-gray-400">Updated</div>
 <div className="text-xl font-medium text-blue-400">
 {new Date(mindfolio.last_updated).toLocaleString()}
 </div>
 </div>
 </div>

 {/* Action Buttons */}
 <div className="flex space-x-2 pt-4 border-t border-gray-700">
 <button 
 className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-blue-600 text-[rgb(252, 251, 255)] rounded-lg hover:bg-blue-700 transition-colors"
 onClick={(e) => {
 e.stopPropagation();
 navigate(`/mindfolios/${mindfolio.id}`);
 }}
 >
 <PieChart size={16} />
 <span>View</span>
 </button>
 <button 
 className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-gray-700 text-[rgb(252, 251, 255)] rounded-lg hover:bg-gray-600 transition-colors"
 onClick={(e) => {
 e.stopPropagation();
 navigate(`/mindfolios/${mindfolio.id}/charts`);
 }}
 >
 <BarChart3 size={16} />
 <span>Charts</span>
 </button>
 </div>
 </div>
 </div>
 );
 })
 ) : (
 <div className="col-span-full text-center py-12">
 <Briefcase className="mx-auto h-16 w-16 text-gray-400 mb-4" />
 <h3 className="text-3xl font-medium text-gray-300 mb-2">No mindfolios found</h3>
 <p className="text-gray-500 mb-6">
 Get started by creating your first mindfolio or check your TradeStation connection.
 </p>
 <button 
 onClick={() => navigate('/mindfolios/create')}
 className="bg-blue-600 text-[rgb(252, 251, 255)] px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 mx-auto"
 >
 <Plus size={20} />
 <span>Create Your First Mindfolio</span>
 </button>
 </div>
 )}
 </div>
 </div>
 </div>
 );
};

export default AllMindfolios;