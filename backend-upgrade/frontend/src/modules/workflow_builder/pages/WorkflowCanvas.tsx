import React, { useState } from 'react';

export const WorkflowCanvas: React.FC = () => {
  const [zoom, setZoom] = useState(100);

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Workflow Builder</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">High Intent Lead Follow-up</span>
            <span className="text-[10px] text-green-400 font-mono">v3 • Active</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="text-white/60 hover:text-white text-sm font-medium transition-colors">Test</button>
          <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">Save Draft</button>
          <button className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(79,70,229,0.4)]">Publish</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Node Palette (Sidebar) */}
        <div className="w-64 bg-black/40 border-r border-white/10 p-4 flex flex-col gap-6 overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div>
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">Triggers</h3>
            <div className="space-y-2">
              <div className="p-3 bg-white/5 border border-white/10 rounded-lg cursor-grab hover:bg-white/10 transition-colors flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-yellow-500/20 text-yellow-400 flex items-center justify-center">⚡</div>
                <span className="text-sm">Signal Created</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/10 rounded-lg cursor-grab hover:bg-white/10 transition-colors flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-yellow-500/20 text-yellow-400 flex items-center justify-center">⏰</div>
                <span className="text-sm">Schedule / Cron</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">Logic</h3>
            <div className="space-y-2">
              <div className="p-3 bg-white/5 border border-white/10 rounded-lg cursor-grab hover:bg-white/10 transition-colors flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-blue-500/20 text-blue-400 flex items-center justify-center">⑂</div>
                <span className="text-sm">If / Else Condition</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">AI & Actions</h3>
            <div className="space-y-2">
              <div className="p-3 bg-white/5 border border-white/10 rounded-lg cursor-grab hover:bg-white/10 transition-colors flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-purple-500/20 text-purple-400 flex items-center justify-center">✨</div>
                <span className="text-sm">AI Research Node</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/10 rounded-lg cursor-grab hover:bg-white/10 transition-colors flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-green-500/20 text-green-400 flex items-center justify-center">✓</div>
                <span className="text-sm">Create CRM Task</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/10 rounded-lg cursor-grab hover:bg-white/10 transition-colors flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-pink-500/20 text-pink-400 flex items-center justify-center">#</div>
                <span className="text-sm">Slack Notification</span>
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Canvas Area */}
        <div className="flex-1 relative bg-[#0a0a0a] overflow-hidden" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.05) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="absolute top-4 right-4 z-10 flex items-center gap-2 bg-black/60 border border-white/10 rounded-lg p-1 backdrop-blur-md">
            <button onClick={() => setZoom(z => Math.max(50, z - 10))} className="p-1.5 hover:bg-white/10 rounded text-white/60 hover:text-white">−</button>
            <span className="text-xs font-mono w-12 text-center text-white/60">{zoom}%</span>
            <button onClick={() => setZoom(z => Math.min(150, z + 10))} className="p-1.5 hover:bg-white/10 rounded text-white/60 hover:text-white">+</button>
          </div>

          {/* Render Graph (Simulated Visual Layout) */}
          <div className="absolute inset-0 transition-transform origin-top-left" style={{ transform: `scale(${zoom / 100})`, padding: '100px' }}>
            
            {/* Edge line drawing (SVG background) */}
            <svg className="absolute inset-0 pointer-events-none w-full h-full" style={{ zIndex: 0 }}>
              <path d="M 300 140 L 300 220" stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none" />
              <path d="M 300 300 L 150 400" stroke="rgba(34,197,94,0.5)" strokeWidth="2" fill="none" />
              <path d="M 300 300 L 450 400" stroke="rgba(239,68,68,0.5)" strokeWidth="2" fill="none" />
            </svg>

            <div className="relative z-10">
              {/* Trigger Node */}
              <div className="absolute left-[180px] top-[40px] w-64 glass-card bg-black/80 border-t-2 border-t-yellow-400 border-x border-b border-white/10 rounded-xl p-4 shadow-xl backdrop-blur-md">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-yellow-400">⚡</span>
                    <span className="font-bold text-sm">Signal Created</span>
                  </div>
                  <span className="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white/60 font-mono">n1</span>
                </div>
                <div className="bg-white/5 rounded p-2 text-xs font-mono text-white/80 border border-white/10">
                  <span className="text-white/40">signal_type:</span> "high_intent"
                </div>
                <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-4 h-4 bg-yellow-400 rounded-full border-2 border-[#0a0a0a]"></div>
              </div>

              {/* Condition Node */}
              <div className="absolute left-[180px] top-[220px] w-64 glass-card bg-black/80 border-t-2 border-t-blue-400 border-x border-b border-white/10 rounded-xl p-4 shadow-xl backdrop-blur-md">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-4 h-4 bg-[#0a0a0a] rounded-full border-2 border-white/20"></div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-blue-400">⑂</span>
                    <span className="font-bold text-sm">Condition Match</span>
                  </div>
                  <span className="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white/60 font-mono">n2</span>
                </div>
                <div className="bg-white/5 rounded p-2 text-xs font-mono text-blue-300 border border-blue-500/20">
                  {"{{trigger.payload.score}} > 80"}
                </div>
                <div className="absolute -bottom-3 left-8 w-4 h-4 bg-green-500 rounded-full border-2 border-[#0a0a0a] flex items-center justify-center text-[8px] font-bold">T</div>
                <div className="absolute -bottom-3 right-8 w-4 h-4 bg-red-500 rounded-full border-2 border-[#0a0a0a] flex items-center justify-center text-[8px] font-bold">F</div>
              </div>

              {/* Action Node (True Branch) */}
              <div className="absolute left-[20px] top-[400px] w-64 glass-card bg-black/80 border-t-2 border-t-green-400 border-x border-b border-white/10 rounded-xl p-4 shadow-xl backdrop-blur-md">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-4 h-4 bg-[#0a0a0a] rounded-full border-2 border-green-500/50"></div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span className="font-bold text-sm">Create CRM Task</span>
                  </div>
                  <span className="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white/60 font-mono">n3</span>
                </div>
                <div className="bg-white/5 rounded p-2 text-xs font-mono text-white/80 border border-white/10">
                  <span className="text-white/40">assignee:</span> "sales_rep"
                </div>
              </div>

              {/* Action Node (False Branch) */}
              <div className="absolute left-[340px] top-[400px] w-64 glass-card bg-black/80 border-t-2 border-t-pink-400 border-x border-b border-white/10 rounded-xl p-4 shadow-xl backdrop-blur-md">
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-4 h-4 bg-[#0a0a0a] rounded-full border-2 border-red-500/50"></div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-pink-400">#</span>
                    <span className="font-bold text-sm">Slack Notification</span>
                  </div>
                  <span className="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white/60 font-mono">n4</span>
                </div>
                <div className="bg-white/5 rounded p-2 text-xs font-mono text-white/80 border border-white/10">
                  <span className="text-white/40">channel:</span> "#general"
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
