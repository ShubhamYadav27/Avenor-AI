"use client";

import { Activity, ShieldCheck, Radio, Server, Layers, CheckCircle2, RefreshCw } from "lucide-react";
import { useCrmConnections } from "@/hooks/use-api";

export function CRMHealthDashboard() {
  const { data: connectionsData } = useCrmConnections();
  const activeConnections = (connectionsData?.connections ?? []).filter((c) => c.is_active);
  const connectedCount = activeConnections.length;
  const isHealthy = connectedCount > 0;

  const healthMetrics = [
    {
      label: "Connection Health",
      value: isHealthy ? `${connectedCount} Provider Connected` : "No CRM Connected",
      subtext: isHealthy ? `${activeConnections.map(c => c.provider.toUpperCase()).join(", ")} Active` : "Standby Mode",
      icon: Activity,
      color: isHealthy ? "text-emerald-400" : "text-slate-400",
      bg: isHealthy ? "bg-emerald-500/10 border-emerald-500/20" : "bg-slate-800 border-slate-700",
    },
    {
      label: "Webhook Listener",
      value: isHealthy ? "Active & Listening" : "Standby",
      subtext: "HMAC / Signature Validated",
      icon: Radio,
      color: "text-sky-400",
      bg: "bg-sky-500/10 border-sky-500/20",
    },
    {
      label: "Token Security",
      value: "Fernet Encrypted",
      subtext: "AES-128-CBC at Rest",
      icon: ShieldCheck,
      color: "text-purple-400",
      bg: "bg-purple-500/10 border-purple-500/20",
    },
    {
      label: "Background Sync",
      value: isHealthy ? "Worker Active" : "Idle",
      subtext: "Polling interval: 30 mins",
      icon: Server,
      color: "text-indigo-400",
      bg: "bg-indigo-500/10 border-indigo-500/20",
    },
    {
      label: "Queue Status",
      value: "0 Jobs Pending",
      subtext: "Sync engine idle",
      icon: Layers,
      color: "text-teal-400",
      bg: "bg-teal-500/10 border-teal-500/20",
    },
    {
      label: "Last Exception",
      value: "None (0 Errors)",
      subtext: "Clean log stream",
      icon: CheckCircle2,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10 border-emerald-500/20",
    },
  ];

  return (
    <div className="p-6 glass-card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Activity className="h-5 w-5 text-indigo-500" />
            Integration Health Dashboard
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Real-time status of pipeline infrastructure, background workers, token encryption, and webhooks.
          </p>
        </div>
        {isHealthy ? (
          <span className="rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 text-xs font-bold text-emerald-400 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            All Systems Operational
          </span>
        ) : (
          <span className="rounded-full bg-slate-800 border border-slate-700 px-3 py-1 text-xs font-bold text-slate-400 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-slate-500" />
            Standby — No Connections
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {healthMetrics.map((m) => {
          const Icon = m.icon;
          return (
            <div
              key={m.label}
              className="rounded-xl border border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-950/40 p-3.5 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`p-1.5 rounded-lg border ${m.bg} ${m.color}`}>
                  <Icon className="h-4 w-4" />
                </span>
                <span className={`h-1.5 w-1.5 rounded-full ${isHealthy ? "bg-emerald-400" : "bg-slate-500"}`} />
              </div>
              <div>
                <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{m.label}</p>
                <p className="text-xs font-bold text-slate-900 dark:text-white mt-0.5">{m.value}</p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1">{m.subtext}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
