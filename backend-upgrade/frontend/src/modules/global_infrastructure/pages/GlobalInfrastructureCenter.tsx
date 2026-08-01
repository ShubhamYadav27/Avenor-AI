import React, { useState } from 'react';

export const GlobalInfrastructureCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('regions');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Global Infrastructure</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Anycast Orchestration</span>
            <span className="text-[10px] text-cyan-400 font-mono">Routing 4.2B Req/Day</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-bold transition-colors shadow-[0_0_15px_rgba(6,182,212,0.3)] flex items-center gap-2">
            <span>⚙️</span> Manage Routing Policies
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Hyperscale Control</h3>
            <button 
              onClick={() => setActiveTab('regions')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'regions' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🌍</span> Global Regions
            </button>
            <button 
              onClick={() => setActiveTab('failover')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'failover' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🛡️</span> Disaster Recovery
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'regions' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Active Region Registry</h2>
                    <p className="text-sm text-white/60 mt-1">Real-time health, latency, and throughput metrics across all physical data centers.</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  {/* Region 1: US East */}
                  <div className="glass-card bg-black/80 border border-emerald-500/30 rounded-xl p-6 shadow-lg backdrop-blur-md relative overflow-hidden">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded bg-emerald-500/20 flex items-center justify-center border border-emerald-500/50">
                          <span className="text-lg">🇺🇸</span>
                        </div>
                        <div>
                          <h3 className="font-bold text-white">US East (N. Virginia)</h3>
                          <p className="text-xs text-white/40 font-mono">aws_us-east-1</p>
                        </div>
                      </div>
                      <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 text-xs font-bold rounded-lg flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> HEALTHY
                      </span>
                    </div>

                    <div className="space-y-4 pt-4 border-t border-white/5">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase">Edge Latency (p99)</span>
                        <span className="text-sm font-bold text-white font-mono">14.2 ms</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase">Current Traffic</span>
                        <span className="text-sm font-bold text-emerald-400 font-mono">185k req/s</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase">Replication Lag</span>
                        <span className="text-sm font-bold text-white font-mono">11 ms</span>
                      </div>
                    </div>
                  </div>

                  {/* Region 2: Europe */}
                  <div className="glass-card bg-black/80 border border-emerald-500/30 rounded-xl p-6 shadow-lg backdrop-blur-md relative overflow-hidden">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded bg-emerald-500/20 flex items-center justify-center border border-emerald-500/50">
                          <span className="text-lg">🇪🇺</span>
                        </div>
                        <div>
                          <h3 className="font-bold text-white">Europe (Ireland)</h3>
                          <p className="text-xs text-white/40 font-mono">aws_eu-west-1</p>
                        </div>
                      </div>
                      <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 text-xs font-bold rounded-lg flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> HEALTHY
                      </span>
                    </div>

                    <div className="space-y-4 pt-4 border-t border-white/5">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase">Edge Latency (p99)</span>
                        <span className="text-sm font-bold text-white font-mono">18.5 ms</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase">Current Traffic</span>
                        <span className="text-sm font-bold text-emerald-400 font-mono">142k req/s</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase">Replication Lag</span>
                        <span className="text-sm font-bold text-white font-mono">14 ms</span>
                      </div>
                    </div>
                  </div>

                  {/* Region 3: Japan (Degraded) */}
                  <div className="glass-card bg-black/80 border border-amber-500/50 rounded-xl p-6 shadow-[0_0_20px_rgba(245,158,11,0.15)] backdrop-blur-md relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl"></div>
                    
                    <div className="flex justify-between items-start mb-4 relative z-10">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded bg-amber-500/20 flex items-center justify-center border border-amber-500/50">
                          <span className="text-lg">🇯🇵</span>
                        </div>
                        <div>
                          <h3 className="font-bold text-white">Asia Pacific (Tokyo)</h3>
                          <p className="text-xs text-white/40 font-mono">gcp_asia-northeast1</p>
                        </div>
                      </div>
                      <span className="px-3 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/50 text-xs font-bold rounded-lg flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span> DEGRADED
                      </span>
                    </div>

                    <div className="space-y-4 pt-4 border-t border-white/5 relative z-10">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase">Edge Latency (p99)</span>
                        <span className="text-sm font-bold text-amber-400 font-mono">485.2 ms</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white/40 uppercase">Current Traffic</span>
                        <span className="text-sm font-bold text-white font-mono">85k req/s</span>
                      </div>
                      <div className="flex justify-between items-center bg-amber-500/10 p-2 rounded border border-amber-500/20">
                        <span className="text-[10px] font-bold text-amber-400">ALERT: High network latency detected on incoming connections. Auto-failover prepared.</span>
                      </div>
                    </div>
                  </div>

                </div>
              </>
            )}

            {activeTab === 'failover' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Active-Passive Failover Console</h2>
                    <p className="text-sm text-white/60 mt-1">Execute manual Disaster Recovery (DR) protocols to force-drain global regions.</p>
                  </div>
                </div>

                {/* DR Execution Panel */}
                <div className="glass-card bg-black/80 border border-rose-500/30 rounded-xl p-8 shadow-[0_0_30px_rgba(244,63,94,0.1)] backdrop-blur-md mb-8">
                  <div className="flex justify-between items-center mb-8">
                    <h3 className="text-lg font-bold text-rose-400 flex items-center gap-2">
                      <span>⚠️</span> Initiate Disaster Recovery Failover
                    </h3>
                  </div>

                  <div className="flex items-center gap-6">
                    {/* Source */}
                    <div className="flex-1 bg-white/5 border border-white/10 rounded-lg p-4">
                      <label className="text-[10px] text-white/40 uppercase font-bold mb-2 block">Drain Traffic From (Failed Region)</label>
                      <select className="w-full bg-black/50 border border-white/20 rounded p-2 text-white font-mono text-sm outline-none focus:border-rose-500">
                        <option value="us-east-1">aws_us-east-1 (US East)</option>
                        <option value="eu-west-1">aws_eu-west-1 (Europe)</option>
                        <option value="asia-northeast1">gcp_asia-northeast1 (Tokyo)</option>
                      </select>
                    </div>

                    <div className="flex flex-col items-center justify-center pt-6">
                      <svg className="w-6 h-6 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                      </svg>
                    </div>

                    {/* Target */}
                    <div className="flex-1 bg-white/5 border border-white/10 rounded-lg p-4">
                      <label className="text-[10px] text-white/40 uppercase font-bold mb-2 block">Failover To (Healthy Target)</label>
                      <select className="w-full bg-black/50 border border-white/20 rounded p-2 text-white font-mono text-sm outline-none focus:border-rose-500">
                        <option value="eu-west-1">aws_eu-west-1 (Europe)</option>
                        <option value="us-east-1">aws_us-east-1 (US East)</option>
                        <option value="asia-northeast1">gcp_asia-northeast1 (Tokyo)</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-8 flex justify-end">
                    <button className="px-6 py-3 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-sm font-bold transition-colors shadow-[0_0_15px_rgba(225,29,72,0.4)] flex items-center gap-2">
                      <span>⚡</span> EXECUTE GLOBAL FAILOVER
                    </button>
                  </div>
                </div>

                {/* DR Incident History */}
                <h3 className="text-sm font-bold text-white/60 uppercase tracking-wider mb-4">Recent DR Incidents</h3>
                <div className="glass-card bg-black/80 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-white/5 border-b border-white/10 text-[10px] text-white/40 uppercase tracking-wider">
                        <th className="p-4 font-bold">Incident ID</th>
                        <th className="p-4 font-bold">Timestamp</th>
                        <th className="p-4 font-bold">Route Transition</th>
                        <th className="p-4 font-bold">Status</th>
                      </tr>
                    </thead>
                    <tbody className="text-sm font-mono">
                      <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4 text-white">dr_9f8e7d6c</td>
                        <td className="p-4 text-white/60">2026-06-15 14:22:01 UTC</td>
                        <td className="p-4">
                          <div className="flex items-center gap-2 text-white/80">
                            <span className="line-through text-rose-400">aws_eu-central-1</span>
                            <span>→</span>
                            <span className="text-emerald-400">aws_eu-west-1</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 text-[10px] font-bold rounded">COMPLETED</span>
                        </td>
                      </tr>
                      <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4 text-white">dr_1a2b3c4d</td>
                        <td className="p-4 text-white/60">2025-11-03 09:15:44 UTC</td>
                        <td className="p-4">
                          <div className="flex items-center gap-2 text-white/80">
                            <span className="line-through text-rose-400">gcp_us-west1</span>
                            <span>→</span>
                            <span className="text-emerald-400">aws_us-east-1</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 text-[10px] font-bold rounded">COMPLETED</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </>
            )}

          </div>
        </div>

      </div>
    </div>
  );
};
