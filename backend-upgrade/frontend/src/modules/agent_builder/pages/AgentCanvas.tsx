import React, { useState } from 'react';

export const AgentCanvas: React.FC = () => {
  const [zoom, setZoom] = useState(100);

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Agent Builder</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Deal Desk Research Team</span>
            <span className="text-[10px] text-green-400 font-mono">2 Agents • Active</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="text-white/60 hover:text-white text-sm font-medium transition-colors">Test Run Goal</button>
          <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">Save Draft</button>
          <button className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(6,182,212,0.4)]">Deploy Team</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Node Palette (Sidebar) */}
        <div className="w-64 bg-black/40 border-r border-white/10 p-4 flex flex-col gap-6 overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div>
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">Agent Roles</h3>
            <div className="space-y-2">
              <div className="p-3 bg-white/5 border border-white/10 rounded-lg cursor-grab hover:bg-white/10 transition-colors flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-purple-500/20 text-purple-400 flex items-center justify-center">🧠</div>
                <span className="text-sm">Research Analyst</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/10 rounded-lg cursor-grab hover:bg-white/10 transition-colors flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-blue-500/20 text-blue-400 flex items-center justify-center">✍️</div>
                <span className="text-sm">Strategic Writer</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">Tool Sandboxes</h3>
            <div className="space-y-2">
              <div className="p-2 border border-dashed border-white/20 rounded text-xs text-center text-white/40 cursor-grab hover:border-white/40">
                + Drag Tool Sandbox
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Canvas Area */}
        <div className="flex-1 relative bg-[#0a0a0a] overflow-hidden" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.05) 1px, transparent 0)', backgroundSize: '32px 32px' }}>
          
          <div className="absolute top-4 right-4 z-10 flex items-center gap-2 bg-black/60 border border-white/10 rounded-lg p-1 backdrop-blur-md">
            <button onClick={() => setZoom(z => Math.max(50, z - 10))} className="p-1.5 hover:bg-white/10 rounded text-white/60 hover:text-white">−</button>
            <span className="text-xs font-mono w-12 text-center text-white/60">{zoom}%</span>
            <button onClick={() => setZoom(z => Math.min(150, z + 10))} className="p-1.5 hover:bg-white/10 rounded text-white/60 hover:text-white">+</button>
          </div>

          {/* Render Graph (Simulated Visual Layout) */}
          <div className="absolute inset-0 transition-transform origin-top-left" style={{ transform: `scale(${zoom / 100})`, padding: '100px' }}>
            
            {/* Agent Delegation Line */}
            <svg className="absolute inset-0 pointer-events-none w-full h-full" style={{ zIndex: 0 }}>
              <path d="M 320 200 C 400 200, 400 200, 480 200" stroke="rgba(255,255,255,0.2)" strokeWidth="3" strokeDasharray="5,5" fill="none" />
              <polygon points="480,200 470,195 470,205" fill="rgba(255,255,255,0.2)" />
            </svg>

            <div className="relative z-10 flex gap-40">
              
              {/* Agent 1: Researcher */}
              <div className="w-[300px] glass-card bg-black/80 border border-white/10 rounded-xl overflow-hidden shadow-2xl backdrop-blur-md transform transition-transform hover:scale-[1.02]">
                <div className="h-2 bg-gradient-to-r from-purple-500 to-indigo-500"></div>
                <div className="p-5">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-lg text-white">Company Intelligence</h3>
                      <p className="text-xs text-purple-400">Role: Senior Research Analyst</p>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-lg">🧠</div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-white/40 block mb-1">Prompt Studio Link</span>
                      <div className="bg-white/5 border border-white/10 rounded p-2 text-xs font-mono text-white/80 flex justify-between">
                        <span>pt_research</span>
                        <span className="text-purple-400">v2.1</span>
                      </div>
                    </div>
                    
                    <div>
                      <span className="text-[10px] uppercase font-bold text-white/40 block mb-1">Permitted Tools</span>
                      <div className="space-y-1">
                        <div className="bg-green-500/10 border border-green-500/20 rounded px-2 py-1 text-[11px] font-mono text-green-400">
                          public_api.get_company
                        </div>
                        <div className="bg-green-500/10 border border-green-500/20 rounded px-2 py-1 text-[11px] font-mono text-green-400">
                          workflow.trigger_enrichment
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Agent 2: Writer */}
              <div className="w-[300px] glass-card bg-black/80 border border-white/10 rounded-xl overflow-hidden shadow-2xl backdrop-blur-md transform transition-transform hover:scale-[1.02]">
                <div className="h-2 bg-gradient-to-r from-blue-500 to-cyan-500"></div>
                <div className="p-5">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-lg text-white">Executive Briefing</h3>
                      <p className="text-xs text-blue-400">Role: Strategic Content Writer</p>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-lg">✍️</div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-white/40 block mb-1">Prompt Studio Link</span>
                      <div className="bg-white/5 border border-white/10 rounded p-2 text-xs font-mono text-white/80 flex justify-between">
                        <span>pt_writer</span>
                        <span className="text-blue-400">v1.0</span>
                      </div>
                    </div>
                    
                    <div>
                      <span className="text-[10px] uppercase font-bold text-white/40 block mb-1">Permitted Tools</span>
                      <div className="space-y-1">
                        <div className="bg-pink-500/10 border border-pink-500/20 rounded px-2 py-1 text-[11px] font-mono text-pink-400">
                          workflow.start_approval
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>

          </div>
        </div>

      </div>
    </div>
  );
};
