"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Building2 } from "lucide-react";
import { useCompanies, useCompanyStats } from "@/hooks/use-api";
import { ScoreRing } from "@/components/ui/score-ring";
import { BuyingWindowBadge } from "@/components/ui/buying-window-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { FeedSkeleton } from "@/components/ui/skeleton";
import { formatDate } from "@/lib/utils";
import { TopBar } from "@/components/layout/top-bar";

const STATUS_TABS = [
  { label: "All Accounts", value: undefined },
  { label: "Hot Window", value: "hot" },
  { label: "Warm Intent", value: "warm" },
  { label: "Evaluating", value: "evaluating" },
  { label: "Monitoring", value: "monitoring" },
];

export default function CompaniesPage() {
  const router = useRouter();
  const [windowFilter, setWindowFilter] = useState<string | undefined>(undefined);
  const [search, setSearch] = useState("");
  const { data: statsData } = useCompanyStats();
  const { data, isLoading, isError } = useCompanies(windowFilter ? { buying_window: windowFilter, limit: 500 } : { limit: 500 });

  const filtered = data?.companies.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    (c.domain ?? "").toLowerCase().includes(search.toLowerCase())
  ) ?? [];

  return (
    <div className="flex flex-1 flex-col w-full min-h-0 bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
      <TopBar title="Companies" subtitle="Monitored enterprise accounts ranked by AI predictive signal score" />

      {/* Stats strip */}
      {statsData && (
        <div className="flex gap-8 items-center border-b border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 px-6 py-4.5 mb-3 shadow-2xs transition-colors overflow-x-auto">
          {[
            { label: "Total Universe", value: statsData.total },
            { label: "Hot Window", value: statsData.active_by_window?.hot ?? 0, color: "text-emerald-700 dark:text-emerald-500" },
            { label: "Warm Intent", value: statsData.active_by_window?.warm ?? 0, color: "text-amber-700 dark:text-amber-500" },
            { label: "Evaluating", value: statsData.active_by_window?.evaluating ?? 0, color: "text-sky-700 dark:text-sky-500" },
            { label: "Monitoring", value: statsData.active_by_window?.monitoring ?? 0, color: "text-slate-500" },
          ].map(({ label, value, color }) => (
            <div key={label} className="shrink-0 flex flex-col justify-center gap-1">
              <p className={`text-lg font-black tracking-tight leading-none ${color ?? "text-slate-900 dark:text-white"}`}>{value}</p>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 whitespace-nowrap">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 px-6 py-3 transition-colors">
        <div className="flex gap-1.5 flex-wrap">
          {STATUS_TABS.map(({ label, value }) => (
            <button
              key={label}
              onClick={() => setWindowFilter(value)}
              className={`rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all cursor-pointer ${
                windowFilter === value
                  ? "bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 font-bold border border-indigo-200/80 dark:border-indigo-500/30"
                  : "text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search accounts or domain…"
            className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-950 py-1.5 pl-9 pr-3.5 text-xs text-slate-900 dark:text-white outline-none focus:border-indigo-500 dark:focus:border-indigo-500 focus:bg-white dark:focus:bg-slate-900 shadow-2xs transition-colors"
          />
        </div>
      </div>

      <div className="flex-1 p-6 pb-20">
        {isLoading && <FeedSkeleton />}

        {isError && (
          <EmptyState
            icon={Building2}
            title="Failed to load companies"
            description="Check that the backend API is running."
          />
        )}

        {!isLoading && !isError && filtered.length === 0 && (
          <EmptyState
            icon={Building2}
            title="No companies found"
            description="Run a Salesforce sync to populate companies."
          />
        )}

        {!isLoading && filtered.length > 0 && (
          <div className="overflow-hidden rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 shadow-xs transition-colors">
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="border-b border-slate-200/80 dark:border-slate-800/80 bg-slate-50/80 dark:bg-slate-900/80 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider sticky top-0 transition-colors">
                    <th className="px-5 py-3.5 text-left">Company & AI Reason</th>
                    <th className="px-5 py-3.5 text-left">Industry</th>
                    <th className="px-5 py-3.5 text-center">Score</th>
                    <th className="px-5 py-3.5 text-center">Buying Window</th>
                    <th className="px-5 py-3.5 text-left">Last Scored</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {filtered.map((c) => (
                    <tr
                      key={c.id}
                      onClick={() => router.push(`/dashboard/companies/${c.id}`)}
                      className="cursor-pointer hover:bg-indigo-50/40 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      <td className="px-5 py-3.5">
                        <div className="space-y-0.5">
                          <div className="flex items-center gap-2">
                            <p className="font-bold text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">{c.name}</p>
                            {c.domain && <span className="text-xs text-slate-400 font-mono">({c.domain})</span>}
                          </div>
                          {(c as any).buying_window_reasoning && (
                            <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-snug line-clamp-2">
                              {(c as any).buying_window_reasoning}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-xs font-medium text-slate-600 dark:text-slate-300">{c.industry ?? "—"}</td>
                      <td className="px-5 py-3.5">
                        <div className="flex justify-center">
                          <ScoreRing score={c.composite_score} size={36} />
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex justify-center">
                          <BuyingWindowBadge window={c.buying_window} size="sm" />
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-xs text-slate-500 dark:text-slate-400 whitespace-nowrap">
                        {c.last_scored_at ? formatDate(c.last_scored_at) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="border-t border-slate-100 dark:border-slate-800 px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 bg-slate-50/50 dark:bg-slate-900/50 transition-colors">
              Showing {filtered.length} of {data?.total ?? 0} enterprise accounts
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
