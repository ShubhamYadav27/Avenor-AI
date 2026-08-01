import React, { useState } from 'react';

export const PromptEditor: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'editor' | 'history' | 'eval'>('editor');
  const [systemPrompt, setSystemPrompt] = useState('You are a senior sales strategist at AVENOR.');
  const [userPrompt, setUserPrompt] = useState('Generate a brief for {{company.name}} focusing on {{signal.type}}.');

  return (
    <div className="min-h-screen bg-[#050505] text-white font-sans overflow-hidden flex flex-col">
      {/* Top Navbar */}
      <header className="h-14 bg-white/5 border-b border-white/10 flex items-center justify-between px-6 shrink-0 z-10 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <span className="font-bold text-lg tracking-tight">Prompt Studio</span>
          </div>
          <div className="h-4 w-px bg-white/20 mx-2"></div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">sales.executive_brief</span>
            <span className="text-[10px] text-yellow-400 font-mono">v1.2.0-draft</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="text-white/60 hover:text-white text-sm font-medium transition-colors">Diff Viewer</button>
          <button className="px-4 py-1.5 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors">Test Run</button>
          <button className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-[0_0_15px_rgba(79,70,229,0.4)]">Submit for Approval</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar (Variables & Config) */}
        <div className="w-64 bg-black/40 border-r border-white/10 p-4 flex flex-col gap-6 overflow-y-auto shrink-0 z-10">
          <div>
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">Model Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-white/60 mb-1 block">Provider</label>
                <select className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/80 focus:outline-none focus:border-indigo-500">
                  <option>Google Gemini</option>
                  <option>OpenAI</option>
                  <option>Anthropic</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-white/60 mb-1 block">Model</label>
                <select className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white/80 focus:outline-none focus:border-indigo-500">
                  <option>gemini-1.5-pro</option>
                  <option>gemini-1.5-flash</option>
                </select>
              </div>
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs text-white/60">Temperature</label>
                  <span className="text-xs font-mono text-white/40">0.7</span>
                </div>
                <input type="range" min="0" max="100" defaultValue="70" className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer" />
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-white/10">
            <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-3">Context Variables</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/10">
                <span className="text-xs font-mono text-blue-300">company.name</span>
                <span className="text-[10px] text-white/40">String</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/10">
                <span className="text-xs font-mono text-blue-300">company.industry</span>
                <span className="text-[10px] text-white/40">String</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-white/5 rounded border border-white/10">
                <span className="text-xs font-mono text-blue-300">signal.type</span>
                <span className="text-[10px] text-white/40">Enum</span>
              </div>
            </div>
            <button className="w-full mt-3 py-1.5 text-xs text-indigo-400 bg-indigo-500/10 rounded border border-indigo-500/20 hover:bg-indigo-500/20 transition-colors">
              + Add Variable
            </button>
          </div>
        </div>

        {/* Main Editor Area */}
        <div className="flex-1 flex flex-col bg-[#0a0a0a]">
          <div className="flex border-b border-white/10 px-4">
            <button className="px-4 py-3 text-sm font-medium border-b-2 border-indigo-500 text-indigo-400">Editor</button>
            <button className="px-4 py-3 text-sm font-medium border-b-2 border-transparent text-white/40 hover:text-white transition-colors">Live Preview</button>
            <button className="px-4 py-3 text-sm font-medium border-b-2 border-transparent text-white/40 hover:text-white transition-colors">Evaluation (92%)</button>
          </div>

          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            
            {/* System Prompt */}
            <div className="glass-card bg-black/40 border border-white/10 rounded-xl overflow-hidden shadow-lg">
              <div className="bg-white/5 border-b border-white/10 px-4 py-2 flex justify-between items-center">
                <span className="text-xs font-bold uppercase tracking-wider text-white/60">System Message</span>
                <span className="text-[10px] text-white/40 font-mono">11 Tokens</span>
              </div>
              <div className="p-4">
                <textarea 
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  className="w-full h-24 bg-transparent resize-none text-sm text-white/80 focus:outline-none font-mono"
                  placeholder="Enter system instructions..."
                />
              </div>
            </div>

            {/* User Prompt */}
            <div className="glass-card bg-black/40 border border-white/10 rounded-xl overflow-hidden shadow-lg relative">
              <div className="bg-white/5 border-b border-white/10 px-4 py-2 flex justify-between items-center">
                <span className="text-xs font-bold uppercase tracking-wider text-white/60">User Message</span>
                <span className="text-[10px] text-white/40 font-mono">~45 Tokens (Computed)</span>
              </div>
              <div className="p-4 relative">
                {/* Simulated Syntax Highlighting Overlay for Variables */}
                <div className="absolute inset-4 pointer-events-none text-sm font-mono whitespace-pre-wrap text-transparent">
                  Generate a brief for <span className="bg-indigo-500/30 text-indigo-300 rounded px-1">{'{{company.name}}'}</span> focusing on <span className="bg-indigo-500/30 text-indigo-300 rounded px-1">{'{{signal.type}}'}</span>.
                </div>
                <textarea 
                  value={userPrompt}
                  onChange={(e) => setUserPrompt(e.target.value)}
                  className="w-full h-32 bg-transparent resize-none text-sm text-white/80 focus:outline-none font-mono relative z-10 opacity-70"
                  placeholder="Enter user prompt..."
                />
              </div>
            </div>

            {/* Simulated AI Output (Playground) */}
            <div className="border border-green-500/30 bg-green-500/5 rounded-xl overflow-hidden">
              <div className="bg-green-500/10 border-b border-green-500/20 px-4 py-2 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                  <span className="text-xs font-bold uppercase tracking-wider text-green-400">Test Run Output</span>
                </div>
                <span className="text-[10px] text-green-400 font-mono">1.2s • 420 Tokens</span>
              </div>
              <div className="p-4 text-sm text-white/70 font-serif leading-relaxed">
                Here is the executive brief for <strong>Acme Corp</strong>, tailored specifically to address their recent <strong>high_intent</strong> signals...
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};
