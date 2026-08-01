import React, { useState } from 'react';

export const BillingCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Billing & Licensing</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Acme Corp Global</span>
            <span className="text-[10px] text-blue-400 font-mono">Professional Tier • Active</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="text-white/60 hover:text-white text-sm font-medium transition-colors">Download Invoices</button>
          <button className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(37,99,235,0.4)]">Upgrade to Enterprise</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Commercial</h3>
            <button 
              onClick={() => setActiveTab('overview')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'overview' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">📊</span> Overview & Usage
            </button>
            <button 
              onClick={() => setActiveTab('licenses')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'licenses' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">👥</span> Seats & Licenses
            </button>
            <button 
              onClick={() => setActiveTab('invoices')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'invoices' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">📄</span> Invoices & Payments
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'overview' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Current Billing Cycle</h2>
                    <p className="text-sm text-white/60 mt-1">July 1, 2026 - July 31, 2026</p>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] uppercase font-bold text-white/40 mb-1">Estimated Upcoming Invoice</div>
                    <div className="text-3xl font-bold text-white font-mono">$349.50</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  {/* Current Plan */}
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl"></div>
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <h4 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-1">Current Plan</h4>
                        <div className="text-2xl font-bold text-white flex items-center gap-2">
                          Professional <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded">ACTIVE</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-white">$299.00</div>
                        <div className="text-[10px] text-white/60">/ month base</div>
                      </div>
                    </div>
                    
                    <div className="space-y-3 pt-4 border-t border-white/10">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-white/80">✅ Up to 5 Autonomous Agents</span>
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-white/80">✅ Full Public API Access</span>
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-white/80">✅ Standard Workflow Engine</span>
                      </div>
                    </div>
                  </div>

                  {/* Metered Usage */}
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md">
                    <h4 className="text-sm font-bold text-white mb-6">Metered Overages (This Month)</h4>
                    
                    <div className="space-y-6">
                      {/* LLM Tokens */}
                      <div>
                        <div className="flex justify-between text-xs mb-2">
                          <span className="text-white/80 font-bold">LLM Token Usage</span>
                          <span className="font-mono text-white/60">2,500,000 tokens <span className="text-blue-400 ml-2">($50.50)</span></span>
                        </div>
                        <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500 w-[60%]"></div>
                        </div>
                        <div className="mt-1 text-[10px] text-white/40">Billed at $0.02 per 1k tokens</div>
                      </div>

                      {/* API Calls */}
                      <div>
                        <div className="flex justify-between text-xs mb-2">
                          <span className="text-white/80 font-bold">Public API Requests</span>
                          <span className="font-mono text-white/60">45,000 / 100,000 free</span>
                        </div>
                        <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                          <div className="h-full bg-emerald-500 w-[45%]"></div>
                        </div>
                        <div className="mt-1 text-[10px] text-white/40">Included in Professional Plan</div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'licenses' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">License & Entitlements</h2>
                    <p className="text-sm text-white/60 mt-1">Manage seat allocations and feature quotas.</p>
                  </div>
                  <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">Purchase More Seats</button>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md flex flex-col items-center justify-center py-8">
                    <div className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2">User Seats</div>
                    <div className="text-4xl font-bold text-white font-mono mb-1">12 <span className="text-white/20">/ 15</span></div>
                    <div className="text-xs text-emerald-400">3 Seats Available</div>
                  </div>
                  
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md flex flex-col items-center justify-center py-8">
                    <div className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2">Active AI Agents</div>
                    <div className="text-4xl font-bold text-white font-mono mb-1">5 <span className="text-white/20">/ 5</span></div>
                    <div className="text-xs text-rose-400">Entitlement Cap Reached</div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'invoices' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Payment History</h2>
                    <p className="text-sm text-white/60 mt-1">Past invoices and receipts.</p>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl shadow-lg backdrop-blur-md overflow-hidden font-mono text-xs">
                  <div className="p-3 bg-white/5 border-b border-white/10 flex gap-4 text-white/40 uppercase font-bold tracking-wider text-[10px]">
                    <div className="w-32">Date</div>
                    <div className="w-48">Invoice Number</div>
                    <div className="w-24 text-right">Amount</div>
                    <div className="w-24 text-center">Status</div>
                    <div className="flex-1 text-right"></div>
                  </div>
                  <div className="divide-y divide-white/5">
                    <div className="p-3 flex items-center gap-4 hover:bg-white/5 transition-colors">
                      <div className="w-32 text-white/60">Jun 30, 2026</div>
                      <div className="w-48 text-white">INV-2026-06-A1B2</div>
                      <div className="w-24 text-right text-white font-bold">$324.00</div>
                      <div className="w-24 text-center"><span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded">PAID</span></div>
                      <div className="flex-1 text-right text-blue-400 hover:text-blue-300 cursor-pointer">Download PDF ⬇</div>
                    </div>
                    <div className="p-3 flex items-center gap-4 hover:bg-white/5 transition-colors">
                      <div className="w-32 text-white/60">May 31, 2026</div>
                      <div className="w-48 text-white">INV-2026-05-X9Y8</div>
                      <div className="w-24 text-right text-white font-bold">$299.00</div>
                      <div className="w-24 text-center"><span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded">PAID</span></div>
                      <div className="flex-1 text-right text-blue-400 hover:text-blue-300 cursor-pointer">Download PDF ⬇</div>
                    </div>
                  </div>
                </div>
              </>
            )}

          </div>
        </div>

      </div>
    </div>
  );
};
