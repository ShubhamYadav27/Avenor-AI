'use client'

import { motion } from 'framer-motion'
import { ArrowRight, Activity, Brain, Shield, Database, Lock, Globe, Zap, Cpu, Server, Network } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  return (
    <div className="w-full flex flex-col items-center">
      
      {/* 2. HERO SECTION */}
      <section className="relative w-full min-h-[90vh] flex items-center justify-center overflow-hidden bg-grid-pattern">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#050505]/80 to-[#050505] pointer-events-none"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-500/20 rounded-full blur-[120px] pointer-events-none"></div>
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative z-10 max-w-5xl mx-auto text-center px-6"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-card border-indigo-500/30 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-8">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
            Introducing the Intelligence Cloud
          </div>
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-8 leading-[1.1]">
            AI-Native Predictive <br />
            <span className="gradient-text">Revenue Intelligence</span>
          </h1>
          <p className="text-xl md:text-2xl text-white/60 mb-12 max-w-3xl mx-auto font-medium">
            Know who will buy. Know when. Know why. <br/> The Intelligence Layer for Modern Revenue Teams.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/contact" className="px-8 py-4 rounded-xl bg-white text-black font-bold text-lg hover:bg-white/90 transition shadow-[0_0_30px_rgba(255,255,255,0.3)] w-full sm:w-auto">
              Book Enterprise Demo
            </Link>
            <Link href="/platform" className="px-8 py-4 rounded-xl glass-card text-white font-bold text-lg hover:bg-white/5 transition flex items-center gap-2 w-full sm:w-auto justify-center">
              Watch Platform Tour <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </motion.div>
      </section>

      {/* 3. TRUST SECTION */}
      <section className="w-full py-20 border-y border-white/5 bg-white/[0.02]">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm font-bold text-white/40 uppercase tracking-widest mb-10">Trusted infrastructure ecosystem</p>
          <div className="flex flex-wrap justify-center gap-12 opacity-50 grayscale hover:grayscale-0 transition duration-500">
            {['Salesforce', 'HubSpot', 'Microsoft', 'AWS', 'Google Cloud', 'Snowflake', 'Databricks'].map((brand) => (
              <span key={brand} className="text-2xl font-bold font-mono tracking-tighter">{brand}</span>
            ))}
          </div>
        </div>
      </section>

      {/* 4. WHY AVENOR EXISTS */}
      <section className="w-full py-32 max-w-4xl mx-auto px-6 text-center">
        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <h2 className="text-4xl md:text-5xl font-bold mb-8">Sales teams don't suffer from lack of data.<br/><span className="text-white/40">They suffer from lack of intelligence.</span></h2>
          <p className="text-xl text-white/60 leading-relaxed mb-12">
            CRMs record the past. Intent tools generate noise. Lead databases create static lists. Manual research doesn't scale. 
            AVENOR continuously understands companies, people, technology, and global signals to predict exactly who will buy, when, and what to do next.
          </p>
        </motion.div>
      </section>

      {/* 5. PLATFORM OVERVIEW (ARCHITECTURE) */}
      <section className="w-full py-32 bg-[#020202]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">The Architecture of Intelligence</h2>
            <p className="text-xl text-white/50 max-w-3xl mx-auto">From raw global signals to autonomous revenue execution.</p>
          </div>
          
          {/* Animated Architecture Tree Mockup */}
          <div className="glass-card rounded-3xl p-10 flex flex-col md:flex-row items-center justify-between gap-8 border-white/10 relative overflow-hidden">
             <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 blur-[100px]"></div>
             
             <div className="flex-1 space-y-6 z-10">
               <div className="glass-card p-4 rounded-xl border-white/5 text-center"><Database className="mx-auto text-blue-400 mb-2" /> 1. Global Signals</div>
               <div className="w-1 h-8 bg-gradient-to-b from-white/20 to-transparent mx-auto"></div>
               <div className="glass-card p-4 rounded-xl border-indigo-500/30 text-center shadow-[0_0_30px_rgba(79,70,229,0.1)]"><Network className="mx-auto text-indigo-400 mb-2" /> 2. Knowledge Graph (Identity Resolution)</div>
               <div className="w-1 h-8 bg-gradient-to-b from-white/20 to-transparent mx-auto"></div>
               <div className="glass-card p-4 rounded-xl border-purple-500/30 text-center shadow-[0_0_30px_rgba(168,85,247,0.1)]"><Brain className="mx-auto text-purple-400 mb-2" /> 3. Foundation Models & Agents</div>
             </div>
             
             <div className="hidden md:flex flex-1 items-center justify-center z-10">
                <ArrowRight className="w-12 h-12 text-white/20" />
             </div>

             <div className="flex-1 z-10 w-full h-full glass-card p-8 rounded-2xl border-white/20 bg-white/5">
                <h3 className="text-2xl font-bold mb-4">Revenue OS</h3>
                <p className="text-white/60 text-sm mb-6">The operating system for the modern revenue team.</p>
                <div className="space-y-3">
                  <div className="h-10 bg-white/10 rounded flex items-center px-4 text-xs font-mono">Buying Window: HIGH</div>
                  <div className="h-10 bg-white/10 rounded flex items-center px-4 text-xs font-mono">Agent Action: PENDING APPROVAL</div>
                  <div className="h-10 bg-white/10 rounded flex items-center px-4 text-xs font-mono">Forecast Accuracy: 98.4%</div>
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* 7. ENTERPRISE INTELLIGENCE CLOUD */}
      <section className="w-full py-32 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-4xl md:text-5xl font-bold mb-16 text-center">Enterprise Intelligence Cloud</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { t: 'Company Intelligence', d: 'Firmographics & Growth' },
              { t: 'Contact Intelligence', d: 'Professional History' },
              { t: 'Buying Committee', d: 'Decision Maker Maps' },
              { t: 'Funding Signals', d: 'Venture & IPO events' },
              { t: 'Hiring Signals', d: 'Executive Movements' },
              { t: 'Competitive Intel', d: 'Market Share Shifts' }
            ].map((engine, i) => (
              <div key={i} className="glass-card p-8 rounded-2xl hover:bg-white/10 transition duration-300 cursor-pointer group">
                <Cpu className="w-8 h-8 text-indigo-400 mb-4 group-hover:scale-110 transition" />
                <h3 className="text-xl font-bold mb-2">{engine.t}</h3>
                <p className="text-sm text-white/50">{engine.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 10. MULTI AGENT PLATFORM */}
      <section className="w-full py-32 bg-[#020202] border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center gap-16">
          <div className="flex-1">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Multi-Agent Platform</h2>
            <p className="text-xl text-white/50 mb-8">Deploy fleets of autonomous SDRs and RevOps agents that reason, plan, and execute using your private Knowledge Graph.</p>
            <ul className="space-y-4 mb-8">
              <li className="flex items-center gap-3"><span className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm">✓</span> Prompt Studio & Versioning</li>
              <li className="flex items-center gap-3"><span className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm">✓</span> Tool Sandbox Execution</li>
              <li className="flex items-center gap-3"><span className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm">✓</span> Human-In-The-Loop Approval Gates</li>
            </ul>
            <Link href="/agents" className="text-indigo-400 font-bold hover:text-indigo-300 flex items-center gap-2">Explore Agents <ArrowRight className="w-4 h-4"/></Link>
          </div>
          <div className="flex-1 w-full glass-card rounded-2xl p-6 border-white/10">
            <div className="space-y-4">
              <div className="bg-white/5 p-4 rounded-lg text-sm border border-white/5 font-mono text-white/70">Agent: Analyze Q3 earnings of [Acme Corp]</div>
              <div className="bg-white/5 p-4 rounded-lg text-sm border border-white/5 font-mono text-white/70">Action: Extracting sentiment...</div>
              <div className="bg-indigo-500/20 p-4 rounded-lg text-sm border border-indigo-500/30 font-mono text-indigo-300">Result: High Churn Risk detected. Initiating Defense Workflow.</div>
            </div>
          </div>
        </div>
      </section>

      {/* 14. ENTERPRISE SECURITY */}
      <section className="w-full py-32 border-t border-white/5 relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-b from-blue-900/10 to-transparent pointer-events-none"></div>
        <div className="max-w-7xl mx-auto px-6 text-center">
          <Shield className="w-16 h-16 text-blue-400 mx-auto mb-8" />
          <h2 className="text-4xl md:text-5xl font-bold mb-6">Uncompromising Enterprise Security</h2>
          <p className="text-xl text-white/50 max-w-2xl mx-auto mb-16">Built for FinServ and Healthcare. Absolute workspace isolation, SOC2 Type II compliance, and strict GDPR right-to-erasure enforcement.</p>
          
          <div className="flex flex-wrap justify-center gap-6">
            {['SOC2 Type II', 'GDPR Compliant', 'ISO27001', 'RBAC', 'KMS Encryption', 'Audit Logs'].map((cert) => (
              <div key={cert} className="glass-card px-6 py-3 rounded-full text-sm font-bold tracking-wide border-white/20">
                {cert}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 20 & 21. PLATFORM EVOLUTION & FUTURE VISION */}
      <section className="w-full py-32 bg-[#020202] border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">The Future Vision</h2>
            <p className="text-xl text-white/50 max-w-3xl mx-auto">From a Predictive Revenue Platform to a Global Enterprise Digital Twin.</p>
          </div>

          <div className="glass-card p-12 rounded-3xl border-white/10 text-center relative overflow-hidden">
            <Globe className="w-20 h-20 text-white/10 absolute -top-4 -right-4" />
            <h3 className="text-2xl font-bold mb-4 text-white">Revenue Operating System 2.0</h3>
            <p className="text-white/60 max-w-2xl mx-auto mb-8">
              The next decade belongs to Autonomous Revenue Teams, Federated Learning across enterprises, and Industry-specific Foundation Models operating on a global Knowledge Graph.
            </p>
            <Link href="/roadmap" className="px-6 py-3 bg-white text-black font-bold rounded-lg hover:bg-white/90 transition shadow-lg">Read the Master Roadmap</Link>
          </div>
        </div>
      </section>

      {/* 23. FINAL CTA */}
      <section className="w-full py-32 bg-gradient-to-b from-[#050505] to-[#0a0a1a] text-center px-6">
        <h2 className="text-5xl md:text-7xl font-black mb-8 tracking-tighter">The Future of Revenue Intelligence <br/>Starts Here.</h2>
        <div className="flex justify-center gap-4">
          <Link href="/contact" className="px-8 py-4 rounded-xl bg-white text-black font-bold text-lg hover:bg-white/90 transition shadow-[0_0_30px_rgba(255,255,255,0.2)]">Book Enterprise Demo</Link>
          <Link href="/docs" className="px-8 py-4 rounded-xl glass-card text-white font-bold text-lg hover:bg-white/5 transition border-white/20">Developer Docs</Link>
        </div>
      </section>

    </div>
  )
}
