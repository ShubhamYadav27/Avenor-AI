"use client";

import {
  AlertCircle,
  CheckCircle2,
  Clock,
  FileText,
  MessageSquare,
  Send,
  ShieldAlert,
  Target,
  Users,
  Zap,
} from "lucide-react";
import type { ResearchResponse } from "@/types/api";
import {
  EmphasisBadge,
  ResearchItem,
  ResearchSection,
} from "@/components/research/research-section";

/**
 * Renders a completed AI research report.
 *
 * Every section degrades gracefully: the model is instructed to omit sections
 * it has no evidence for, so an empty list is a valid outcome, not an error.
 */
export function ResearchReport({ data }: { data: ResearchResponse }) {
  const {
    summary,
    buying_signals,
    pain_points,
    recommended_personas,
    outreach_strategy,
    talking_points,
    risks,
    next_actions,
  } = data;

  return (
    <div className="space-y-3">
      {/* Executive summary — always visible, never collapsed */}
      {summary && (
        <ResearchSection title="Executive summary" icon={FileText} collapsible={false}>
          <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">{summary}</p>
        </ResearchSection>
      )}

      {/* Buying signals */}
      {buying_signals.length > 0 && (
        <ResearchSection title="Buying signals" icon={Zap} count={buying_signals.length}>
          <div className="space-y-3">
            {buying_signals.map((signal, i) => (
              <ResearchItem key={i}>
                <div className="mb-1 flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{signal.title}</p>
                  <EmphasisBadge level={signal.strength} />
                </div>
                <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                  {signal.why_it_matters}
                </p>
                <p className="mt-1.5 border-l-2 border-indigo-200 dark:border-indigo-500/30 pl-2 text-xs text-slate-500 dark:text-slate-400">
                  {signal.evidence}
                </p>
              </ResearchItem>
            ))}
          </div>
        </ResearchSection>
      )}

      {/* Pain points */}
      {pain_points.length > 0 && (
        <ResearchSection title="Pain points" icon={AlertCircle} count={pain_points.length}>
          <div className="space-y-3">
            {pain_points.map((pain, i) => (
              <ResearchItem key={i}>
                <div className="mb-1 flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{pain.title}</p>
                  <EmphasisBadge level={pain.priority} />
                </div>
                <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">{pain.description}</p>
                {pain.evidence && (
                  <p className="mt-1.5 border-l-2 border-indigo-200 dark:border-indigo-500/30 pl-2 text-xs text-slate-500 dark:text-slate-400">
                    {pain.evidence}
                  </p>
                )}
              </ResearchItem>
            ))}
          </div>
        </ResearchSection>
      )}

      {/* Recommended personas */}
      {recommended_personas.length > 0 && (
        <ResearchSection
          title="Recommended personas"
          icon={Users}
          count={recommended_personas.length}
        >
          <div className="space-y-3">
            {recommended_personas.map((persona, i) => (
              <ResearchItem key={i}>
                <div className="mb-1 flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{persona.title}</p>
                  <EmphasisBadge level={persona.priority} />
                  {persona.matched_contact_name && (
                    <span className="rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 px-2 py-0.5 text-xs text-indigo-700 dark:text-indigo-400">
                      {persona.matched_contact_name}
                    </span>
                  )}
                </div>
                <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">{persona.rationale}</p>
              </ResearchItem>
            ))}
          </div>
        </ResearchSection>
      )}

      {/* Outreach strategy */}
      {outreach_strategy && (
        <ResearchSection title="Outreach strategy" icon={Send}>
          <div className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <ResearchItem>
                <p className="mb-1 flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-slate-400">
                  <Target className="h-3 w-3" /> Channel
                </p>
                <p className="text-sm capitalize text-slate-800 dark:text-slate-200">
                  {outreach_strategy.recommended_channel}
                </p>
              </ResearchItem>
              <ResearchItem>
                <p className="mb-1 flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-slate-400">
                  <Clock className="h-3 w-3" /> Timing
                </p>
                <p className="text-sm text-slate-800 dark:text-slate-200">{outreach_strategy.timing}</p>
              </ResearchItem>
            </div>
            <div>
              <p className="mb-1 text-xs font-medium text-slate-500 dark:text-slate-400">Angle</p>
              <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
                {outreach_strategy.angle}
              </p>
            </div>
            <div className="border-l-2 border-indigo-300 dark:border-indigo-500/30 pl-3">
              <p className="mb-1 text-xs font-medium text-indigo-700 dark:text-indigo-400">Opening hook</p>
              <p className="text-sm italic leading-relaxed text-slate-700 dark:text-slate-300">
                &ldquo;{outreach_strategy.opening_hook}&rdquo;
              </p>
            </div>
          </div>
        </ResearchSection>
      )}

      {/* Talking points */}
      {talking_points.length > 0 && (
        <ResearchSection
          title="Talking points"
          icon={MessageSquare}
          count={talking_points.length}
        >
          <ul className="space-y-3">
            {talking_points.map((tp, i) => (
              <li key={i} className="flex gap-3">
                <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-indigo-500 dark:bg-indigo-400" />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{tp.point}</p>
                  <p className="mt-0.5 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                    {tp.supporting_detail}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </ResearchSection>
      )}

      {/* Risks */}
      {risks.length > 0 && (
        <ResearchSection title="Risks" icon={ShieldAlert} count={risks.length}>
          <div className="space-y-3">
            {risks.map((risk, i) => (
              <ResearchItem key={i}>
                <div className="mb-1 flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{risk.title}</p>
                  <EmphasisBadge level={risk.severity} />
                </div>
                <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">{risk.description}</p>
                {risk.mitigation && (
                  <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">
                    <span className="font-medium text-slate-600 dark:text-slate-300">Mitigation: </span>
                    {risk.mitigation}
                  </p>
                )}
              </ResearchItem>
            ))}
          </div>
        </ResearchSection>
      )}

      {/* Next actions */}
      {next_actions.length > 0 && (
        <ResearchSection title="Next actions" icon={CheckCircle2} count={next_actions.length}>
          <div className="space-y-3">
            {next_actions.map((action, i) => (
              <ResearchItem key={i}>
                <div className="mb-1 flex items-center gap-2 flex-wrap">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{action.action}</p>
                  <EmphasisBadge level={action.priority} />
                  {action.suggested_timeframe && (
                    <span className="flex items-center gap-1 text-xs text-slate-400 dark:text-slate-500">
                      <Clock className="h-3 w-3" />
                      {action.suggested_timeframe}
                    </span>
                  )}
                </div>
                <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">{action.rationale}</p>
              </ResearchItem>
            ))}
          </div>
        </ResearchSection>
      )}
    </div>
  );
}
