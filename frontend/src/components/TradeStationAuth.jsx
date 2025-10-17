import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const TradeStationAuth = ({ onAuthSuccess }) => {
    const navigate = useNavigate();
    const [accessToken, setAccessToken] = useState('');
    const [refreshToken, setRefreshToken] = useState('');
    const [expiresIn, setExpiresIn] = useState('3600');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

    const handleInitTokens = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            const response = await axios.post(`${BACKEND_URL}/api/tradestation/auth/init`, {
                access_token: accessToken,
                refresh_token: refreshToken,
                expires_in: parseInt(expiresIn)
            });

            if (response.data.status === 'success') {
                setSuccess(true);
                setAccessToken('');
                setRefreshToken('');
                
                if (onAuthSuccess) {
                    setTimeout(() => onAuthSuccess(), 1000);
                }
            }
        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Failed to initialize tokens');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h2 className="text-[20px] text-white mb-4">TradeStation Authentication</h2>
            
            {/* OAuth Live Connection Button */}
            <div className="mb-6 p-4 bg-gradient-to-br from-blue-900/40 to-blue-800/20 border border-blue-700/50 rounded-lg">
                <h3 className="text-[14px] text-white mb-2">Connect with OAuth (Recommended)</h3>
                <p className="text-[14px] text-gray-400 mb-4">
                    Secure connection using TradeStation OAuth flow
                </p>
                <button
                    onClick={() => navigate('/tradestation/login')}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white text-[14px] py-3 rounded-lg transition-colors"
                >
                    Connect Live Account →
                </button>
            </div>

            {/* Divider */}
            <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-700"></div>
                </div>
                <div className="relative flex justify-center text-[14px]">
                    <span className="px-4 bg-gray-900 text-gray-400">OR</span>
                </div>
            </div>

            {/* Manual Token Entry */}
            <p className="text-[14px] text-gray-400 mb-6">
                Or enter tokens manually (for testing)
            </p>

            {error && (
                <div className="bg-red-900/30 border border-red-700 text-red-200 p-4 rounded-lg mb-4">
                    <p className="text-[14px]">{error}</p>
                </div>
            )}

            {success && (
                <div className="bg-green-900/30 border border-green-700 text-green-200 p-4 rounded-lg mb-4">
                    <p className="text-[14px]">Tokens initialized successfully!</p>
                </div>
            )}

            <form onSubmit={handleInitTokens} className="space-y-4">
                <div>
                    <label className="block text-[14px] text-gray-300 mb-2">
                        Access Token
                    </label>
                    <input
                        type="text"
                        value={accessToken}
                        onChange={(e) => setAccessToken(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white text-[14px] focus:outline-none focus:border-blue-500"
                        placeholder="Enter access token"
                        required
                    />
                </div>

                <div>
                    <label className="block text-[14px] text-gray-300 mb-2">
                        Refresh Token
                    </label>
                    <input
                        type="text"
                        value={refreshToken}
                        onChange={(e) => setRefreshToken(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white text-[14px] focus:outline-none focus:border-blue-500"
                        placeholder="Enter refresh token"
                        required
                    />
                </div>

                <div>
                    <label className="block text-[14px] text-gray-300 mb-2">
                        Expires In (seconds)
                    </label>
                    <input
                        type="number"
                        value={expiresIn}
                        onChange={(e) => setExpiresIn(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white text-[14px] focus:outline-none focus:border-blue-500"
                        placeholder="3600"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white text-[14px] py-3 rounded-lg transition-colors"
                >
                    {loading ? 'Initializing...' : 'Initialize Tokens'}
                </button>
            </form>

            <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                <p className="text-[14px] text-gray-400 mb-2">How to get tokens:</p>
                <ol className="list-decimal list-inside space-y-1 text-[14px] text-gray-300">
                    <li>Login to TradeStation Developer Portal</li>
                    <li>Complete OAuth flow to get tokens</li>
                    <li>Copy access_token and refresh_token</li>
                    <li>Paste them above and click Initialize</li>
                </ol>
            </div>
        </div>
    );
};

export default TradeStationAuth;
