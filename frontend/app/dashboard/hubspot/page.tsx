"use client";

import { useState } from "react";
import { Link2, CheckCircle2, XCircle, RefreshCw, Clock, AlertTriangle } from "lucide-react";
import {
  useHubSpotStatus,
  useHubSpotConnect,
  useTriggerHubSpotSync,
  useDisconnectHubSpot,
} from "@/hooks/use-api";
import { TopBar } from "@/components/layout/top-bar";
import { Skeleton } from "@/components/ui/skeleton";
import { timeAgo } from "@/lib/utils";
import type { SyncStateItem } from "@/types/api";

const OBJECT_TYPE_LABELS: Record<string, string> = {
  company: "Companies",
  contact: "Contacts",
  deal: "Deals",
  owner: "Owners",
};

function SyncStateRow({ state }: { state: SyncStateItem }) {
  const isOk = state.status === "completed";
  const isFailed = state.status === "failed";
  const isRunning = state.status === "running";

  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-100 last:border-0">
      <div className="flex items-center gap-3">
        {isOk && <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />}
        {isFailed && <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />}
        {isRunning && <RefreshCw className="h-4 w-4 text-blue-500 animate-spin flex-shrink-0" />}
        {!isOk && !isFailed && !isRunning && (
          <Clock className="h-4 w-4 text-slate-400 flex-shrink-0" />
        )}
        <div>
          <p className="text-sm font-medium text-slate-800">
            {OBJECT_TYPE_LABELS[state.object_type] ?? state.object_type}
          </p>
          {state.last_run_error && (
            <p className="text-xs text-red-600 mt-0.5">{state.last_run_error}</p>
          )}
          {state.historical_import_completed && (
            <p className="text-xs text-green-600 mt-0.5">
              Historical import: {state.historical_deals_imported} deals
            </p>
          )}
        </div>
      </div>
      <div className="text-right">
        <div className="flex items-center gap-3 text-xs text-slate-500">
          {state.last_run_created > 0 && (
            <span className="text-green-700">+{state.last_run_created}</span>
          )}
          {state.last_run_updated > 0 && (
            <span className="text-blue-700">~{state.last_run_updated}</span>
          )}
          <span>{state.total_synced} total</span>
        </div>
        <p className="mt-0.5 text-xs text-slate-400">
          {state.last_synced_at ? timeAgo(state.last_synced_at) : "Never synced"}
        </p>
      </div>
    </div>
  );
}

