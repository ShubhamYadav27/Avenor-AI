import React, { useState } from 'react';

export const CollectiveIntelligenceCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('patterns');
  const [isOptedIn, setIsOptedIn] = useState(true);

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-fuchsia-500 to-indigo-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Cross-Customer Intelligence</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-lg">
            <span className="text-xs font-medium text-white/60">Data Contribution:</span>
            <button 
              onClick={() => setIsOptedIn(!isOptedIn)}
              className={`w-10 h-5 rounded-full relative transition-colors ${isOptedIn ? 'bg-emerald-500' : 'bg-white/20'}`}
            >
              <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${isOptedIn ? 'left-[22px]' : 'left-[2px]'}`}></div>
            </button>
            <span className={`text-xs font-bold ${isOptedIn ? 'text-emerald-400' : 'text-white/40'}`}>
              {isOptedIn ? 'OPTED IN' : 'OPTED OUT'}
            </span>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Discovery</h3>
            <button 
              onClick={() => setActiveTab('patterns')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'patterns' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🎯</span> Discovered Patterns
            </button>
            <button 
              onClick={() => setActiveTab('correlations')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'correlations' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🕸️</span> Signal Graph
            </button>
            <button 
              onClick={() => setActiveTab('privacy')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'privacy' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🛡️</span> Privacy & Consent
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          {/* Block Access if Opted Out */}
          {!isOptedIn ? (
            <div className="h-full flex flex-col items-center justify-center max-w-lg mx-auto text-center space-y-6">
              <div className="w-20 h-20 bg-rose-500/10 rounded-full flex items-center justify-center border border-rose-500/30">
                <span className="text-4xl">🔒</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Access Revoked</h2>
                <p className="text-white/60">Your organization has opted out of Collective Intelligence. You must contribute anonymous data to access the global pattern discovery network.</p>
              </div>
              <button 
                onClick={() => setIsOptedIn(true)}
                className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold transition-colors shadow-[0_0_15px_rgba(16,185,129,0.3)]"
              >
                Opt-In to Collective Intelligence
              </button>
            </div>
          ) : (
            <div className="max-w-5xl mx-auto space-y-8">
              
              {activeTab === 'patterns' && (
                <>
                  <div className="flex justify-between items-end">
                    <div>
                      <h2 className="text-2xl font-bold text-white tracking-tight">Discovered Market Patterns</h2>
                      <p className="text-sm text-white/60 mt-1">AI-generated correlations mathematically proven across the global ecosystem.</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-4">
                    {/* Pattern 1 */}
                    <div className="glass-card bg-black/80 border border-fuchsia-500/30 rounded-xl p-6 shadow-[0_0_15px_rgba(217,70,239,0.1)] backdrop-blur-md flex flex-col gap-4">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded bg-fuchsia-500/20 flex items-center justify-center shrink-0">
                            <span className="text-xl">📈</span>
                          </div>
                          <div>
                            <h4 className="text-sm font-bold text-fuchsia-400 mb-1">Hiring Velocity ➔ Buying Intent</h4>
                            <p className="text-sm text-white/80">Organizations experiencing high growth engineering hiring are highly likely to show active buying windows within 90 days.</p>
                          </div>
                        </div>
                        <div className="text-right shrink-0">
                          <div className="text-xs text-white/40 uppercase font-bold mb-1">Confidence</div>
                          <div className="text-xl font-bold text-emerald-400 font-mono">82.0%</div>
                        </div>
                      </div>
                      
                      <div className="bg-white/5 rounded-lg p-3 border border-white/10 flex justify-between items-center mt-2">
                        <div className="flex gap-4">
                          <div className="flex flex-col">
                            <span className="text-[10px] text-white/40">Trigger Event</span>
                            <span className="text-xs font-bold text-white">Engineering Hiring = High Growth</span>
                          </div>
                          <div className="flex flex-col justify-center text-white/20">➔</div>
                          <div className="flex flex-col">
                            <span className="text-[10px] text-white/40">Correlated Outcome</span>
                            <span className="text-xs font-bold text-white">Buying Window = Active</span>
                          </div>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[10px] text-white/40">Statistical Base</span>
                          <span className="text-xs font-mono text-white/60">14,500 Orgs</span>
                        </div>
                      </div>
                    </div>

                    {/* Pattern 2 */}
                    <div className="glass-card bg-black/80 border border-indigo-500/30 rounded-xl p-6 shadow-[0_0_15px_rgba(99,102,241,0.1)] backdrop-blur-md flex flex-col gap-4">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded bg-indigo-500/20 flex items-center justify-center shrink-0">
                            <span className="text-xl">🤖</span>
                          </div>
                          <div>
                            <h4 className="text-sm font-bold text-indigo-400 mb-1">AI Adoption ➔ Pipeline Velocity</h4>
                            <p className="text-sm text-white/80">Organizations actively adopting AI CRM tools correlate strongly with high growth pipeline acceleration.</p>
                          </div>
                        </div>
                        <div className="text-right shrink-0">
                          <div className="text-xs text-white/40 uppercase font-bold mb-1">Confidence</div>
                          <div className="text-xl font-bold text-emerald-400 font-mono">74.5%</div>
                        </div>
                      </div>
                      
                      <div className="bg-white/5 rounded-lg p-3 border border-white/10 flex justify-between items-center mt-2">
                        <div className="flex gap-4">
                          <div className="flex flex-col">
                            <span className="text-[10px] text-white/40">Trigger Event</span>
                            <span className="text-xs font-bold text-white">Tech Adoption (AI) = Active</span>
                          </div>
                          <div className="flex flex-col justify-center text-white/20">➔</div>
                          <div className="flex flex-col">
                            <span className="text-[10px] text-white/40">Correlated Outcome</span>
                            <span className="text-xs font-bold text-white">Pipeline Growth = High Growth</span>
                          </div>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[10px] text-white/40">Statistical Base</span>
                          <span className="text-xs font-mono text-white/60">8,200 Orgs</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'privacy' && (
                <>
                  <div className="flex justify-between items-end">
                    <div>
                      <h2 className="text-2xl font-bold text-white tracking-tight">Privacy & Consent Shield</h2>
                      <p className="text-sm text-white/60 mt-1">Audit how your organizational data is mathematically stripped of identity.</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-6 shadow-lg backdrop-blur-md">
                      <div className="flex items-center gap-3 mb-6">
                        <span className="text-2xl">📥</span>
                        <h4 className="font-bold text-white">Raw Signal Ingestion</h4>
                      </div>
                      <pre className="text-xs text-rose-400 font-mono bg-rose-500/5 p-4 rounded-lg border border-rose-500/20">
{`{
  "org_id": "acme_global_123",
  "org_name": "Acme Corp",
  "signal": "engineering_hiring",
  "raw_value": 45,
  "contacts_added": 12
}`}
                      </pre>
                      <div className="mt-4 text-xs text-white/60">
                        Contains highly sensitive identifying markers and raw numerical limits. Never exposed to the intelligence pool.
                      </div>
                    </div>
                    
                    <div className="glass-card bg-black/80 border border-emerald-500/30 rounded-xl p-6 shadow-[0_0_15px_rgba(16,185,129,0.1)] backdrop-blur-md relative overflow-hidden">
                      <div className="absolute top-1/2 left-[-20px] -translate-y-1/2 text-white/20 text-4xl">➔</div>
                      
                      <div className="flex items-center gap-3 mb-6">
                        <span className="text-2xl">🛡️</span>
                        <h4 className="font-bold text-white">Anonymized Output</h4>
                      </div>
                      <pre className="text-xs text-emerald-400 font-mono bg-emerald-500/5 p-4 rounded-lg border border-emerald-500/20">
{`{
  "id": "anon_8f3b2a1c",
  "cohort": "B2B SaaS (Series C)",
  "signal": "engineering_hiring",
  "bucketed_value": "high_growth"
}`}
                      </pre>
                      <div className="mt-4 text-xs text-white/60">
                        Identity permanently stripped. Raw numbers mathematically converted to statistical ranges.
                      </div>
                    </div>
                  </div>
                </>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
};
