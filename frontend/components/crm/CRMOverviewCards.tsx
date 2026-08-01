"use client";

import { Link2, Building2, Users, DollarSign, Clock, Cpu, Loader2 } from "lucide-react";
import type { HubSpotStatus } from "@/types/api";
import { useCrmConnections, useCompanyStats, useCrmAnalytics } from "@/hooks/use-api";

interface CRMOverviewCardsProps {
  hubspotStatus?: HubSpotStatus;
}

function formatLastSync(isoString: string | null | undefined): string {
  if (!isoString) return "Never";
  const diffMs = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diffMs / 60_000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins} min${mins !== 1 ? "s" : ""} ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hr${hrs !== 1 ? "s" : ""} ago`;
  return `${Math.floor(hrs / 24)} day(s) ago`;
}

export function CRMOverviewCards({ hubspotStatus }: CRMOverviewCardsProps) {
  const { data: connectionsData, isLoading: connectionsLoading } = useCrmConnections();
  const { data: statsData, isLoading: statsLoading } = useCompanyStats();
  const { data: analyticsData } = useCrmAnalytics();

  const activeConnections = (connectionsData?.connections ?? []).filter((c) => c.is_active);
  const connectedCount = activeConnections.length;

  const latestSyncAt = activeConnections.reduce<string | null>((latest, conn) => {
    if (!conn.last_sync_at) return latest;
    if (!latest) return conn.last_sync_at;
    return new Date(conn.last_sync_at) > new Date(latest) ? conn.last_sync_at : latest;
  }, null);

  const lastSyncLabel = formatLastSync(latestSyncAt);

  const totalDealsSynced = analyticsData?.summary?.total_opportunities ?? 0;
  const totalCompaniesCount = statsData?.total ?? 0;

  const stats = [
    {
      title: "Connected Providers",
      value: connectionsLoading ? "…" : `${connectedCount} / 4`,
      subtitle: "HubSpot, Salesforce, Dynamics, Zoho",
      badge: connectedCount > 0 ? "Operational" : "No CRM Connected",
      badgeColor: connectedCount > 0
        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
        : "bg-slate-800 text-slate-400 border-slate-700",
      icon: Link2,
      iconBg: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
      loading: connectionsLoading,
    },
    {
      title: "Total Companies",
      value: statsLoading ? "…" : (totalCompaniesCount > 0 ? totalCompaniesCount.toLocaleString() : "0"),
      subtitle: "Synced from active CRMs",
      badge: totalCompaniesCount > 0 ? "Canonical Match" : "Empty",
      badgeColor: totalCompaniesCount > 0 ? "bg-sky-500/10 text-sky-400 border-sky-500/20" : "bg-slate-800 text-slate-400 border-slate-700",
      icon: Building2,
      iconBg: "bg-sky-500/10 text-sky-400 border-sky-500/20",
      loading: statsLoading,
    },
    {
      title: "Active Monitored",
      value: statsLoading ? "…" : (statsData?.by_status?.active ?? 0).toLocaleString(),
      subtitle: "Accounts in active pipeline",
      badge: (statsData?.by_status?.active ?? 0) > 0 ? "Enriched" : "Empty",
      badgeColor: (statsData?.by_status?.active ?? 0) > 0 ? "bg-purple-500/10 text-purple-400 border-purple-500/20" : "bg-slate-800 text-slate-400 border-slate-700",
      icon: Users,
      iconBg: "bg-purple-500/10 text-purple-400 border-purple-500/20",
      loading: statsLoading,
    },
    {
      title: "Synced Deals",
      value: totalDealsSynced > 0 ? totalDealsSynced.toLocaleString() : "0",
      subtitle: "Closed-won & Closed-lost",
      badge: totalDealsSynced > 0 ? "Synced to AI Engine" : "No Deals",
      badgeColor: totalDealsSynced > 0 ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-slate-800 text-slate-400 border-slate-700",
      icon: DollarSign,
      iconBg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      loading: false,
    },
    {
      title: "Last Successful Sync",
      value: connectionsLoading ? "…" : lastSyncLabel,
      subtitle: "Background sync scheduler",
      badge: connectedCount > 0 ? "Active Scheduler" : "No Connections",
      badgeColor: connectedCount > 0
        ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
        : "bg-slate-800 text-slate-400 border-slate-700",
      icon: Clock,
      iconBg: "bg-amber-500/10 text-amber-400 border-amber-500/20",
      loading: connectionsLoading,
    },
    {
      title: "AI Learning Status",
      value: connectedCount > 0 ? "Active Model" : "Standby",
      subtitle: "Signals recalibrated periodically",
      badge: connectedCount > 0 ? "Online" : "Offline",
      badgeColor: connectedCount > 0 ? "bg-indigo-500/10 text-indigo-400 border-indigo-500/20" : "bg-slate-800 text-slate-400 border-slate-700",
      icon: Cpu,
      iconBg: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
      loading: false,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3.5">
      {stats.map((item) => {
        const Icon = item.icon;
        return (
          <div
            key={item.title}
            className="flex flex-col justify-between p-4 glass-card glass-card-hover"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className={`p-2 rounded-xl border ${item.iconBg}`}>
                  <Icon className="h-4 w-4" />
                </span>
                <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold ${item.badgeColor}`}>
                  {item.badge}
                </span>
              </div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">{item.title}</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white mt-1 tracking-tight flex items-center gap-1.5">
                {item.loading ? <Loader2 className="h-4 w-4 animate-spin text-slate-400" /> : item.value}
              </p>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 border-t border-slate-100 dark:border-slate-800/60 pt-2">
              {item.subtitle}
            </p>
          </div>
        );
      })}
    </div>
  );
}
