import React, { useState } from 'react';

export const ModelCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('deployment');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">AI Model Platform</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Global MLOps Control</span>
            <span className="text-[10px] text-indigo-400 font-mono">Status: All Pipelines Healthy</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-bold transition-colors shadow-[0_0_15px_rgba(79,70,229,0.3)] flex items-center gap-2">
            <span>🚀</span> New Training Run
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Lifecycle Management</h3>
            <button 
              onClick={() => setActiveTab('experiments')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'experiments' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🧪</span> Experiment Tracker
            </button>
            <button 
              onClick={() => setActiveTab('evaluation')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'evaluation' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">⚖️</span> Model Evaluation
            </button>
            <button 
              onClick={() => setActiveTab('deployment')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'deployment' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🚦</span> Canary Deployments
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'deployment' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Deployment & Traffic Routing</h2>
                    <p className="text-sm text-white/60 mt-1">Safely orchestrate Canary and Shadow deployments across the global inference fleet.</p>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-indigo-500/30 rounded-xl p-8 shadow-[0_0_20px_rgba(79,70,229,0.1)] backdrop-blur-md relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl"></div>
                  
                  <h3 className="text-xl font-bold text-white mb-6 relative z-10 flex items-center gap-3">
                    <span className="text-indigo-400">TARGET:</span> deal_risk_prediction
                  </h3>

                  {/* Traffic Splitting Visualizer */}
                  <div className="w-full h-8 flex rounded-lg overflow-hidden mb-8 shadow-inner relative z-10">
                    <div className="bg-emerald-500 flex items-center justify-center text-[10px] font-bold text-black" style={{ width: '90%' }}>CHAMPION (90%)</div>
                    <div className="bg-amber-500 flex items-center justify-center text-[10px] font-bold text-black" style={{ width: '10%' }}>CANARY (10%)</div>
                  </div>

                  <div className="space-y-4 relative z-10">
                    {/* Champion Row */}
                    <div className="flex items-center justify-between p-4 bg-white/5 border border-emerald-500/30 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded bg-emerald-500/20 flex items-center justify-center border border-emerald-500/50">
                          <span className="text-xl">👑</span>
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-white">DealRiskNet_v2.0.0</h4>
                            <span className="px-2 py-0.5 bg-emerald-500 text-black text-[10px] font-bold rounded">CHAMPION</span>
                          </div>
                          <p className="text-xs text-white/60">Serving majority production traffic.</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Live Traffic</div>
                          <div className="text-xl font-bold text-emerald-400 font-mono">90%</div>
                        </div>
                        <button className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-xs font-bold transition-colors">Edit</button>
                      </div>
                    </div>

                    {/* Canary Row */}
                    <div className="flex items-center justify-between p-4 bg-white/5 border border-amber-500/30 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded bg-amber-500/20 flex items-center justify-center border border-amber-500/50">
                          <span className="text-xl">🐦</span>
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-white">DealRiskNet_v2.1.0-beta</h4>
                            <span className="px-2 py-0.5 bg-amber-500 text-black text-[10px] font-bold rounded">CANARY</span>
                          </div>
                          <p className="text-xs text-white/60">Testing new competitor embedding feature.</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Live Traffic</div>
                          <div className="text-xl font-bold text-amber-400 font-mono">10%</div>
                        </div>
                        <button className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-xs font-bold transition-colors">Edit</button>
                      </div>
                    </div>

                    {/* Shadow Row */}
                    <div className="flex items-center justify-between p-4 bg-white/5 border border-blue-500/30 rounded-lg opacity-80">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded bg-blue-500/20 flex items-center justify-center border border-blue-500/50">
                          <span className="text-xl">👻</span>
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-bold text-white">DealRiskNet_v3.0.0-experimental</h4>
                            <span className="px-2 py-0.5 bg-blue-500 text-black text-[10px] font-bold rounded">SHADOW</span>
                          </div>
                          <p className="text-xs text-white/60">Deep learning architecture. Generating offline metrics only.</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Live Traffic</div>
                          <div className="text-xl font-bold text-blue-400 font-mono">0% (100% Async)</div>
                        </div>
                        <button className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-xs font-bold transition-colors">Edit</button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'evaluation' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">AI Fairness & Evaluation Matrix</h2>
                    <p className="text-sm text-white/60 mt-1">Strict metric gating preventing biased or underperforming models from entering production.</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  {/* Successful Eval */}
                  <div className="glass-card bg-black/80 border border-emerald-500/30 rounded-xl p-6 shadow-lg backdrop-blur-md">
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <div className="text-xs text-white/40 font-mono mb-1">run_9a8b7c6d</div>
                        <h3 className="text-lg font-bold text-white">v2.1.0-beta</h3>
                      </div>
                      <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 text-xs font-bold rounded-lg flex items-center gap-2">
                        <span>✓</span> PASSED
                      </span>
                    </div>

                    <div className="space-y-4">
                      <div className="flex justify-between items-center pb-3 border-b border-white/5">
                        <span className="text-sm text-white/80">Accuracy (F1)</span>
                        <span className="text-sm font-bold text-emerald-400">0.912</span>
                      </div>
                      <div className="flex justify-between items-center pb-3 border-b border-white/5">
                        <span className="text-sm text-white/80">ROC AUC</span>
                        <span className="text-sm font-bold text-emerald-400">0.945</span>
                      </div>
                      <div className="flex justify-between items-center pb-3 border-b border-white/5">
                        <span className="text-sm text-white/80">Inference Latency</span>
                        <span className="text-sm font-bold text-white">48ms</span>
                      </div>
                      <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/10">
                        <span className="text-sm font-bold text-white">Bias Score (Fairness)</span>
                        <span className="text-sm font-bold text-emerald-400">0.02 (Safe)</span>
                      </div>
                    </div>
                  </div>

                  {/* Failed Eval (Blocked by Fairness) */}
                  <div className="glass-card bg-black/80 border border-rose-500/50 rounded-xl p-6 shadow-[0_0_20px_rgba(244,63,94,0.15)] backdrop-blur-md relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-rose-500/10 rounded-full blur-2xl"></div>
                    
                    <div className="flex justify-between items-start mb-6 relative z-10">
                      <div>
                        <div className="text-xs text-white/40 font-mono mb-1">run_4f5e6d7c</div>
                        <h3 className="text-lg font-bold text-white">v2.2.0-experimental</h3>
                      </div>
                      <span className="px-3 py-1 bg-rose-500/20 text-rose-400 border border-rose-500/50 text-xs font-bold rounded-lg flex items-center gap-2">
                        <span>⨯</span> BLOCKED
                      </span>
                    </div>

                    <div className="space-y-4 relative z-10">
                      <div className="flex justify-between items-center pb-3 border-b border-white/5">
                        <span className="text-sm text-white/80">Accuracy (F1)</span>
                        <span className="text-sm font-bold text-emerald-400">0.965</span>
                      </div>
                      <div className="flex justify-between items-center pb-3 border-b border-white/5">
                        <span className="text-sm text-white/80">ROC AUC</span>
                        <span className="text-sm font-bold text-emerald-400">0.980</span>
                      </div>
                      <div className="flex justify-between items-center pb-3 border-b border-white/5">
                        <span className="text-sm text-white/80">Inference Latency</span>
                        <span className="text-sm font-bold text-white">52ms</span>
                      </div>
                      <div className="flex justify-between items-center bg-rose-500/10 p-3 rounded-lg border border-rose-500/30">
                        <div className="flex flex-col">
                          <span className="text-sm font-bold text-white">Bias Score (Fairness)</span>
                          <span className="text-[10px] text-rose-400 mt-1">Exceeds 0.10 absolute threshold. Automatically blocked from production.</span>
                        </div>
                        <span className="text-sm font-bold text-rose-400">0.15 (Failed)</span>
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
