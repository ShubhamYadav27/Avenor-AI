import React, { useState } from 'react';

export const ComplianceCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('frameworks');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Compliance Cloud</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">Enterprise Trust & Security</span>
            <span className="text-[10px] text-blue-400 font-mono">Continuous Audit: ACTIVE</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-bold transition-colors shadow-[0_0_15px_rgba(37,99,235,0.3)] flex items-center gap-2">
            <span>📄</span> Export SOC2 Report
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Navigation Sidebar */}
        <div className="w-64 bg-black/40 border-r border-white/10 flex flex-col overflow-y-auto shrink-0 z-10 backdrop-blur-md">
          <div className="p-4 space-y-1">
            <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-wider mb-2 px-2">Governance Console</h3>
            <button 
              onClick={() => setActiveTab('frameworks')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'frameworks' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🏛️</span> Regulatory Frameworks
            </button>
            <button 
              onClick={() => setActiveTab('classification')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'classification' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🏷️</span> Data Classification
            </button>
            <button 
              onClick={() => setActiveTab('privacy')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${activeTab === 'privacy' ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <span className="text-lg">🛡️</span> Privacy Requests (DSAR)
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-[#0a0a0a] overflow-y-auto p-8" 
             style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.02) 1px, transparent 0)', backgroundSize: '24px 24px' }}>
          
          <div className="max-w-5xl mx-auto space-y-8">
            
            {activeTab === 'frameworks' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Compliance Framework Readiness</h2>
                    <p className="text-sm text-white/60 mt-1">Real-time control auditing across all infrastructure and AI assets.</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  {/* SOC2 */}
                  <div className="glass-card bg-black/80 border border-emerald-500/30 rounded-xl p-6 shadow-[0_0_20px_rgba(16,185,129,0.1)] backdrop-blur-md relative overflow-hidden">
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded bg-emerald-500/20 flex items-center justify-center border border-emerald-500/50">
                          <span className="text-xl">🔐</span>
                        </div>
                        <div>
                          <h3 className="font-bold text-white text-lg">SOC 2 Type II</h3>
                          <p className="text-xs text-white/40">Security, Availability, Confidentiality</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-bold text-emerald-400 font-mono">100%</span>
                        <p className="text-[10px] text-white/40 uppercase">Readiness Score</p>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between items-center text-sm p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
                        <span className="text-white/80">CC-1.1: Logical Access Policies Enforced</span>
                        <span className="text-emerald-400">✓ PASS</span>
                      </div>
                      <div className="flex justify-between items-center text-sm p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
                        <span className="text-white/80">CC-2.1: Data Encryption At-Rest (AES-256)</span>
                        <span className="text-emerald-400">✓ PASS</span>
                      </div>
                      <div className="flex justify-between items-center text-sm p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
                        <span className="text-white/80">CC-3.1: Change Management (GitOps)</span>
                        <span className="text-emerald-400">✓ PASS</span>
                      </div>
                    </div>
                  </div>

                  {/* GDPR */}
                  <div className="glass-card bg-black/80 border border-amber-500/30 rounded-xl p-6 shadow-[0_0_20px_rgba(245,158,11,0.1)] backdrop-blur-md relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl"></div>
                    
                    <div className="flex justify-between items-start mb-6 relative z-10">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded bg-amber-500/20 flex items-center justify-center border border-amber-500/50">
                          <span className="text-xl">🇪🇺</span>
                        </div>
                        <div>
                          <h3 className="font-bold text-white text-lg">GDPR Compliance</h3>
                          <p className="text-xs text-white/40">General Data Protection Regulation</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-bold text-amber-400 font-mono">94%</span>
                        <p className="text-[10px] text-white/40 uppercase">Readiness Score</p>
                      </div>
                    </div>

                    <div className="space-y-3 relative z-10">
                      <div className="flex justify-between items-center text-sm p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
                        <span className="text-white/80">Art. 17: Right to Erasure Enforcement</span>
                        <span className="text-emerald-400">✓ PASS</span>
                      </div>
                      <div className="flex justify-between items-center text-sm p-2 bg-emerald-500/10 border border-emerald-500/20 rounded">
                        <span className="text-white/80">Art. 32: Security of Processing</span>
                        <span className="text-emerald-400">✓ PASS</span>
                      </div>
                      <div className="flex justify-between items-center text-sm p-2 bg-amber-500/10 border border-amber-500/30 rounded">
                        <div className="flex flex-col">
                          <span className="text-white font-bold">Art. 30: Record of Processing Activities</span>
                          <span className="text-[10px] text-amber-400">Missing documentation mapping for new AI pipeline.</span>
                        </div>
                        <span className="text-amber-400">⚠ PENDING</span>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'classification' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Data Classification & Retention</h2>
                    <p className="text-sm text-white/60 mt-1">Immutable time-to-live policies bound to security classification levels.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {/* Public */}
                  <div className="glass-card bg-black/80 border border-white/10 rounded-xl p-5 shadow-lg backdrop-blur-md flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded bg-white/5 flex items-center justify-center border border-white/10">
                        <span className="text-white/40 font-bold text-xs">PUB</span>
                      </div>
                      <div>
                        <h3 className="font-bold text-white text-sm">PUBLIC DATA</h3>
                        <p className="text-xs text-white/40">Marketing assets, public API documentation.</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Retention Rule (TTL)</div>
                      <div className="text-sm font-bold text-white font-mono">Indefinite</div>
                    </div>
                  </div>

                  {/* Confidential */}
                  <div className="glass-card bg-black/80 border border-blue-500/30 rounded-xl p-5 shadow-lg backdrop-blur-md flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded bg-blue-500/20 flex items-center justify-center border border-blue-500/30">
                        <span className="text-blue-400 font-bold text-xs">CNF</span>
                      </div>
                      <div>
                        <h3 className="font-bold text-white text-sm">CONFIDENTIAL</h3>
                        <p className="text-xs text-white/40">Financial records, internal AI model artifacts.</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Retention Rule (TTL)</div>
                      <div className="text-sm font-bold text-blue-400 font-mono">180 Days</div>
                    </div>
                  </div>

                  {/* Restricted */}
                  <div className="glass-card bg-black/80 border border-rose-500/40 rounded-xl p-5 shadow-[0_0_15px_rgba(244,63,94,0.15)] backdrop-blur-md flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded bg-rose-500/20 flex items-center justify-center border border-rose-500/40">
                        <span className="text-rose-400 font-bold text-xs">RST</span>
                      </div>
                      <div>
                        <div className="flex gap-2 items-center">
                          <h3 className="font-bold text-white text-sm">RESTRICTED (PII / PCI)</h3>
                          <span className="px-1.5 py-0.5 bg-rose-500 text-black text-[9px] font-bold rounded">HIGH RISK</span>
                        </div>
                        <p className="text-xs text-white/40">Personally Identifiable Information, unmasked emails.</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-white/40 uppercase font-bold mb-1">Retention Rule (TTL)</div>
                      <div className="text-sm font-bold text-rose-400 font-mono">30 Days (Strict)</div>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'privacy' && (
              <>
                <div className="flex justify-between items-end mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-white tracking-tight">Privacy Requests (DSAR)</h2>
                    <p className="text-sm text-white/60 mt-1">Manage GDPR Data Subject Access Requests (Right to Erasure, Data Export).</p>
                  </div>
                </div>

                <div className="glass-card bg-black/80 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-white/5 border-b border-white/10 text-[10px] text-white/40 uppercase tracking-wider">
                        <th className="p-4 font-bold">Request ID</th>
                        <th className="p-4 font-bold">User Identity</th>
                        <th className="p-4 font-bold">Type</th>
                        <th className="p-4 font-bold">Submitted Date</th>
                        <th className="p-4 font-bold">Status</th>
                        <th className="p-4 font-bold text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="text-sm font-mono">
                      <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4 text-white">pr_a1b2c3d4</td>
                        <td className="p-4 text-white/60">usr_982...771</td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-rose-500/20 text-rose-400 border border-rose-500/30 text-[10px] font-bold rounded uppercase">ERASURE</span>
                        </td>
                        <td className="p-4 text-white/60">2026-07-28 09:12 UTC</td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-bold rounded">PENDING</span>
                        </td>
                        <td className="p-4 text-right">
                          <button className="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-bold transition-colors">Execute Delete</button>
                        </td>
                      </tr>
                      
                      <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-4 text-white">pr_f5e4d3c2</td>
                        <td className="p-4 text-white/60">usr_123...abc</td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-blue-500/20 text-blue-400 border border-blue-500/30 text-[10px] font-bold rounded uppercase">EXPORT</span>
                        </td>
                        <td className="p-4 text-white/60">2026-07-27 14:45 UTC</td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold rounded">COMPLETED</span>
                        </td>
                        <td className="p-4 text-right">
                          <span className="text-xs text-white/40">Archived</span>
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
