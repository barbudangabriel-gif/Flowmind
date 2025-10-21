import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { mfClient } from '../services/mindfolioClient';

/**
 * MindfolioPage - Complete Mindfolio Management UI
 * Respects FlowMind critical rules:
 * - Dark theme only (hardcoded Tailwind dark classes)
 * - Typography: 9px/14.4px for content, 13px/20.8px for navigation
 * - Zero emoji policy
 * - Romanian language support
 */

export default function MindfolioPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [mindfolio, setMindfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    cash_balance: 0,
    status: 'ACTIVE'
  });

  // Fetch mindfolio on mount
  useEffect(() => {
    const fetchMindfolio = async () => {
      try {
        setLoading(true);
        setError('');
        
        if (id) {
          const data = await mfClient.get(id);
          setMindfolio(data);
          setFormData({
            name: data.name || '',
            cash_balance: data.cash_balance || 0,
            status: data.status || 'ACTIVE'
          });
        }
      } catch (err) {
        console.error('Failed to load mindfolio:', err);
        setError(String(err));
      } finally {
        setLoading(false);
      }
    };

    fetchMindfolio();
  }, [id]);

  const handleSave = async () => {
    try {
      if (!formData.name.trim()) {
        setError('Mindfolio name is required');
        return;
      }

      const updated = await mfClient.update(id, {
        name: formData.name,
        cash_balance: formData.cash_balance,
        status: formData.status
      });

      setMindfolio(updated);
      setEditMode(false);
      setError('');
    } catch (err) {
      setError(String(err));
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this mindfolio?')) {
      return;
    }

    try {
      await mfClient.delete(id);
      navigate('/mindfolio');
    } catch (err) {
      setError(String(err));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0f1419] to-[#0a0e1a] p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <p style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
                Loading mindfolio data
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !mindfolio) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0f1419] to-[#0a0e1a] p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-6">
            <Link 
              to="/mindfolio" 
              style={{ color: 'rgb(59, 130, 246)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}
              className="hover:underline"
            >
              Back to Mindfolios
            </Link>
          </div>
          <div className="bg-red-900/20 border border-red-700/40 rounded-lg p-6">
            <p style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
              Error: {error}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!mindfolio) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0f1419] to-[#0a0e1a] p-8">
        <div className="max-w-6xl mx-auto text-center">
          <p style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
            Mindfolio not found
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f1419] to-[#0a0e1a]">
      {/* Header Navigation */}
      <div className="border-b border-[#1e293b] bg-gradient-to-r from-[#0f1419] to-[#0a0e1a] sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-8 py-4 flex items-center justify-between">
          <Link 
            to="/mindfolio"
            style={{ color: 'rgb(59, 130, 246)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}
            className="hover:underline"
          >
            Back
          </Link>
          <h1 style={{ color: 'rgb(252, 251, 255)', fontSize: '13px', lineHeight: '20.8px', fontWeight: '500' }}>
            {mindfolio.name}
          </h1>
          <div className="flex gap-2">
            {!editMode && (
              <>
                <button
                  onClick={() => setEditMode(true)}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-[9px] hover:bg-blue-700 transition"
                >
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  className="px-3 py-1 bg-red-600 text-white rounded text-[9px] hover:bg-red-700 transition"
                >
                  Delete
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-900/20 border border-red-700/40 rounded-lg p-4">
            <p style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
              {error}
            </p>
          </div>
        )}

        {/* Edit Mode */}
        {editMode && (
          <div className="mb-8 bg-[#1a1f2e] border border-[#2d3748] rounded-lg p-6">
            <h2 style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500', marginBottom: '12px' }}>
              Edit Mindfolio
            </h2>
            <div className="space-y-4">
              <div>
                <label style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }} className="block mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-[#0f1419] border border-[#2d3748] rounded px-3 py-2 text-white text-[9px]"
                />
              </div>
              <div>
                <label style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }} className="block mb-2">
                  Cash Balance (USD)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.cash_balance}
                  onChange={(e) => setFormData({ ...formData, cash_balance: Number(e.target.value) })}
                  className="w-full bg-[#0f1419] border border-[#2d3748] rounded px-3 py-2 text-white text-[9px]"
                />
              </div>
              <div>
                <label style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }} className="block mb-2">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full bg-[#0f1419] border border-[#2d3748] rounded px-3 py-2 text-white text-[9px]"
                >
                  <option>ACTIVE</option>
                  <option>PAUSED</option>
                  <option>CLOSED</option>
                </select>
              </div>
              <div className="flex gap-2 pt-4">
                <button
                  onClick={handleSave}
                  className="px-4 py-2 bg-green-600 text-white rounded text-[9px] hover:bg-green-700 transition"
                >
                  Save
                </button>
                <button
                  onClick={() => setEditMode(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded text-[9px] hover:bg-gray-700 transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-[#1a1f2e] border border-[#2d3748] rounded-lg p-4">
            <p style={{ color: 'rgb(156, 163, 175)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }} className="mb-2">
              Cash Balance
            </p>
            <p style={{ color: 'rgb(252, 251, 255)', fontSize: '13px', lineHeight: '20.8px', fontWeight: '500' }}>
              ${mindfolio.cash_balance?.toLocaleString() || 0}
            </p>
          </div>
          <div className="bg-[#1a1f2e] border border-[#2d3748] rounded-lg p-4">
            <p style={{ color: 'rgb(156, 163, 175)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }} className="mb-2">
              Status
            </p>
            <p style={{ color: 'rgb(252, 251, 255)', fontSize: '13px', lineHeight: '20.8px', fontWeight: '500' }}>
              {mindfolio.status}
            </p>
          </div>
          <div className="bg-[#1a1f2e] border border-[#2d3748] rounded-lg p-4">
            <p style={{ color: 'rgb(156, 163, 175)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }} className="mb-2">
              Modules
            </p>
            <p style={{ color: 'rgb(252, 251, 255)', fontSize: '13px', lineHeight: '20.8px', fontWeight: '500' }}>
              {mindfolio.modules?.length || 0}
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-[#2d3748] mb-6 flex gap-6">
          {['overview', 'modules', 'transactions'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                color: activeTab === tab ? 'rgb(252, 251, 255)' : 'rgb(156, 163, 175)',
                fontSize: '9px',
                lineHeight: '14.4px',
                fontWeight: '500',
                borderBottomWidth: activeTab === tab ? '2px' : '0px',
                borderBottomColor: 'rgb(59, 130, 246)',
                paddingBottom: '8px',
                textTransform: 'capitalize'
              }}
              className="hover:text-white transition"
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-[#1a1f2e] border border-[#2d3748] rounded-lg p-6">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div>
                <p style={{ color: 'rgb(156, 163, 175)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
                  Created At
                </p>
                <p style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
                  {new Date(mindfolio.created_at).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p style={{ color: 'rgb(156, 163, 175)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
                  Last Updated
                </p>
                <p style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
                  {new Date(mindfolio.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          )}

          {activeTab === 'modules' && (
            <div>
              {mindfolio.modules && mindfolio.modules.length > 0 ? (
                <div className="space-y-2">
                  {mindfolio.modules.map((mod, idx) => (
                    <div key={idx} className="bg-[#0f1419] border border-[#2d3748] rounded p-3">
                      <p style={{ color: 'rgb(252, 251, 255)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
                        {mod.module}
                      </p>
                      <p style={{ color: 'rgb(156, 163, 175)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
                        Budget: ${mod.budget}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'rgb(156, 163, 175)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
                  No modules configured
                </p>
              )}
            </div>
          )}

          {activeTab === 'transactions' && (
            <p style={{ color: 'rgb(156, 163, 175)', fontSize: '9px', lineHeight: '14.4px', fontWeight: '500' }}>
              Transaction history coming soon
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
