"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import {
  useHubSpotStatus,
  useHubSpotConnect,
  useTriggerHubSpotSync,
  useDisconnectHubSpot,
  useCrmSyncActive,
  useRefreshCrmStatus,
  useCrmSyncStatus,
} from "@/hooks/use-api";
import { timeAgo } from "@/lib/utils";
import { TopBar } from "@/components/layout/top-bar";
import { Skeleton } from "@/components/ui/skeleton";
import { CRMOverviewCards } from "@/components/crm/CRMOverviewCards";
import { CRMProviderCards } from "@/components/crm/CRMProviderCards";
import { CRMHealthDashboard } from "@/components/crm/CRMHealthDashboard";
import { CRMSyncActivityTimeline } from "@/components/crm/CRMSyncActivityTimeline";
import { CRMAILearningDashboard } from "@/components/crm/CRMAILearningDashboard";
import { CRMProviderConfiguration } from "@/components/crm/CRMProviderConfiguration";
import { CRMSyncControls } from "@/components/crm/CRMSyncControls";
import { RefreshCw, CheckCircle2, AlertCircle, Database, Loader2 } from "lucide-react";
import { getErrorMessage } from "@/lib/api-client";

export default function CRMIntegrationsPage() {
  const searchParams = useSearchParams();
  const connectedProvider = searchParams.get("provider");
  const isConnectedSuccess = searchParams.get("status") === "connected";

  const refreshStatus = useRefreshCrmStatus();

  // Legacy HubSpot-specific hooks (kept for backward compat with HubSpot provider card)
  const { data: status, isLoading } = useHubSpotStatus();
  const connect = useHubSpotConnect();
  const hubspotSync = useTriggerHubSpotSync();
  const disconnect = useDisconnectHubSpot();

  // Generic CRM sync — used by "Sync All Providers" button and CRMSyncControls
  const syncActive = useCrmSyncActive();

  // Real-time sync status — polls /crm/sync/status every 8s when connected
  const { data: syncStatus } = useCrmSyncStatus();
  const isConnected = syncStatus?.connected ?? false;

  // Re-fetch connections immediately when arriving via OAuth redirect
  useEffect(() => {
    if (isConnectedSuccess) {
      refreshStatus();
    }
  }, [isConnectedSuccess, refreshStatus]);

  // "Sync All Providers" button triggers the generic /crm/sync endpoint
  const handleSyncAll = () => syncActive.mutate();
  const isSyncingAll = syncActive.isPending;

  if (isLoading) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
        <TopBar
          title="CRM Integrations"
          subtitle="Connect your CRM platforms to continuously train Avenor's Predictive Revenue Intelligence Engine."
        />
        <div className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-7xl space-y-6">
            <Skeleton className="h-28 rounded-2xl" />
            <Skeleton className="h-64 rounded-2xl" />
            <Skeleton className="h-48 rounded-2xl" />
          </div>
        </div>
      </div>
    );
  }

  // Derive sync totals from the status endpoint
  const objectNames = ["account", "contact", "lead", "opportunity", "user"] as const;
  const totalSynced = syncStatus?.objects
    ? objectNames.reduce((sum, k) => sum + (syncStatus.objects[k]?.current_sync_records ?? syncStatus.objects[k]?.total_synced ?? 0), 0)
    : 0;
  const lastSyncAt = syncStatus?.last_sync_at;
  const hasSyncedOnce = !!lastSyncAt;
  const hasAnySyncError = !!syncStatus?.sync_error;

  return (
    <div className="flex flex-1 flex-col w-full min-h-0 bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
      {/* Top Header */}
      <TopBar
        title="CRM Integrations"
        subtitle="Connect your CRM platforms to continuously train Avenor's Predictive Revenue Intelligence Engine."
        action={
          <button
            id="btn-sync-all-providers"
            onClick={handleSyncAll}
            disabled={isSyncingAll}
            className="flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-50 transition-all shadow-xs cursor-pointer"
          >
            <RefreshCw className={`h-3.5 w-3.5 text-indigo-500 ${isSyncingAll ? "animate-spin" : ""}`} />
            {isSyncingAll ? "Syncing…" : "Force Sync"}
          </button>
        }
      />

      {/* Dashboard Body */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-7xl space-y-6">

          {/* OAuth Success Banner — shown after OAuth callback redirect */}
          {isConnectedSuccess && (
            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                {connectedProvider
                  ? `${connectedProvider.toUpperCase()} connected! Salesforce sync starting automatically in the background.`
                  : "CRM provider connected! Full sync starting automatically."}
              </div>
              <div className="flex items-center gap-1.5 text-[11px] text-emerald-300/80 font-normal">
                <Loader2 className="h-3 w-3 animate-spin" />
                Importing your data…
              </div>
            </div>
          )}

          {/* Sync Progress Banner — shows live sync state from /crm/sync/status */}
          {isConnected && hasSyncedOnce && (
            <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-4 py-3">
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-3">
                  <Database className="h-4 w-4 text-indigo-500 shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-slate-800 dark:text-slate-100">
                      {totalSynced.toLocaleString()} records synced from {syncStatus?.provider ?? "CRM"}
                    </p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                      Last sync: {lastSyncAt ? timeAgo(lastSyncAt) : "—"}
                      {hasAnySyncError && (
                        <span className="ml-2 text-red-400 font-medium">
                          · Sync error: {syncStatus?.sync_error}
                        </span>
                      )}
                    </p>
                  </div>
                </div>
                {/* Per-object breakdown chips */}
                <div className="flex flex-wrap gap-2">
                  {objectNames.map((obj) => {
                    const state = syncStatus?.objects?.[obj];
                    if (!state) return null;
                    const isOk = state.last_run_status === "completed";
                    return (
                      <span
                        key={obj}
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                          isOk
                            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500"
                            : "bg-amber-500/10 border-amber-500/20 text-amber-500"
                        }`}
                      >
                        <span className="capitalize">{obj}s</span>
                        <span className="opacity-75">·</span>
                        <span>{(state.current_sync_records ?? state.total_synced ?? 0).toLocaleString()}</span>
                      </span>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* API Success Banner — real response from /crm/sync */}
          {syncActive.isSuccess && (
            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 flex items-center gap-2 text-xs font-bold text-emerald-400">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
              Force sync completed. Account reconciliation &amp; intelligence feed updating in background.
            </div>
          )}

          {/* API Error Banner — real error from /crm/sync */}
          {syncActive.isError && (
            <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 flex items-center gap-2 text-xs font-bold text-red-400">
              <AlertCircle className="h-4 w-4 text-red-400 shrink-0" />
              Sync failed: {getErrorMessage(syncActive.error)}
            </div>
          )}

          {/* Section 1: Integration Overview — live data from /crm/connections */}
          <CRMOverviewCards hubspotStatus={status} />

          {/* Section 2: CRM Provider Cards — live data from /crm/connections + /crm/providers */}
          <CRMProviderCards
            hubspotStatus={status}
            onConnectHubSpot={() => connect.mutate()}
            onSyncHubSpot={() => hubspotSync.mutate()}
            onDisconnectHubSpot={() => disconnect.mutate()}
            isConnectingHubSpot={connect.isPending}
            isSyncingHubSpot={hubspotSync.isPending}
          />

          {/* Section 3: Integration Health Dashboard */}
          <CRMHealthDashboard />

          {/* Section 4 & 5: Activity Timeline & AI Learning Dashboard */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CRMSyncActivityTimeline />
            <div className="space-y-6">
              <CRMAILearningDashboard />
              <CRMProviderConfiguration />
            </div>
          </div>

          {/* Section 7: Sync Controls — all buttons wired to real API */}
          <CRMSyncControls
            onSyncNow={() => hubspotSync.mutate()}
            isSyncing={hubspotSync.isPending}
          />

        </div>
      </div>
    </div>
  );
}
