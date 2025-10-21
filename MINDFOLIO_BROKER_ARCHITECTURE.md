# Mindfolio Manager - Broker Accounts Architecture

> **Data:** 20 Octombrie 2025  
> **Status:** NEW REQUIREMENT - Critical architectural change  
> **Priority:** HIGHEST - Must implement before other features

---

## 🎯 Overview

Mindfolio Manager trebuie reorganizat pentru a gestiona conturi pe **multiple brokeri** cu **environments separate** (SIM/LIVE) și **tipuri de conturi** (Equity, Futures, Crypto).

### Hierarchy Structure

```
Mindfolio Manager (Root)
├── TradeStation (Tab 1)
│   ├── SIM (Sub-tab/Branch)
│   │   ├── Account Type Dropdown: [All | Equity | Futures | Crypto]
│   │   └── Mindfolios filtered by: broker=TradeStation, env=SIM, account_type=selected
│   └── LIVE (Sub-tab/Branch)
│       ├── Account Type Dropdown: [All | Equity | Futures | Crypto]
│       └── Mindfolios filtered by: broker=TradeStation, env=LIVE, account_type=selected
└── TastyTrade (Tab 2)
    ├── SIM (Sub-tab/Branch)
    │   ├── Account Type Dropdown: [All | Equity | Futures | Crypto]
    │   └── Mindfolios filtered by: broker=TastyTrade, env=SIM, account_type=selected
    └── LIVE (Sub-tab/Branch)
        ├── Account Type Dropdown: [All | Equity | Futures | Crypto]
        └── Mindfolios filtered by: broker=TastyTrade, env=LIVE, account_type=selected
```

---

## 📊 Data Model Changes

### Backend: Mindfolio Model Extension

**File:** `backend/mindfolio.py`  
**Current Model (lines 82-89):**
```python
class Mindfolio(BaseModel):
    id: str
    name: str
    cash_balance: float
    starting_balance: float = 10000.0
    status: str = "ACTIVE"
    modules: List[ModuleAllocation] = []
    created_at: str
    updated_at: str
```

**NEW Model (with broker fields):**
```python
class Mindfolio(BaseModel):
    id: str
    name: str
    
    # Broker account information
    broker: str  # "TradeStation" | "TastyTrade"
    environment: str  # "SIM" | "LIVE"
    account_type: str  # "Equity" | "Futures" | "Crypto"
    account_id: Optional[str] = None  # Broker's account number (optional)
    
    # Financial data
    cash_balance: float
    starting_balance: float = 10000.0
    status: str = "ACTIVE"  # ACTIVE, PAUSED, CLOSED
    
    # Configuration
    modules: List[ModuleAllocation] = []
    
    # Metadata
    created_at: str
    updated_at: str
```

### Backend: MindfolioCreate Model Extension

```python
class MindfolioCreate(BaseModel):
    name: str
    
    # NEW: Required broker fields
    broker: str  # Validate: must be "TradeStation" or "TastyTrade"
    environment: str  # Validate: must be "SIM" or "LIVE"
    account_type: str  # Validate: must be "Equity", "Futures", or "Crypto"
    account_id: Optional[str] = None  # Optional broker account number
    
    starting_balance: float = 10000.0
    modules: List[ModuleAllocation] = []
    
    @validator('broker')
    def validate_broker(cls, v):
        if v not in ["TradeStation", "TastyTrade"]:
            raise ValueError('broker must be TradeStation or TastyTrade')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ["SIM", "LIVE"]:
            raise ValueError('environment must be SIM or LIVE')
        return v
    
    @validator('account_type')
    def validate_account_type(cls, v):
        if v not in ["Equity", "Futures", "Crypto"]:
            raise ValueError('account_type must be Equity, Futures, or Crypto')
        return v
```

### Backend: API Endpoints Extension

**GET /api/mindfolio** - Add query params for filtering:
```python
@router.get("", response_model=List[Mindfolio])
async def list_mindfolios(
    broker: Optional[str] = None,  # Filter by broker
    environment: Optional[str] = None,  # Filter by SIM/LIVE
    account_type: Optional[str] = None,  # Filter by account type
    status: Optional[str] = None  # Existing filter
):
    """List mindfolios with optional filtering by broker/env/type"""
    all_mindfolios = await pf_list()
    
    # Apply filters
    filtered = all_mindfolios
    if broker:
        filtered = [p for p in filtered if p.broker == broker]
    if environment:
        filtered = [p for p in filtered if p.environment == environment]
    if account_type:
        filtered = [p for p in filtered if p.account_type == account_type]
    if status:
        filtered = [p for p in filtered if p.status == status]
    
    return filtered
```

