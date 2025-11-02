import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function MindfolioTemplateModal({ isOpen, onClose, onCreateFromTemplate }) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [mindfolioName, setMindfolioName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchTemplates();
    }
  }, [isOpen]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/mindfolio/templates`);
      const data = await response.json();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setMindfolioName(template.name);
  };

  const handleCreate = async () => {
    if (!selectedTemplate || !mindfolioName.trim()) return;

    setCreating(true);
    try {
      await onCreateFromTemplate({
        name: mindfolioName,
        starting_balance: selectedTemplate.starting_balance,
        modules: selectedTemplate.modules,
      });
      onClose();
      setSelectedTemplate(null);
      setMindfolioName('');
    } catch (error) {
      console.error('Failed to create mindfolio:', error);
      alert('Failed to create mindfolio: ' + error.message);
    } finally {
      setCreating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-900 border-b border-slate-700 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">📋 Choose Template</h2>
            <p className="text-sm text-gray-400">Select a pre-configured mindfolio template to get started</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <>
              {/* Template Selection */}
              {!selectedTemplate ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {templates.map((template) => (
                    <button
                      key={template.id}
                      onClick={() => handleTemplateSelect(template)}
                      className="text-left bg-slate-800/50 border-2 border-slate-700 hover:border-blue-500 rounded-lg p-6 transition-all hover:scale-[1.02]"
                    >
                      {/* Icon & Title */}
                      <div className="flex items-center gap-3 mb-3">
                        <span className="text-4xl">{template.icon}</span>
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-white">{template.name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              template.risk_level === 'HIGH' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                              template.risk_level === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                              template.risk_level === 'LOW' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                              'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                            }`}>
                              {template.risk_level} RISK
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-sm text-gray-400 mb-4">{template.description}</p>

                      {/* Starting Balance */}
                      <div className="bg-slate-900/50 rounded-lg p-3 mb-3">
                        <div className="text-xs text-gray-500 mb-1">Starting Balance</div>
                        <div className="text-xl font-bold text-green-400">
                          ${template.starting_balance.toLocaleString('en-US')}
                        </div>
                      </div>

                      {/* Modules */}
                      {template.modules.length > 0 && (
                        <div className="space-y-2">
                          <div className="text-xs text-gray-500 font-semibold">Modules ({template.modules.length})</div>
                          {template.modules.map((module, idx) => (
                            <div key={idx} className="bg-slate-900/50 rounded p-2 text-xs">
                              <div className="text-blue-400 font-semibold">{module.module}</div>
                              <div className="text-gray-500 mt-1">
                                Budget: ${module.budget.toLocaleString()} • Max Risk: ${module.max_risk_per_trade}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Recommended For */}
                      <div className="mt-4 pt-3 border-t border-slate-700/50">
                        <div className="text-xs text-gray-500 mb-1">👤 Recommended for:</div>
                        <div className="text-xs text-gray-400">{template.recommended_for}</div>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                /* Customize Template */
                <div className="space-y-6">
                  {/* Selected Template Card */}
                  <div className="bg-slate-800/50 border border-blue-500/30 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <span className="text-4xl">{selectedTemplate.icon}</span>
                        <div>
                          <h3 className="text-xl font-bold text-white">{selectedTemplate.name}</h3>
                          <p className="text-sm text-gray-400">{selectedTemplate.description}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => setSelectedTemplate(null)}
                        className="text-gray-400 hover:text-white text-sm"
                      >
                        ← Back
                      </button>
                    </div>

                    {/* Customization Form */}
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-300 mb-2">
                          Mindfolio Name
                        </label>
                        <input
                          type="text"
                          value={mindfolioName}
                          onChange={(e) => setMindfolioName(e.target.value)}
                          placeholder="My Trading Account"
                          className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-3 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                        />
                      </div>

                      <div className="bg-slate-900/50 rounded-lg p-4">
                        <div className="text-sm text-gray-400 mb-2">Starting Balance</div>
                        <div className="text-2xl font-bold text-green-400">
                          ${selectedTemplate.starting_balance.toLocaleString('en-US')}
                        </div>
                      </div>

                      {selectedTemplate.modules.length > 0 && (
                        <div>
                          <div className="text-sm font-semibold text-gray-300 mb-3">
                            Pre-configured Modules ({selectedTemplate.modules.length})
                          </div>
                          <div className="space-y-2">
                            {selectedTemplate.modules.map((module, idx) => (
                              <div key={idx} className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50">
                                <div className="flex items-center justify-between mb-2">
                                  <span className="text-white font-semibold">{module.module}</span>
                                  <span className="text-sm text-gray-500">
                                    {module.autotrade ? '🤖 Auto' : '👤 Manual'}
                                  </span>
                                </div>
                                <div className="grid grid-cols-3 gap-2 text-xs text-gray-400">
                                  <div>
                                    <div className="text-gray-500">Budget</div>
                                    <div className="text-white font-mono">${module.budget.toLocaleString()}</div>
                                  </div>
                                  <div>
                                    <div className="text-gray-500">Max Risk</div>
                                    <div className="text-white font-mono">${module.max_risk_per_trade}</div>
                                  </div>
                                  <div>
                                    <div className="text-gray-500">Daily Limit</div>
                                    <div className="text-white font-mono">${module.daily_loss_limit || 0}</div>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center justify-end gap-3">
                    <button
                      onClick={() => setSelectedTemplate(null)}
                      className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-semibold transition-colors"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleCreate}
                      disabled={!mindfolioName.trim() || creating}
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {creating ? 'Creating...' : '✓ Create Mindfolio'}
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
