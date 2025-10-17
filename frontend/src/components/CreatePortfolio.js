import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
 X,
 Link,
 Upload,
 Plus,
 FileText,
 TrendingUp,
 AlertCircle,
 CheckCircle
} from 'lucide-react';

const CreatePortfolio = () => {
 const navigate = useNavigate();
 const [portfolioName, setPortfolioName] = useState('Portfolio 4');
 const [selectedMethod, setSelectedMethod] = useState(null);
 const [isCreating, setIsCreating] = useState(false);

 const handleCancel = () => {
 navigate('/portfolios');
 };

 const handleCreatePortfolio = async () => {
 if (!portfolioName.trim()) {
 alert('Please enter a portfolio name');
 return;
 }

 setIsCreating(true);
 
 // Simulate portfolio creation
 setTimeout(() => {
 setIsCreating(false);
 // Navigate back to all portfolios or to the new portfolio
 navigate('/portfolios');
 }, 2000);
 };

 const creationMethods = [
 {
 id: 'link-broker',
 title: 'Link Broker',
 description: 'Connect your existing brokerage account to sync holdings automatically',
 icon: Link,
 color: 'border-blue-500 hover:bg-blue-50',
 iconColor: 'text-blue-600'
 },
 {
 id: 'upload-csv',
 title: 'Upload CSV',
 description: 'Import your portfolio holdings from a CSV file',
 icon: Upload,
 color: 'border-green-500 hover:bg-green-50', 
 iconColor: 'text-green-600'
 },
 {
 id: 'manual-entry',
 title: 'Manual Entry',
 description: 'Add stocks manually one by one to build your portfolio',
 icon: Plus,
 color: 'border-purple-500 hover:bg-purple-50',
 iconColor: 'text-purple-600'
 }
 ];

 return (
 <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
 {/* Modal Container */}
 <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl relative">
 
 {/* Header */}
 <div className="flex items-center justify-between p-8 pb-4">
 <h1 className="text-3xl font-medium text-gray-800">Create Portfolio</h1>
 <button
 onClick={handleCancel}
 className="text-2xl font-medium text-gray-600 hover:text-gray-800 transition-colors"
 >
 Cancel
 </button>
 </div>

 {/* Content */}
 <div className="px-8 pb-8">
 
 {/* Portfolio Name Input */}
 <div className="mb-8">
 <label className="block text-gray-600 text-3xl font-medium mb-4">
 Name:
 </label>
 <input
 type="text"
 value={portfolioName}
 onChange={(e) => setPortfolioName(e.target.value)}
 className="w-full px-6 py-4 text-xl border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
 placeholder="Enter portfolio name"
 />
 </div>

 {/* Create Portfolio Button */}
 <button
 onClick={handleCreatePortfolio}
 disabled={isCreating || !portfolioName.trim()}
 className="w-full bg-black text-[rgb(252, 251, 255)] text-xl font-medium py-4 rounded-xl hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mb-8 flex items-center justify-center"
 >
 {isCreating ? (
 <>
 <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
 Creating Portfolio...
 </>
 ) : (
 'Create Portfolio'
 )}
 </button>

 {/* Creation Methods */}
 <div className="space-y-4">
 {creationMethods.map((method) => {
 const IconComponent = method.icon;
 return (
 <button
 key={method.id}
 onClick={() => setSelectedMethod(method.id)}
 className={`w-full p-6 border-2 rounded-xl transition-all duration-200 text-left ${
 selectedMethod === method.id 
 ? method.color + ' border-opacity-100 shadow-lg' 
 : 'border-gray-300 hover:border-gray-400'
 }`}
 >
 <div className="flex items-center">
 <div className={`p-3 rounded-lg mr-4 ${
 selectedMethod === method.id ? 'bg-white' : 'bg-gray-100'
 }`}>
 <IconComponent 
 size={24} 
 className={selectedMethod === method.id ? method.iconColor : 'text-gray-600'} 
 />
 </div>
 <div className="flex-1">
 <h3 className="text-xl font-medium text-gray-800 mb-1">
 {method.title}
 </h3>
 <p className="text-gray-600 text-xl">
 {method.description}
 </p>
 </div>
 {selectedMethod === method.id && (
 <CheckCircle className="text-green-500 ml-4" size={24} />
 )}
 </div>
 </button>
 );
 })}
 </div>

 {/* Selected Method Details */}
 {selectedMethod && (
 <div className="mt-6 p-6 bg-blue-50 rounded-xl border border-blue-200">
 <div className="flex items-start">
 <AlertCircle className="text-blue-600 mr-3 mt-1" size={20} />
 <div>
 <h4 className="font-medium text-blue-800 mb-2">
 {selectedMethod === 'link-broker' && 'Broker Integration'}
 {selectedMethod === 'upload-csv' && 'CSV Upload Requirements'}
 {selectedMethod === 'manual-entry' && 'Manual Entry Process'}
 </h4>
 <div className="text-xl text-blue-700">
 {selectedMethod === 'link-broker' && (
 <ul className="space-y-1">
 <li>• Supported brokers: TradeStation, TD Ameritrade, E*TRADE</li>
 <li>• Secure OAuth authentication</li>
 <li>• Real-time position sync</li>
 <li>• Automatic updates every 15 minutes</li>
 </ul>
 )}
 {selectedMethod === 'upload-csv' && (
 <ul className="space-y-1">
 <li>• Required columns: Symbol, Quantity, Average Cost</li>
 <li>• Optional: Purchase Date, Current Value</li>
 <li>• Supported formats: .csv, .xlsx</li>
 <li>• Maximum file size: 5MB</li>
 </ul>
 )}
 {selectedMethod === 'manual-entry' && (
 <ul className="space-y-1">
 <li>• Add stocks one by one with full control</li>
 <li>• Set custom purchase prices and dates</li>
 <li>• Track cost basis and performance</li>
 <li>• Edit positions anytime</li>
 </ul>
 )}
 </div>
 </div>
 </div>
 </div>
 )}

 {/* Action Buttons */}
 {selectedMethod && (
 <div className="mt-6 flex space-x-4">
 <button
 onClick={handleCancel}
 className="flex-1 py-3 px-6 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
 >
 Back
 </button>
 <button
 onClick={() => {
 // Navigate to appropriate creation method
 if (selectedMethod === 'link-broker') {
 navigate('/portfolios/create/link-broker');
 } else if (selectedMethod === 'upload-csv') {
 navigate('/portfolios/create/upload-csv');
 } else if (selectedMethod === 'manual-entry') {
 navigate('/portfolios/create/manual');
 }
 }}
 className="flex-1 py-3 px-6 bg-blue-600 text-[rgb(252, 251, 255)] rounded-xl hover:bg-blue-700 transition-colors font-medium"
 >
 Continue
 </button>
 </div>
 )}

 </div>
 </div>

 {/* Background Overlay */}
 <div className="fixed inset-0 bg-black bg-opacity-50 -z-10"></div>
 </div>
 );
};

export default CreatePortfolio;