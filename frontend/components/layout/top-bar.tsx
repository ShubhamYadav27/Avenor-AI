"use client";

import { RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function TopBar({ title, subtitle, action }: Props) {
  return (
    <div className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-6">
      <div>
        <h1 className="text-sm font-semibold text-slate-900">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
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
      className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-slate-300 hover:text-slate-800 disabled:opacity-50 transition-colors"
    >
      <RefreshCw className={cn("h-3 w-3", loading && "animate-spin")} />
      {label}
    </button>
  );
}
