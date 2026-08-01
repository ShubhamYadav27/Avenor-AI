"use client";

import { RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/common/ThemeToggle";

interface Props {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function TopBar({ title, subtitle, action }: Props) {
  return (
    <div className="sticky top-0 z-30 shrink-0 flex h-16 items-center justify-between glass-navbar px-6 shadow-2xs transition-colors">
      <div>
        <h1 className="text-sm font-bold tracking-tight text-slate-900 dark:text-white">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3">
        {action}
        <ThemeToggle />
      </div>
    </div>
  );
}

interface RefreshButtonProps {
  onClick: () => void;
  loading?: boolean;
  label?: string;
}

export function RefreshButton({ onClick, loading, label = "Refresh" }: RefreshButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-50 transition-all shadow-2xs cursor-pointer"
    >
      <RefreshCw className={cn("h-3 w-3 text-indigo-600 dark:text-indigo-400", loading && "animate-spin")} />
      {label}
    </button>
  );
}
