import React from 'react';

export const InstalledApps: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-8">
      <div className="max-w-7xl mx-auto mb-12">
        <h1 className="text-4xl font-bold text-white mb-2">Installed Apps</h1>
        <p className="text-white/60 text-lg">Manage integrations and permissions for your workspace.</p>
      </div>
      
      <div className="max-w-7xl mx-auto">
        <div className="glass-card p-8 border border-white/10 rounded-2xl bg-white/5">
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 border border-blue-500/50 flex items-center justify-center text-blue-400 font-bold">
                SF
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Salesforce Sync</h3>
                <p className="text-sm text-green-400">Activated • v2.0.0</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm transition-colors border border-white/10">
                Configure
              </button>
              <button className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-sm transition-colors border border-red-500/20">
                Suspend
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
