import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import TradeStationAuth from '../components/TradeStationAuth.jsx';
import axios from 'axios';

const AccountBalancePage = () => {
 const [accounts, setAccounts] = useState([]);
 const [selectedAccount, setSelectedAccount] = useState(null);
 const [balances, setBalances] = useState(null);
 const [positions, setPositions] = useState([]);
 const [loading, setLoading] = useState(false);
 const [authStatus, setAuthStatus] = useState(null);
 const [error, setError] = useState(null);

 const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
 const API = `${BACKEND_URL}/api`;

 // Check authentication status
 useEffect(() => {
 checkAuthStatus();
 }, []);

    const checkAuthStatus = async () => {
        try {
            const response = await axios.get(`${API}/tradestation/auth/status`);
            setAuthStatus(response.data.data);
            
            if (response.data.data.authenticated) {
                loadAccounts();
            } else {
                // Load demo data immediately if not authenticated
                loadDemoData();
            }
        } catch (err) {
            console.error('Failed to check auth status:', err);
            loadDemoData();
        }
    };

    const loadDemoData = () => {
        const mockAccounts = [
            { AccountID: 'DEMO123456', AccountType: 'Margin', Name: 'Demo Trading Account' }
        ];
        setAccounts(mockAccounts);
        selectAccount(mockAccounts[0]);
    };

    const loadAccounts = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API}/tradestation/accounts`);
            const accountsList = response.data.data?.Accounts || [];
            setAccounts(accountsList);
            
            if (accountsList.length > 0) {
                selectAccount(accountsList[0]);
            }
        } catch (err) {
            setError(`Failed to load accounts: ${err.message}`);
            const mockAccounts = [
                { AccountID: 'DEMO123456', AccountType: 'Margin', Name: 'Demo Account' }
            ];
            setAccounts(mockAccounts);
            selectAccount(mockAccounts[0]);
        } finally {
            setLoading(false);
        }
    };

    const selectAccount = async (account) => {
        try {
            setSelectedAccount(account);
            setLoading(true);
            setError(null);

            // Try to fetch real data if authenticated
            if (authStatus?.authenticated) {
                const balResponse = await axios.get(`${API}/tradestation/accounts/${account.AccountID}/balances`);
                setBalances(balResponse.data.data);

                const posResponse = await axios.get(`${API}/tradestation/accounts/${account.AccountID}/positions`);
                setPositions(posResponse.data.data?.Positions || []);
            } else {
                // Use demo data
                setBalances({
                    CashBalance: 50000,
                    BuyingPower: 100000,
                    AccountValue: 75000,
                    MarketValue: 25000,
                    UnrealizedProfitLoss: 2500,
                    RealizedProfitLoss: 1250
                });
                setPositions([
                    { 
                        Symbol: 'TSLA', 
                        Quantity: 100, 
                        AveragePrice: 250.00, 
                        Last: 252.50, 
                        MarketValue: 25250, 
                        UnrealizedProfitLoss: 250, 
                        UnrealizedProfitLossPercent: 1.0 
                    },
                    { 
                        Symbol: 'AAPL', 
                        Quantity: 50, 
                        AveragePrice: 180.00, 
                        Last: 185.00, 
                        MarketValue: 9250, 
                        UnrealizedProfitLoss: 250, 
                        UnrealizedProfitLossPercent: 2.78 
                    },
                    { 
                        Symbol: 'NVDA', 
                        Quantity: 25, 
                        AveragePrice: 500.00, 
                        Last: 520.00, 
                        MarketValue: 13000, 
                        UnrealizedProfitLoss: 500, 
                        UnrealizedProfitLossPercent: 4.0 
                    }
                ]);
            }
        } catch (err) {
            setError(`Failed to load account data: ${err.message}`);
            // Fallback to demo data on error
            setBalances({
                CashBalance: 50000,
                BuyingPower: 100000,
                AccountValue: 75000,
                MarketValue: 25000,
                UnrealizedProfitLoss: 2500,
                RealizedProfitLoss: 1250
            });
            setPositions([
                { Symbol: 'TSLA', Quantity: 100, AveragePrice: 250.00, Last: 252.50, MarketValue: 25250, UnrealizedProfitLoss: 250, UnrealizedProfitLossPercent: 1.0 }
            ]);
        } finally {
            setLoading(false);
        }
    };

 const formatCurrency = (value) => {
 if (value === null || value === undefined) return '$0.00';
 return new Intl.NumberFormat('en-US', {
 style: 'currency',
 currency: 'USD',
 }).format(value);
 };

 const formatPercent = (value) => {
 if (value === null || value === undefined) return '0.00%';
 return `${(value * 100).toFixed(2)}%`;
 };

 const isAuthenticated = authStatus?.authenticated;

 return (
 <div className="min-h-screen bg-[#0f1419] p-4">
 <div className="max-w-7xl mx-auto space-y-4">
            <div>
                <div className="flex items-center justify-between mb-1">
                    <h1 className="text-xl text-white">Account Balance</h1>
                    <Link 
                        to="/mindfolios" 
                        className="px-3 py-2 bg-[#0a0e1a] hover:bg-slate-700 text-white rounded-lg transition-colors border border-[#1a1f26] text-sm"
                    >
                        View Mindfolios →
                    </Link>
                </div>
                <p className="text-sm text-gray-400">View your TradeStation account balances and positions</p>
            </div>

 {/* Authentication Section */}
 {!isAuthenticated && (
 <div className="mb-6">
 <TradeStationAuth />
 </div>
 )}

 {/* Error Message */}
 {error && (
 <div className="bg-red-900/30 border border-red-700 text-red-200 p-4 rounded-lg mb-3">
 <p className="text-sm">{error}</p>
 </div>
 )}

 {/* Account Selector */}
 {isAuthenticated && accounts.length > 0 && (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3">
 <h2 className="text-base text-white mb-4">Select Account</h2>
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
 {accounts.map((account) => (
 <button
 key={account.AccountID}
 onClick={() => selectAccount(account)}
 className={`p-4 rounded-lg border-2 transition-all text-left ${
 selectedAccount?.AccountID === account.AccountID
 ? 'bg-blue-900/30 border-blue-600'
 : 'bg-[#0f1419] border-[#1a1f26] hover:border-gray-600'
 }`}
 >
 <div className="text-sm text-gray-400 mb-1">{account.AccountType}</div>
 <div className="text-sm font-mono text-white">{account.AccountID}</div>
 <div className="text-sm text-gray-400 mt-1">{account.Name}</div>
 </button>
 ))}
 </div>
 </div>
 )}

 {/* Loading State */}
 {loading && (
 <div className="flex items-center justify-center py-12">
 <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mr-3"></div>
 <span className="text-gray-300">Loading account data...</span>
 </div>
 )}

 {/* Balances Section */}
 {isAuthenticated && selectedAccount && balances && !loading && (
 <>
 {/* Account Summary Cards */}
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
 {/* Total Account Value */}
 <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/20 border border-blue-700/50 rounded-lg p-3">
 <div className="flex items-center justify-between mb-2">
 <span className="text-sm text-gray-300">Total Value</span>
 </div>
 <div className="text-[20px] text-white mb-1">
 {formatCurrency(balances.AccountValue || balances.TotalValue)}
 </div>
 <div className="text-sm text-gray-400">Account Equity</div>
 </div>

 {/* Cash Balance */}
 <div className="bg-gradient-to-br from-green-900/40 to-green-800/20 border border-green-700/50 rounded-lg p-3">
 <div className="flex items-center justify-between mb-2">
 <span className="text-sm text-gray-300">Cash Balance</span>
 </div>
 <div className="text-[20px] text-white mb-1">
 {formatCurrency(balances.CashBalance)}
 </div>
 <div className="text-sm text-gray-400">Available Cash</div>
 </div>

 {/* Buying Power */}
 <div className="bg-gradient-to-br from-purple-900/40 to-purple-800/20 border border-purple-700/50 rounded-lg p-3">
 <div className="flex items-center justify-between mb-2">
 <span className="text-sm text-gray-300">Buying Power</span>
 </div>
 <div className="text-[20px] text-white mb-1">
 {formatCurrency(balances.BuyingPower || balances.DayTradingBuyingPower)}
 </div>
 <div className="text-sm text-gray-400">Available to Trade</div>
 </div>

 {/* Market Value */}
 <div className="bg-gradient-to-br from-orange-900/40 to-orange-800/20 border border-orange-700/50 rounded-lg p-3">
 <div className="flex items-center justify-between mb-2">
 <span className="text-sm text-gray-300">Market Value</span>
 </div>
 <div className="text-[20px] text-white mb-1">
 {formatCurrency(balances.MarketValue)}
 </div>
 <div className="text-sm text-gray-400">Positions Value</div>
 </div>
 </div>

 {/* Detailed Balance Information */}
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3">
 <h2 className="text-base text-white mb-4">Account Details</h2>
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
 {balances.UnrealizedProfitLoss !== undefined && (
 <div className="bg-[#0f1419] p-3 rounded-lg">
 <div className="text-sm text-gray-400 mb-1">Unrealized P&L</div>
 <div className={`text-sm ${
 balances.UnrealizedProfitLoss >= 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatCurrency(balances.UnrealizedProfitLoss)}
 </div>
 </div>
 )}
 {balances.RealizedProfitLoss !== undefined && (
 <div className="bg-[#0f1419] p-3 rounded-lg">
 <div className="text-sm text-gray-400 mb-1">Realized P&L (Today)</div>
 <div className={`text-sm ${
 balances.RealizedProfitLoss >= 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatCurrency(balances.RealizedProfitLoss)}
 </div>
 </div>
 )}
 {balances.Commission !== undefined && (
 <div className="bg-[#0f1419] p-3 rounded-lg">
 <div className="text-sm text-gray-400 mb-1">Commissions (Today)</div>
 <div className="text-sm text-white">
 {formatCurrency(balances.Commission)}
 </div>
 </div>
 )}
 {balances.OptionBuyingPower !== undefined && (
 <div className="bg-[#0f1419] p-3 rounded-lg">
 <div className="text-sm text-gray-400 mb-1">Option Buying Power</div>
 <div className="text-sm text-white">
 {formatCurrency(balances.OptionBuyingPower)}
 </div>
 </div>
 )}
 {balances.MaintenanceMargin !== undefined && (
 <div className="bg-[#0f1419] p-3 rounded-lg">
 <div className="text-sm text-gray-400 mb-1">Maintenance Margin</div>
 <div className="text-sm text-white">
 {formatCurrency(balances.MaintenanceMargin)}
 </div>
 </div>
 )}
 {balances.DayTrades !== undefined && (
 <div className="bg-[#0f1419] p-3 rounded-lg">
 <div className="text-sm text-gray-400 mb-1">Day Trades Used</div>
 <div className="text-sm text-white">
 {balances.DayTrades} / {balances.DayTradesRemaining || 'N/A'}
 </div>
 </div>
 )}
 </div>
 </div>

 {/* Positions Table */}
 {positions.length > 0 && (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3">
 <h2 className="text-base text-white mb-4">Current Positions</h2>
 <div className="overflow-x-auto">
 <table className="w-full">
 <thead>
 <tr className="border-b border-[#1a1f26]">
 <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Symbol</th>
 <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Quantity</th>
 <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Avg Price</th>
 <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Last Price</th>
 <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">Market Value</th>
 <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">P&L</th>
 <th className="text-right py-3 px-4 text-sm font-medium text-gray-400">P&L %</th>
 </tr>
 </thead>
 <tbody>
 {positions.map((position, index) => {
 const pnl = position.UnrealizedProfitLoss || 0;
 const pnlPercent = position.UnrealizedProfitLossPercent || 0;
 
 return (
 <tr key={index} className="border-b border-[#1a1f26]/50 hover:bg-[#0f1419]/50 transition-colors">
 <td className="py-3 px-4">
 <div className="font-mono text-white text-base">{position.Symbol}</div>
 <div className="text-xs text-gray-400">{position.AssetType}</div>
 </td>
 <td className="text-right py-3 px-4 text-white">{position.Quantity}</td>
 <td className="text-right py-3 px-4 text-gray-300 font-mono">
 {formatCurrency(position.AveragePrice)}
 </td>
 <td className="text-right py-3 px-4 text-white font-mono">
 {formatCurrency(position.Last)}
 </td>
 <td className="text-right py-3 px-4 text-white">
 {formatCurrency(position.MarketValue)}
 </td>
 <td className={`text-right py-3 px-4 ${
 pnl >= 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatCurrency(pnl)}
 </td>
 <td className={`text-right py-3 px-4 ${
 pnlPercent >= 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatPercent(pnlPercent)}
 </td>
 </tr>
 );
 })}
 </tbody>
 </table>
 </div>
 </div>
 )}

 {/* No Positions Message */}
 {positions.length === 0 && !loading && (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-12 text-center">
 <h3 className="text-base text-white mb-2">No Open Positions</h3>
 <p className="text-gray-400 mb-4">This account currently has no open positions</p>
 <Link 
 to="/builder" 
 className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
 >
 Explore Options Strategies →
 </Link>
 </div>
 )}
 </>
 )}

 {/* Not Authenticated State */}
 {isAuthenticated && accounts.length === 0 && !loading && (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-12 text-center">
 <h3 className="text-base text-white mb-2">No Accounts Found</h3>
 <p className="text-gray-400">Could not find any TradeStation accounts</p>
 </div>
 )}
 </div>
 </div>
 );
};

export default AccountBalancePage;
