import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || '';

const TradeStationLogin = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [config, setConfig] = useState(null);
    const [error, setError] = useState(null);

    // Fetch OAuth config from backend on mount
    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const response = await fetch(`${API}/api/oauth/tradestation/config`);
                if (!response.ok) throw new Error('Failed to fetch OAuth config');
                const data = await response.json();
                setConfig(data);
            } catch (err) {
                console.error('Config fetch error:', err);
                setError(err.message);
            }
        };
        fetchConfig();
    }, []);

    const initiateOAuth = () => {
        if (!config) {
            setError('OAuth configuration not loaded');
            return;
        }

        setLoading(true);
        
        const oauthUrl = `${config.auth_url}?` + new URLSearchParams({
            client_id: config.client_id,
            response_type: 'code',
            redirect_uri: config.redirect_uri,
            audience: 'https://api.tradestation.com',
            scope: config.scope
        });

        // Open OAuth in same window
        window.location.href = oauthUrl;
    };

    if (!config) {
        return (
            <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center p-6">
                <div className="text-center">
                    {error ? (
                        <div className="text-red-400">
                            <p className="text-[14px]">Error loading configuration</p>
                            <p className="text-xs text-gray-500 mt-2">{error}</p>
                        </div>
                    ) : (
                        <p className="text-[14px] text-gray-400">Loading OAuth configuration...</p>
                    )}
                </div>
            </div>
        );
    }

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
                            <div className="mb-2">Mode: <span className="text-white">{config.mode}</span></div>
                            <div className="mb-2 text-xs">
                                <span className="text-gray-400">Callback:</span>
                                <div className="text-gray-500 break-all mt-1">{config.redirect_uri}</div>
                            </div>
                            <div className="text-xs text-gray-400">
                                {config.mode === 'SIMULATION' ? 'Using simulation environment for testing' : 'Using live trading environment'}
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
                        onClick={() => navigate('/tradestation/connect')}
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
