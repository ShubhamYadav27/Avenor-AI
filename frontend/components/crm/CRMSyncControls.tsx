"use client";

import {
  Play, RefreshCw, RotateCcw, Download, Sliders, CheckCircle2, Layers,
  AlertCircle, Loader2,
} from "lucide-react";
import {
  useCrmSyncActive,
  useCrmSyncProvider,
  useRefreshCrmStatus,
  useCrmConnections,
} from "@/hooks/use-api";
import { getErrorMessage } from "@/lib/api-client";

// ── Download Logs ─────────────────────────────────────────────

/**
 * Generates a real audit-log text file from connection data returned by the
 * backend. Every line is derived from actual CrmConnection records; no fake
 * content is included.
 */
function buildLogContent(connections: { provider: string; last_sync_at: string | null; is_active: boolean; sync_error: string | null; external_account_id: string | null }[]): string {
  const ts = new Date().toISOString();
  const lines: string[] = [
    `[${ts}] INFO  Avenor CRM Sync Audit Log — generated at ${ts}`,
    `[${ts}] INFO  Active connections: ${connections.filter((c) => c.is_active).length}`,
    "",
  ];

  for (const conn of connections) {
    const lastSync = conn.last_sync_at
      ? `Last sync: ${conn.last_sync_at}`
      : "Last sync: never";
    const status = conn.is_active ? "ACTIVE" : "INACTIVE";
    const error = conn.sync_error ? `ERROR: ${conn.sync_error}` : "No errors";
    lines.push(`[${ts}] INFO  Provider: ${conn.provider.toUpperCase().padEnd(12)} | ${status} | Account: ${conn.external_account_id ?? "—"} | ${lastSync} | ${error}`);
  }

  if (connections.length === 0) {
    lines.push(`[${ts}] WARN  No CRM connections found for this workspace.`);
  }

  lines.push("");
  lines.push(`[${ts}] INFO  Log export complete.`);
  return lines.join("\n");
}

// ── Component ──────────────────────────────────────────────────

interface CRMSyncControlsProps {
  /** Legacy HubSpot sync — kept for backward compat; the "Run Incremental Sync" button now uses the generic /crm/sync endpoint instead */
  onSyncNow: () => void;
  isSyncing: boolean;
}

export function CRMSyncControls({ isSyncing }: CRMSyncControlsProps) {
  // Generic hooks
  const syncActive = useCrmSyncActive();
  const syncProvider = useCrmSyncProvider();
  const refreshStatus = useRefreshCrmStatus();
  const { data: connectionsData } = useCrmConnections();

  // Unified loading state: either the legacy HubSpot sync or the generic sync
  const anySyncing = isSyncing || syncActive.isPending || syncProvider.isPending;

  // Last error / last success message from API mutations
  const lastError =
    (syncActive.isError ? getErrorMessage(syncActive.error) : null) ??
    (syncProvider.isError ? getErrorMessage(syncProvider.error) : null);

  const lastSuccess =
    syncActive.isSuccess || syncProvider.isSuccess;

  const handleHistoricalSync = () => {
    // Run incremental sync on the active provider (backend handles full backfill
    // when no prior sync state exists — this is the correct behaviour for the
    // generic sync engine).
    syncActive.mutate();
  };

  const handleIncrementalSync = () => {
    syncActive.mutate();
  };

  const handleRefreshStatus = () => {
    // Invalidate all CRM-related queries so cards and connections re-fetch
    refreshStatus();
  };

  const handleRetryFailedJobs = () => {
    // Re-trigger sync for each provider that has a recorded sync_error
    const failedConnections = (connectionsData?.connections ?? []).filter(
      (c) => c.is_active && c.sync_error
    );

    if (failedConnections.length === 0) {
      // No known failed connections — fall back to triggering the active sync
      syncActive.mutate();
    } else {
      // Retry each failing provider in sequence
      for (const conn of failedConnections) {
        syncProvider.mutate(conn.provider);
      }
    }
  };

  const handleDownloadLogs = () => {
    // Build real log from actual backend connection data
    const connections = (connectionsData?.connections ?? []).map((c) => ({
      provider: c.provider,
      last_sync_at: c.last_sync_at,
      is_active: c.is_active,
      sync_error: c.sync_error,
      external_account_id: c.external_account_id,
    }));

    const content = buildLogContent(connections);
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `avenor-crm-sync-audit-${Date.now()}.log`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sliders className="h-5 w-5 text-indigo-500" />
            Global Sync &amp; Control Plane
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Execute manual synchronization routines, trigger historical backfills, retry stalled jobs, and export audit logs.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Run Historical Sync → POST /crm/sync (full backfill when no prior state) */}
          <button
            id="btn-historical-sync"
            onClick={handleHistoricalSync}
            disabled={anySyncing}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-bold text-white hover:bg-indigo-500 disabled:opacity-50 transition-all cursor-pointer shadow-sm"
          >
            {syncActive.isPending ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Play className="h-3.5 w-3.5" />
            )}
            Run Historical Sync
          </button>

          {/* Run Incremental Sync → POST /crm/sync */}
          <button
            id="btn-incremental-sync"
            onClick={handleIncrementalSync}
            disabled={anySyncing}
            className="flex items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 py-2.5 text-xs font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-50 transition-all cursor-pointer"
          >
            <RefreshCw className={`h-3.5 w-3.5 text-indigo-400 ${anySyncing ? "animate-spin" : ""}`} />
            Run Incremental Sync
          </button>

          {/* Refresh Status → invalidates crm-connections, crm-providers, hubspot-status queries */}
          <button
            id="btn-refresh-status"
            onClick={handleRefreshStatus}
            className="flex items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3.5 py-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all cursor-pointer"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Refresh Status
          </button>

          {/* Retry Failed Jobs → POST /crm/{provider}/sync for each errored connection */}
          <button
            id="btn-retry-failed"
            onClick={handleRetryFailedJobs}
            disabled={anySyncing}
            className="flex items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3.5 py-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-50 transition-all cursor-pointer"
          >
            {syncProvider.isPending ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-400" />
            ) : (
              <Layers className="h-3.5 w-3.5" />
            )}
            Retry Failed Jobs
          </button>

          {/* Download Logs → generates real log file from backend connection data */}
          <button
            id="btn-download-logs"
            onClick={handleDownloadLogs}
            className="flex items-center gap-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3.5 py-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all cursor-pointer"
          >
            <Download className="h-3.5 w-3.5" />
            Download Logs
          </button>
        </div>
      </div>

      {/* Real API success feedback */}
      {lastSuccess && (
        <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3 flex items-center gap-2 text-xs font-semibold text-emerald-400">
          <CheckCircle2 className="h-4 w-4" />
          Sync dispatched successfully. CRM data is updating in the background.
        </div>
      )}

      {/* Real API error feedback */}
      {lastError && (
        <div className="mt-4 rounded-xl border border-red-500/20 bg-red-500/10 p-3 flex items-center gap-2 text-xs font-semibold text-red-400">
          <AlertCircle className="h-4 w-4" />
          Sync error: {lastError}
        </div>
      )}
    </div>
  );
}
