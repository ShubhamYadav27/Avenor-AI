import React, { useState } from 'react';

export const GlobalDataCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('explorer');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Global Data Platform</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Knowledge Graph Sync</span>
            <span className="text-[10px] text-emerald-400 font-mono">142.3M Nodes • Last sync: Just now</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="text-white/60 hover:text-white text-sm font-medium transition-colors">Run Freshness Recalculation</button>
          <button className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(79,70,229,0.4)]">Add Data Source</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Intelligence</h3>
            <button 
              onClick={() => setActiveTab('explorer')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'explorer' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🌐</span> Entity Explorer
            </button>
            <button 
              onClick={() => setActiveTab('provenance')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'provenance' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">📜</span> Provenance Inspector
            </button>
            <button 
              onClick={() => setActiveTab('merge_queue')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'merge_queue' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">⚡</span> Conflict Resolution
            </button>
            <button 
              onClick={() => setActiveTab('sources')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'sources' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🔗</span> Source Reliability
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'explorer' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Entity Explorer</h2>
                    <p className="text-sm text-white/60 mt-1">Search and traverse the canonical knowledge graph.</p>
                  </div>
                  <div className="relative">
                    <input type="text" placeholder="Search entities (e.g., Apple)..." className="w-64 bg-white/5 border border-white/10 rounded-lg px-4 py-1.5 text-sm text-white outline-none focus:border-indigo-500" />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-6">
                  {/* Canonical Profile */}
                  <div className="col-span-2 glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl"></div>
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center text-2xl">🍎</div>
                        <div>
                          <h4 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-1">COMPANY ENTITY</h4>
                          <div className="text-2xl font-bold text-white">Apple Inc.</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-white/60 mb-1">Global Trust Score</div>
                        <div className="text-lg font-bold text-emerald-400 font-mono">98.5%</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 border-t border-white/10 pt-4">
                      <div>
                        <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Canonical Revenue</div>
                        <div className="text-sm text-white font-mono">$394.3B <span className="text-[10px] text-indigo-400 ml-2">via Salesforce CRM</span></div>
                      </div>
                      <div>
                        <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Canonical CEO</div>
                        <div className="text-sm text-white font-mono">Tim Cook <span className="text-[10px] text-indigo-400 ml-2">via Web Scraper</span></div>
                      </div>
                    </div>
                  </div>

                  {/* Relationship Graph Summary */}
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md">
                    <h4 className="text-sm font-bold text-white mb-4">Graph Edges (1st Degree)</h4>
                    
                    <div className="space-y-3">
                      <div className="p-2 bg-white/5 border border-white/10 rounded">
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-white/60">employs</span>
                          <span className="text-white font-bold">Tim Cook (Executive)</span>
                        </div>
                      </div>
                      <div className="p-2 bg-white/5 border border-white/10 rounded">
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-white/60">uses_tech</span>
                          <span className="text-white font-bold">Swift (Technology)</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'provenance' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Provenance Inspector</h2>
                    <p className="text-sm text-white/60 mt-1">Audit the origin and conflict history of every field.</p>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl shadow-lg backdrop-blur-md overflow-hidden">
                  <div className="p-4 border-b border-white/10 bg-white/5 flex justify-between items-center">
                    <span className="font-bold text-white">Field: Employee Count (Microsoft)</span>
                    <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-400 text-xs rounded border border-indigo-500/30">Canonical: 221,000</span>
                  </div>
                  <table className="w-full text-left text-sm">
                    <thead className="bg-white/5 border-b border-white/10">
                      <tr>
                        <th className="px-4 py-3 font-medium text-white/60">Asserted Value</th>
                        <th className="px-4 py-3 font-medium text-white/60">Provider</th>
                        <th className="px-4 py-3 font-medium text-white/60">Confidence Score</th>
                        <th className="px-4 py-3 font-medium text-white/60">Timestamp</th>
                        <th className="px-4 py-3 text-right">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      <tr className="hover:bg-white/5 transition-colors bg-indigo-500/5">
                        <td className="px-4 py-3 font-bold text-white">221,000</td>
                        <td className="px-4 py-3 text-white/80">clearbit_api</td>
                        <td className="px-4 py-3 text-emerald-400 font-mono">0.850</td>
                        <td className="px-4 py-3 text-white/40 font-mono text-xs">2026-08-01T00:05:30Z</td>
                        <td className="px-4 py-3 text-right"><span className="text-[10px] font-bold text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded">WINNER</span></td>
                      </tr>
                      <tr className="hover:bg-white/5 transition-colors">
                        <td className="px-4 py-3 text-white/60 line-through">180,000</td>
                        <td className="px-4 py-3 text-white/60">public_web_scraper</td>
                        <td className="px-4 py-3 text-rose-400 font-mono">0.400</td>
                        <td className="px-4 py-3 text-white/40 font-mono text-xs">2026-08-01T00:05:28Z</td>
                        <td className="px-4 py-3 text-right"><span className="text-[10px] font-bold text-rose-400 border border-rose-500/30 px-1.5 py-0.5 rounded">OVERRIDDEN</span></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {activeTab === 'sources' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Source Reliability Engine</h2>
                    <p className="text-sm text-white/60 mt-1">Configure Base Trust Scores for Data Providers.</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md">
                    <div className="flex justify-between items-center mb-4">
                      <span className="font-bold text-white">Salesforce CRM</span>
                      <span className="text-xs text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded">HIGH TRUST</span>
                    </div>
                    <div className="text-4xl font-bold text-white font-mono mb-2">0.95</div>
                    <div className="text-xs text-white/60">Overrides 95% of conflicts.</div>
                  </div>
                  
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md">
                    <div className="flex justify-between items-center mb-4">
                      <span className="font-bold text-white">Clearbit API</span>
                      <span className="text-xs text-blue-400 font-bold bg-blue-500/10 px-2 py-0.5 rounded">MODERATE TRUST</span>
                    </div>
                    <div className="text-4xl font-bold text-white font-mono mb-2">0.85</div>
                    <div className="text-xs text-white/60">High accuracy, standard API.</div>
                  </div>

                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md opacity-80">
                    <div className="flex justify-between items-center mb-4">
                      <span className="font-bold text-white">Web Scraper</span>
                      <span className="text-xs text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded">LOW TRUST</span>
                    </div>
                    <div className="text-4xl font-bold text-white font-mono mb-2">0.40</div>
                    <div className="text-xs text-white/60">Easily overridden by CRMs.</div>
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
