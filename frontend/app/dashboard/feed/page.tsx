"use client";

import { useState } from "react";
import { Zap, RefreshCw, Flame, TrendingUp, Eye, Snowflake } from "lucide-react";
import { useFeed, useRefreshFeed } from "@/hooks/use-api";
import { FeedCard } from "@/components/feed/feed-card";
import { FeedSkeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { TopBar } from "@/components/layout/top-bar";
import type { BuyingWindow } from "@/types/api";

const WINDOW_FILTERS: Array<{ label: string; value: BuyingWindow | "all"; icon: React.ElementType; count?: number }> = [
  { label: "All Accounts", value: "all", icon: Zap },
  { label: "Hot Window", value: "hot", icon: Flame },
  { label: "Warm Intent", value: "warm", icon: TrendingUp },
  { label: "Evaluating", value: "watch", icon: Eye },
  { label: "Monitoring", value: "cold", icon: Snowflake },
];

export default function FeedPage() {
  const [activeWindow, setActiveWindow] = useState<BuyingWindow | "all">("all");
  const refresh = useRefreshFeed();

  const { data, isLoading, isError } = useFeed({
    buying_window: activeWindow === "all" ? undefined : activeWindow,
    limit: 500,
  });


  const summary = data?.buying_window_summary;

  function getCounts(w: BuyingWindow | "all"): number | undefined {
    if (!summary) return undefined;
    if (w === "all") return Object.values(summary).reduce((a, b) => a + b, 0);
    return summary[w as BuyingWindow];
  }

  return (
    <div className="flex flex-1 flex-col w-full min-h-0 bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
      <TopBar
        title="Account Intelligence Feed"
        subtitle="Accounts showing active buying signals, ranked by predictive opportunity score"
        action={
          <button
            onClick={() => refresh.mutate()}
            disabled={refresh.isPending}
            className="flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all shadow-2xs disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw className={`h-3 w-3 text-indigo-600 dark:text-indigo-400 ${refresh.isPending ? "animate-spin" : ""}`} />
            Refresh Feed
          </button>
        }
      />

      {/* Buying window filter tabs */}
      <div className="border-b border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 px-6 transition-colors">
        <div className="flex gap-2 -mb-px overflow-x-auto">
          {WINDOW_FILTERS.map(({ label, value, icon: Icon }) => {
            const count = getCounts(value);
            const active = activeWindow === value;
            return (
              <button
                key={value}
                onClick={() => setActiveWindow(value)}
                className={`flex items-center gap-2 whitespace-nowrap border-b-2 px-4 py-3 text-xs font-bold transition-all cursor-pointer ${
                  active
                    ? "border-indigo-600 dark:border-indigo-500 text-indigo-600 dark:text-indigo-400"
                    : "border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-300"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {label}
                {count !== undefined && count > 0 && (
                  <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${active ? "bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400" : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"}`}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Feed content */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {isLoading && <FeedSkeleton />}

        {isError && (
          <EmptyState
            icon={Zap}
            title="Failed to load account feed"
            description="Check that the backend service is running at the configured API URL."
          />
        )}

        {!isLoading && !isError && data?.items.length === 0 && (
          <EmptyState
            icon={Zap}
            title="No accounts in this buying window"
            description={
              activeWindow === "all"
                ? "Run a signal pipeline cycle to populate the feed with scored accounts."
                : `No accounts currently in the "${activeWindow}" buying window.`
            }
          />
        )}

        {!isLoading && !isError && data && data.items.length > 0 && (
          <div className="space-y-4 max-w-4xl">
            <div className="flex items-center justify-between">
              <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                {data.total} account{data.total !== 1 ? "s" : ""} in intent window
              </p>
            </div>
            {data.items.map((item) => (
              <FeedCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
