"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

/** Shared badge palette, aligned with WINDOW_CONFIG in lib/utils. */
export const EMPHASIS_STYLES: Record<string, string> = {
  high: "bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30 text-red-700 dark:text-red-400 font-semibold",
  strong: "bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30 text-red-700 dark:text-red-400 font-semibold",
  medium: "bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/30 text-amber-700 dark:text-amber-400 font-semibold",
  moderate: "bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/30 text-amber-700 dark:text-amber-400 font-semibold",
  low: "bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 font-semibold",
  weak: "bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 font-semibold",
};

export function EmphasisBadge({ level }: { level: string }) {
  return (
    <span
      className={cn(
        "rounded-full border px-2.5 py-0.5 text-xs capitalize transition-colors",
        EMPHASIS_STYLES[level] ?? EMPHASIS_STYLES.low
      )}
    >
      {level}
    </span>
  );
}

interface ResearchSectionProps {
  title: string;
  icon: LucideIcon;
  count?: number;
  defaultOpen?: boolean;
  collapsible?: boolean;
  children: React.ReactNode;
}

export function ResearchSection({
  title,
  icon: Icon,
  count,
  defaultOpen = true,
  collapsible = true,
  children,
}: ResearchSectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  const isOpen = collapsible ? open : true;
  const panelId = `research-section-${title.toLowerCase().replace(/\s+/g, "-")}`;

  const heading = (
    <>
      <Icon className="h-4 w-4 text-indigo-600 dark:text-indigo-400 flex-shrink-0" />
      <span className="text-sm font-bold text-slate-900 dark:text-white">{title}</span>
      {typeof count === "number" && count > 0 && (
        <span className="rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2 py-0.5 text-xs font-semibold text-slate-600 dark:text-slate-400">
          {count}
        </span>
      )}
    </>
  );

  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 shadow-xs transition-colors">
      {collapsible ? (
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={isOpen}
          aria-controls={panelId}
          className="flex w-full items-center gap-2 rounded-2xl px-5 py-4 text-left transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/60 focus:outline-none cursor-pointer"
        >
          {heading}
          <ChevronDown
            className={cn(
              "ml-auto h-4 w-4 text-slate-400 dark:text-slate-500 transition-transform motion-reduce:transition-none",
              isOpen && "rotate-180"
            )}
          />
        </button>
      ) : (
        <div className="flex items-center gap-2 px-5 py-4">{heading}</div>
      )}

      {isOpen && (
        <div id={panelId} className="border-t border-slate-100 dark:border-slate-800 px-5 py-4 text-slate-800 dark:text-slate-200">
          {children}
        </div>
      )}
    </div>
  );
}

/** Consistent inner card for list items across sections. */
export function ResearchItem({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={cn("rounded-xl border border-slate-100 dark:border-slate-800/60 bg-slate-50 dark:bg-slate-800/40 p-3.5 transition-colors", className)}>
      {children}
    </div>
  );
}
