"use client";

import { useState } from "react";
import {
  CheckCircle2, RefreshCw, Link2, ShieldCheck, Radio,
  AlertCircle, Loader2, XCircle,
} from "lucide-react";
import type { HubSpotStatus, CrmConnection } from "@/types/api";
import {
  useCrmConnections,
  useCrmProviders,
  useCrmStartOAuth,
  useCrmSyncProvider,
  useCrmDisconnect,
} from "@/hooks/use-api";

// ── Static provider metadata (branding only — no state) ────────────────────

interface ProviderMeta {
  id: string;
  name: string;
  category: string;
  logoBg: string;
  accentColor: string;
  logoSvg: React.ReactNode;
  defaultScopes: string[];
}

const PROVIDER_META: ProviderMeta[] = [
  {
    id: "hubspot",
    name: "HubSpot CRM",
    category: "Marketing & Sales",
    logoBg: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    accentColor: "from-orange-500 to-amber-600",
    logoSvg: (
      <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
        <path d="M18.8 8.6a3 3 0 0 0-2.8 2h-2.5a4.2 4.2 0 0 0-3.3-3.3V5.1a2.8 2.8 0 1 0-2 0v2.2a4.2 4.2 0 0 0-3.3 3.3H2.8a2.8 2.8 0 1 0 0 2h2.1a4.2 4.2 0 0 0 3.3 3.3v2.5a2.8 2.8 0 1 0 2 0v-2.5a4.2 4.2 0 0 0 3.3-3.3h2.5a3 3 0 1 0 2.8-3.4zM9.2 12a2.2 2.2 0 1 1 2.2-2.2A2.2 2.2 0 0 1 9.2 12z" />
      </svg>
    ),
    defaultScopes: ["crm.objects.deals.read", "crm.objects.companies.read", "crm.objects.contacts.read", "oauth"],
  },
  {
    id: "salesforce",
    name: "Salesforce CRM",
    category: "Enterprise Sales",
    logoBg: "bg-sky-500/10 text-sky-400 border-sky-500/20",
    accentColor: "from-sky-500 to-blue-600",
    logoSvg: (
      <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
        <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
      </svg>
    ),
    defaultScopes: ["api", "refresh_token", "offline_access", "web"],
  },
  {
    id: "dynamics",
    name: "Microsoft Dynamics 365",
    category: "Enterprise ERP & CRM",
    logoBg: "bg-teal-500/10 text-teal-400 border-teal-500/20",
    accentColor: "from-teal-500 to-emerald-600",
    logoSvg: (
      <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
      </svg>
    ),
    defaultScopes: ["user_impersonation", "offline_access"],
  },
  {
    id: "zoho",
    name: "Zoho CRM",
    category: "SMB & Growth CRM",
    logoBg: "bg-red-500/10 text-red-400 border-red-500/20",
    accentColor: "from-red-500 to-rose-600",
    logoSvg: (
      <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z" />
      </svg>
    ),
    defaultScopes: ["ZohoCRM.modules.ALL", "ZohoCRM.settings.ALL", "ZohoCRM.users.ALL"],
  },
];

// ── Helpers ────────────────────────────────────────────────────

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

// ── Component ──────────────────────────────────────────────────

interface CRMProviderCardsProps {
  /** Legacy HubSpot status — kept for backward compat; connection data from /crm/connections takes precedence */
  hubspotStatus?: HubSpotStatus;
  /** Legacy HubSpot OAuth start — used for HubSpot only (existing /integrations/hubspot/connect) */
  onConnectHubSpot: () => void;
  /** Legacy HubSpot sync trigger */
  onSyncHubSpot: () => void;
  /** Legacy HubSpot disconnect */
  onDisconnectHubSpot: () => void;
  isConnectingHubSpot: boolean;
  isSyncingHubSpot: boolean;
}

