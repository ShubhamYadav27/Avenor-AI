"use client";

import { Building2, Sparkles, Server, Search } from "lucide-react";
import { TopBar } from "@/components/layout/top-bar";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useState } from "react";

export default function IntelligenceCenterPage() {
  const [loading, setLoading] = useState(false);

  return (
    <div className="flex flex-1 flex-col w-full min-h-0 bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
      <TopBar
        title="Enterprise Intelligence Cloud"
        subtitle="Proprietary AI intelligence spanning Companies, Contacts, and Markets."
        action={
          <button className="flex items-center gap-1.5 rounded-xl border border-indigo-200/80 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-900/20 px-3.5 py-1.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-all shadow-2xs cursor-pointer">
            <Sparkles className="h-3 w-3" />
            Discover Intelligence
          </button>
        }
      />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-6xl space-y-8">
          
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search companies, executives, or technologies..." 
              className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-3 pl-10 pr-4 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <section className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-indigo-500/10 p-2 text-indigo-600 dark:text-indigo-400">
                  <Building2 className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Company Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Deep AI analysis of synced CRM accounts</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Mock Company Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                        <Building2 className="h-4 w-4" />
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                        High Buying Intent
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Company Domain</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">acmecorp.com</p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-indigo-600 dark:text-indigo-400">AI Summary:</strong> Acme Corp exhibits strong hiring signals and recently secured funding. Ideal target for expansion.
                    </p>
                  </div>
                </div>

                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover border-dashed">
                  <EmptyState 
                    icon={Server} 
                    title="Connect Data Sources" 
                    description="Sync more CRM accounts to generate automated Company Intelligence profiles." 
                  />
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-emerald-500/10 p-2 text-emerald-600 dark:text-emerald-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Contact Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Profile, Seniority, and Purchasing Influence Analysis</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Mock Contact Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border-indigo-500/20">
                        High Influence
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Contact Email</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">jane.doe@acmecorp.com</p>
                    <p className="text-xs text-slate-500 mt-1">VP of Engineering • Engineering Dept</p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-emerald-600 dark:text-emerald-400">AI Summary:</strong> Contact holds a VP role. Projected to have strong purchasing influence. High engagement sentiment.
                    </p>
                  </div>
                </div>

                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover border-dashed">
                  <EmptyState 
                    icon={Sparkles} 
                    title="Enrich More Contacts" 
                    description="Sync email integrations to resolve more contact identities automatically." 
                  />
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-blue-500/10 p-2 text-blue-600 dark:text-blue-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Technology Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Deep AI analysis of tech stacks, infrastructure, and tools</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Technology Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-blue-500/10 text-blue-400 border-blue-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-blue-500/10 text-blue-400 border-blue-500/20">
                        High Fit Score: 85%
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Company Domain</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">acmecorp.com</p>
                    
                    <div className="flex flex-wrap gap-2 mt-4">
                      <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md text-xs font-medium text-slate-600 dark:text-slate-300">AWS</span>
                      <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md text-xs font-medium text-slate-600 dark:text-slate-300">Salesforce</span>
                      <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md text-xs font-medium text-slate-600 dark:text-slate-300">React</span>
                      <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md text-xs font-medium text-slate-600 dark:text-slate-300">Python</span>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-blue-600 dark:text-blue-400">AI Summary:</strong> Modern tech stack with strong cloud infrastructure and CRM adoption. Likely expanding data analytics capabilities. Opportunity to pitch Revenue OS. Low vendor lock-in risk.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-orange-500/10 p-2 text-orange-600 dark:text-orange-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Buying Committee Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Identify decision makers, champions, blockers, and missing stakeholders</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Mock Buying Committee Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-orange-500/10 text-orange-400 border-orange-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-amber-500/10 text-amber-500 border-amber-500/20">
                        Medium Risk: Missing Economic Buyer
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">acmecorp.com Committee</p>
                    
                    <div className="mt-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-xs font-bold text-indigo-700 dark:text-indigo-300">JD</div>
                          <div>
                            <p className="text-sm font-medium text-slate-900 dark:text-white leading-tight">Jane Doe</p>
                            <p className="text-[10px] text-slate-500">VP Eng • <span className="text-emerald-500 font-semibold">Champion</span></p>
                          </div>
                        </div>
                        <span className="text-xs font-medium text-slate-500">Influence: High</span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-rose-100 dark:bg-rose-900 flex items-center justify-center text-xs font-bold text-rose-700 dark:text-rose-300">BS</div>
                          <div>
                            <p className="text-sm font-medium text-slate-900 dark:text-white leading-tight">Bob Smith</p>
                            <p className="text-[10px] text-slate-500">Legal • <span className="text-rose-500 font-semibold">Blocker</span></p>
                          </div>
                        </div>
                        <span className="text-xs font-medium text-slate-500">Influence: Med</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-orange-600 dark:text-orange-400">AI Recommendation:</strong> Multi-threading score is low. You are missing the Economic Buyer. Engage Jane Doe to get an introduction to the CFO.
                    </p>
                  </div>
                </div>

                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover border-dashed">
                  <EmptyState 
                    icon={Sparkles} 
                    title="Map the Org Chart" 
                    description="Automatically reconstruct reporting relationships from CRM activity." 
                  />
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-green-500/10 p-2 text-green-600 dark:text-green-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Funding Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Analyze investment rounds, growth signals, and buying windows</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Funding Intelligence Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-green-500/10 text-green-400 border-green-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-green-500/10 text-green-500 border-green-500/20">
                        High Buying Window
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Company Domain</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">acmecorp.com</p>
                    
                    <div className="mt-4 flex flex-col sm:flex-row gap-6">
                      <div className="flex-1">
                        <p className="text-xs font-medium text-slate-500">Latest Round</p>
                        <p className="text-lg font-bold text-slate-900 dark:text-white">Series B ($45M)</p>
                        <p className="text-xs text-slate-500">Announced: 2 months ago</p>
                      </div>
                      <div className="flex-1 border-l border-slate-200 dark:border-slate-800 pl-6">
                        <p className="text-xs font-medium text-slate-500">Growth Probability</p>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-green-500 w-[90%] rounded-full"></div>
                          </div>
                          <span className="text-xs font-bold text-slate-700 dark:text-slate-300">90% Hiring</span>
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-500 w-[85%] rounded-full"></div>
                          </div>
                          <span className="text-xs font-bold text-slate-700 dark:text-slate-300">85% Tech</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-green-600 dark:text-green-400">AI Summary:</strong> Company recently secured Series B funding. High probability of technology and headcount expansion in the next 6 months. Strong imminent budget expansion.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-fuchsia-500/10 p-2 text-fuchsia-600 dark:text-fuchsia-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Hiring Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Track organizational growth, velocity, and department-specific expansion signals</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Hiring Intelligence Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <div className="flex gap-2">
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-fuchsia-500/10 text-fuchsia-500 border-fuchsia-500/20">
                          Accelerating Velocity
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-green-500/10 text-green-500 border-green-500/20">
                          High Buying Window
                        </span>
                      </div>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Company Domain</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">acmecorp.com</p>
                    
                    <div className="mt-4 flex flex-col sm:flex-row gap-6">
                      <div className="flex-1">
                        <p className="text-xs font-medium text-slate-500">Open Roles</p>
                        <p className="text-2xl font-black text-slate-900 dark:text-white tracking-tighter">42</p>
                        <p className="text-[10px] font-medium text-green-500">+12% vs last month</p>
                      </div>
                      <div className="flex-[2] border-l border-slate-200 dark:border-slate-800 pl-6 grid grid-cols-2 gap-2">
                        <div>
                          <p className="text-[10px] font-medium text-slate-500">Engineering</p>
                          <p className="text-sm font-bold text-slate-700 dark:text-slate-300">18 roles</p>
                        </div>
                        <div>
                          <p className="text-[10px] font-medium text-slate-500">Sales</p>
                          <p className="text-sm font-bold text-slate-700 dark:text-slate-300">12 roles</p>
                        </div>
                        <div>
                          <p className="text-[10px] font-medium text-slate-500">Marketing</p>
                          <p className="text-sm font-bold text-slate-700 dark:text-slate-300">5 roles</p>
                        </div>
                        <div>
                          <p className="text-[10px] font-medium text-slate-500">AI/ML</p>
                          <p className="text-sm font-bold text-indigo-500">7 roles (Surge)</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-fuchsia-600 dark:text-fuchsia-400">AI Summary:</strong> Detected 42 open roles. Hiring velocity is accelerating. Strong technical scale-up (AI/ML) combined with aggressive GTM expansion (Sales). Excellent time to engage.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-yellow-500/10 p-2 text-yellow-600 dark:text-yellow-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Executive Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Map leadership teams, influence scores, and strategic priorities</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Executive Intelligence Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-yellow-500/10 text-yellow-500 border-yellow-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <div className="flex gap-2">
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-yellow-500/10 text-yellow-600 dark:text-yellow-500 border-yellow-500/20">
                          Moderate Risk: Leadership Change
                        </span>
                      </div>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Executive Team Profile</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">acmecorp.com</p>
                    
                    <div className="mt-4 flex flex-col sm:flex-row gap-6">
                      <div className="flex-[1.5]">
                        <p className="text-xs font-medium text-slate-500 mb-2">Key Executives</p>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-700 dark:text-slate-300">AS</div>
                              <div>
                                <p className="text-xs font-bold text-slate-900 dark:text-white leading-tight">Alice Smith</p>
                                <p className="text-[9px] text-slate-500">CEO • High Authority</p>
                              </div>
                            </div>
                            <span className="text-[10px] font-medium text-slate-500">Influence: 95%</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-[10px] font-bold text-blue-700 dark:text-blue-300">TJ</div>
                              <div>
                                <p className="text-xs font-bold text-slate-900 dark:text-white leading-tight">Tom Jones <span className="text-yellow-500 ml-1">(New)</span></p>
                                <p className="text-[9px] text-slate-500">CFO • High Authority</p>
                              </div>
                            </div>
                            <span className="text-[10px] font-medium text-slate-500">Influence: 85%</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex-[1] border-l border-slate-200 dark:border-slate-800 pl-6">
                        <p className="text-xs font-medium text-slate-500 mb-2">Top Strategic Priorities</p>
                        <div className="flex flex-wrap gap-2">
                          <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md text-[10px] font-medium text-slate-600 dark:text-slate-300">Cost Optimization</span>
                          <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md text-[10px] font-medium text-slate-600 dark:text-slate-300">AI Transformation</span>
                          <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-md text-[10px] font-medium text-slate-600 dark:text-slate-300">Margin Expansion</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-yellow-600 dark:text-yellow-500">AI Engagement Strategy:</strong> New CFO appointed 2 months ago. Priority is Cost Optimization and Margin Expansion. Pitch Revenue OS as a consolidation play to reduce redundant SaaS spend.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-rose-500/10 p-2 text-rose-600 dark:text-rose-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Competitive Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Analyze market position, feature gaps, and displacement opportunities</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Competitive Intelligence Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-rose-500/10 text-rose-500 border-rose-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <div className="flex gap-2">
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-rose-500/10 text-rose-600 dark:text-rose-500 border-rose-500/20">
                          High Competitive Risk
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-green-500/10 text-green-500 border-green-500/20">
                          Displacement Opportunity
                        </span>
                      </div>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Competitive Landscape</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">acmecorp.com</p>
                    
                    <div className="mt-4 flex flex-col sm:flex-row gap-6">
                      <div className="flex-1">
                        <p className="text-xs font-medium text-slate-500 mb-2">Incumbents</p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-700 dark:text-slate-300">LegacyCRM Inc.</span>
                            <span className="text-[9px] font-medium text-rose-500 bg-rose-500/10 px-1.5 py-0.5 rounded-full border border-rose-500/20">Leader</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-700 dark:text-slate-300">SalesForceTracker</span>
                            <span className="text-[9px] font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded-full border border-slate-200 dark:border-slate-700">Challenger</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex-[2] border-l border-slate-200 dark:border-slate-800 pl-6">
                        <p className="text-xs font-medium text-slate-500 mb-2">Feature Gaps & Displacements</p>
                        <ul className="list-disc list-inside space-y-1">
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Displace LegacyCRM:</strong> Highlight lower TCO and faster time-to-value.</li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Gap:</strong> LegacyCRM lacks advanced AI orchestration capabilities.</li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Block SalesForceTracker:</strong> Emphasize enterprise scale and deep security controls.</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-rose-600 dark:text-rose-400">AI Recommended Positioning:</strong> Position Avenor as the next-generation AI-native alternative to legacy platforms. Lead with the Knowledge Graph. Highly competitive red ocean market requires strong technical differentiation.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-emerald-500/10 p-2 text-emerald-600 dark:text-emerald-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Market Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Monitor macro trends, industry demand, and buying patterns</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Market Intelligence Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-emerald-500/10 text-emerald-500 border-emerald-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <div className="flex gap-2">
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-500 border-emerald-500/20">
                          Bullish Sentiment
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-indigo-500/10 text-indigo-500 border-indigo-500/20">
                          High Opportunity
                        </span>
                      </div>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Industry: Software & SaaS</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">Enterprise B2B</p>
                    
                    <div className="mt-4 flex flex-col sm:flex-row gap-6">
                      <div className="flex-1">
                        <p className="text-xs font-medium text-slate-500 mb-2">Macro Trends</p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-700 dark:text-slate-300">AI Tool Consolidation</span>
                            <span className="text-[9px] font-medium text-emerald-500 bg-emerald-500/10 px-1.5 py-0.5 rounded-full border border-emerald-500/20">Positive</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-slate-700 dark:text-slate-300">SaaS Budget Contraction</span>
                            <span className="text-[9px] font-medium text-rose-500 bg-rose-500/10 px-1.5 py-0.5 rounded-full border border-rose-500/20">Negative</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex-[2] border-l border-slate-200 dark:border-slate-800 pl-6">
                        <p className="text-xs font-medium text-slate-500 mb-2">Signals & Buying Patterns</p>
                        <ul className="list-disc list-inside space-y-1">
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Expansion Opportunity:</strong> Upsell existing accounts facing budget cuts by offering consolidated tooling.</li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Seasonal Pattern:</strong> Approaching Q4 budget flush period.</li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Regulatory Shift:</strong> New EU AI Act compliance creating demand for audit features.</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-emerald-600 dark:text-emerald-400">AI Strategic Recommendation:</strong> Aggressively target the Software sector. Strong macro tailwinds for consolidation plays. Position Avenor as a unified Revenue OS to replace fragmented tech stacks ahead of the Q4 buying season.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-600 dark:text-cyan-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Industry Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Analyze vertical-specific maturity, KPIs, and technology adoption</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Industry Intelligence Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-cyan-500/10 text-cyan-500 border-cyan-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <div className="flex gap-2">
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-cyan-500/10 text-cyan-600 dark:text-cyan-500 border-cyan-500/20">
                          High Readiness (85%)
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-blue-500/10 text-blue-500 border-blue-500/20">
                          Mature Lifecycle
                        </span>
                      </div>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Target Vertical</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">Financial Technology (FinTech)</p>
                    
                    <div className="mt-4 flex flex-col sm:flex-row gap-6">
                      <div className="flex-1">
                        <p className="text-xs font-medium text-slate-500 mb-2">Industry Benchmarks</p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Avg. Sales Cycle</span>
                            <span className="text-[10px] font-bold text-slate-800 dark:text-slate-200">120 Days</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Tech Adoption</span>
                            <span className="text-[10px] font-bold text-cyan-500">High (90%)</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Regulatory Risk</span>
                            <span className="text-[10px] font-bold text-rose-500">High</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex-[2] border-l border-slate-200 dark:border-slate-800 pl-6">
                        <p className="text-xs font-medium text-slate-500 mb-2">Buying Patterns & Engagement Strategy</p>
                        <ul className="list-disc list-inside space-y-1">
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Consensus-Based:</strong> Requires high technical evaluation and deep security reviews.</li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Best Practice:</strong> Lead with technical differentiation and compliance-ready architecture.</li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Multi-Threading:</strong> Must involve Engineering, Security (CISO), and RevOps.</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-cyan-600 dark:text-cyan-400">AI Strategic Recommendation:</strong> High readiness in FinTech. Allocate Tier 1 GTM resources. Pitch digital transformation and workflow consolidation, ensuring SOC2/compliance messaging is front and center.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-orange-500/10 p-2 text-orange-600 dark:text-orange-400">
                  <Activity className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Global Signal Intelligence Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Unified signal fusion, correlation, and buying window detection</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Signal Intelligence Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-orange-500/10 text-orange-500 border-orange-500/20">
                        <Activity className="h-4 w-4" />
                      </span>
                      <div className="flex gap-2">
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-orange-500/10 text-orange-600 dark:text-orange-500 border-orange-500/20">
                          Tier 1 Priority
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-green-500/10 text-green-500 border-green-500/20">
                          Active Buying Window
                        </span>
                      </div>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Signal Fusion Timeline</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">acmecorp.com</p>
                    
                    <div className="mt-4 flex flex-col sm:flex-row gap-6">
                      <div className="flex-1">
                        <p className="text-xs font-medium text-slate-500 mb-2">Signal Heatmap & Scores</p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Buying Intent</span>
                            <span className="text-[10px] font-bold text-orange-500">High (92%)</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Growth Indicators</span>
                            <span className="text-[10px] font-bold text-green-500">Strong (85%)</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Risk Indicators</span>
                            <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400">Low (12%)</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex-[2] border-l border-slate-200 dark:border-slate-800 pl-6">
                        <p className="text-xs font-medium text-slate-500 mb-2">Correlated Events & AI Explanations</p>
                        <ul className="list-disc list-inside space-y-1">
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Event:</strong> High-intent Expansion Window</li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Insight:</strong> Company is showing direct buying intent alongside growth markers.</li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300"><strong className="text-slate-800 dark:text-slate-200">Confidence:</strong> 95% based on 12 active signals across CRM and public web.</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-orange-600 dark:text-orange-400">AI Signal Summary:</strong> High priority account. 12 active signals detected pointing to immediate buying window. Growth indicators corroborate budget availability. Initiate immediate outreach to Economic Buyer.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-pink-500/10 p-2 text-pink-600 dark:text-pink-400">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">Identity Resolution Engine</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Canonical identity management, entity deduplication, and AI merge suggestions</p>
                </div>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Skeleton className="h-48 rounded-2xl glass-card" />
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                
                {/* Mock Identity Resolution Card using glass-card token */}
                <div className="flex flex-col justify-between p-5 glass-card glass-card-hover">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="p-2 rounded-xl border bg-pink-500/10 text-pink-500 border-pink-500/20">
                        <Server className="h-4 w-4" />
                      </span>
                      <div className="flex gap-2">
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-pink-500/10 text-pink-600 dark:text-pink-500 border-pink-500/20">
                          3 Pending Merges
                        </span>
                        <span className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold bg-blue-500/10 text-blue-500 border-blue-500/20">
                          Company Entity
                        </span>
                      </div>
                    </div>
                    <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Conflict Resolution Queue</p>
                    <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight">Acme Corporation</p>
                    
                    <div className="mt-4 flex flex-col sm:flex-row gap-6">
                      <div className="flex-1">
                        <p className="text-xs font-medium text-slate-500 mb-2">Canonical Target</p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Primary Domain</span>
                            <span className="text-[10px] font-bold text-slate-800 dark:text-slate-200">acmecorp.com</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Resolution Status</span>
                            <span className="text-[10px] font-bold text-emerald-500">Verified</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Subsidiaries</span>
                            <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400">2 Linked</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex-[2] border-l border-slate-200 dark:border-slate-800 pl-6">
                        <p className="text-xs font-medium text-slate-500 mb-2">AI Merge Suggestions & Duplicate Candidates</p>
                        <ul className="list-disc list-inside space-y-1">
                          <li className="text-[10px] text-slate-600 dark:text-slate-300">
                            <strong className="text-slate-800 dark:text-slate-200">Merge Candidate:</strong> "Acme Corp" (ID: 111...111) 
                            <span className="ml-1 text-emerald-500 font-bold">[95% Match]</span>
                          </li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300">
                            <strong className="text-slate-800 dark:text-slate-200">Merge Candidate:</strong> "Acme Inc." (ID: 222...222) 
                            <span className="ml-1 text-emerald-500 font-bold">[88% Match]</span>
                          </li>
                          <li className="text-[10px] text-slate-600 dark:text-slate-300">
                            <strong className="text-slate-800 dark:text-slate-200">Alias Detected:</strong> Sub-addressing "john+sales@acme.com" mapped to Canonical Contact.
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60">
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      <strong className="text-pink-600 dark:text-pink-400">AI Generated Explanation:</strong> High confidence canonical match for "Acme Corp" and "Acme Inc." based on domain overlap and standardized legal suffixes. Recommend auto-merge to preserve signal timeline integrity.
                    </p>
                  </div>
                </div>

              </div>
            )}
          </section>

        </div>
      </div>
    </div>
  );
}
