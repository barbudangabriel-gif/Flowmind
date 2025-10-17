import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const TradeStationLogin = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const CLIENT_ID = 'XEs0URG1rMrGDUFRKVhlDaclvQKq8Qpj';
    const REDIRECT_URI = 'https://sturdy-system-wvrqjjp49wg29qxx-8000.app.github.dev/api/oauth/tradestation/callback';
    const MODE = 'LIVE'; // SIMULATION not accessible from Codespaces
    
    const AUTH_URL = MODE === 'LIVE' 
        ? 'https://signin.tradestation.com/authorize'
        : 'https://sim-signin.tradestation.com/authorize';

    const initiateOAuth = () => {
        setLoading(true);
        
        const oauthUrl = `${AUTH_URL}?` + new URLSearchParams({
            client_id: CLIENT_ID,
            response_type: 'code',
            redirect_uri: REDIRECT_URI,
            audience: 'https://api.tradestation.com',
            scope: 'openid profile MarketData ReadAccount Trade Crypto offline_access'
        });

        // Open OAuth in same window
        window.location.href = oauthUrl;
    };

    return (
        <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center p-6">
            <div className="max-w-md w-full">
                <div className="bg-gray-900 border border-gray-800 rounded-lg p-8">
                    <h1 className="text-[20px] text-white mb-4">
                        Connect to TradeStation
                    </h1>
                    
                    <p className="text-[14px] text-gray-400 mb-6">
                        Connect your TradeStation account to view live balances and positions.
                    </p>

                    <div className="mb-6 p-4 bg-blue-900/20 border border-blue-700/50 rounded-lg">
                        <div className="text-[14px] text-blue-200">
                            <div className="mb-2">Mode: <span className="text-white">{MODE}</span></div>
                            <div className="text-xs text-gray-400">
                                {MODE === 'SIMULATION' ? 'Using simulation environment for testing' : 'Using live trading environment'}
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={initiateOAuth}
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white text-[14px] py-3 rounded-lg transition-colors mb-4"
                    >
                        {loading ? 'Redirecting...' : 'Connect with TradeStation'}
                    </button>

                    <button
                        onClick={() => navigate('/account/balance')}
                        className="w-full bg-gray-800 hover:bg-gray-700 text-white text-[14px] py-3 rounded-lg transition-colors"
                    >
                        Back to Account Balance
                    </button>

                    <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                        <p className="text-[14px] text-gray-400 mb-2">What happens next:</p>
                        <ol className="list-decimal list-inside space-y-1 text-[14px] text-gray-300">
                            <li>Login to TradeStation</li>
                            <li>Authorize FlowMind access</li>
                            <li>Redirect back with live data</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TradeStationLogin;