---

## 🎨 Frontend UI Design

### Main Layout - Tab Structure

**File:** `frontend/src/pages/MindfolioList.jsx`

```jsx
export default function MindfolioList() {
  // State for broker/environment navigation
  const [activeBroker, setActiveBroker] = useState('TradeStation'); // TradeStation | TastyTrade
  const [activeEnvironment, setActiveEnvironment] = useState('SIM'); // SIM | LIVE
  const [selectedAccountType, setSelectedAccountType] = useState('All'); // All | Equity | Futures | Crypto
  
  // Fetch all mindfolios
  const [items, setItems] = useState([]);
  
  // Filter items based on selections
  const filteredItems = React.useMemo(() => {
    let result = items.filter(p => 
      p.broker === activeBroker && 
      p.environment === activeEnvironment
    );
    
    if (selectedAccountType !== 'All') {
      result = result.filter(p => p.account_type === selectedAccountType);
    }
    
    return result;
  }, [items, activeBroker, activeEnvironment, selectedAccountType]);
  
  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white mb-2">Mindfolio Manager</h1>
          <p className="text-gray-400">Multi-broker mindfolio management</p>
        </div>
        <Link 
          to="/mindfolio/new" 
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
        >
          + Create Mindfolio
        </Link>
      </div>
      
      {/* BROKER TABS */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-1">
        <div className="flex gap-1">
          <button
            onClick={() => setActiveBroker('TradeStation')}
            className={`flex-1 px-6 py-3 rounded-lg font-semibold transition ${
              activeBroker === 'TradeStation'
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-slate-700'
            }`}
          >
            TradeStation
          </button>
          <button
            onClick={() => setActiveBroker('TastyTrade')}
            className={`flex-1 px-6 py-3 rounded-lg font-semibold transition ${
              activeBroker === 'TastyTrade'
                ? 'bg-orange-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-slate-700'
            }`}
          >
            TastyTrade
          </button>
        </div>
      </div>
      
      {/* ENVIRONMENT SUB-TABS */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveEnvironment('SIM')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              activeEnvironment === 'SIM'
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                : 'text-gray-400 hover:text-white border border-slate-700'
            }`}
          >
            SIM (Paper Trading)
          </button>
          <button
            onClick={() => setActiveEnvironment('LIVE')}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              activeEnvironment === 'LIVE'
                ? 'bg-red-500/20 text-red-400 border border-red-500/50'
                : 'text-gray-400 hover:text-white border border-slate-700'
            }`}
          >
            LIVE (Real Money)
          </button>
        </div>
        
        {/* ACCOUNT TYPE DROPDOWN */}
        <select
          value={selectedAccountType}
          onChange={(e) => setSelectedAccountType(e.target.value)}
          className="px-4 py-2 bg-gray-900 border border-gray-700 text-white rounded-lg"
        >
          <option value="All">All Account Types</option>
          <option value="Equity">Equity</option>
          <option value="Futures">Futures</option>
          <option value="Crypto">Crypto</option>
        </select>
      </div>
      
      {/* STATS CARDS - Per Broker/Environment */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">
            {activeBroker} {activeEnvironment} Accounts
          </div>
          <div className="text-xl font-bold text-white">
            {filteredItems.length}
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Total Balance</div>
          <div className={`text-xl font-bold ${
            activeEnvironment === 'SIM' ? 'text-blue-400' : 'text-green-400'
          }`}>
            ${filteredItems.reduce((sum, p) => sum + p.cash_balance, 0).toLocaleString()}
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Active</div>
          <div className="text-xl font-bold text-green-400">
            {filteredItems.filter(p => p.status === 'ACTIVE').length}
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Paused</div>
          <div className="text-xl font-bold text-yellow-400">
            {filteredItems.filter(p => p.status === 'PAUSED').length}
          </div>
        </div>
      </div>
      
      {/* MINDFOLIO CARDS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredItems.map(p => (
          <MindfolioCard 
            key={p.id} 
            mindfolio={p} 
            broker={activeBroker}
            environment={activeEnvironment}
          />
        ))}
      </div>
    </div>
  );
}
```

### Mindfolio Card - With Broker Context

