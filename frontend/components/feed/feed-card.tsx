"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  ExternalLink, X, ChevronRight, Users, MapPin,
  TrendingUp, Zap, MessageSquarePlus,
} from "lucide-react";
import { BuyingWindowBadge } from "@/components/ui/buying-window-badge";
import { ScoreRing } from "@/components/ui/score-ring";
import { OutcomeModal } from "@/components/outcomes/outcome-modal";
import { useDismissCompany } from "@/hooks/use-api";
import { formatCurrency, SIGNAL_TYPE_LABELS, timeAgo } from "@/lib/utils";
import type { FeedItem } from "@/types/api";

interface Props {
  item: FeedItem;
}

export function FeedCard({ item }: Props) {
  const router = useRouter();
  const dismiss = useDismissCompany();
  const [showOutcome, setShowOutcome] = useState(false);
  const { company, intelligence, recommended_contact } = item;

  function handleDismiss(e: React.MouseEvent) {
    e.stopPropagation();
    dismiss.mutate(company.id);
  }

  function handleCardClick() {
    router.push(`/dashboard/companies/${company.id}`);
  }

  return (
    <>
      <div className="group relative rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:border-violet-300 hover:shadow-md transition-all cursor-pointer">
        {/* Dismiss */}
        <button
          onClick={handleDismiss}
          className="absolute right-3 top-3 hidden rounded p-1 text-slate-300 hover:bg-slate-100 hover:text-slate-500 group-hover:flex"
        >
          <X className="h-3.5 w-3.5" />
        </button>

        <div onClick={handleCardClick}>
          {/* Header */}
          <div className="flex items-start gap-4">
            <ScoreRing score={intelligence.composite_score} size={52} className="flex-shrink-0 mt-0.5" />

            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-sm font-semibold text-slate-900 truncate">{company.name}</h3>
                <BuyingWindowBadge window={intelligence.buying_window} size="sm" />
                {company.funding_stage && (
                  <span className="rounded-full bg-violet-50 border border-violet-200 px-2 py-0.5 text-xs font-medium text-violet-700">
                    {company.funding_stage}
                  </span>
                )}
              </div>

              <div className="mt-1 flex items-center gap-3 text-xs text-slate-500">
                {company.industry && <span>{company.industry}</span>}
                {company.employee_count && (
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    {company.employee_range ?? `${company.employee_count}`}
                  </span>
                )}
                {company.location && (
                  <span className="flex items-center gap-1 truncate">
                    <MapPin className="h-3 w-3 flex-shrink-0" />
                    {company.location}
                  </span>
                )}
              </div>
            </div>

            <ChevronRight className="h-4 w-4 text-slate-300 flex-shrink-0 mt-1" />
          </div>

          {/* Signal summary */}
          <div className="mt-4 rounded-lg bg-slate-50 border border-slate-100 px-4 py-3">
            <p className="text-xs font-medium text-slate-500 mb-1 flex items-center gap-1">
              <TrendingUp className="h-3 w-3" /> Why now
            </p>
            <p className="text-sm text-slate-700 leading-relaxed">{intelligence.signal_summary}</p>
          </div>

          {/* Top signals */}
          {intelligence.top_signals.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {intelligence.top_signals.slice(0, 3).map((sig, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 rounded-full bg-white border border-slate-200 px-2.5 py-1 text-xs text-slate-600"
                >
                  <Zap className="h-2.5 w-2.5 text-violet-500" />
                  {SIGNAL_TYPE_LABELS[sig.type] ?? sig.type}
                  <span className="text-slate-400">· {timeAgo(sig.detected_at)}</span>
                </span>
              ))}
            </div>
          )}

          {/* Recommended angle */}
          {intelligence.recommended_angle && (
            <div className="mt-3 border-l-2 border-violet-300 pl-3">
              <p className="text-xs font-medium text-violet-700 mb-0.5">Recommended approach</p>
              <p className="text-xs text-slate-600 leading-relaxed">{intelligence.recommended_angle}</p>
            </div>
          )}

          {/* Footer */}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs text-slate-400">
              {recommended_contact?.name && (
                <span>Contact: <span className="text-slate-600 font-medium">{recommended_contact.name}</span>
                  {recommended_contact.title && ` · ${recommended_contact.title}`}
                </span>
              )}
              {company.domain && (
                <a
                  href={`https://${company.domain}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="flex items-center gap-1 hover:text-violet-600"
                >
                  {company.domain}
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>

            {company.funding_total_usd && (
              <span className="text-xs text-slate-400">
                {formatCurrency(company.funding_total_usd)} raised
              </span>
            )}
          </div>
        </div>

        {/* Log outcome button */}
        <button
          onClick={(e) => { e.stopPropagation(); setShowOutcome(true); }}
          className="mt-3 flex w-full items-center justify-center gap-1.5 rounded-lg border border-slate-200 py-1.5 text-xs font-medium text-slate-500 hover:border-violet-300 hover:text-violet-600 transition-colors"
        >
          <MessageSquarePlus className="h-3.5 w-3.5" />
          Log outcome
        </button>
      </div>

      {showOutcome && (
        <OutcomeModal
          companyId={company.id}
          companyName={company.name}
          onClose={() => setShowOutcome(false)}
        />
      )}
    </>
  );
}
