import React, { useState } from 'react';

export const FeatureStoreCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('catalog');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Enterprise Feature Store</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Global Feature Catalog</span>
            <span className="text-[10px] text-teal-400 font-mono">14,204 Materialized Features</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="px-4 py-1.5 bg-teal-600 hover:bg-teal-500 text-white rounded-lg text-sm font-bold transition-colors shadow-[0_0_15px_rgba(20,184,166,0.3)] flex items-center gap-2">
            <span>+</span> Register Feature
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Data Operations</h3>
            <button 
              onClick={() => setActiveTab('catalog')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'catalog' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">📚</span> Feature Catalog
            </button>
            <button 
              onClick={() => setActiveTab('lineage')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'lineage' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🧬</span> Feature Lineage
            </button>
            <button 
              onClick={() => setActiveTab('health')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'health' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🩺</span> Health & Drift
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'catalog' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Feature Catalog</h2>
                    <p className="text-sm text-white/60 mt-1">Single source of truth for all reusable AI variables across training and serving.</p>
                  </div>
                  <div className="flex gap-2">
                    <input type="text" placeholder="Search features..." className="w-64 bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-white outline-none focus:border-teal-500" />
                    <button className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-bold transition-colors">Filter</button>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {/* Feature Row 1 */}
                  <div className="glass-card bg-black/80 border border-teal-500/30 rounded-xl p-5 shadow-[0_0_15px_rgba(20,184,166,0.1)] backdrop-blur-md flex flex-col gap-4">
                    <div className="flex justify-between items-start">
                      <div className="flex gap-4">
                        <div className="w-10 h-10 rounded bg-teal-500/20 flex items-center justify-center shrink-0 border border-teal-500/30">
                          <span className="text-teal-400 text-xs font-bold">NUM</span>
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-base font-bold text-white font-mono">decision_maker_engaged_90d</h3>
                            <span className="px-2 py-0.5 bg-teal-500 text-black text-[10px] font-bold rounded">PRODUCTION</span>
                            <span className="text-[10px] text-white/40 border border-white/10 px-2 py-0.5 rounded">v2.1.0</span>
                          </div>
                          <p className="text-xs text-white/60">Count of unique decision-maker interactions across email, calls, and meetings in a 90-day rolling window.</p>
                        </div>
                      </div>
                      <div className="flex flex-col items-end shrink-0">
                        <span className="text-[10px] text-white/40 uppercase font-bold mb-1">Dependent Models</span>
                        <div className="flex gap-1">
                          <span className="px-2 py-0.5 bg-white/10 text-white/80 text-[10px] rounded">DealRiskNet</span>
                          <span className="px-2 py-0.5 bg-white/10 text-white/80 text-[10px] rounded">BuyingWindowNet</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Feature Row 2 */}
                  <div className="glass-card bg-black/80 border border-indigo-500/30 rounded-xl p-5 shadow-[0_0_15px_rgba(99,102,241,0.1)] backdrop-blur-md flex flex-col gap-4">
                    <div className="flex justify-between items-start">
                      <div className="flex gap-4">
                        <div className="w-10 h-10 rounded bg-indigo-500/20 flex items-center justify-center shrink-0 border border-indigo-500/30">
                          <span className="text-indigo-400 text-xs font-bold">EMB</span>
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-base font-bold text-white font-mono">competitive_threat_vector</h3>
                            <span className="px-2 py-0.5 bg-white/10 text-white/80 text-[10px] font-bold rounded">DRAFT</span>
                            <span className="text-[10px] text-white/40 border border-white/10 px-2 py-0.5 rounded">v1.0.0</span>
                          </div>
                          <p className="text-xs text-white/60">Dense vector embedding (1536d) representing the contextual threat of competitor mentions in recent call transcripts.</p>
                        </div>
                      </div>
                      <div className="flex flex-col items-end shrink-0">
                        <span className="text-[10px] text-white/40 uppercase font-bold mb-1">Dependent Models</span>
                        <div className="flex gap-1">
                          <span className="px-2 py-0.5 bg-white/5 text-white/40 text-[10px] rounded">None (Draft)</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'lineage' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Feature Lineage Viewer</h2>
                    <p className="text-sm text-white/60 mt-1">Cryptographic origin tracking for AI compliance.</p>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-8 shadow-lg backdrop-blur-md overflow-hidden relative">
                  
                  {/* Central line */}
                  <div className="absolute top-8 bottom-8 left-1/2 w-0.5 bg-white/10 -translate-x-1/2 z-0"></div>

                  <div className="relative z-10 flex flex-col gap-8">
                    
                    {/* Source System */}
                    <div className="flex justify-between items-center w-full">
                      <div className="w-5/12 text-right pr-8">
                        <h4 className="text-lg font-bold text-white">CRM Data Warehouse</h4>
                        <p className="text-xs text-white/60 mt-1">Raw tables: `events_log`, `contacts`</p>
                      </div>
                      <div className="w-10 h-10 rounded-full bg-blue-500/20 border border-blue-500/50 flex items-center justify-center shrink-0">
                        <span className="text-blue-400">1</span>
                      </div>
                      <div className="w-5/12 pl-8">
                        <div className="p-3 bg-white/5 rounded-lg border border-white/10 text-xs text-white/80 font-mono">
                          SELECT contact_id, timestamp, type FROM raw.events WHERE type IN ('call', 'email')
                        </div>
                      </div>
                    </div>

                    {/* Transformation Logic */}
                    <div className="flex justify-between items-center w-full">
                      <div className="w-5/12 text-right pr-8">
                        <div className="p-3 bg-fuchsia-500/5 rounded-lg border border-fuchsia-500/20 text-xs text-fuchsia-400 font-mono text-left inline-block">
                          events.filter(time &gt; now - 90d)<br/>
                          .join(contacts, on='contact_id')<br/>
                          .filter(contacts.role == 'Decision Maker')<br/>
                          .group_by('company_id').count()
                        </div>
                      </div>
                      <div className="w-10 h-10 rounded-full bg-fuchsia-500/20 border border-fuchsia-500/50 flex items-center justify-center shrink-0">
                        <span className="text-fuchsia-400">2</span>
                      </div>
                      <div className="w-5/12 pl-8">
                        <h4 className="text-lg font-bold text-white">Spark Materialization Job</h4>
                        <p className="text-xs text-white/60 mt-1">Nightly batch process executed by Airflow cluster.</p>
                      </div>
                    </div>

                    {/* Feature Definition */}
                    <div className="flex justify-between items-center w-full">
                      <div className="w-5/12 text-right pr-8">
                        <h4 className="text-lg font-bold text-emerald-400 font-mono">decision_maker_engaged_90d</h4>
                        <p className="text-xs text-white/60 mt-1">Materialized and synced to Online Store.</p>
                      </div>
                      <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(16,185,129,0.3)]">
                        <span className="text-emerald-400">3</span>
                      </div>
                      <div className="w-5/12 pl-8">
                        <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/30 text-xs text-emerald-400 font-mono">
                          Status: PRODUCTION<br/>
                          Sync: Redis (1.2ms latency)
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              </>
            )}

            {activeTab === 'health' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Feature Health & Drift Monitoring</h2>
                    <p className="text-sm text-white/60 mt-1">Real-time alerts for data degradation and statistical distribution drift.</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-6">
                  {/* Healthy */}
                  <div className="glass-card bg-black/80 border border-emerald-500/30 rounded-xl p-6 shadow-lg backdrop-blur-md">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-sm font-bold text-white font-mono break-all">decision_maker_engaged_90d</h3>
                      <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] mt-1"></span>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-[10px] text-white/40 mb-1 uppercase font-bold">
                          <span>Null Values</span>
                          <span className="text-emerald-400">0.2%</span>
                        </div>
                        <div className="w-full bg-white/5 h-1 rounded-full"><div className="bg-emerald-500 h-1 rounded-full" style={{width: '2%'}}></div></div>
                      </div>
                      <div>
                        <div className="flex justify-between text-[10px] text-white/40 mb-1 uppercase font-bold">
                          <span>Distribution Drift Score</span>
                          <span className="text-emerald-400">0.05 (Stable)</span>
                        </div>
                        <div className="w-full bg-white/5 h-1 rounded-full"><div className="bg-emerald-500 h-1 rounded-full" style={{width: '5%'}}></div></div>
                      </div>
                    </div>
                  </div>

                  {/* Degraded */}
                  <div className="glass-card bg-black/80 border border-amber-500/50 rounded-xl p-6 shadow-[0_0_20px_rgba(245,158,11,0.15)] backdrop-blur-md">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-sm font-bold text-white font-mono break-all">competitor_mentioned_7d</h3>
                      <span className="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)] mt-1 animate-pulse"></span>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-[10px] text-white/40 mb-1 uppercase font-bold">
                          <span>Null Values</span>
                          <span className="text-amber-400">22.5%</span>
                        </div>
                        <div className="w-full bg-white/5 h-1 rounded-full"><div className="bg-amber-500 h-1 rounded-full" style={{width: '22.5%'}}></div></div>
                      </div>
                      <div>
                        <div className="flex justify-between text-[10px] text-white/40 mb-1 uppercase font-bold">
                          <span>Distribution Drift Score</span>
                          <span className="text-white/80">0.12 (Monitor)</span>
                        </div>
                        <div className="w-full bg-white/5 h-1 rounded-full"><div className="bg-white/20 h-1 rounded-full" style={{width: '12%'}}></div></div>
                      </div>
                    </div>
                  </div>

                  {/* Critical */}
                  <div className="glass-card bg-black/80 border border-rose-500/50 rounded-xl p-6 shadow-[0_0_20px_rgba(244,63,94,0.15)] backdrop-blur-md relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-16 h-16 bg-rose-500/20 blur-xl"></div>
                    <div className="flex justify-between items-start mb-4 relative z-10">
                      <h3 className="text-sm font-bold text-white font-mono break-all">funding_round_size_usd</h3>
                      <span className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)] mt-1 animate-ping"></span>
                    </div>
                    <div className="space-y-4 relative z-10">
                      <div>
                        <div className="flex justify-between text-[10px] text-white/40 mb-1 uppercase font-bold">
                          <span>Null Values</span>
                          <span className="text-rose-400">65.2%</span>
                        </div>
                        <div className="w-full bg-white/5 h-1 rounded-full"><div className="bg-rose-500 h-1 rounded-full" style={{width: '65.2%'}}></div></div>
                      </div>
                      <div className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 p-2 rounded">
                        <strong>CRITICAL:</strong> API connection to Crunchbase timed out, halting materialization job.
                      </div>
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
