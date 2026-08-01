import React, { useState } from 'react';

export const DashboardBuilder: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Analytics Studio</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">CRO Command Center</span>
            <span className="text-[10px] text-green-400 font-mono">Published • Global View</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="text-white/60 hover:text-white text-sm font-medium transition-colors">Export PDF</button>
          <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">Share Link</button>
          <button className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(16,185,129,0.4)]">Edit Dashboard</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Widget Palette (Sidebar) */}
        <div className="w-64 bg-black/40 border-r border-white/10 p-4 flex flex-col gap-6 overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          
          <div>
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">Widgets</h3>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-white/5 border border-white/10 rounded-lg p-3 cursor-grab hover:bg-white/10 transition-colors flex flex-col items-center justify-center gap-2">
                <span className="text-emerald-400 text-xl">#</span>
                <span className="text-[10px] font-bold text-white/60 text-center">KPI Card</span>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-lg p-3 cursor-grab hover:bg-white/10 transition-colors flex flex-col items-center justify-center gap-2">
                <span className="text-blue-400 text-xl">📊</span>
                <span className="text-[10px] font-bold text-white/60 text-center">Bar Chart</span>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-lg p-3 cursor-grab hover:bg-white/10 transition-colors flex flex-col items-center justify-center gap-2">
                <span className="text-purple-400 text-xl">📈</span>
                <span className="text-[10px] font-bold text-white/60 text-center">Line Chart</span>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-lg p-3 cursor-grab hover:bg-white/10 transition-colors flex flex-col items-center justify-center gap-2">
                <span className="text-yellow-400 text-xl">✨</span>
                <span className="text-[10px] font-bold text-white/60 text-center">AI Summary</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">Global Filters</h3>
            <div className="space-y-3">
              <div>
                <label className="text-[10px] text-white/60 mb-1 block">Time Range</label>
                <select className="w-full bg-white/5 border border-white/10 rounded px-2 py-1.5 text-xs text-white/80 focus:outline-none">
                  <option>Current Quarter (Q3 2026)</option>
                  <option>Year to Date</option>
                  <option>Last 30 Days</option>
                </select>
              </div>
              <div>
                <label className="text-[10px] text-white/60 mb-1 block">Region</label>
                <select className="w-full bg-white/5 border border-white/10 rounded px-2 py-1.5 text-xs text-white/80 focus:outline-none">
                  <option>Global</option>
                  <option>North America</option>
                  <option>EMEA</option>
                  <option>APAC</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Interactive Canvas Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-6" 
             style={{ backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.02) 1px, transparent 1px)', backgroundSize: '100px 100px' }}>
          
          <div className="max-w-6xl mx-auto space-y-6">
            
            {/* Top Row: KPIs */}
            <div className="grid grid-cols-4 gap-6">
              
              <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md relative overflow-hidden group hover:border-emerald-500/50 transition-colors">
                <div className="absolute top-3 right-3 text-white/20 group-hover:text-white/60 transition-colors">⚙️</div>
                <h4 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-1">Total Pipeline</h4>
                <div className="text-2xl font-bold text-white">$14.2M</div>
                <div className="mt-2 text-xs font-medium text-emerald-400 flex items-center gap-1">
                  <span>↑ 12% vs last Q</span>
                </div>
              </div>

              <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md relative overflow-hidden group hover:border-blue-500/50 transition-colors">
                <div className="absolute top-3 right-3 text-white/20 group-hover:text-white/60 transition-colors">⚙️</div>
                <h4 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-1">Closed Won ARR</h4>
                <div className="text-2xl font-bold text-white">$2.5M</div>
                <div className="mt-2 text-xs font-medium text-emerald-400 flex items-center gap-1">
                  <span>↑ 8% vs last Q</span>
                </div>
              </div>

              <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md relative overflow-hidden group hover:border-yellow-500/50 transition-colors">
                <div className="absolute top-3 right-3 text-white/20 group-hover:text-white/60 transition-colors">⚙️</div>
                <h4 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-1">Win Rate</h4>
                <div className="text-2xl font-bold text-white">34%</div>
                <div className="mt-2 text-xs font-medium text-red-400 flex items-center gap-1">
                  <span>↓ 2% vs last Q</span>
                </div>
              </div>

              <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md relative overflow-hidden group hover:border-purple-500/50 transition-colors">
                <div className="absolute top-3 right-3 text-white/20 group-hover:text-white/60 transition-colors">⚙️</div>
                <h4 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-1">Avg Sales Cycle</h4>
                <div className="text-2xl font-bold text-white">42 Days</div>
                <div className="mt-2 text-xs font-medium text-emerald-400 flex items-center gap-1">
                  <span>↓ 5 Days vs last Q</span>
                </div>
              </div>

            </div>

            {/* Middle Row: Charts */}
            <div className="grid grid-cols-3 gap-6">
              
              <div className="col-span-2 glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md relative group hover:border-white/20 transition-colors min-h-[300px] flex flex-col">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-sm font-bold text-white">Pipeline Generation Trend</h4>
                  <div className="text-white/20 group-hover:text-white/60 transition-colors">⚙️</div>
                </div>
                {/* Simulated Chart Container */}
                <div className="flex-1 w-full flex items-end justify-between px-2 pb-2 gap-4">
                  {[40, 55, 30, 70, 85, 60, 95].map((height, i) => (
                    <div key={i} className="w-full bg-indigo-500/20 rounded-t relative group/bar hover:bg-indigo-500/40 transition-colors" style={{ height: `${height}%` }}>
                      <div className="absolute -top-1 left-0 right-0 h-1 bg-indigo-400"></div>
                    </div>
                  ))}
                </div>
                <div className="flex justify-between px-2 pt-2 border-t border-white/10 text-[10px] text-white/40 font-mono">
                  <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span><span>Jul</span>
                </div>
              </div>

              <div className="col-span-1 glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md relative group hover:border-white/20 transition-colors flex flex-col">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-sm font-bold text-white">Revenue by Region</h4>
                  <div className="text-white/20 group-hover:text-white/60 transition-colors">⚙️</div>
                </div>
                {/* Simulated Horizontal Bar Chart */}
                <div className="flex-1 flex flex-col justify-center gap-4">
                  <div>
                    <div className="flex justify-between text-xs mb-1"><span className="text-white/60">North America</span><span className="font-mono text-white/80">$1.2M</span></div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-blue-500 w-[70%]"></div></div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1"><span className="text-white/60">EMEA</span><span className="font-mono text-white/80">$800K</span></div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-blue-400 w-[45%]"></div></div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1"><span className="text-white/60">APAC</span><span className="font-mono text-white/80">$500K</span></div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden"><div className="h-full bg-blue-300 w-[25%]"></div></div>
                  </div>
                </div>
              </div>

            </div>

            {/* Bottom Row: AI Insights */}
            <div className="glass-card bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/30 rounded-xl p-6 shadow-lg backdrop-blur-md relative group">
              <div className="absolute -top-3 left-6 px-3 py-1 bg-emerald-500 text-[#0a0a0a] text-[10px] font-bold uppercase tracking-wider rounded-full flex items-center gap-1">
                <span>✨</span> AI Executive Insight
              </div>
              <p className="text-sm text-white/80 leading-relaxed font-serif mt-2">
                Pipeline generation in <strong>EMEA</strong> has accelerated by 18% over the last 30 days, largely driven by the new FinTech campaign. However, win rates in <strong>North America</strong> have dipped slightly due to increased competitive presence from <em>Competitor X</em> in enterprise deals. Consider allocating additional technical presales resources to NA.
              </p>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};