export default function HubSpotPage() {
  const { data: status, isLoading } = useHubSpotStatus();
  const connect = useHubSpotConnect();
  const syncNow = useTriggerHubSpotSync();
  const disconnect = useDisconnectHubSpot();
  const [confirmDisconnect, setConfirmDisconnect] = useState(false);

  if (isLoading) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar title="HubSpot CRM" subtitle="Sync your CRM data into Avenor" />
        <div className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-2xl space-y-4">
            <Skeleton className="h-40 rounded-xl" />
            <Skeleton className="h-48 rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  const isConnected = status?.connected;

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <TopBar
        title="HubSpot CRM"
        subtitle="Connect your CRM to capture deal outcomes and improve predictions"
        action={
          isConnected ? (
            <button
              onClick={() => { syncNow.mutate(); }}
              disabled={syncNow.isPending}
              className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-slate-300 disabled:opacity-50 transition-colors"
            >
              <RefreshCw className={`h-3 w-3 ${syncNow.isPending ? "animate-spin" : ""}`} />
              Sync now
            </button>
          ) : null
        }
      />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-2xl space-y-4">

          {/* Connection status card */}
          <div className={`rounded-xl border p-5 ${
            isConnected
              ? "border-green-200 bg-green-50"
              : "border-slate-200 bg-white"
          }`}>
            <div className="flex items-start gap-4">
              <div className={`rounded-xl p-3 ${isConnected ? "bg-green-100" : "bg-slate-100"}`}>
                <Link2 className={`h-6 w-6 ${isConnected ? "text-green-600" : "text-slate-400"}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-semibold text-slate-900">
                    {isConnected ? "HubSpot connected" : "Connect HubSpot"}
                  </h2>
                  {isConnected && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                      <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                      Active
                    </span>
                  )}
                </div>

                {isConnected ? (
                  <div className="mt-1 space-y-0.5 text-xs text-slate-600">
                    {status.hub_domain && <p>Portal: <span className="font-medium">{status.hub_domain}</span></p>}
                    {status.hub_id && <p>Hub ID: {status.hub_id}</p>}
                    {status.last_sync_at && (
                      <p>Last synced: {timeAgo(status.last_sync_at)}</p>
                    )}
                    <p>Deals synced: <span className="font-medium">{status.deals_synced ?? 0}</span></p>
                    {status.sync_error && (
                      <p className="flex items-center gap-1 text-red-600 mt-1">
                        <AlertTriangle className="h-3 w-3" />
                        {status.sync_error}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="mt-1 text-xs text-slate-500 max-w-sm">
                    Connect your HubSpot account to automatically import deal outcomes.
                    Closed-won and closed-lost deals feed into Avenor&apos;s prediction model.
                  </p>
                )}
              </div>

              {!isConnected && (
                <button
                  onClick={() => connect.mutate()}
                  disabled={connect.isPending}
                  className="flex-shrink-0 rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white hover:bg-orange-600 disabled:opacity-60 transition-colors"
                >
                  {connect.isPending ? "Connecting…" : "Connect HubSpot"}
                </button>
              )}
            </div>

            {/* Disconnect */}
            {isConnected && (
              <div className="mt-4 border-t border-green-200 pt-3">
                {!confirmDisconnect ? (
                  <button
                    onClick={() => setConfirmDisconnect(true)}
                    className="text-xs text-slate-400 hover:text-red-500 transition-colors"
                  >
                    Disconnect HubSpot
                  </button>
                ) : (
                  <div className="flex items-center gap-3">
                    <p className="text-xs text-slate-600">Disconnect and stop syncing?</p>
                    <button
                      onClick={() => { disconnect.mutate(); setConfirmDisconnect(false); }}
                      className="rounded px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                    >
                      Yes, disconnect
                    </button>
                    <button
                      onClick={() => setConfirmDisconnect(false)}
                      className="rounded px-2 py-1 text-xs text-slate-500 hover:bg-slate-100"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sync state details */}
          {isConnected && status.sync_states && status.sync_states.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h3 className="mb-1 text-sm font-semibold text-slate-800">Sync status</h3>
              <p className="mb-4 text-xs text-slate-500">
                Per-object sync state. Green = last run successful.
              </p>
              <div>
                {status.sync_states.map((s) => (
                  <SyncStateRow key={s.object_type} state={s} />
                ))}
              </div>
            </div>
          )}

          {/* How it works */}
          {!isConnected && (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h3 className="mb-3 text-sm font-semibold text-slate-800">How it works</h3>
              <ol className="space-y-3">
                {[
                  { n: "1", text: "Connect your HubSpot account with one click — read-only access to deals, companies, and contacts." },
                  { n: "2", text: "Avenor imports the past 180 days of deal history to bootstrap the prediction model." },
                  { n: "3", text: "Deal stage changes sync automatically every 30 minutes. Closed-won and closed-lost deals are instantly logged as outcomes." },
                  { n: "4", text: "The model recalibrates weekly using outcome data, improving which signals it weights most for your ICP." },
                ].map(({ n, text }) => (
                  <li key={n} className="flex gap-3 text-sm text-slate-600">
                    <span className="flex-shrink-0 flex h-5 w-5 items-center justify-center rounded-full bg-violet-100 text-xs font-bold text-violet-700 mt-0.5">
                      {n}
                    </span>
                    {text}
                  </li>
                ))}
              </ol>
              <div className="mt-4 rounded-lg bg-slate-50 border border-slate-200 px-3 py-2">
                <p className="text-xs text-slate-500">
                  <span className="font-medium">Required HubSpot scopes:</span>{" "}
                  crm.objects.deals.read · crm.objects.companies.read · crm.objects.contacts.read · oauth
                </p>
              </div>
            </div>
          )}

          {/* Sync success notice */}
          {syncNow.isSuccess && (
            <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600 flex-shrink-0" />
              <p className="text-sm text-green-700">Sync queued. Results will appear within a minute.</p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
