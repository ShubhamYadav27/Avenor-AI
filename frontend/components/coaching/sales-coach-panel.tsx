"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Archive,
  Clipboard,
  Download,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  Target,
} from "lucide-react";
import {
  useArchiveSalesCoaching,
  useCompanySalesCoaching,
  useGenerateSalesCoaching,
  useRegenerateSalesCoaching,
} from "@/hooks/use-api";
import { getErrorMessage } from "@/lib/api-client";
import { cn, timeAgo } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { EmphasisBadge } from "@/components/research/research-section";
import type {
  SalesCoachActionItem,
  SalesCoachEvidence,
  SalesCoachPayload,
  SalesCoachResponse,
  SalesCoachStageGuidance,
} from "@/types/api";

const PROGRESS_STAGES = [
  "Reading briefing and CRM context",
  "Mapping objections and stakeholders",
  "Building coaching plays",
  "Scoring win probability",
];

function markdownList(items: string[]) {
  return items.length ? items.map((item) => `- ${item}`).join("\n") : "- None available";
}

function actionList(items: SalesCoachActionItem[]) {
  return items.length
    ? items
        .map((item) => {
          const details = [item.owner, item.timeframe].filter(Boolean).join(", ");
          return `- ${item.action} (${item.priority})${details ? ` - ${details}` : ""}: ${item.rationale}`;
        })
        .join("\n")
    : "- None available";
}

function evidenceMarkdown(evidence: SalesCoachEvidence) {
  return [
    ["Buying signals", evidence.buying_signals],
    ["Research findings", evidence.research_findings],
    ["CRM information", evidence.crm_information],
    ["Briefing insights", evidence.briefing_insights],
  ]
    .map(([title, items]) => `### ${title}\n\n${markdownList(items as string[])}`)
    .join("\n\n");
}

function buildMarkdown(coaching: SalesCoachResponse) {
  const data = coaching.coaching_json;
  if (!data) return coaching.summary ?? "";

  const stage = (title: string, item: SalesCoachStageGuidance) =>
    `## ${title}\n\nObjective: ${item.objective}\n\n${item.coaching}\n\nQuestions:\n${markdownList(item.questions)}`;

  const sections: [string, string][] = [
    ["Executive Coaching Summary", data.executive_coaching_summary],
    ["Deal Health", data.deal_health_assessment],
    ["Win Probability", `${Math.round(data.win_probability * 100)}%\n\n${data.win_probability_explanation}`],
    [
      "Positive Buying Signals",
      data.positive_buying_signals
        .map((signal) => `- ${signal.title} (${signal.strength}): ${signal.evidence} Impact: ${signal.impact}`)
        .join("\n"),
    ],
    [
      "Risk Factors",
      data.risk_factors
        .map((risk) => `- ${risk.title} (${risk.severity}): ${risk.description}${risk.mitigation ? ` Mitigation: ${risk.mitigation}` : ""}`)
        .join("\n"),
    ],
    [
      "Deal Blockers",
      data.deal_blockers
        .map((risk) => `- ${risk.title} (${risk.severity}): ${risk.description}${risk.mitigation ? ` Mitigation: ${risk.mitigation}` : ""}`)
        .join("\n"),
    ],
    ["Decision Maker Analysis", data.decision_maker_analysis],
    [
      "Stakeholder Influence Map",
      data.stakeholder_influence_map
        .map((stakeholder) => {
          const name = stakeholder.name ? `${stakeholder.name}, ` : "";
          return `- ${name}${stakeholder.title} (${stakeholder.influence}, ${stakeholder.priority}): ${stakeholder.recommended_approach}`;
        })
        .join("\n"),
    ],
    [
      "Likely Customer Objections",
      data.likely_customer_objections
        .map((item) => [
          `- ${item.objection} (${item.severity})`,
          `  Customer: ${item.customer_statement}`,
          `  Why: ${item.why_customer_may_say_this}`,
          `  Response: ${item.recommended_response}`,
          `  Follow-up: ${item.follow_up_question}`,
          `  Goal: ${item.goal_of_response}`,
        ].join("\n"))
        .join("\n"),
    ],
    [
      "Competitive Battle Cards",
      data.competitive_battle_cards
        .map((card) => `- ${card.competitor_or_alternative}: ${card.recommended_talk_track}`)
        .join("\n"),
    ],
    ["Competitor Comparison", data.competitor_comparison],
    ["Pricing Negotiation Strategy", data.pricing_negotiation_strategy],
    ["Expansion Opportunity", data.expansion_opportunity],
    ["Next Best Action", data.recommended_next_best_action],
    ["Immediate Action Plan", actionList(data.immediate_action_plan)],
    ["Follow-up Strategy", actionList(data.follow_up_strategy)],
    ["Long-term Action Plan", actionList(data.long_term_action_plan)],
    ["Escalation Recommendation", data.escalation_recommendation ?? "No escalation recommended."],
    ["Confidence", `${Math.round(data.confidence_score * 100)}%\n\n${data.confidence_explanation}`],
    ["Explainability", evidenceMarkdown(data.explainability)],
  ];

  return [
    ...sections.map(([title, content]) => `## ${title}\n\n${content || "None available"}`),
    stage("Discovery Coaching", data.discovery_coaching),
    stage("Demo Coaching", data.demo_coaching),
    stage("Negotiation Coaching", data.negotiation_coaching),
    stage("Closing Coaching", data.closing_coaching),
  ].join("\n\n");
}

