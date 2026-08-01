"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft, ExternalLink, Users, MapPin, Building2,
  MessageSquarePlus, TrendingUp, Calendar, Sparkles, DollarSign, Contact, Mail, CheckCircle, Clock, XCircle
} from "lucide-react";
import { useCompanyDetail } from "@/hooks/use-api";
import { BuyingWindowBadge } from "@/components/ui/buying-window-badge";
import { ScoreRing } from "@/components/ui/score-ring";
import { OutcomeModal } from "@/components/outcomes/outcome-modal";
import { ResearchPanel } from "@/components/research/research-panel";
import { EmailGeneratorPanel } from "@/components/emails/email-generator-panel";
import { SalesBriefingPanel } from "@/components/briefings/sales-briefing-panel";
import { SalesCoachPanel } from "@/components/coaching/sales-coach-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import {
  formatCurrency, timeAgo,
  SIGNAL_TYPE_LABELS, WINDOW_CONFIG,
} from "@/lib/utils";

type TabType = "overview" | "contacts" | "deals" | "insights" | "activity";

export default function CompanyDetailPage() {
  const { companyId } = useParams<{ companyId: string }>();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [showOutcome, setShowOutcome] = useState(false);
  const { data, isLoading, isError } = useCompanyDetail(companyId);

  if (isLoading) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
        <div className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/90 px-6 py-4">
          <Skeleton className="h-5 w-48" />
        </div>
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-48 rounded-2xl" />
          <Skeleton className="h-64 rounded-2xl" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-1 items-center justify-center bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
        <EmptyState
          icon={Building2}
          title="Company not found"
          description="This company may not be in your workspace."
          action={
            <button
              onClick={() => router.back()}
              className="mt-2 text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300"
            >
              Go back
            </button>
          }
        />
      </div>
    );
  }

  const { company, intelligence, signals, contacts, opportunities = [] } = data;
  const winCfg = WINDOW_CONFIG[company.buying_window] ?? WINDOW_CONFIG.cold;

  return (
    <div className="flex flex-1 flex-col w-full min-h-0 bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
      {/* Top bar */}
      <div className="sticky top-0 z-30 shrink-0 flex h-16 items-center gap-3 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-6 shadow-xs">
        <button
          onClick={() => router.back()}
          className="rounded-xl p-1.5 text-slate-400 dark:text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-700 dark:hover:text-slate-300 transition-colors cursor-pointer"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="truncate text-sm font-bold text-slate-900 dark:text-white">{company.name}</h1>
        </div>
        <button
          onClick={() => setShowOutcome(true)}
          className="flex items-center gap-1.5 rounded-xl bg-indigo-600 dark:bg-indigo-500 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors shadow-2xs cursor-pointer"
        >
          <MessageSquarePlus className="h-3.5 w-3.5" />
          Log Outcome
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-4xl space-y-5">
          {/* Header Profile Card */}
          <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs">
            <div className="flex items-start gap-5">
              <ScoreRing score={company.composite_score} size={64} className="flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <h2 className="text-xl font-black text-slate-900 dark:text-white">{company.name}</h2>
                  <BuyingWindowBadge window={company.buying_window} />
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500 dark:text-slate-400 font-medium">
                  {company.industry && (
                    <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5 text-slate-400 dark:text-slate-500" />{company.industry}</span>
                  )}
                  {company.employee_count && (
                    <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5 text-slate-400 dark:text-slate-500" />{company.employee_count} employees</span>
                  )}
                  {company.location && (
                    <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5 text-slate-400 dark:text-slate-500" />{company.location}</span>
                  )}
                  {company.funding_stage && (
                    <span className="flex items-center gap-1">
                      <TrendingUp className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                      {company.funding_stage}
                      {company.funding_total_usd ? ` · ${formatCurrency(company.funding_total_usd)} raised` : ""}
                    </span>
                  )}
                </div>
                {company.description && (
                  <p className="mt-2.5 text-xs text-slate-600 dark:text-slate-300 leading-relaxed line-clamp-2">
                    {company.description}
                  </p>
                )}
                <div className="mt-3.5 flex gap-4">
                  {company.website && (
                    <a href={company.website} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">
                      <ExternalLink className="h-3 w-3" />Website
                    </a>
                  )}
                  {company.linkedin_url && (
                    <a href={company.linkedin_url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">
                      <ExternalLink className="h-3 w-3" />LinkedIn Profile
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Interconnected Tabs Navigation */}
            <div className="mt-6 border-b border-slate-200 dark:border-slate-800 flex gap-2">
              {[
                { id: "overview", label: "Overview", icon: Building2 },
                { id: "contacts", label: `Contacts (${contacts.length})`, icon: Contact },
                { id: "deals", label: `Deals (${opportunities.length})`, icon: DollarSign },
                { id: "insights", label: "AI Insights & Copilot", icon: Sparkles },
                { id: "activity", label: `Activity (${signals.length})`, icon: Calendar },
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id as TabType)}
                  className={`flex items-center gap-1.5 py-2.5 px-3 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                    activeTab === id
                      ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400"
                      : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-5">
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: "Composite Score", value: `${Math.round(company.composite_score * 100)}%`, highlight: true },
                  { label: "ICP Fit Score", value: `${Math.round(company.icp_score * 100)}%`, highlight: false },
                  { label: "Buying Signal Score", value: `${Math.round((company.signal_score ?? 0) * 100)}%`, highlight: false },
                ].map(({ label, value, highlight }) => (
                  <div key={label} className={`rounded-xl border p-3.5 text-center ${highlight ? `${winCfg.bg} border-current` : "border-slate-100 dark:border-slate-800/60 bg-slate-50 dark:bg-slate-800/50"}`}>
                    <p className={`text-2xl font-black ${highlight ? winCfg.color : "text-slate-900 dark:text-white"}`}>{value}</p>
                    <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-0.5">{label}</p>
                  </div>
                ))}
              </div>

              {company.technologies && company.technologies.length > 0 && (
                <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs">
                  <h3 className="mb-3 text-sm font-bold text-slate-900 dark:text-white">Tech Stack Fingerprint</h3>
                  <div className="flex flex-wrap gap-2">
                    {company.technologies.map((t) => (
                      <span key={t} className="rounded-xl bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800/60 px-3 py-1 text-xs font-semibold text-slate-700 dark:text-slate-300">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: CONTACTS */}
          {activeTab === "contacts" && (
            <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 space-y-4 shadow-xs">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Users className="h-4 w-4 text-slate-400" /> Synced Decision Makers ({contacts.length})
                </h3>
                <Link href="/dashboard/crm/contacts" className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">
                  View All CRM Contacts →
                </Link>
              </div>

              {contacts.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No contacts synced for this company yet.</p>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {contacts.map((c) => (
                    <div key={c.id} className="flex items-center justify-between py-3.5">
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-bold text-slate-900 dark:text-white">{c.name ?? "Unknown"}</p>
                          {c.is_primary && (
                            <span className="rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 px-2 py-0.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400">Primary</span>
                          )}
                        </div>
                        {c.title && <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{c.title}</p>}
                      </div>
                      <div className="flex items-center gap-3">
                        {c.email && (
                          <a href={`mailto:${c.email}`} className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">
                            {c.email}
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: DEALS */}
          {activeTab === "deals" && (
            <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 space-y-4 shadow-xs">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-emerald-500" /> Synced Salesforce Opportunities ({opportunities.length})
                </h3>
                <Link href="/dashboard/crm/deals" className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
                  View All CRM Deals →
                </Link>
              </div>

              {opportunities.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No opportunities linked to this account in Salesforce.</p>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {opportunities.map((o) => (
                    <div key={o.id} className="flex items-center justify-between py-3.5">
                      <div>
                        <p className="text-sm font-bold text-slate-900 dark:text-white">{o.name}</p>
                        <p className="text-xs text-slate-500">Stage: {o.stage || "In Progress"}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                          {o.amount_usd ? `$${o.amount_usd.toLocaleString()}` : "—"}
                        </p>
                        <p className="text-[10px] text-slate-400">Close: {o.close_date ? new Date(o.close_date).toLocaleDateString() : "N/A"}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: AI INSIGHTS */}
          {activeTab === "insights" && (
            <div className="space-y-5">
              {(intelligence.signal_summary || intelligence.recommended_angle) && (
                <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 space-y-4 shadow-xs">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> AI Intelligence Synthesis
                  </h3>
                  {intelligence.signal_summary && (
                    <div>
                      <p className="text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Why Now Catalyst</p>
                      <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed">{intelligence.signal_summary}</p>
                    </div>
                  )}
                  {intelligence.recommended_angle && (
                    <div className="border-l-2 border-indigo-600 dark:border-indigo-500 pl-3.5 py-0.5">
                      <p className="text-xs font-bold text-indigo-700 dark:text-indigo-400 mb-1">Recommended Approach</p>
                      <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed">{intelligence.recommended_angle}</p>
                    </div>
                  )}
                </div>
              )}

              <ResearchPanel companyId={company.id} />
              <EmailGeneratorPanel companyId={company.id} contacts={contacts} />
              <SalesBriefingPanel companyId={company.id} />
              <SalesCoachPanel companyId={company.id} />
            </div>
          )}

          {/* TAB 5: ACTIVITY */}
          {activeTab === "activity" && (
            <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs">
              <h3 className="mb-4 text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Calendar className="h-4 w-4 text-slate-400 dark:text-slate-500" /> Market Signal Timeline ({signals.length})
              </h3>

              {signals.length === 0 ? (
                <p className="text-sm text-slate-400 dark:text-slate-500">No signals detected yet.</p>
              ) : (
                <div className="relative">
                  <div className="absolute left-2 top-2 bottom-2 w-px bg-slate-200 dark:bg-slate-800" />
                  <div className="space-y-4">
                    {signals.map((sig) => (
                      <div key={sig.id} className="flex gap-4">
                        <div className="relative z-10 mt-1 flex-shrink-0">
                          <div className="h-4 w-4 rounded-full bg-indigo-600 dark:bg-indigo-500 flex items-center justify-center">
                            <div className="h-1.5 w-1.5 rounded-full bg-white dark:bg-slate-900" />
                          </div>
                        </div>
                        <div className="min-w-0 flex-1 pb-2">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="rounded-full bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800/80 px-2.5 py-0.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
                              {SIGNAL_TYPE_LABELS[sig.type] ?? sig.type}
                            </span>
                            <span className="text-xs font-medium text-slate-400 dark:text-slate-500">{timeAgo(sig.detected_at)}</span>
                          </div>
                          <p className="mt-1 text-sm font-bold text-slate-900 dark:text-white">{sig.title}</p>
                          {sig.description && (
                            <p className="mt-0.5 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{sig.description}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {showOutcome && (
        <OutcomeModal
          companyId={company.id}
          companyName={company.name}
          onClose={() => setShowOutcome(false)}
        />
      )}
    </div>
  );
}
