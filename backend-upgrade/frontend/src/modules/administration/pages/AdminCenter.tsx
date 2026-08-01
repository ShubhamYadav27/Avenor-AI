import React, { useState } from 'react';

export const AdminCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('security');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Enterprise Admin</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Acme Corp Global</span>
            <span className="text-[10px] text-emerald-400 font-mono">System Healthy • 0 Active Alerts</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="text-white/60 hover:text-white text-sm font-medium transition-colors">Export Compliance Report</button>
          <button className="px-4 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(225,29,72,0.4)]">Enforce Global Policy</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Governance</h3>
            <button 
              onClick={() => setActiveTab('security')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'security' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🛡️</span> Security Center
            </button>
            <button 
              onClick={() => setActiveTab('rbac')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'rbac' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🔑</span> Role Management (RBAC)
            </button>
            <button 
              onClick={() => setActiveTab('audit')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'audit' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">📜</span> Immutable Audit Ledger
            </button>
            <button 
              className="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 text-white/60 hover:text-white hover:bg-white/5"
            >
              <span className="text-lg">🏢</span> Workspaces & Isolation
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'security' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Security Posture</h2>
                    <p className="text-sm text-white/60 mt-1">Global security policies and risk detection.</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-6">
                  {/* Policies */}
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md hover:border-white/20 transition-colors">
                    <div className="flex justify-between items-start mb-4">
                      <h4 className="text-sm font-bold text-white">Active Policies</h4>
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded">ENFORCING</span>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-white/80">Strict IP Allowlist</span>
                        <div className="w-8 h-4 bg-emerald-500 rounded-full relative"><div className="absolute right-1 top-1 w-2 h-2 bg-black rounded-full"></div></div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-white/80">Enforce MFA (All Users)</span>
                        <div className="w-8 h-4 bg-emerald-500 rounded-full relative"><div className="absolute right-1 top-1 w-2 h-2 bg-black rounded-full"></div></div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-white/80">15-Min Session Timeout</span>
                        <div className="w-8 h-4 bg-white/20 rounded-full relative"><div className="absolute left-1 top-1 w-2 h-2 bg-white rounded-full"></div></div>
                      </div>
                    </div>
                  </div>

                  {/* Risks */}
                  <div className="glass-card bg-gradient-to-br from-rose-500/10 to-orange-500/10 border border-rose-500/30 rounded-xl p-5 shadow-lg backdrop-blur-md">
                    <h4 className="text-sm font-bold text-white mb-4">Recent Security Risks</h4>
                    <div className="space-y-3">
                      <div className="p-2 bg-rose-500/10 border border-rose-500/20 rounded">
                        <div className="text-xs font-bold text-rose-400">Suspicious Login Blocked</div>
                        <div className="text-[10px] text-white/60 font-mono mt-1">IP: 45.22.1.9 (Blocked by Policy)</div>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'rbac' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Role-Based Access Control</h2>
                    <p className="text-sm text-white/60 mt-1">Manage granular permissions across the Enterprise.</p>
                  </div>
                  <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">+ Create Custom Role</button>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl shadow-lg backdrop-blur-md overflow-hidden">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-white/5 border-b border-white/10">
                      <tr>
                        <th className="px-4 py-3 font-medium text-white/60">Role Name</th>
                        <th className="px-4 py-3 font-medium text-white/60">Assigned Users</th>
                        <th className="px-4 py-3 font-medium text-white/60">Key Permissions</th>
                        <th className="px-4 py-3 text-right"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      <tr className="hover:bg-white/5 transition-colors">
                        <td className="px-4 py-3 font-medium text-white">Super Admin</td>
                        <td className="px-4 py-3 text-white/60">12 Users</td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-0.5 bg-rose-500/20 text-rose-400 text-[10px] font-mono rounded">* (Full Access)</span>
                        </td>
                        <td className="px-4 py-3 text-right text-white/40">⚙️</td>
                      </tr>
                      <tr className="hover:bg-white/5 transition-colors">
                        <td className="px-4 py-3 font-medium text-white">Sales Rep</td>
                        <td className="px-4 py-3 text-white/60">450 Users</td>
                        <td className="px-4 py-3 flex gap-2">
                          <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-[10px] font-mono rounded">dashboard:read</span>
                          <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-[10px] font-mono rounded">agent:execute</span>
                        </td>
                        <td className="px-4 py-3 text-right text-white/40">⚙️</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {activeTab === 'audit' && (
              <>
                <div className="flex justify-between items-end">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Immutable Audit Ledger</h2>
                    <p className="text-sm text-white/60 mt-1">Cryptographically verifiable log of all platform actions.</p>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl shadow-lg backdrop-blur-md overflow-hidden font-mono text-xs">
                  <div className="p-3 bg-white/5 border-b border-white/10 flex gap-4 text-white/40 uppercase font-bold tracking-wider text-[10px]">
                    <div className="w-32">Timestamp (UTC)</div>
                    <div className="w-48">Action</div>
                    <div className="w-32">Actor ID</div>
                    <div className="flex-1">Details Context</div>
                  </div>
                  <div className="divide-y divide-white/5">
                    <div className="p-3 flex gap-4 hover:bg-white/5 transition-colors">
                      <div className="w-32 text-white/60">2026-07-31T23:44:12Z</div>
                      <div className="w-48 text-emerald-400">rbac.evaluation</div>
                      <div className="w-32 text-white/80">u_1</div>
                      <div className="flex-1 text-white/60">{"{granted: true, resource: 'system:wipe'}"}</div>
                    </div>
                    <div className="p-3 flex gap-4 hover:bg-white/5 transition-colors">
                      <div className="w-32 text-white/60">2026-07-31T23:44:11Z</div>
                      <div className="w-48 text-rose-400">security.login_attempt</div>
                      <div className="w-32 text-white/80">anonymous</div>
                      <div className="flex-1 text-white/60">{"{client_ip: '45.22.1.9', blocked_by_policy: true}"}</div>
                    </div>
                    <div className="p-3 flex gap-4 hover:bg-white/5 transition-colors">
                      <div className="w-32 text-white/60">2026-07-31T23:44:05Z</div>
                      <div className="w-48 text-purple-400">prompt.published</div>
                      <div className="w-32 text-white/80">u_1</div>
                      <div className="flex-1 text-white/60">{"{template_id: 'pt_writer', version: 'v1.0'}"}</div>
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
