"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Archive,
  Clipboard,
  Download,
  FileText,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import {
  useArchiveBriefing,
  useCompanyBriefings,
  useGenerateBriefing,
  useRegenerateBriefing,
} from "@/hooks/use-api";
import { getErrorMessage } from "@/lib/api-client";
import { cn, timeAgo } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import { EmphasisBadge } from "@/components/research/research-section";
import type { BriefingPayload, BriefingResponse } from "@/types/api";

const PROGRESS_STAGES = [
  "Collecting account intelligence",
  "Reviewing emails and CRM context",
  "Building meeting guidance",
  "Scoring confidence",
];

function markdownList(items: string[]) {
  return items.length ? items.map((item) => `- ${item}`).join("\n") : "- None available";
}

function buildMarkdown(briefing: BriefingResponse) {
  const data = briefing.briefing_json;
  if (!data) return briefing.summary ?? "";

  const sections: [string, string][] = [
    ["Executive Summary", data.executive_summary],
    ["Company Overview", data.company_overview],
    [
      "Current Buying Signals",
      data.current_buying_signals
        .map((signal) => `- ${signal.title} (${signal.strength}): ${signal.evidence}`)
        .join("\n"),
    ],
    ["Why This Company May Buy Now", markdownList(data.why_buy_now)],
    ["Recent Company Changes", markdownList(data.recent_company_changes)],
    ["Existing Relationship Summary", data.existing_relationship_summary],
    ["CRM Activity Summary", data.crm_activity_summary],
    [
      "Key Stakeholders",
      data.key_stakeholders
        .map((stakeholder) => {
          const name = stakeholder.name ? `${stakeholder.name}, ` : "";
          return `- ${name}${stakeholder.title} (${stakeholder.priority}): ${stakeholder.rationale}`;
        })
        .join("\n"),
    ],
    [
      "Recommended Contact Priority",
      data.recommended_contact_priority
        .map((contact) => `- ${contact.contact_or_persona} (${contact.priority}): ${contact.reason}`)
        .join("\n"),
    ],
    ["Existing AI Research Summary", data.existing_ai_research_summary],
    [
      "Previous Generated Emails",
      data.previous_generated_emails
        .map((email) => `- ${email.subject} (${email.variation}): ${email.summary}${email.cta ? ` CTA: ${email.cta}` : ""}`)
        .join("\n"),
    ],
    [
      "Pain Points",
      data.pain_points
        .map((pain) => `- ${pain.title} (${pain.priority}): ${pain.description}`)
        .join("\n"),
    ],
    [
      "Business Opportunities",
      data.business_opportunities
        .map((opportunity) => `- ${opportunity.title} (${opportunity.priority}): ${opportunity.rationale}`)
        .join("\n"),
    ],
    ["Suggested Value Proposition", data.suggested_value_proposition],
    ["Competitive Landscape", data.competitive_landscape],
    ["Discovery Questions", markdownList(data.discovery_questions)],
    ["Technical Questions", markdownList(data.technical_questions)],
    ["Business Questions", markdownList(data.business_questions)],
    ["Executive Questions", markdownList(data.executive_questions)],
    ["Possible Customer Objections", markdownList(data.possible_customer_objections)],
    [
      "Suggested Responses",
      data.suggested_responses
        .map((item) => `- ${item.objection}: ${item.response}`)
        .join("\n"),
    ],
    ["Recommended Meeting Agenda", markdownList(data.recommended_meeting_agenda)],
    ["Meeting Goals", markdownList(data.meeting_goals)],
    ["Recommended Demo Focus", markdownList(data.recommended_demo_focus)],
    ["Recommended Pricing Strategy", data.recommended_pricing_strategy],
    ["Recommended Follow-up Timeline", markdownList(data.recommended_follow_up_timeline)],
    ["Next Best Action", data.next_best_action],
    [
      "Risk Factors",
      data.risk_factors
        .map((risk) => `- ${risk.title} (${risk.severity}): ${risk.description}${risk.mitigation ? ` Mitigation: ${risk.mitigation}` : ""}`)
        .join("\n"),
    ],
    ["Confidence", `${Math.round(data.confidence_score * 100)}%\n\n${data.confidence_explanation}`],
  ];

  return sections
    .map(([title, content]) => `## ${title}\n\n${content || "None available"}`)
    .join("\n\n");
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

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
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

function BriefingView({ data }: { data: BriefingPayload }) {
  return (
    <div className="grid gap-3">
      <Section title="Executive Summary">
        <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.executive_summary}</p>
      </Section>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Buying Signals">
          <div className="space-y-2">
            {data.current_buying_signals.map((signal) => (
              <div key={signal.title} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-bold text-slate-900 dark:text-white">{signal.title}</p>
                  <EmphasisBadge level={signal.strength} />
                </div>
                <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{signal.evidence}</p>
              </div>
            ))}
          </div>
        </Section>
        <Section title="Stakeholders">
          <div className="space-y-2">
            {data.key_stakeholders.map((stakeholder) => (
              <div key={`${stakeholder.name}-${stakeholder.title}`} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-bold text-slate-900 dark:text-white">
                    {stakeholder.name ? `${stakeholder.name} - ` : ""}
                    {stakeholder.title}
                  </p>
                  <EmphasisBadge level={stakeholder.priority} />
                </div>
                <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{stakeholder.rationale}</p>
              </div>
            ))}
          </div>
        </Section>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Pain Points">
          <div className="space-y-2">
            {data.pain_points.map((pain) => (
              <div key={pain.title} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
                <p className="text-sm font-bold text-slate-900 dark:text-white">{pain.title}</p>
                <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{pain.description}</p>
              </div>
            ))}
          </div>
        </Section>
        <Section title="Business Opportunities">
          <div className="space-y-2">
            {data.business_opportunities.map((opportunity) => (
              <div key={opportunity.title} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
                <p className="text-sm font-bold text-slate-900 dark:text-white">{opportunity.title}</p>
                <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{opportunity.rationale}</p>
              </div>
            ))}
          </div>
        </Section>
      </div>

      <Section title="Recommended Questions">
        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <p className="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">Discovery</p>
            <BulletList items={data.discovery_questions} />
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">Technical</p>
            <BulletList items={data.technical_questions} />
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">Business</p>
            <BulletList items={data.business_questions} />
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold text-slate-500 dark:text-slate-400">Executive</p>
            <BulletList items={data.executive_questions} />
          </div>
        </div>
      </Section>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Meeting Agenda">
          <BulletList items={data.recommended_meeting_agenda} />
        </Section>
        <Section title="Demo Focus">
          <BulletList items={data.recommended_demo_focus} />
        </Section>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Pricing Strategy">
          <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.recommended_pricing_strategy}</p>
        </Section>
        <Section title="Next Best Action">
          <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200">{data.next_best_action}</p>
        </Section>
      </div>

      <Section title="Objections and Responses">
        <div className="space-y-2">
          {data.suggested_responses.map((item) => (
            <div key={item.objection} className="rounded-lg border border-slate-200/60 dark:border-slate-700/60 bg-white dark:bg-slate-900/60 p-3 shadow-2xs">
              <p className="text-sm font-bold text-slate-900 dark:text-white">{item.objection}</p>
              <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{item.response}</p>
            </div>
          ))}
        </div>
      </Section>

      <div className="grid gap-3 lg:grid-cols-2">
        <Section title="Follow-up Timeline">
          <BulletList items={data.recommended_follow_up_timeline} />
        </Section>
        <Section title="Confidence Score">
          <p className="text-2xl font-black text-slate-900 dark:text-white">{Math.round(data.confidence_score * 100)}%</p>
          <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{data.confidence_explanation}</p>
        </Section>
      </div>
    </div>
  );
}