function ProgressState() {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const timer = setInterval(
      () => setStage((s) => Math.min(s + 1, PROGRESS_STAGES.length - 1)),
      2300
    );
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="rounded-xl border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50/50 dark:bg-indigo-500/10 p-4 transition-colors">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-indigo-900 dark:text-indigo-300">
        <RefreshCw className="h-4 w-4 animate-spin text-indigo-600 dark:text-indigo-400 motion-reduce:animate-none" />
        {PROGRESS_STAGES[stage]}
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
        <div
          className="h-full rounded-full bg-indigo-600 dark:bg-indigo-400 transition-all duration-700"
          style={{ width: `${((stage + 1) / PROGRESS_STAGES.length) * 100}%` }}
        />
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200/80 dark:border-slate-800/80 bg-slate-50/80 dark:bg-slate-800/40 p-3.5 transition-colors">
      <p className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">{title}</p>
      {children}
    </div>
  );
}

function BulletList({ items }: { items: string[] }) {
  if (!items.length) return <p className="text-sm text-slate-400 dark:text-slate-500">None available.</p>;
  return (
    <ul className="space-y-1.5 text-sm leading-relaxed text-slate-800 dark:text-slate-200">
      {items.map((item, index) => (
        <li key={`${item}-${index}`}>- {item}</li>
      ))}
    </ul>
  );
}

