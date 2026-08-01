"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  ExternalLink, X, ChevronRight, Users, MapPin, Zap, MessageSquarePlus, Sparkles
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
      <div className="group relative rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs hover:shadow-md hover:border-indigo-300 dark:hover:border-indigo-500/40 transition-all duration-300 cursor-pointer">
        {/* Dismiss Button */}
        <button
          onClick={handleDismiss}
          className="absolute right-3.5 top-3.5 hidden rounded-lg p-1.5 text-slate-400 dark:text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-slate-300 group-hover:flex transition-colors"
          title="Dismiss from feed"
          aria-label={`Dismiss ${company.name} from feed`}
        >
          <X className="h-4 w-4" />
        </button>

        <div onClick={handleCardClick}>
          {/* Header */}
          <div className="flex items-start gap-4">
            <ScoreRing score={intelligence.composite_score} size={52} className="flex-shrink-0 mt-0.5" />

            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="text-base font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                  {company.name}
                </h3>
                <BuyingWindowBadge window={intelligence.buying_window} size="sm" />
                {company.funding_stage && (
                  <span className="rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200/80 dark:border-indigo-500/30 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 dark:text-indigo-400">
                    {company.funding_stage}
                  </span>
                )}
              </div>

              <div className="mt-1 flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                {company.industry && <span>{company.industry}</span>}
                {company.employee_count && (
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3 text-slate-400 dark:text-slate-500" />
                    {company.employee_range ?? `${company.employee_count}`}
                  </span>
                )}
                {company.location && (
                  <span className="flex items-center gap-1 truncate">
                    <MapPin className="h-3 w-3 text-slate-400 dark:text-slate-500 flex-shrink-0" />
                    {company.location}
                  </span>
                )}
              </div>
            </div>

            <ChevronRight className="h-4 w-4 text-slate-300 dark:text-slate-600 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all flex-shrink-0 mt-1" />
          </div>

          {/* Signal summary */}
          <div className="mt-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/60 p-3.5 space-y-1">
            <p className="text-xs font-bold text-indigo-700 dark:text-indigo-400 flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
              Avenor-AI Signal Catalyst
            </p>
            <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-normal">{intelligence.signal_summary}</p>
          </div>

          {/* Top signals */}
          {intelligence.top_signals.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {intelligence.top_signals.slice(0, 3).map((sig, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 rounded-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 px-2.5 py-1 text-xs font-medium text-slate-700 dark:text-slate-300"
                >
                  <Zap className="h-2.5 w-2.5 text-indigo-600 dark:text-indigo-400" />
                  {SIGNAL_TYPE_LABELS[sig.type] ?? sig.type}
                  <span className="text-slate-400 dark:text-slate-500">Â· {timeAgo(sig.detected_at)}</span>
                </span>
              ))}
            </div>
          )}

          {/* Recommended approach */}
          {intelligence.recommended_angle && (
            <div className="mt-3 border-l-2 border-indigo-500 dark:border-indigo-400 pl-3">
              <p className="text-xs font-bold text-indigo-700 dark:text-indigo-400 mb-0.5">Recommended GTM Approach</p>
              <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{intelligence.recommended_angle}</p>
            </div>
          )}

          {/* Footer details */}
          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-4">
              {recommended_contact?.name && (
                <span>Decision Maker: <span className="text-slate-800 dark:text-slate-200 font-semibold">{recommended_contact.name}</span>
                  {recommended_contact.title && ` Â· ${recommended_contact.title}`}
                </span>
              )}
              {company.domain && (
                <a
                  href={`https://${company.domain}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="flex items-center gap-1 text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
                >
                  {company.domain}
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>

            {company.funding_total_usd && (
              <span className="text-xs text-slate-500 dark:text-slate-400 font-semibold">
                {formatCurrency(company.funding_total_usd)} Funding
              </span>
            )}
          </div>
        </div>

        {/* Log outcome button */}
        <button
          onClick={(e) => { e.stopPropagation(); setShowOutcome(true); }}
          className="mt-3.5 flex w-full items-center justify-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-xs cursor-pointer"
        >
          <MessageSquarePlus className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
          Log Outcome & Train AI Engine
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