export function SalesBriefingPanel({ companyId }: { companyId: string }) {
  const { data, isLoading, isError, error } = useCompanyBriefings(companyId);
  const generate = useGenerateBriefing(companyId);
  const regenerate = useRegenerateBriefing(companyId);
  const archive = useArchiveBriefing(companyId);
  const [markdownEdit, setMarkdownEdit] = useState<{ briefingId: string; value: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const latest = useMemo(
    () => data?.briefings.find((briefing) => briefing.status === "completed") ?? data?.briefings[0],
    [data?.briefings]
  );
  const generatedMarkdown = useMemo(
    () => (latest?.status === "completed" ? buildMarkdown(latest) : ""),
    [latest]
  );
  const markdown =
    latest && markdownEdit?.briefingId === latest.id ? markdownEdit.value : generatedMarkdown;
  const generating = data?.status === "pending" || data?.status === "running" || generate.isPending;

  const copySummary = async () => {
    await navigator.clipboard.writeText(latest?.summary ?? latest?.briefing_json?.executive_summary ?? "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const exportMarkdown = () => {
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `avenor-sales-briefing-${companyId}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs transition-colors">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
            <FileText className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            AI Executive Sales Briefing
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
            className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60 transition-colors cursor-pointer shadow-xs"
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
            {data.error_message ?? latest?.error_message ?? "Briefing generation failed."}
          </div>
        )}

        {!isLoading && !generating && !latest && (
          <div className="rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/40 p-6 text-center">
            <p className="text-sm font-bold text-slate-800 dark:text-white">No Sales Briefing Yet</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              Generate a meeting-ready briefing from research, email drafts, CRM context and signals.
            </p>
          </div>
        )}

        {!generating && latest?.status === "completed" && latest.briefing_json && (
          <>
            {copied && (
              <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10 px-3.5 py-2 text-xs font-semibold text-emerald-800 dark:text-emerald-300">
                Summary copied to clipboard.
              </div>
            )}
            <BriefingView data={latest.briefing_json} />
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
                  latest && setMarkdownEdit({ briefingId: latest.id, value: event.target.value })
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
