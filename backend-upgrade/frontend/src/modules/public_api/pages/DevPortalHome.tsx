import React, { useState } from 'react';

export const DevPortalHome: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'keys' | 'usage' | 'sdks' | 'webhooks' | 'docs'>('keys');
  const [showKeySecret, setShowKeySecret] = useState<string | null>(null);

  const mockKeys = [
    { id: 'key_1', name: 'Production Sync', prefix: 'av_live_xh29s', scopes: ['read:companies', 'write:companies'], created: '2026-07-30', lastUsed: '5 mins ago' },
    { id: 'key_2', name: 'Analytics Dashboard', prefix: 'av_live_m09q', scopes: ['read:signals', 'read:opportunities'], created: '2026-07-28', lastUsed: '1 hour ago' }
  ];

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-12 border-b border-white/10 pb-8">
          <div>
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300 tracking-tight">
              Developer Portal
            </h1>
            <p className="text-white/60 mt-3 text-lg">Manage API Keys, view usage telemetry, and build integrations.</p>
          </div>
          <button className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)]">
            + Generate New Key
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-6 mb-8 border-b border-white/10">
          {['Keys', 'Usage', 'SDKs', 'Webhooks', 'Docs'].map(tab => {
            const val = tab.toLowerCase() as 'keys' | 'usage' | 'sdks' | 'webhooks' | 'docs';
            return (
              <button 
                key={tab}
                onClick={() => setActiveTab(val)}
                className={`pb-4 px-2 text-sm font-medium transition-colors border-b-2 ${
                  activeTab === val ? 'border-blue-500 text-blue-400' : 'border-transparent text-white/50 hover:text-white'
                }`}
              >
                {tab}
              </button>
            )
          })}
        </div>

        {/* Tab Content: Keys */}
        {activeTab === 'keys' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl text-yellow-300 text-sm flex gap-3">
              <svg className="w-5 h-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Keep your API keys secure. Do not expose them in client-side code or public repositories.
            </div>

            {mockKeys.map(key => (
              <div key={key.id} className="glass-card bg-white/5 border border-white/10 p-6 rounded-2xl flex flex-col md:flex-row gap-6 md:items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                    {key.name}
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">Pro Tier</span>
                  </h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {key.scopes.map(scope => (
                      <span key={scope} className="text-xs text-white/60 bg-black/40 px-2 py-1 rounded font-mono border border-white/5">
                        {scope}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col items-end gap-3">
                  <div className="flex items-center gap-3">
                    <code className="text-sm font-mono bg-black/60 px-4 py-2 rounded-lg text-white/80 border border-white/10">
                      {key.prefix}••••••••••••
                    </code>
                    <button className="text-white/40 hover:text-white transition-colors" title="Copy to clipboard">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                  <div className="text-xs text-white/40 flex items-center gap-4">
                    <span>Created: {key.created}</span>
                    <span>Last Used: {key.lastUsed}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab Content: Usage */}
        {activeTab === 'usage' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="glass-card bg-white/5 border border-white/10 p-6 rounded-2xl">
                <h4 className="text-white/60 text-sm font-medium">API Requests (24h)</h4>
                <p className="text-4xl font-bold text-white mt-2">12,458</p>
                <div className="w-full bg-white/10 h-1 mt-4 rounded-full overflow-hidden">
                  <div className="bg-blue-500 h-full w-[25%] rounded-full"></div>
                </div>
                <p className="text-xs text-white/40 mt-2">25% of 50,000 daily quota</p>
              </div>

              <div className="glass-card bg-white/5 border border-white/10 p-6 rounded-2xl">
                <h4 className="text-white/60 text-sm font-medium">Error Rate</h4>
                <p className="text-4xl font-bold text-green-400 mt-2">0.02%</p>
                <p className="text-xs text-white/40 mt-4 border-t border-white/10 pt-2">System healthy</p>
              </div>

              <div className="glass-card bg-white/5 border border-white/10 p-6 rounded-2xl">
                <h4 className="text-white/60 text-sm font-medium">Average Latency</h4>
                <p className="text-4xl font-bold text-white mt-2">42ms</p>
                <p className="text-xs text-white/40 mt-4 border-t border-white/10 pt-2">99th percentile: 104ms</p>
              </div>
            </div>
          </div>
        )}

        {/* Tab Content: SDKs */}
        {activeTab === 'sdks' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-6">
              <h2 className="text-2xl font-bold">Official SDKs</h2>
              <p className="text-white/60">Integrate AVENOR into your applications with strict type safety, automatic retries, and pagination support.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Python SDK */}
              <div className="glass-card bg-white/5 border border-white/10 p-6 rounded-2xl flex flex-col justify-between">
                <div>
                  <h3 className="text-xl font-bold flex items-center gap-3">
                    <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-sm">v1.2.0</span>
                    Python
                  </h3>
                  <p className="text-sm text-white/60 mt-2">Perfect for data engineering, AI agent integrations, and backend scripting.</p>
                </div>
                <div className="mt-6">
                  <div className="bg-black/60 rounded-lg p-4 font-mono text-sm border border-white/10 flex justify-between items-center text-white/80">
                    <code>pip install avenor-sdk</code>
                  </div>
                  <button className="mt-4 w-full py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">
                    View Python Docs
                  </button>
                </div>
              </div>

              {/* TypeScript SDK */}
              <div className="glass-card bg-white/5 border border-white/10 p-6 rounded-2xl flex flex-col justify-between">
                <div>
                  <h3 className="text-xl font-bold flex items-center gap-3">
                    <span className="bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-sm">v2.0.1</span>
                    TypeScript / Node.js
                  </h3>
                  <p className="text-sm text-white/60 mt-2">Build robust full-stack applications and Marketplace Cards with strict typings.</p>
                </div>
                <div className="mt-6">
                  <div className="bg-black/60 rounded-lg p-4 font-mono text-sm border border-white/10 flex justify-between items-center text-white/80">
                    <code>npm install @avenor/sdk</code>
                  </div>
                  <button className="mt-4 w-full py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">
                    View TypeScript Docs
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Content: Webhooks */}
        {activeTab === 'webhooks' && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-6 flex justify-between items-end">
              <div>
                <h2 className="text-2xl font-bold">Webhook Endpoints</h2>
                <p className="text-white/60">Subscribe to real-time events via HTTPS. Payloads are secured with HMAC SHA-256 signatures.</p>
              </div>
              <button className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium transition-colors border border-white/10">
                + Add Endpoint
              </button>
            </div>
            
            <div className="glass-card bg-white/5 border border-white/10 p-6 rounded-2xl flex flex-col justify-between">
              <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]"></div>
                  <h3 className="font-mono text-lg font-bold">https://api.mycompany.com/avenor-webhook</h3>
                </div>
                <button className="text-sm text-white/50 hover:text-white transition-colors">Edit</button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-xs uppercase text-white/40 font-bold tracking-wider mb-2">Subscribed Events</h4>
                  <div className="flex flex-wrap gap-2">
                    <span className="text-xs text-white/80 bg-blue-500/10 px-2 py-1 rounded font-mono border border-blue-500/20">company.*</span>
                    <span className="text-xs text-white/80 bg-blue-500/10 px-2 py-1 rounded font-mono border border-blue-500/20">opportunity.won</span>
                  </div>
                </div>

                <div>
                  <h4 className="text-xs uppercase text-white/40 font-bold tracking-wider mb-2">Signing Secret</h4>
                  <div className="flex items-center gap-3">
                    <code className="text-sm font-mono bg-black/60 px-4 py-2 rounded-lg text-white border border-white/10 flex-1">
                      whsec_••••••••••••••••••••••••
                    </code>
                    <button className="text-white/40 hover:text-white transition-colors" title="Reveal secret">
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                  </div>
                  <p className="text-[11px] text-white/40 mt-2">Use this secret to verify the <code className="text-white/60">X-Avenor-Signature</code> header.</p>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-white/10">
                <h4 className="text-xs uppercase text-white/40 font-bold tracking-wider mb-3">Recent Deliveries</h4>
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between text-sm py-1">
                    <div className="flex items-center gap-3">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                      <span className="font-mono text-white/80">evt_001a4b</span>
                      <span className="text-white/50">company.created</span>
                    </div>
                    <span className="text-white/40">2 mins ago</span>
                  </div>
                  <div className="flex items-center justify-between text-sm py-1">
                    <div className="flex items-center gap-3">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                      <span className="font-mono text-white/80">evt_001a4c</span>
                      <span className="text-white/50">opportunity.won</span>
                      <span className="text-red-400 text-xs ml-2">ERR_CONNECTION_REFUSED (Retrying)</span>
                    </div>
                    <span className="text-white/40">15 mins ago</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