function ActionList({ items }: { items: SalesCoachActionItem[] }) {
  if (!items.length) return <p className="text-sm text-slate-400 dark:text-slate-500">None available.</p>;
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.action} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-bold text-slate-900 dark:text-white">{item.action}</p>
            <EmphasisBadge level={item.priority} />
          </div>
          <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{item.rationale}</p>
          {(item.owner || item.timeframe) && (
            <p className="mt-1 text-xs font-medium text-slate-500 dark:text-slate-400">
              {[item.owner, item.timeframe].filter(Boolean).join(" - ")}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

function StageCard({ item }: { item: SalesCoachStageGuidance }) {
  return (
    <div className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
      <p className="text-sm font-bold capitalize text-slate-900 dark:text-white">{item.stage}</p>
      <p className="mt-1 text-xs font-semibold text-slate-600 dark:text-slate-300">{item.objective}</p>
      <p className="mt-1 text-xs leading-relaxed text-slate-700 dark:text-slate-200">{item.coaching}</p>
      <div className="mt-2">
        <BulletList items={item.questions} />
      </div>
    </div>
  );
}

function SalesCoachView({ data }: { data: SalesCoachPayload }) {
  return (
    <div className="grid gap-3">
      <Section title="Executive Coaching Summary">
        <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.executive_coaching_summary}</p>
      </Section>

      <div className="grid gap-3 md:grid-cols-3">
        <Section title="Win Probability">
          <p className="text-2xl font-black text-slate-900 dark:text-white">{Math.round(data.win_probability * 100)}%</p>
          <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{data.win_probability_explanation}</p>
        </Section>
        <Section title="Deal Health">
          <p className="text-lg font-bold capitalize text-indigo-700 dark:text-indigo-400">
            {data.deal_health_assessment.replace("_", " ")}
          </p>
        </Section>
        <Section title="Confidence Score">
          <p className="text-2xl font-black text-slate-900 dark:text-white">{Math.round(data.confidence_score * 100)}%</p>
          <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{data.confidence_explanation}</p>
        </Section>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Buying Signals">
          <div className="space-y-2">
            {data.positive_buying_signals.map((signal) => (
              <div key={signal.title} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-bold text-slate-900 dark:text-white">{signal.title}</p>
                  <EmphasisBadge level={signal.strength} />
                </div>
                <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{signal.evidence}</p>
                <p className="mt-1 text-xs leading-relaxed text-slate-700 dark:text-slate-200 font-medium">{signal.impact}</p>
              </div>
            ))}
          </div>
        </Section>
        <Section title="Decision Makers">
          <p className="mb-2 text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.decision_maker_analysis}</p>
          <div className="space-y-2">
            {data.stakeholder_influence_map.map((stakeholder) => (
              <div key={`${stakeholder.name}-${stakeholder.title}`} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-bold text-slate-900 dark:text-white">
                    {stakeholder.name ? `${stakeholder.name} - ` : ""}
                    {stakeholder.title}
                  </p>
                  <span className="rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2.5 py-0.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
                    {stakeholder.influence.replace("_", " ")}
                  </span>
                </div>
                <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{stakeholder.recommended_approach}</p>
              </div>
            ))}
          </div>
        </Section>
      </div>

      <Section title="Likely Objections">
        <div className="space-y-2">
          {data.likely_customer_objections.map((item) => (
            <div key={item.objection} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3.5 shadow-2xs">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-bold text-slate-900 dark:text-white">{item.objection}</p>
                <span className="rounded-full bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30 px-2.5 py-0.5 text-xs font-semibold text-amber-800 dark:text-amber-300">
                  {item.severity}
                </span>
              </div>
              <p className="mt-2 text-xs font-semibold text-slate-500 dark:text-slate-400">Customer Statement</p>
              <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200 italic">&ldquo;{item.customer_statement}&rdquo;</p>
              <p className="mt-2 text-xs font-semibold text-indigo-700 dark:text-indigo-400">Recommended Response</p>
              <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{item.recommended_response}</p>
              <p className="mt-2 text-xs font-semibold text-slate-500 dark:text-slate-400">Follow-up Question</p>
              <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{item.follow_up_question}</p>
              <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">Goal: {item.goal_of_response}</p>
            </div>
          ))}
        </div>
      </Section>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Risk Factors">
          <ActionRiskList items={data.risk_factors} />
        </Section>
        <Section title="Deal Blockers">
          <ActionRiskList items={data.deal_blockers} />
        </Section>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Competitive Battle Cards">
          <div className="space-y-2">
            {data.competitive_battle_cards.map((card) => (
              <div key={card.competitor_or_alternative} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
                <p className="text-sm font-bold text-slate-900 dark:text-white">{card.competitor_or_alternative}</p>
                <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{card.recommended_talk_track}</p>
              </div>
            ))}
          </div>
        </Section>
        <Section title="Pricing Strategy">
          <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.pricing_negotiation_strategy}</p>
        </Section>
      </div>

      <Section title="Stage Coaching">
        <div className="grid gap-2 md:grid-cols-2">
          <StageCard item={data.discovery_coaching} />
          <StageCard item={data.demo_coaching} />
          <StageCard item={data.negotiation_coaching} />
          <StageCard item={data.closing_coaching} />
        </div>
      </Section>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Next Best Action">
          <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.recommended_next_best_action}</p>
        </Section>
        <Section title="Expansion Opportunity">
          <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.expansion_opportunity}</p>
        </Section>
      </div>

      <div className="grid gap-3 lg:grid-cols-3">
        <Section title="Immediate Plan">
          <ActionList items={data.immediate_action_plan} />
        </Section>
        <Section title="Follow-up Strategy">
          <ActionList items={data.follow_up_strategy} />
        </Section>
        <Section title="Long-term Plan">
          <ActionList items={data.long_term_action_plan} />
        </Section>
      </div>

      {data.escalation_recommendation && (
        <Section title="Escalation Recommendation">
          <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.escalation_recommendation}</p>
        </Section>
      )}

      <Section title="Explainability & Provenance">
        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <p className="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">Buying Signals</p>
            <BulletList items={data.explainability.buying_signals} />
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">Research Findings</p>
            <BulletList items={data.explainability.research_findings} />
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">CRM Information</p>
            <BulletList items={data.explainability.crm_information} />
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">Briefing Insights</p>
            <BulletList items={data.explainability.briefing_insights} />
          </div>
        </div>
      </Section>
    </div>
  );
}

function ActionRiskList({ items }: { items: SalesCoachPayload["risk_factors"] }) {
  if (!items.length) return <p className="text-sm text-slate-400 dark:text-slate-500">None available.</p>;
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.title} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-bold text-slate-900 dark:text-white">{item.title}</p>
            <EmphasisBadge level={item.severity} />
          </div>
          <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{item.description}</p>
          {item.mitigation && (
            <p className="mt-1 text-xs leading-relaxed text-slate-700 dark:text-slate-200 font-medium">Mitigation: {item.mitigation}</p>
          )}
        </div>
      ))}
    </div>
  );
}

