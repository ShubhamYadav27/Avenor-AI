"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft, ExternalLink, Users, MapPin, Building2,
  Zap, MessageSquarePlus, TrendingUp, Calendar,
} from "lucide-react";
import { useCompanyDetail } from "@/hooks/use-api";
import { BuyingWindowBadge } from "@/components/ui/buying-window-badge";
import { ScoreRing } from "@/components/ui/score-ring";
import { OutcomeModal } from "@/components/outcomes/outcome-modal";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import {
  formatCurrency, timeAgo,
  SIGNAL_TYPE_LABELS, WINDOW_CONFIG,
} from "@/lib/utils";

export default function CompanyDetailPage() {
  const { companyId } = useParams<{ companyId: string }>();
  const router = useRouter();
  const [showOutcome, setShowOutcome] = useState(false);
  const { data, isLoading, isError } = useCompanyDetail(companyId);

  if (isLoading) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden">
        <div className="border-b border-slate-200 bg-white px-6 py-4">
          <Skeleton className="h-5 w-48" />
        </div>
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <Skeleton className="h-32 rounded-xl" />
          <Skeleton className="h-48 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <EmptyState
          icon={Building2}
          title="Company not found"
          description="This company may not be in your workspace."
          action={
            <button
              onClick={() => router.back()}
              className="mt-2 text-sm text-violet-600 hover:text-violet-700"
            >
              Go back
            </button>
          }
        />
      </div>
    );
  }

  const { company, intelligence, signals, contacts } = data;
  const winCfg = WINDOW_CONFIG[company.buying_window] ?? WINDOW_CONFIG.cold;

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Top bar */}
      <div className="flex h-14 items-center gap-3 border-b border-slate-200 bg-white px-6">
        <button
          onClick={() => router.back()}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
        >
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="truncate text-sm font-semibold text-slate-900">{company.name}</h1>
        </div>
        <button
          onClick={() => setShowOutcome(true)}
          className="flex items-center gap-1.5 rounded-lg bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-violet-700 transition-colors"
        >
          <MessageSquarePlus className="h-3.5 w-3.5" />
          Log outcome
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-3xl space-y-4">

          {/* Company profile card */}
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <div className="flex items-start gap-4">
              <ScoreRing score={company.composite_score} size={64} className="flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <h2 className="text-lg font-bold text-slate-900">{company.name}</h2>
                  <BuyingWindowBadge window={company.buying_window} />
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
                  {company.industry && (
                    <span className="flex items-center gap-1"><Building2 className="h-3 w-3" />{company.industry}</span>
                  )}
                  {company.employee_count && (
                    <span className="flex items-center gap-1"><Users className="h-3 w-3" />{company.employee_count} employees</span>
                  )}
                  {company.location && (
                    <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{company.location}</span>
                  )}
                  {company.funding_stage && (
                    <span className="flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" />
                      {company.funding_stage}
                      {company.funding_total_usd ? ` · ${formatCurrency(company.funding_total_usd)} raised` : ""}
                    </span>
                  )}
                </div>
                {company.description && (
                  <p className="mt-2 text-xs text-slate-600 leading-relaxed line-clamp-2">
                    {company.description}
                  </p>
                )}
                <div className="mt-3 flex gap-3">
                  {company.website && (
                    <a href={company.website} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs text-violet-600 hover:underline">
                      <ExternalLink className="h-3 w-3" />Website
                    </a>
                  )}
                  {company.linkedin_url && (
                    <a href={company.linkedin_url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-1 text-xs text-violet-600 hover:underline">
                      <ExternalLink className="h-3 w-3" />LinkedIn
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Score breakdown */}
            <div className="mt-4 grid grid-cols-3 gap-3">
              {[
                { label: "Composite score", value: `${Math.round(company.composite_score * 100)}%`, highlight: true },
                { label: "ICP match", value: `${Math.round(company.icp_score * 100)}%`, highlight: false },
                { label: "Signal score", value: `${Math.round((company.signal_score ?? 0) * 100)}%`, highlight: false },
              ].map(({ label, value, highlight }) => (
                <div key={label} className={`rounded-lg border p-3 text-center ${highlight ? `${winCfg.bg} border-current` : "border-slate-100 bg-slate-50"}`}>
                  <p className={`text-xl font-bold ${highlight ? winCfg.color : "text-slate-800"}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* AI Intelligence */}
          {(intelligence.signal_summary || intelligence.recommended_angle) && (
            <div className="rounded-xl border border-slate-200 bg-white p-5 space-y-4">
              <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
                <Zap className="h-4 w-4 text-violet-500" /> AI Intelligence
              </h3>
              {intelligence.signal_summary && (
                <div>
                  <p className="text-xs font-medium text-slate-500 mb-1">Why now</p>
                  <p className="text-sm text-slate-700 leading-relaxed">{intelligence.signal_summary}</p>
                </div>
              )}
              {intelligence.buying_window_reasoning && (
                <div>
                  <p className="text-xs font-medium text-slate-500 mb-1">Buying window reasoning</p>
                  <p className="text-sm text-slate-600 leading-relaxed">{intelligence.buying_window_reasoning}</p>
                </div>
              )}
              {intelligence.recommended_angle && (
                <div className="border-l-2 border-violet-300 pl-3">
                  <p className="text-xs font-medium text-violet-700 mb-1">Recommended approach</p>
                  <p className="text-sm text-slate-700 leading-relaxed">{intelligence.recommended_angle}</p>
                </div>
              )}
              {intelligence.similar_converted_companies.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-slate-500 mb-2">Similar companies that converted</p>
                  <div className="flex flex-wrap gap-2">
                    {intelligence.similar_converted_companies.map((c, i) => (
                      <span key={i} className="rounded-full bg-green-50 border border-green-200 px-2.5 py-1 text-xs text-green-700">
                        {c.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Signal timeline */}
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h3 className="mb-4 text-sm font-semibold text-slate-800 flex items-center gap-2">
              <Calendar className="h-4 w-4 text-slate-400" /> Signal timeline
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-normal text-slate-500">
                {signals.length}
              </span>
            </h3>

            {signals.length === 0 ? (
              <p className="text-sm text-slate-400">No signals detected yet.</p>
            ) : (
              <div className="relative">
                <div className="absolute left-2 top-2 bottom-2 w-px bg-slate-200" />
                <div className="space-y-4">
                  {signals.map((sig) => (
                    <div key={sig.id} className="flex gap-4">
                      <div className="relative z-10 mt-1 flex-shrink-0">
                        <div className="h-4 w-4 rounded-full bg-violet-500 flex items-center justify-center">
                          <div className="h-1.5 w-1.5 rounded-full bg-white" />
                        </div>
                      </div>
                      <div className="min-w-0 flex-1 pb-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                            {SIGNAL_TYPE_LABELS[sig.type] ?? sig.type}
                          </span>
                          <span className="text-xs text-slate-400">{timeAgo(sig.detected_at)}</span>
                          <span className="text-xs text-slate-400">
                            strength {Math.round(sig.strength * 100)}%
                          </span>
                        </div>
                        <p className="mt-1 text-sm font-medium text-slate-800">{sig.title}</p>
                        {sig.description && (
                          <p className="mt-0.5 text-xs text-slate-500 leading-relaxed">{sig.description}</p>
                        )}
                        {sig.url && (
                          <a href={sig.url} target="_blank" rel="noopener noreferrer"
                            className="mt-1 inline-flex items-center gap-1 text-xs text-violet-600 hover:underline">
                            Source <ExternalLink className="h-2.5 w-2.5" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Contacts */}
          {contacts.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h3 className="mb-4 text-sm font-semibold text-slate-800 flex items-center gap-2">
                <Users className="h-4 w-4 text-slate-400" /> Decision makers
              </h3>
              <div className="divide-y divide-slate-100">
                {contacts.map((c) => (
                  <div key={c.id} className="flex items-center justify-between py-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-slate-800">{c.name ?? "Unknown"}</p>
                        {c.is_primary && (
                          <span className="rounded-full bg-violet-50 border border-violet-200 px-1.5 py-0.5 text-xs text-violet-700">Primary</span>
                        )}
                      </div>
                      {c.title && <p className="text-xs text-slate-500">{c.title}</p>}
                    </div>
                    <div className="flex items-center gap-2">
                      {c.email && (
                        <a href={`mailto:${c.email}`}
                          className="text-xs text-violet-600 hover:underline truncate max-w-40">
                          {c.email}
                        </a>
                      )}
                      {c.linkedin_url && (
                        <a href={c.linkedin_url} target="_blank" rel="noopener noreferrer"
                          className="text-slate-400 hover:text-violet-600">
                          <ExternalLink className="h-3.5 w-3.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Technologies */}
          {company.technologies && company.technologies.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h3 className="mb-3 text-sm font-semibold text-slate-800">Tech stack</h3>
              <div className="flex flex-wrap gap-2">
                {company.technologies.map((t) => (
                  <span key={t} className="rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                    {t}
                  </span>
                ))}
              </div>
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
