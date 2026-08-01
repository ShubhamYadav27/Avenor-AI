export default function Page() {
  return (
    <div className="w-full min-h-[70vh] flex flex-col items-center justify-center px-6 text-center">
      <h1 className="text-5xl font-bold mb-6 capitalize">ai</h1>
      <p className="text-xl text-white/50 max-w-2xl mx-auto mb-10">
        Detailed documentation and product capabilities for ai are actively being migrated to this enterprise portal.
      </p>
      <div className="glass-card p-8 rounded-2xl border-white/10 max-w-3xl w-full text-left text-white/70 space-y-4">
         <p><strong>Architecture Segment:</strong> Enterprise Grade</p>
         <p><strong>Status:</strong> Certified & Locked (Phase 9.10)</p>
         <p>Please refer to the <a href="https://github.com/Avenor/Avenor-AI/blob/main/docs/ROADMAP.md" className="text-indigo-400 hover:underline">Official GitHub Documentation</a> for full architectural deep-dives.</p>
      </div>
    </div>
  )
}
