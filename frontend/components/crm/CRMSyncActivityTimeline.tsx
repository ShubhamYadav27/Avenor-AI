"use client";

import { Clock, CheckCircle2, AlertCircle, Database, Layers, RefreshCw } from "lucide-react";
import { useCrmSyncStatus, useCrmConnections } from "@/hooks/use-api";

export function CRMSyncActivityTimeline() {
  const { data: syncStatus, isLoading } = useCrmSyncStatus();
  const { data: connectionsData } = useCrmConnections();

  const activeConnections = (connectionsData?.connections ?? []).filter((c) => c.is_active);
  const isConnected = activeConnections.length > 0;
  const objects = syncStatus?.objects ?? {};

  const objectKeys = Object.keys(objects);
  const hasObjects = objectKeys.length > 0;

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Clock className="h-5 w-5 text-indigo-500" />
            Recent Sync Activity
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Real-time audit log of synchronization events for connected CRM providers.
          </p>
        </div>
        <span className="text-xs font-semibold text-slate-400">
          {isConnected ? `${activeConnections.length} Provider Active` : "Disconnected"}
        </span>
      </div>

      {!isConnected ? (
        <div className="rounded-xl border border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-950/40 p-6 text-center">
          <Database className="h-8 w-8 text-slate-400 mx-auto mb-2 opacity-50" />
          <p className="text-xs font-bold text-slate-700 dark:text-slate-300">No CRM connected</p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
            Connect Salesforce to begin synchronizing accounts and opportunities.
          </p>
        </div>
      ) : !hasObjects ? (
        <div className="rounded-xl border border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-950/40 p-6 text-center">
          <RefreshCw className="h-6 w-6 text-indigo-400 animate-spin mx-auto mb-2" />
          <p className="text-xs font-bold text-slate-700 dark:text-slate-300">Sync in progress</p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
            Fetching records from connected CRM provider…
          </p>
        </div>
      ) : (
        <div className="relative pl-4 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
          {objectKeys.map((key) => {
            const item = objects[key];
            const isOk = item.last_run_status === "completed";
            const lastTime = item.last_synced_at || item.last_run_at;
            const formattedTime = lastTime ? new Date(lastTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Just now";

            return (
              <div key={key} className="relative flex items-start gap-3 group">
                <div className="absolute -left-4 top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 border border-slate-700 shadow-sm">
                  <span className={`h-1.5 w-1.5 rounded-full ${isOk ? "bg-emerald-400" : "bg-red-400"}`} />
                </div>

                <div className="flex-1 rounded-xl border border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-950/40 p-3.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {isOk ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-400" />
                      )}
                      <p className="text-xs font-bold text-slate-900 dark:text-white capitalize">
                        {key} Synchronization
                      </p>
                      <span className="rounded-full border border-indigo-500/20 bg-indigo-500/10 px-2 py-0.5 text-[10px] font-bold text-indigo-400">
                        {syncStatus?.provider?.toUpperCase() ?? "CRM"}
                      </span>
                    </div>
                    <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                      {formattedTime}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    {(item.current_sync_records ?? item.total_synced).toLocaleString()} total {key}s synced into PostgreSQL database.
                    {item.last_run_created > 0 && ` ${item.last_run_created} created.`}
                    {item.last_run_updated > 0 && ` ${item.last_run_updated} updated.`}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
