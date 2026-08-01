import React, { useState } from 'react';

export const AIGovernanceCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('human_approval');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">AI Governance</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Responsible AI Platform</span>
            <span className="text-[10px] text-purple-400 font-mono">Safety Guards: ACTIVE</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-sm font-bold transition-colors shadow-[0_0_15px_rgba(147,51,234,0.3)] flex items-center gap-2">
            <span>⚙️</span> Manage Safety Policies
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Decision Gates</h3>
            <button 
              onClick={() => setActiveTab('human_approval')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'human_approval' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🧑‍⚖️</span> Human-In-The-Loop
              <span className="ml-auto bg-rose-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold">3</span>
            </button>
            <button 
              onClick={() => setActiveTab('safety')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'safety' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🛡️</span> Hallucination Monitor
            </button>
            <button 
              onClick={() => setActiveTab('audit')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'audit' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🔎</span> Explainability Audit
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'human_approval' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Human Approval Queue</h2>
                    <p className="text-sm text-white/60 mt-1">High-risk autonomous decisions currently intercepted and awaiting manual authorization.</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Decision 1 */}
                  <div className="glass-card bg-black/80 border border-rose-500/30 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(225,29,72,0.1)] backdrop-blur-md">
                    <div className="p-4 bg-rose-500/10 border-b border-rose-500/20 flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <span className="px-2 py-1 bg-rose-500 text-black text-[10px] font-bold rounded uppercase">CRITICAL RISK</span>
                        <span className="text-sm font-mono text-white/60">dec_8f73b1a2</span>
                      </div>
                      <span className="text-xs text-white/40">Intercepted 4 mins ago</span>
                    </div>
                    
                    <div className="p-6">
                      <div className="flex gap-8">
                        <div className="flex-1 space-y-4">
                          <div>
                            <h4 className="text-[10px] font-bold text-white/40 uppercase mb-1">Proposed AI Action</h4>
                            <p className="text-lg text-white font-medium bg-white/5 p-3 rounded border border-white/10">
                              Terminate multi-year contract for GlobalCorp due to predicted insolvency.
                            </p>
                          </div>
                          <div>
                            <h4 className="text-[10px] font-bold text-white/40 uppercase mb-1">AI Reasoning (Explainability Trace)</h4>
                            <p className="text-sm text-white/70">
                              GlobalCorp's Q3 filings indicate a 40% drop in liquidity. Feature store signal `fin_health_idx` dropped below threshold 0.2. Autonomous Agent policy `contract_defense_v2` triggered immediate termination recommendation.
                            </p>
                          </div>
                        </div>
                        
                        <div className="w-64 space-y-4 border-l border-white/10 pl-8">
                          <div>
                            <h4 className="text-[10px] font-bold text-white/40 uppercase mb-1">Confidence Score</h4>
                            <span className="text-2xl font-bold text-white font-mono">94.2%</span>
                          </div>
                          <div>
                            <h4 className="text-[10px] font-bold text-white/40 uppercase mb-1">Model Chain</h4>
                            <div className="text-xs text-white/60 font-mono space-y-1">
                              <div>avenor_reasoning_v4</div>
                              <div>agent_defense_v2</div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="mt-8 flex justify-end gap-3 pt-4 border-t border-white/10">
                        <button className="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded text-sm font-bold transition-colors">
                          Reject Action
                        </button>
                        <button className="px-6 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded text-sm font-bold transition-colors shadow-[0_0_15px_rgba(225,29,72,0.4)]">
                          Authorize Action
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Decision 2 */}
                  <div className="glass-card bg-black/80 border border-amber-500/30 rounded-xl overflow-hidden shadow-lg backdrop-blur-md">
                    <div className="p-4 bg-amber-500/10 border-b border-amber-500/20 flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <span className="px-2 py-1 bg-amber-500 text-black text-[10px] font-bold rounded uppercase">HIGH RISK</span>
                        <span className="text-sm font-mono text-white/60">dec_4c2d9e1f</span>
                      </div>
                      <span className="text-xs text-white/40">Intercepted 12 mins ago</span>
                    </div>
                    
                    <div className="p-6">
                      <div className="flex gap-8">
                        <div className="flex-1 space-y-4">
                          <div>
                            <h4 className="text-[10px] font-bold text-white/40 uppercase mb-1">Proposed AI Action</h4>
                            <p className="text-lg text-white font-medium bg-white/5 p-3 rounded border border-white/10">
                              Approve $450,000 credit line extension for Acme Logistics.
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="mt-6 flex justify-end gap-3">
                        <button className="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/20 text-white rounded text-sm font-bold transition-colors">Reject Action</button>
                        <button className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-sm font-bold transition-colors">Authorize Action</button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'safety' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Hallucination & Bias Monitor</h2>
                    <p className="text-sm text-white/60 mt-1">Real-time safety intervention logs. Displays generations blocked prior to user delivery.</p>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-white/5 border-b border-white/10 text-[10px] text-white/40 uppercase tracking-wider">
                        <th className="p-4 font-bold">Timestamp</th>
                        <th className="p-4 font-bold">Intervention Type</th>
                        <th className="p-4 font-bold">Flagged Content</th>
                        <th className="p-4 font-bold">Action Taken</th>
                      </tr>
                    </thead>
                    <tbody className="text-sm">
                      <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4 text-white/60 font-mono text-xs">2026-07-28 14:02:11</td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-rose-500/20 text-rose-400 border border-rose-500/30 text-[10px] font-bold rounded uppercase">Factual Hallucination</span>
                        </td>
                        <td className="p-4 text-white/80">"Competitor Acme filed for bankruptcy." <span className="text-rose-400 text-xs block mt-1">(0% Grounding Evidence Found)</span></td>
                        <td className="p-4"><span className="text-rose-400 font-bold text-xs uppercase">BLOCKED</span></td>
                      </tr>
                      <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4 text-white/60 font-mono text-xs">2026-07-28 11:45:03</td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-purple-500/20 text-purple-400 border border-purple-500/30 text-[10px] font-bold rounded uppercase">Bias Detection</span>
                        </td>
                        <td className="p-4 text-white/80">Pricing model weighed protected cohort zip codes heavily.</td>
                        <td className="p-4"><span className="text-purple-400 font-bold text-xs uppercase">BLOCKED</span></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {activeTab === 'audit' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">AI Explainability Audit Trail</h2>
                    <p className="text-sm text-white/60 mt-1">Cryptographic lineage of models, prompt versions, and data vectors for every decision.</p>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-8 backdrop-blur-md flex flex-col items-center justify-center py-16">
                  <span className="text-4xl mb-4">🔎</span>
                  <h3 className="text-lg font-bold text-white">Search AI Audit Logs</h3>
                  <p className="text-sm text-white/40 mt-2 text-center max-w-md">
                    Enter a Decision ID or Trace ID to explore the exact Model Version, Prompt Hash, and Vector Space used to generate the output.
                  </p>
                  <div className="mt-6 flex w-full max-w-md">
                    <input type="text" placeholder="Enter Decision ID (e.g. dec_8f73b1a2)" className="flex-1 bg-black/50 border border-white/20 rounded-l p-3 text-white font-mono text-sm outline-none focus:border-purple-500" />
                    <button className="px-6 bg-purple-600 hover:bg-purple-500 text-white rounded-r font-bold transition-colors">Search</button>
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
