import { Outlet, Link } from 'react-router-dom';
import { Activity, Shield, Database, Brain, Cpu, Server, Lock } from 'lucide-react';

export default function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-[#050505]">
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-white/10 bg-[#020202] flex flex-col">
        <div className="p-4 border-b border-white/10 flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-gradient-to-br from-indigo-500 to-purple-600"></div>
          <span className="font-bold text-lg text-white">AVENOR-AI</span>
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-2 text-sm text-white/60">
          <div className="text-xs font-bold text-white/30 uppercase mb-2">Revenue OS</div>
          <Link to="/dashboard/revenue-os" className="flex items-center gap-2 hover:text-white"><Activity size={16}/> Revenue OS</Link>
          <Link to="/dashboard/billing" className="flex items-center gap-2 hover:text-white"><Database size={16}/> Billing</Link>
          
          <div className="text-xs font-bold text-white/30 uppercase mt-6 mb-2">AI Platform</div>
          <Link to="/dashboard/prompt-studio" className="flex items-center gap-2 hover:text-white"><Brain size={16}/> Prompt Studio</Link>
          <Link to="/dashboard/agents" className="flex items-center gap-2 hover:text-white"><Cpu size={16}/> Agent Builder</Link>
          <Link to="/dashboard/feature-store" className="flex items-center gap-2 hover:text-white"><Database size={16}/> Feature Store</Link>
          <Link to="/dashboard/foundation-models" className="flex items-center gap-2 hover:text-white"><Server size={16}/> Models</Link>
          
          <div className="text-xs font-bold text-white/30 uppercase mt-6 mb-2">Enterprise</div>
          <Link to="/dashboard/admin" className="flex items-center gap-2 hover:text-white"><Shield size={16}/> Administration</Link>
          <Link to="/dashboard/ai-governance" className="flex items-center gap-2 hover:text-white"><Lock size={16}/> AI Governance</Link>
          <Link to="/dashboard/compliance" className="flex items-center gap-2 hover:text-white"><Shield size={16}/> Compliance</Link>
          <Link to="/dashboard/developer-portal" className="flex items-center gap-2 hover:text-white"><Cpu size={16}/> Developer Portal</Link>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative">
        <header className="h-16 border-b border-white/10 bg-[#020202] flex items-center px-6 justify-between">
            <input type="text" placeholder="Command Palette (Cmd+K)..." className="bg-white/5 border border-white/10 rounded-lg px-4 py-1.5 text-sm w-96 text-white focus:outline-none focus:border-indigo-500 transition" />
            <div className="flex items-center gap-4">
               <div className="w-8 h-8 bg-indigo-500/20 rounded-full border border-indigo-500/50 flex items-center justify-center text-xs font-bold text-indigo-400">AE</div>
            </div>
        </header>
        <div className="flex-1 overflow-auto p-8 relative">
          {/* Global Loading Suspense would go here */}
          <Outlet />
        </div>
      </main>
    </div>
  );
}
