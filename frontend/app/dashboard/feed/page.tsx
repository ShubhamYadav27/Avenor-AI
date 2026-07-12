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
  { label: "All", value: "all", icon: Zap },
  { label: "Hot", value: "hot", icon: Flame },
  { label: "Warm", value: "warm", icon: TrendingUp },
  { label: "Watch", value: "watch", icon: Eye },
  { label: "Cold", value: "cold", icon: Snowflake },
];

export default function FeedPage() {
  const [activeWindow, setActiveWindow] = useState<BuyingWindow | "all">("all");
  const refresh = useRefreshFeed();

  const { data, isLoading, isError } = useFeed({
    buying_window: activeWindow === "all" ? undefined : activeWindow,
    limit: 30,
  });

  const summary = data?.buying_window_summary;

  function getCounts(w: BuyingWindow | "all"): number | undefined {
    if (!summary) return undefined;
    if (w === "all") return Object.values(summary).reduce((a, b) => a + b, 0);
    return summary[w as BuyingWindow];
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <TopBar
        title="Account Intelligence Feed"
        subtitle="Accounts showing active buying signals, ranked by probability"
        action={
          <button
            onClick={() => refresh.mutate()}
            disabled={refresh.isPending}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-slate-300 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-3 w-3 ${refresh.isPending ? "animate-spin" : ""}`} />
            Refresh feed
          </button>
        }
      />

      {/* Buying window filter tabs */}
      <div className="border-b border-slate-200 bg-white px-6">
        <div className="flex gap-1 -mb-px overflow-x-auto">
          {WINDOW_FILTERS.map(({ label, value, icon: Icon }) => {
            const count = getCounts(value);
            const active = activeWindow === value;
            return (
              <button
                key={value}
                onClick={() => setActiveWindow(value)}
                className={`flex items-center gap-1.5 whitespace-nowrap border-b-2 px-4 py-3 text-xs font-medium transition-colors ${
                  active
                    ? "border-violet-600 text-violet-700"
                    : "border-transparent text-slate-500 hover:text-slate-700"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {label}
                {count !== undefined && count > 0 && (
                  <span className={`rounded-full px-1.5 py-0.5 text-xs ${active ? "bg-violet-100 text-violet-700" : "bg-slate-100 text-slate-500"}`}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Feed content */}
      <div className="flex-1 overflow-y-auto px-6 py-5">
        {isLoading && <FeedSkeleton />}

        {isError && (
          <EmptyState
            icon={Zap}
            title="Failed to load feed"
            description="Check that the backend is running at the configured API URL."
          />
        )}

        {!isLoading && !isError && data?.items.length === 0 && (
          <EmptyState
            icon={Zap}
            title="No accounts in this window"
            description={
              activeWindow === "all"
                ? "Run a pipeline cycle to populate the feed with scored accounts."
                : `No accounts currently in the "${activeWindow}" buying window.`
            }
          />
        )}

        {!isLoading && !isError && data && data.items.length > 0 && (
          <div className="space-y-3 max-w-3xl">
            <p className="text-xs text-slate-400">
              {data.total} account{data.total !== 1 ? "s" : ""} found
            </p>
            {data.items.map((item) => (
              <FeedCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