```jsx
function MindfolioCard({ mindfolio, broker, environment }) {
  // Color scheme per broker
  const brokerColors = {
    TradeStation: {
      primary: 'blue',
      bg: 'bg-blue-500/20',
      border: 'border-blue-500/30',
      text: 'text-blue-400'
    },
    TastyTrade: {
      primary: 'orange',
      bg: 'bg-orange-500/20',
      border: 'border-orange-500/30',
      text: 'text-orange-400'
    }
  };
  
  // Environment badge color
  const envColor = environment === 'SIM' 
    ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    : 'bg-red-500/20 text-red-400 border-red-500/30';
  
  const colors = brokerColors[broker];
  
  return (
    <Link 
      to={`/mindfolio/${mindfolio.id}`}
      className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800 transition"
    >
      {/* Header with Broker Badge */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="text-base font-bold text-white mb-1">
            {mindfolio.name}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className={`px-2 py-1 rounded ${colors.bg} ${colors.text} ${colors.border} border`}>
              {broker}
            </span>
            <span className={`px-2 py-1 rounded border ${envColor}`}>
              {environment}
            </span>
            <span className="px-2 py-1 rounded bg-gray-500/20 text-gray-400 border border-gray-500/30">
              {mindfolio.account_type}
            </span>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${
          mindfolio.status === 'ACTIVE' 
            ? 'bg-green-500/20 text-green-400 border-green-500/30'
            : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
        }`}>
          {mindfolio.status}
        </div>
      </div>
      
      {/* Account ID (if exists) */}
      {mindfolio.account_id && (
        <div className="text-xs text-gray-500 mb-3">
          Account: {mindfolio.account_id}
        </div>
      )}
      
      {/* Balance */}
      <div className="bg-slate-900/50 rounded-lg p-4 mb-4">
        <div className="text-sm text-gray-400 mb-1">Cash Balance</div>
        <div className={`text-lg font-bold ${
          environment === 'SIM' ? 'text-blue-400' : 'text-green-400'
        }`}>
          ${mindfolio.cash_balance.toLocaleString()}
        </div>
      </div>
      
      {/* ROI Badge (if has starting_balance) */}
      {mindfolio.starting_balance && (
        <div className="bg-slate-900/50 rounded-lg p-4 mb-4">
          <div className="text-sm text-gray-400 mb-1">ROI</div>
          <div className={`text-lg font-bold ${
            ((mindfolio.cash_balance - mindfolio.starting_balance) / mindfolio.starting_balance) > 0
              ? 'text-green-400'
              : 'text-red-400'
          }`}>
            {(((mindfolio.cash_balance - mindfolio.starting_balance) / mindfolio.starting_balance) * 100).toFixed(2)}%
          </div>
        </div>
      )}
      
      {/* Modules */}
      <div className="space-y-2">
        <div className="text-sm text-gray-400 font-semibold">
          Modules ({mindfolio.modules?.length || 0})
        </div>
        {mindfolio.modules && mindfolio.modules.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {mindfolio.modules.map((m, idx) => (
              <div 
                key={idx}
                className={`px-2 py-1 text-xs rounded border ${colors.bg} ${colors.text} ${colors.border}`}
              >
                {m.module}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-gray-500">No modules configured</div>
        )}
      </div>
    </Link>
  );
}
```

---

## 📝 Create Form Changes

**File:** `frontend/src/pages/MindfolioCreate.jsx`

```jsx
export default function MindfolioCreate() {
  const [formData, setFormData] = useState({
    name: '',
    broker: 'TradeStation',  // NEW
    environment: 'SIM',      // NEW
    account_type: 'Equity',  // NEW
    account_id: '',          // NEW (optional)
    starting_balance: 10000,
    modules: []
  });
  
  return (
    <div className="p-8">
      <h1 className="text-xl font-bold text-white mb-6">Create New Mindfolio</h1>
      
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 space-y-6">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Mindfolio Name
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2"
            placeholder="My Trading Strategy"
          />
        </div>
        
        {/* BROKER SELECTION */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Broker
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="broker"
                value="TradeStation"
                checked={formData.broker === 'TradeStation'}
                onChange={(e) => setFormData({...formData, broker: e.target.value})}
                className="w-4 h-4"
              />
              <span className="text-white">TradeStation</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="broker"
                value="TastyTrade"
                checked={formData.broker === 'TastyTrade'}
                onChange={(e) => setFormData({...formData, broker: e.target.value})}
                className="w-4 h-4"
              />
              <span className="text-white">TastyTrade</span>
            </label>
          </div>
        </div>
        
        {/* ENVIRONMENT SELECTION */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Environment
          </label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="environment"
                value="SIM"
                checked={formData.environment === 'SIM'}
                onChange={(e) => setFormData({...formData, environment: e.target.value})}
                className="w-4 h-4"
              />
              <span className="text-white">SIM (Paper Trading)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="environment"
                value="LIVE"
                checked={formData.environment === 'LIVE'}
                onChange={(e) => setFormData({...formData, environment: e.target.value})}
                className="w-4 h-4"
              />
              <span className="text-white">LIVE (Real Money)</span>
            </label>
          </div>
        </div>
        
        {/* ACCOUNT TYPE SELECTION */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Account Type
          </label>
          <select
            value={formData.account_type}
            onChange={(e) => setFormData({...formData, account_type: e.target.value})}
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2"
          >
            <option value="Equity">Equity (Stocks & Options)</option>
            <option value="Futures">Futures</option>
            <option value="Crypto">Crypto</option>
          </select>
        </div>
        
        {/* ACCOUNT ID (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Account ID (Optional)
          </label>
          <input
            type="text"
            value={formData.account_id}
            onChange={(e) => setFormData({...formData, account_id: e.target.value})}
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2"
            placeholder="e.g. TS123456 or TT987654"
          />
          <div className="text-xs text-gray-500 mt-1">
            Your broker's account number (if linking to real account)
          </div>
        </div>
        
        {/* Starting Balance */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Starting Balance
          </label>
          <input
            type="number"
            value={formData.starting_balance}
            onChange={(e) => setFormData({...formData, starting_balance: parseFloat(e.target.value)})}
            className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2"
          />
        </div>
        
        {/* Submit */}
        <div className="flex gap-4">
          <button
            onClick={handleCreate}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold"
          >
            Create Mindfolio
          </button>
          <Link
            to="/mindfolio"
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold"
          >
            Cancel
          </Link>
        </div>
      </div>
    </div>
  );
}
```

---

## 🎯 Stats Cards - Broker Breakdown

**NEW Stats Layout (2x2 grid for Broker × Environment):**

```jsx
{/* Global Stats - All Brokers Summary */}
<div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
    <div className="text-sm text-gray-400 mb-1">All Accounts</div>
    <div className="text-xl font-bold text-white">{allItems.length}</div>
  </div>
  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
    <div className="text-sm text-gray-400 mb-1">Total Balance</div>
    <div className="text-xl font-bold text-green-400">
      ${allItems.reduce((s, p) => s + p.cash_balance, 0).toLocaleString()}
    </div>
  </div>
  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
    <div className="text-sm text-gray-400 mb-1">SIM Total</div>
    <div className="text-xl font-bold text-blue-400">
      ${allItems.filter(p => p.environment === 'SIM').reduce((s, p) => s + p.cash_balance, 0).toLocaleString()}
    </div>
  </div>
  <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
    <div className="text-sm text-gray-400 mb-1">LIVE Total</div>
    <div className="text-xl font-bold text-red-400">
      ${allItems.filter(p => p.environment === 'LIVE').reduce((s, p) => s + p.cash_balance, 0).toLocaleString()}
    </div>
  </div>
</div>

{/* Per-Broker Breakdown (2x2) */}
<div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
  {/* TradeStation SIM */}
  <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-6">
    <div className="flex items-center gap-2 mb-2">
      <span className="text-blue-400 font-semibold">TradeStation</span>
      <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">SIM</span>
    </div>
    <div className="text-2xl font-bold text-white mb-1">
      {allItems.filter(p => p.broker === 'TradeStation' && p.environment === 'SIM').length}
    </div>
    <div className="text-sm text-blue-400">
      ${allItems.filter(p => p.broker === 'TradeStation' && p.environment === 'SIM').reduce((s, p) => s + p.cash_balance, 0).toLocaleString()}
    </div>
  </div>
  
  {/* TradeStation LIVE */}
  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
    <div className="flex items-center gap-2 mb-2">
      <span className="text-blue-400 font-semibold">TradeStation</span>
      <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded">LIVE</span>
    </div>
    <div className="text-2xl font-bold text-white mb-1">
      {allItems.filter(p => p.broker === 'TradeStation' && p.environment === 'LIVE').length}
    </div>
    <div className="text-sm text-red-400">
      ${allItems.filter(p => p.broker === 'TradeStation' && p.environment === 'LIVE').reduce((s, p) => s + p.cash_balance, 0).toLocaleString()}
    </div>
  </div>
  
  {/* TastyTrade SIM */}
  <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-6">
    <div className="flex items-center gap-2 mb-2">
      <span className="text-orange-400 font-semibold">TastyTrade</span>
      <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">SIM</span>
    </div>
    <div className="text-2xl font-bold text-white mb-1">
      {allItems.filter(p => p.broker === 'TastyTrade' && p.environment === 'SIM').length}
    </div>
    <div className="text-sm text-blue-400">
      ${allItems.filter(p => p.broker === 'TastyTrade' && p.environment === 'SIM').reduce((s, p) => s + p.cash_balance, 0).toLocaleString()}
    </div>
  </div>
  
  {/* TastyTrade LIVE */}
  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
    <div className="flex items-center gap-2 mb-2">
      <span className="text-orange-400 font-semibold">TastyTrade</span>
      <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded">LIVE</span>
    </div>
    <div className="text-2xl font-bold text-white mb-1">
      {allItems.filter(p => p.broker === 'TastyTrade' && p.environment === 'LIVE').length}
    </div>
    <div className="text-sm text-red-400">
      ${allItems.filter(p => p.broker === 'TastyTrade' && p.environment === 'LIVE').reduce((s, p) => s + p.cash_balance, 0).toLocaleString()}
    </div>
  </div>
</div>
```

---

## 🔄 Quick Actions - Context-Aware

```jsx
// Quick Actions pe card hover - different per environment
<div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
  <div className="flex gap-2">
    {/* SIM accounts: Reset button */}
    {environment === 'SIM' && (
      <button 
        onClick={(e) => { 
          e.preventDefault(); 
          handleReset(mindfolio.id); 
        }}
        className="p-2 bg-blue-500/20 hover:bg-blue-500/30 rounded text-blue-400"
        title="Reset to Starting Balance"
      >
        <RefreshIcon className="w-4 h-4" />
      </button>
    )}
    
    {/* Pause/Resume (all accounts) */}
    <button 
      onClick={(e) => { 
        e.preventDefault(); 
        handleTogglePause(mindfolio.id); 
      }}
      className="p-2 bg-yellow-500/20 hover:bg-yellow-500/30 rounded text-yellow-400"
      title={mindfolio.status === 'ACTIVE' ? 'Pause' : 'Resume'}
    >
      <PauseIcon className="w-4 h-4" />
    </button>
    
    {/* Delete - Extra confirm for LIVE */}
    <button 
      onClick={(e) => { 
        e.preventDefault(); 
        if (environment === 'LIVE') {
          setShowLiveDeleteModal(mindfolio.id);
        } else {
          handleDelete(mindfolio.id);
        }
      }}
      className="p-2 bg-red-500/20 hover:bg-red-500/30 rounded text-red-400"
      title="Delete"
    >
      <TrashIcon className="w-4 h-4" />
    </button>
  </div>
</div>

{/* LIVE Delete Confirmation Modal */}
{showLiveDeleteModal === mindfolio.id && (
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
    <div className="bg-slate-800 border border-red-500 rounded-lg p-6 max-w-md">
      <h3 className="text-lg font-bold text-red-400 mb-3">
        Delete LIVE Account?
      </h3>
      <p className="text-gray-300 mb-4">
        You are about to delete a LIVE trading account. This action cannot be undone.
      </p>
      <p className="text-sm text-gray-400 mb-6">
        Account: <span className="text-white font-mono">{mindfolio.account_id || mindfolio.id}</span>
      </p>
      <div className="flex gap-3">
        <button
          onClick={() => {
            handleDelete(mindfolio.id);
            setShowLiveDeleteModal(null);
          }}
          className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-semibold"
        >
          Yes, Delete LIVE Account
        </button>
        <button
          onClick={() => setShowLiveDeleteModal(null)}
          className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded font-semibold"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
)}
```

---

## 🚀 Implementation Priority

### Phase 0: Foundation (CRITICAL - Do First)

1. **Backend Model Extension**
   - ✅ Add broker, environment, account_type, account_id fields to Mindfolio model
   - ✅ Add validators to MindfolioCreate
   - ✅ Update create_mindfolio() to save new fields
   - ✅ Add filtering to list_mindfolios() endpoint

2. **Test Backend with curl**
   ```bash
   curl -X POST http://localhost:8000/api/mindfolio \
     -H "Content-Type: application/json" \
     -d '{
       "name": "TS SIM Equity Test",
       "broker": "TradeStation",
       "environment": "SIM",
       "account_type": "Equity",
       "starting_balance": 10000
     }'
   ```

3. **Frontend State Management**
   - Add activeBroker, activeEnvironment, selectedAccountType state
   - Implement filtering logic based on selections
   - Update API calls to include new fields

### Phase 1: UI Implementation (Week 1)

1. **Broker Tabs** - Main navigation (TradeStation/TastyTrade)
2. **Environment Sub-tabs** - SIM/LIVE branches
3. **Account Type Dropdown** - Filter by Equity/Futures/Crypto
4. **Update Cards** - Show broker badges and environment colors
5. **Stats Cards Breakdown** - Per-broker/environment totals

### Phase 2: Create Form (Week 1)

1. **Broker Selection** - Radio buttons (TradeStation/TastyTrade)
2. **Environment Selection** - Radio buttons (SIM/LIVE)
3. **Account Type Dropdown** - Select Equity/Futures/Crypto
4. **Account ID Input** - Optional field for broker account number
5. **Validation** - Ensure valid combinations

### Phase 3: Context-Aware Features (Week 2)

1. **Quick Actions** - Different per environment (Reset for SIM, extra confirm for LIVE)
2. **ROI Display** - Color coding based on environment
3. **Detail Page** - Show broker info in header
4. **Bulk Operations** - Broker-aware (can't mix brokers in bulk actions)

### Phase 4: Advanced Features (Week 3+)

1. **Charts** - Per-broker performance comparison
2. **Analytics** - Broker-specific metrics
3. **Export** - Include broker/env metadata
4. **Advanced Filters** - Multi-broker selection

---

## 📋 Validation Rules

### Broker-Specific Rules

**TradeStation:**
- ✅ SIM: All account types (Equity, Futures, Crypto)
- ✅ LIVE: All account types (Equity, Futures, Crypto)
- ✅ Account ID format: `TS[0-9]{6}` (optional)

**TastyTrade:**
- ✅ SIM: All account types (Equity, Futures, Crypto)
- ✅ LIVE: All account types (Equity, Futures, Crypto)
- ✅ Account ID format: `TT[0-9]{6}` (optional)

### Business Rules

1. **Cannot mix brokers** in bulk operations
2. **Cannot mix environments** (SIM/LIVE) in bulk operations
3. **LIVE accounts** require extra confirmation for delete
4. **SIM accounts** can be reset to starting balance
5. **Account ID** is optional but recommended for LIVE accounts

---

## 🎨 Color Schemes

### Broker Colors

**TradeStation:**
- Primary: Blue (`blue-600`, `blue-500`, `blue-400`)
- Background: `bg-blue-500/20`
- Border: `border-blue-500/30`
- Text: `text-blue-400`

**TastyTrade:**
- Primary: Orange (`orange-600`, `orange-500`, `orange-400`)
- Background: `bg-orange-500/20`
- Border: `border-orange-500/30`
- Text: `text-orange-400`

### Environment Colors

**SIM (Paper Trading):**
- Primary: Blue tones
- Badge: `bg-blue-500/20 text-blue-400 border-blue-500/30`
- Balance: `text-blue-400`

**LIVE (Real Money):**
- Primary: Red/Green (P&L dependent)
- Badge: `bg-red-500/20 text-red-400 border-red-500/30`
- Balance: `text-green-400` (profit) or `text-red-400` (loss)

---

## 📝 Notes

- **Migration:** Existing mindfolios need default values: `broker='TradeStation', environment='SIM', account_type='Equity'`
- **Sidebar:** Update nav.simple.js to show broker/env counts in mindfolio dropdown
- **Detail Page:** Add broker info to header (breadcrumb: Manager → TradeStation → SIM → Mindfolio Name)
- **API:** Consider `/api/mindfolio/brokers` endpoint to list available brokers
- **Future:** Add broker-specific features (TS OAuth, TastyTrade API integration)

---

**Last Updated:** 20 Octombrie 2025  
**Critical Priority:** Must implement BEFORE other manager features  
**Estimated Time:** 2-3 days for full implementation