export function SalesCoachPanel({ companyId }: { companyId: string }) {
  const { data, isLoading, isError, error } = useCompanySalesCoaching(companyId);
  const generate = useGenerateSalesCoaching(companyId);
  const regenerate = useRegenerateSalesCoaching(companyId);
  const archive = useArchiveSalesCoaching(companyId);
  const [markdownEdit, setMarkdownEdit] = useState<{ coachingId: string; value: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const latest = useMemo(
    () => data?.coaching.find((coaching) => coaching.status === "completed") ?? data?.coaching[0],
    [data?.coaching]
  );
  const generatedMarkdown = useMemo(
    () => (latest?.status === "completed" ? buildMarkdown(latest) : ""),
    [latest]
  );
  const markdown =
    latest && markdownEdit?.coachingId === latest.id ? markdownEdit.value : generatedMarkdown;
  const generating = data?.status === "pending" || data?.status === "running" || generate.isPending;

  const copySummary = async () => {
    await navigator.clipboard.writeText(
      latest?.summary ?? latest?.coaching_json?.executive_coaching_summary ?? ""
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const exportMarkdown = () => {
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `avenor-sales-coaching-${companyId}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs transition-colors">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
            <Target className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            AI Deal Sales Coach
          </h3>
          {latest?.updated_at && (
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Generated {timeAgo(latest.updated_at)}
              {latest.meta.model_version ? ` - ${latest.meta.model_version}` : ""}
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => generate.mutate({ force_refresh: false })}
            disabled={generating}
            className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60 transition-colors shadow-xs cursor-pointer"
          >
            {generating ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
            Generate
          </button>
          {latest && (
            <>
              <button
                type="button"
                onClick={() => regenerate.mutate(latest.id)}
                disabled={regenerate.isPending || generating}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-60 transition-colors shadow-2xs cursor-pointer"
              >
                <RefreshCw className={cn("h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400", regenerate.isPending && "animate-spin")} />
                Regenerate
              </button>
              <button
                type="button"
                onClick={() => archive.mutate(latest.id)}
                disabled={archive.isPending}
                className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-60 transition-colors shadow-2xs cursor-pointer"
              >
                <Archive className="h-3.5 w-3.5" />
                Archive
              </button>
            </>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {isLoading && (
          <>
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-32 w-full" />
          </>
        )}

        {(isError || generate.isError || regenerate.isError || archive.isError) && (
          <div className="rounded-xl border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 p-4 text-xs font-semibold text-red-700 dark:text-red-400">
            {getErrorMessage(error ?? generate.error ?? regenerate.error ?? archive.error)}
          </div>
        )}

        {generating && <ProgressState />}

        {!generating && data?.status === "failed" && (
          <div className="rounded-xl border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 p-4 text-xs font-semibold text-red-700 dark:text-red-400">
            {data.error_message ?? latest?.error_message ?? "Sales coaching generation failed."}
          </div>
        )}

        {!isLoading && !generating && !latest && (
          <div className="rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/40 p-6 text-center">
            <ShieldAlert className="mx-auto mb-2 h-5 w-5 text-indigo-600 dark:text-indigo-400" />
            <p className="text-sm font-bold text-slate-800 dark:text-white">No Sales Coaching Yet</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Generate after the sales briefing to coach objections, negotiation and next steps.
            </p>
          </div>
        )}

        {!generating && latest?.status === "completed" && latest.coaching_json && (
          <>
            {copied && (
              <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10 px-3.5 py-2 text-xs font-semibold text-emerald-800 dark:text-emerald-300">
                Summary copied to clipboard.
              </div>
            )}
            <SalesCoachView data={latest.coaching_json} />
            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-4 shadow-xs">
              <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Editable Markdown Export</p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={copySummary}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 shadow-2xs cursor-pointer"
                  >
                    <Clipboard className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                    Copy Summary
                  </button>
                  <button
                    type="button"
                    onClick={exportMarkdown}
                    className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 dark:bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 dark:hover:bg-indigo-700 shadow-xs cursor-pointer"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Export Markdown
                  </button>
                </div>
              </div>
              <textarea
                value={markdown}
                onChange={(event) =>
                  latest && setMarkdownEdit({ coachingId: latest.id, value: event.target.value })
                }
                rows={12}
                className="w-full resize-y rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3.5 py-2.5 font-mono text-xs leading-relaxed text-slate-800 dark:text-slate-200 outline-none focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-1 focus:ring-indigo-100 dark:focus:ring-indigo-500/20 transition-colors"
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
