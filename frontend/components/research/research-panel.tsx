"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import { useCompanyResearch, useGenerateResearch } from "@/hooks/use-api";
import { getErrorMessage } from "@/lib/api-client";
import { Skeleton } from "@/components/ui/skeleton";
import { ResearchReport } from "@/components/research/research-report";
import { cn, timeAgo } from "@/lib/utils";

/** Staged labels shown while generation runs, so progress reads as movement. */
const PROGRESS_STAGES = [
  "Reading company intelligence",
  "Analyzing buying signals",
  "Identifying decision makers",
  "Building the research report",
];

function GenerateButton({
  onClick,
  disabled,
  busy,
  label,
  variant = "primary",
}: {
  onClick: () => void;
  disabled?: boolean;
  busy?: boolean;
  label: string;
  variant?: "primary" | "secondary";
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-semibold transition-all disabled:cursor-not-allowed disabled:opacity-60 cursor-pointer shadow-xs",
        variant === "primary"
          ? "bg-indigo-600 text-white hover:bg-indigo-700 shadow-indigo-600/20"
          : "border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
      )}
    >
      {busy ? (
        <RefreshCw className="h-3.5 w-3.5 animate-spin motion-reduce:animate-none" />
      ) : (
        <Sparkles className="h-3.5 w-3.5 text-indigo-500 dark:text-indigo-400" />
      )}
      {label}
    </button>
  );
}

function ProgressState() {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const timer = setInterval(
      () => setStage((s) => Math.min(s + 1, PROGRESS_STAGES.length - 1)),
      2500
    );
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs">
      <div className="mb-4 flex items-center gap-2">
        <RefreshCw className="h-4 w-4 animate-spin text-indigo-600 dark:text-indigo-400 motion-reduce:animate-none" />
        <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{PROGRESS_STAGES[stage]}…</p>
      </div>
      <div className="mb-4 h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
        <div
          className="h-full rounded-full bg-indigo-600 transition-all duration-700 motion-reduce:transition-none"
          style={{ width: `${((stage + 1) / PROGRESS_STAGES.length) * 100}%` }}
        />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-3.5 w-full" />
        <Skeleton className="h-3.5 w-5/6" />
        <Skeleton className="h-3.5 w-2/3" />
      </div>
    </div>
  );
}

function ErrorState({
  message,
  onRetry,
  retrying,
}: {
  message: string;
  onRetry: () => void;
  retrying: boolean;
}) {
  return (
    <div className="rounded-2xl border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 p-5">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-red-600 dark:text-red-400" />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-bold text-red-900 dark:text-red-400">Research didn&apos;t finish</p>
          <p className="mt-0.5 text-xs leading-relaxed text-red-700 dark:text-red-300">{message}</p>
          <div className="mt-3">
            <GenerateButton
              onClick={onRetry}
              busy={retrying}
              disabled={retrying}
              label={retrying ? "Retrying…" : "Try again"}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ onGenerate, busy }: { onGenerate: () => void; busy: boolean }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900/90 p-8 text-center shadow-xs">
      <div className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-indigo-50/50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/30">
        <Sparkles className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
      </div>
      <p className="text-base font-bold text-slate-900 dark:text-white">Generate AI Research Report</p>
      <p className="mx-auto mt-1 max-w-sm text-xs leading-relaxed text-slate-500 dark:text-slate-400">
        Turn this company&apos;s signals, scores and contacts into an executive sales research report:
        why they may be buying, who to reach, and what to say.
      </p>
      <div className="mt-4 flex justify-center">
        <GenerateButton
          onClick={onGenerate}
          busy={busy}
          disabled={busy}
          label={busy ? "Starting…" : "Generate AI Research"}
        />
      </div>
    </div>
  );
}

export function ResearchPanel({ companyId }: { companyId: string }) {
  const { data, isLoading, isError, error } = useCompanyResearch(companyId);
  const generate = useGenerateResearch(companyId);

  const runGenerate = (force: boolean) => generate.mutate({ force_refresh: force });

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-12 w-full rounded-2xl" />
        <Skeleton className="h-36 w-full rounded-2xl" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        message={getErrorMessage(error)}
        onRetry={() => runGenerate(false)}
        retrying={generate.isPending}
      />
    );
  }

  const status = data?.status ?? "none";
  const isGenerating = status === "pending" || status === "running" || generate.isPending;

  if (isGenerating) return <ProgressState />;

  if (status === "failed") {
    return (
      <ErrorState
        message={
          data?.error_message ??
          "The report could not be generated. Try again in a moment."
        }
        onRetry={() => runGenerate(true)}
        retrying={generate.isPending}
      />
    );
  }

  if (generate.isError && status === "none") {
    return (
      <ErrorState
        message={getErrorMessage(generate.error)}
        onRetry={() => runGenerate(false)}
        retrying={generate.isPending}
      />
    );
  }

  if (status === "none" || !data) {
    return <EmptyState onGenerate={() => runGenerate(false)} busy={generate.isPending} />;
  }

  return (
    <div className="space-y-3 text-slate-900 dark:text-slate-200">
      <div className="flex items-center justify-between gap-3 rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 px-5 py-3.5 shadow-xs">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-white">
              <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              AI Research Briefing
            </h3>
            {data.is_stale && (
              <span className="rounded-full border border-amber-200 dark:border-amber-500/30 bg-amber-50 dark:bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-700 dark:text-amber-400">
                New Intelligence Available
              </span>
            )}
          </div>
          {data.updated_at && (
            <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
              Generated {timeAgo(data.updated_at)}
              {data.meta.model_version ? ` · ${data.meta.model_version}` : ""}
            </p>
          )}
        </div>
        <GenerateButton
          onClick={() => runGenerate(true)}
          busy={generate.isPending}
          disabled={generate.isPending}
          label={generate.isPending ? "Regenerating…" : "Regenerate"}
          variant={data.is_stale ? "primary" : "secondary"}
        />
      </div>

      <ResearchReport data={data} />
    </div>
  );
}