export function CRMProviderCards({
  hubspotStatus,
  onConnectHubSpot,
  onSyncHubSpot,
  onDisconnectHubSpot,
  isConnectingHubSpot,
  isSyncingHubSpot,
}: CRMProviderCardsProps) {
  const [activeTab, setActiveTab] = useState<Record<string, "overview" | "config">>({
    hubspot: "overview",
    salesforce: "overview",
    dynamics: "overview",
    zoho: "overview",
  });
  const [confirmDisconnect, setConfirmDisconnect] = useState<string | null>(null);

  // Generic CRM API hooks
  const { data: connectionsData, isLoading: connectionsLoading } = useCrmConnections();
  const { data: providersData } = useCrmProviders();
  const startOAuth = useCrmStartOAuth();
  const syncProvider = useCrmSyncProvider();
  const disconnectProvider = useCrmDisconnect();

  // Build a lookup map: provider id -> CrmConnection (most recent active)
  const connectionMap = new Map<string, CrmConnection>();
  (connectionsData?.connections ?? []).forEach((conn) => {
    if (conn.is_active) {
      connectionMap.set(conn.provider, conn);
    }
  });

  // Build a lookup map: provider id -> enabled flag from registry
  const providerEnabledMap = new Map<string, boolean>();
  (providersData?.providers ?? []).forEach((p) => {
    providerEnabledMap.set(p.name, p.enabled);
  });

  // Active connection count for header badge
  const activeCount = connectionMap.size > 0
    ? connectionMap.size
    : (hubspotStatus?.connected ? 1 : 0);

  const connectedBadgeBg = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
  const disconnectedBadgeBg = "bg-slate-800 text-slate-400 border-slate-700";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white">Connected CRM Platforms</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Real-time synchronization status across all enterprise CRM providers.
          </p>
        </div>
        <span className="rounded-full bg-indigo-500/10 border border-indigo-500/30 px-3 py-1 text-xs font-bold text-indigo-400 flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          {connectionsLoading ? "…" : `${activeCount} Provider${activeCount !== 1 ? "s" : ""} Active`}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-4">
        {PROVIDER_META.map((meta) => {
          const currentTab = activeTab[meta.id] ?? "overview";
          const conn = connectionMap.get(meta.id);

          // Resolve live data from backend connection record
          const isHubspot = meta.id === "hubspot";
          const connected: boolean = conn?.is_active
            ? true
            : isHubspot
            ? (hubspotStatus?.connected ?? false)
            : false;

          const externalId = conn?.external_account_name
            ?? conn?.external_account_id
            ?? (isHubspot && hubspotStatus?.hub_id ? `Hub ID: ${hubspotStatus.hub_id}` : null)
            ?? "—";

          const externalDomain = isHubspot
            ? (hubspotStatus?.hub_domain ?? "—")
            : (conn?.external_account_id ?? "—");

          const lastSyncAt = formatLastSync(
            conn?.last_sync_at ?? (isHubspot ? hubspotStatus?.last_sync_at : null)
          );

          const healthStatus: "Healthy" | "Degraded" | "Disconnected" = conn?.sync_error
            ? "Degraded"
            : connected
            ? "Healthy"
            : "Disconnected";

          const oauthStatus: "Authorized" | "Expired" | "Not Configured" = connected
            ? "Authorized"
            : "Not Configured";

          // Sync state per provider card
          const isThisProviderSyncing = isHubspot
            ? isSyncingHubSpot
            : syncProvider.isPending && syncProvider.variables === meta.id;

          const isThisProviderConnecting = isHubspot
            ? isConnectingHubSpot
            : startOAuth.isPending && startOAuth.variables === meta.id;

          const isThisProviderDisconnecting =
            disconnectProvider.isPending && disconnectProvider.variables === meta.id;

          // Error from last sync
          const syncError = conn?.sync_error ?? null;

          const badgeBg = connected ? connectedBadgeBg : disconnectedBadgeBg;

          return (
            <div
              key={meta.id}
              className="flex flex-col justify-between rounded-2xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-200"
            >
              {/* Header */}
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2.5 rounded-xl border ${meta.logoBg}`}>
                      {meta.logoSvg}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        {meta.name}
                      </h3>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">{meta.category}</p>
                    </div>
                  </div>

                  <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${badgeBg}`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${connected ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
                    {connected ? "Connected" : "Disconnected"}
                  </span>
                </div>

                {/* Tab selector */}
                <div className="flex items-center gap-2 mt-4 border-b border-slate-100 dark:border-slate-800 pb-2">
                  <button
                    onClick={() => setActiveTab((prev) => ({ ...prev, [meta.id]: "overview" }))}
                    className={`text-xs font-semibold px-2 py-1 rounded-md transition-all ${
                      currentTab === "overview"
                        ? "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white"
                        : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                    }`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab((prev) => ({ ...prev, [meta.id]: "config" }))}
                    className={`text-xs font-semibold px-2 py-1 rounded-md transition-all ${
                      currentTab === "config"
                        ? "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white"
                        : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                    }`}
                  >
                    Configuration
                  </button>
                </div>

                {/* Tab content: Overview */}
                {currentTab === "overview" && (
                  <div className="mt-3 space-y-2.5 text-xs">
                    {connectionsLoading ? (
                      <div className="flex items-center gap-2 text-slate-400 py-4 justify-center">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Loading connection data…</span>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                          <span>Account ID</span>
                          <span className="font-semibold text-slate-900 dark:text-slate-200 truncate max-w-[130px]">
                            {externalId}
                          </span>
                        </div>

                        <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                          <span>Health Status</span>
                          <span className={`flex items-center gap-1 font-semibold ${
                            healthStatus === "Healthy"
                              ? "text-emerald-600 dark:text-emerald-400"
                              : healthStatus === "Degraded"
                              ? "text-amber-600 dark:text-amber-400"
                              : "text-slate-500"
                          }`}>
                            {healthStatus === "Healthy" && <CheckCircle2 className="h-3.5 w-3.5" />}
                            {healthStatus === "Degraded" && <AlertCircle className="h-3.5 w-3.5" />}
                            {healthStatus === "Disconnected" && <XCircle className="h-3.5 w-3.5" />}
                            {healthStatus}
                          </span>
                        </div>

                        <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                          <span>OAuth Token</span>
                          <span className={`flex items-center gap-1 font-semibold ${
                            oauthStatus === "Authorized"
                              ? "text-sky-600 dark:text-sky-400"
                              : "text-slate-500"
                          }`}>
                            <ShieldCheck className="h-3.5 w-3.5" />
                            {oauthStatus}
                          </span>
                        </div>

                        <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                          <span>Webhook Pipeline</span>
                          <span className="flex items-center gap-1 font-semibold text-indigo-600 dark:text-indigo-400">
                            <Radio className="h-3.5 w-3.5" />
                            {connected ? "Active" : "Inactive"}
                          </span>
                        </div>

                        <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                          <span>Last Sync</span>
                          <span className="font-medium text-slate-500 dark:text-slate-400">{lastSyncAt}</span>
                        </div>

                        {syncError && (
                          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-2 text-[11px] text-red-400 flex items-start gap-1.5">
                            <AlertCircle className="h-3.5 w-3.5 shrink-0 mt-0.5" />
                            <span className="break-all">{syncError}</span>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}

                {/* Tab content: Configuration */}
                {currentTab === "config" && (
                  <div className="mt-3 space-y-2 text-xs">
                    <div className="rounded-lg bg-slate-50 dark:bg-slate-950/60 p-2.5 border border-slate-200/60 dark:border-slate-800/60">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">API Domain / Account</p>
                      <p className="font-mono text-[11px] text-slate-800 dark:text-slate-200 truncate">
                        {externalDomain}
                      </p>
                    </div>

                    <div className="rounded-lg bg-slate-50 dark:bg-slate-950/60 p-2.5 border border-slate-200/60 dark:border-slate-800/60">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Connection ID</p>
                      <p className="font-mono text-[11px] text-slate-800 dark:text-slate-200 truncate">
                        {conn?.id ?? "—"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-slate-50 dark:bg-slate-950/60 p-2.5 border border-slate-200/60 dark:border-slate-800/60">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Connected Since</p>
                      <p className="font-mono text-[11px] text-slate-800 dark:text-slate-200 truncate">
                        {conn?.created_at ? new Date(conn.created_at).toLocaleDateString() : "—"}
                      </p>
                    </div>

                    <div className="rounded-lg bg-slate-50 dark:bg-slate-950/60 p-2.5 border border-slate-200/60 dark:border-slate-800/60">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Default Scopes</p>
                      <div className="flex flex-wrap gap-1">
                        {meta.defaultScopes.map((s) => (
                          <span
                            key={s}
                            className="rounded bg-slate-200 dark:bg-slate-800 px-1.5 py-0.5 text-[10px] font-mono text-slate-700 dark:text-slate-300"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Actions Footer */}
              <div className="mt-5 pt-3 border-t border-slate-100 dark:border-slate-800/80">
                {connected ? (
                  <div className="flex items-center justify-between gap-2">
                    {/* Force Sync button — uses legacy hook for HubSpot, generic hook for others */}
                    <button
                      onClick={() => {
                        if (isHubspot) {
                          onSyncHubSpot();
                        } else {
                          syncProvider.mutate(meta.id);
                        }
                      }}
                      disabled={isThisProviderSyncing}
                      className="flex-1 flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 px-3 py-2 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-50 transition-all cursor-pointer"
                    >
                      {isThisProviderSyncing ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-500" />
                      ) : (
                        <RefreshCw className="h-3.5 w-3.5 text-indigo-500" />
                      )}
                      {isThisProviderSyncing ? "Syncing…" : "Force Sync"}
                    </button>

                    {/* Disconnect button with confirm step */}
                    {confirmDisconnect !== meta.id ? (
                      <button
                        onClick={() => setConfirmDisconnect(meta.id)}
                        className="rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-xs font-semibold text-red-600 dark:text-red-400 hover:bg-red-500/20 transition-all cursor-pointer"
                      >
                        Disconnect
                      </button>
                    ) : (
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => {
                            if (isHubspot) {
                              onDisconnectHubSpot();
                            } else {
                              disconnectProvider.mutate(meta.id);
                            }
                            setConfirmDisconnect(null);
                          }}
                          disabled={isThisProviderDisconnecting}
                          className="rounded-lg bg-red-600 px-2.5 py-1.5 text-xs font-bold text-white hover:bg-red-700 disabled:opacity-50 transition-all"
                        >
                          {isThisProviderDisconnecting ? "…" : "Confirm"}
                        </button>
                        <button
                          onClick={() => setConfirmDisconnect(null)}
                          className="rounded-lg bg-slate-800 px-2 py-1.5 text-xs font-semibold text-slate-400 hover:text-white"
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  /* Connect button — OAuth start */
                  <button
                    onClick={() => {
                      if (isHubspot) {
                        onConnectHubSpot();
                      } else {
                        startOAuth.mutate(meta.id);
                      }
                    }}
                    disabled={isThisProviderConnecting}
                    className={`w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r ${meta.accentColor} px-4 py-2.5 text-xs font-bold text-white hover:opacity-95 disabled:opacity-60 transition-all cursor-pointer shadow-sm`}
                  >
                    {isThisProviderConnecting ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Link2 className="h-3.5 w-3.5" />
                    )}
                    {isThisProviderConnecting ? "Connecting…" : `Connect ${meta.name}`}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
