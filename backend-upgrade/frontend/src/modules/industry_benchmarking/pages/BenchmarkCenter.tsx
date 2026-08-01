import React, { useState } from 'react';

export const BenchmarkCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('insights');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Industry Benchmarks</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Acme Corp Global</span>
            <span className="text-[10px] text-teal-400 font-mono">B2B SaaS • 100-500 Employees</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="text-white/60 hover:text-white text-sm font-medium transition-colors flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Privacy Guard Active
          </button>
          <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors">Export Report</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Intelligence</h3>
            <button 
              onClick={() => setActiveTab('insights')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'insights' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">💡</span> AI Insights & Action
            </button>
            <button 
              onClick={() => setActiveTab('distributions')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'distributions' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">📊</span> Percentile Analysis
            </button>
            <button 
              onClick={() => setActiveTab('cohorts')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'cohorts' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">👥</span> Peer Cohorts
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'insights' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Executive Benchmark Insights</h2>
                    <p className="text-sm text-white/60 mt-1">AI-generated analysis of your performance relative to your anonymous peer cohort.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {/* Positive Insight */}
                  <div className="glass-card bg-black/80 border border-emerald-500/30 rounded-xl p-5 shadow-[0_0_15px_rgba(16,185,129,0.1)] backdrop-blur-md flex gap-4">
                    <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                      <span className="text-xl">📈</span>
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-emerald-400 mb-1">Top Quartile Performer: Win Rate</h4>
                      <p className="text-sm text-white/80">Excellent. Your Win Rate (43%) is in the Top 25% of the "B2B SaaS (100-500 Employees)" peer group. The median for this cohort is 24.75%.</p>
                    </div>
                  </div>

                  {/* Negative Insight */}
                  <div className="glass-card bg-black/80 border border-rose-500/30 rounded-xl p-5 shadow-[0_0_15px_rgba(225,29,72,0.1)] backdrop-blur-md flex gap-4">
                    <div className="w-10 h-10 rounded-full bg-rose-500/20 flex items-center justify-center shrink-0">
                      <span className="text-xl">⚠️</span>
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-rose-400 mb-1">Action Required: Sales Cycle Length</h4>
                      <p className="text-sm text-white/80">Your Sales Cycle (110 days) is significantly longer than the peer median. You are falling into the bottom 25% of your cohort. We recommend implementing tighter workflow automation during the discovery phase.</p>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'distributions' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Percentile Analysis</h2>
                    <p className="text-sm text-white/60 mt-1">Mathematical distribution of KPIs across your peer group.</p>
                  </div>
                  <div className="flex gap-2">
                    <select className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-white outline-none">
                      <option>Metric: Win Rate</option>
                      <option>Metric: Sales Cycle</option>
                    </select>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-8 shadow-lg backdrop-blur-md relative overflow-hidden">
                  <h4 className="text-sm font-bold text-white mb-8 text-center">Win Rate Distribution (Sample Size: 1,420 companies)</h4>
                  
                  {/* Visual Distribution Bar */}
                  <div className="relative h-12 w-full max-w-3xl mx-auto flex items-center">
                    <div className="absolute w-full h-2 bg-white/10 rounded-full"></div>
                    
                    {/* Markers */}
                    <div className="absolute left-[10%] -translate-x-1/2 flex flex-col items-center">
                      <div className="w-1 h-4 bg-white/40 mb-1"></div>
                      <div className="text-[10px] text-white/40">P10</div>
                      <div className="text-xs font-mono text-white/60">12.0%</div>
                    </div>
                    
                    <div className="absolute left-[25%] -translate-x-1/2 flex flex-col items-center">
                      <div className="w-1 h-4 bg-white/60 mb-1"></div>
                      <div className="text-[10px] text-white/60">P25</div>
                      <div className="text-xs font-mono text-white/80">18.0%</div>
                    </div>
                    
                    <div className="absolute left-[50%] -translate-x-1/2 flex flex-col items-center z-10">
                      <div className="w-1 h-6 bg-white mb-1"></div>
                      <div className="text-[10px] text-white font-bold">MEDIAN</div>
                      <div className="text-sm font-mono text-white font-bold">24.75%</div>
                    </div>
                    
                    <div className="absolute left-[75%] -translate-x-1/2 flex flex-col items-center">
                      <div className="w-1 h-4 bg-white/60 mb-1"></div>
                      <div className="text-[10px] text-white/60">P75</div>
                      <div className="text-xs font-mono text-white/80">35.0%</div>
                    </div>
                    
                    <div className="absolute left-[90%] -translate-x-1/2 flex flex-col items-center">
                      <div className="w-1 h-4 bg-white/40 mb-1"></div>
                      <div className="text-[10px] text-white/40">P90</div>
                      <div className="text-xs font-mono text-white/60">42.3%</div>
                    </div>
                    
                    {/* User Marker */}
                    <div className="absolute left-[92%] -translate-x-1/2 flex flex-col items-center top-[-40px]">
                      <div className="px-2 py-1 bg-emerald-500 rounded text-xs font-bold text-white shadow-lg">YOU (43.0%)</div>
                      <div className="w-0.5 h-10 bg-emerald-500"></div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'cohorts' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Peer Cohorts</h2>
                    <p className="text-sm text-white/60 mt-1">Privacy-preserving anonymous groupings used for your benchmarking.</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md">
                    <div className="flex justify-between items-center mb-4">
                      <span className="font-bold text-white">B2B SaaS (100-500 Employees)</span>
                      <span className="text-xs text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded">ACTIVE</span>
                    </div>
                    <div className="flex gap-4">
                      <div>
                        <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Sample Size</div>
                        <div className="text-lg font-bold text-white font-mono">1,420</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Privacy Guard</div>
                        <div className="text-lg font-bold text-emerald-400 font-mono">SAFE</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md opacity-50 cursor-not-allowed">
                    <div className="flex justify-between items-center mb-4">
                      <span className="font-bold text-white">Financial Services (Enterprise)</span>
                      <span className="text-xs text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded">BLOCKED</span>
                    </div>
                    <div className="flex gap-4">
                      <div>
                        <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Sample Size</div>
                        <div className="text-lg font-bold text-white font-mono">3</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Privacy Guard</div>
                        <div className="text-lg font-bold text-rose-400 font-mono">VIOLATION</div>
                      </div>
                    </div>
                    <div className="mt-4 text-xs text-rose-400">Not enough peers to guarantee anonymity (Requires ≥ 5).</div>
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
