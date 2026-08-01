import React, { useState } from 'react';

export const FoundationModelsCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('explainability');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Foundation Revenue Models</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Model Registry: v4.2</span>
            <span className="text-[10px] text-amber-400 font-mono">14 Active Champions</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="px-4 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-sm font-bold transition-colors shadow-[0_0_15px_rgba(245,158,11,0.3)] flex items-center gap-2">
            Deploy Challenger Model
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">ML Operations</h3>
            <button 
              onClick={() => setActiveTab('explainability')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'explainability' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🔍</span> Explainability Viewer
            </button>
            <button 
              onClick={() => setActiveTab('registry')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'registry' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🏆</span> Champion vs Challenger
            </button>
            <button 
              onClick={() => setActiveTab('features')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'features' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🧩</span> Feature Store Map
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'explainability' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">AI Explainability Viewer</h2>
                    <p className="text-sm text-white/60 mt-1">Audit the mathematical evidence and feature weights behind any prediction.</p>
                  </div>
                  <div className="relative">
                    <input type="text" placeholder="Lookup Entity ID (e.g. ent_acme)..." className="w-72 bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm text-white outline-none focus:border-amber-500" />
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-6 shadow-lg backdrop-blur-md relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl"></div>
                  
                  <div className="flex justify-between items-start mb-8">
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <span className="px-2 py-0.5 bg-amber-500/20 border border-amber-500/30 text-amber-400 text-[10px] font-bold rounded">TARGET: DEAL_RISK</span>
                        <span className="px-2 py-0.5 bg-white/10 text-white/60 text-[10px] font-mono rounded">MODEL: DealRiskNet_v2.1</span>
                      </div>
                      <h3 className="text-xl font-bold text-white">Acme Corp Enterprise Expansion</h3>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-white/60 mb-1">Risk Probability</div>
                      <div className="text-3xl font-bold text-emerald-400 font-mono">15%</div>
                      <div className="text-[10px] text-white/40 mt-1">Confidence: 94.2%</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-8">
                    {/* Top Contributors */}
                    <div>
                      <h4 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-4 border-b border-white/10 pb-2">Top Feature Contributors</h4>
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-white font-mono">decision_maker_engaged</span>
                            <span className="text-emerald-400 font-bold">-65% Risk</span>
                          </div>
                          <div className="w-full bg-white/5 rounded-full h-1.5 flex justify-end">
                            <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '65%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-white font-mono">competitor_mentioned</span>
                            <span className="text-rose-400 font-bold">+25% Risk</span>
                          </div>
                          <div className="w-full bg-white/5 rounded-full h-1.5 flex justify-start">
                            <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: '25%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="text-white font-mono">recent_funding_round</span>
                            <span className="text-emerald-400 font-bold">-20% Risk</span>
                          </div>
                          <div className="w-full bg-white/5 rounded-full h-1.5 flex justify-end">
                            <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '20%' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Supporting Evidence */}
                    <div>
                      <h4 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-4 border-b border-white/10 pb-2">Supporting Evidence (Graph & CRM)</h4>
                      <div className="space-y-3">
                        <div className="flex items-start gap-3 p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
                          <span className="text-emerald-400 mt-0.5">✓</span>
                          <span className="text-sm text-white/80">CFO (Decision Maker) opened the pricing proposal 3 times in the last 24 hours.</span>
                        </div>
                        <div className="flex items-start gap-3 p-3 bg-rose-500/5 border border-rose-500/20 rounded-lg">
                          <span className="text-rose-400 mt-0.5">!</span>
                          <span className="text-sm text-white/80">"Salesforce" was mentioned by the client in the last Gong recording.</span>
                        </div>
                        <div className="flex items-start gap-3 p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
                          <span className="text-emerald-400 mt-0.5">✓</span>
                          <span className="text-sm text-white/80">Acme Corp raised $50M Series B last month, indicating high budget liquidity.</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'registry' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Model Registry (Champion vs Challenger)</h2>
                    <p className="text-sm text-white/60 mt-1">Manage deployments, evaluate challengers, and execute rollbacks.</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Champion Model */}
                  <div className="glass-card bg-black/80 border border-amber-500/30 rounded-xl p-6 shadow-[0_0_15px_rgba(245,158,11,0.1)] backdrop-blur-md relative">
                    <div className="absolute top-0 left-0 w-1 h-full bg-amber-500 rounded-l-xl"></div>
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-bold text-white">BuyingWindowNet</h3>
                          <span className="px-2 py-0.5 bg-amber-500 text-black text-[10px] font-bold rounded">CHAMPION</span>
                          <span className="px-2 py-0.5 bg-white/10 text-white/60 text-[10px] font-mono rounded">v2.0.0</span>
                        </div>
                        <p className="text-xs text-white/60 mb-4">Production model handling 100% of live inference traffic for Buying Window predictions.</p>
                        
                        <div className="flex gap-6">
                          <div>
                            <div className="text-[10px] text-white/40 uppercase font-bold mb-1">F1 Accuracy</div>
                            <div className="text-xl font-bold text-emerald-400 font-mono">0.890</div>
                          </div>
                          <div>
                            <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Latency (p99)</div>
                            <div className="text-xl font-bold text-white font-mono">42ms</div>
                          </div>
                          <div>
                            <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Inferences / Day</div>
                            <div className="text-xl font-bold text-white font-mono">1.2M</div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex flex-col gap-2">
                        <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded text-xs font-bold transition-colors">View Weights</button>
                      </div>
                    </div>
                  </div>

                  {/* Challenger Model */}
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-6 shadow-lg backdrop-blur-md">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-bold text-white/80">BuyingWindowNet</h3>
                          <span className="px-2 py-0.5 bg-blue-500/20 border border-blue-500/30 text-blue-400 text-[10px] font-bold rounded">CHALLENGER (SHADOW)</span>
                          <span className="px-2 py-0.5 bg-white/10 text-white/60 text-[10px] font-mono rounded">v2.1.0-beta</span>
                        </div>
                        <p className="text-xs text-white/60 mb-4">Currently running in shadow mode. Added new features from Cross-Customer Intelligence platform.</p>
                        
                        <div className="flex gap-6">
                          <div>
                            <div className="text-[10px] text-white/40 uppercase font-bold mb-1">F1 Accuracy</div>
                            <div className="text-xl font-bold text-emerald-400 font-mono flex items-center gap-2">0.915 <span className="text-[10px] text-emerald-500 bg-emerald-500/10 px-1 rounded">↑ +0.025</span></div>
                          </div>
                          <div>
                            <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Latency (p99)</div>
                            <div className="text-xl font-bold text-white font-mono">48ms</div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex flex-col gap-2">
                        <button className="px-4 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded text-xs font-bold transition-colors shadow-lg">Promote to Champion</button>
                        <button className="px-4 py-1.5 bg-white/5 hover:bg-white/10 text-white/60 rounded text-xs transition-colors">View Evaluation</button>
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
