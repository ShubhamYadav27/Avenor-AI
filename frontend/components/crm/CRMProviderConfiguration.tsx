"use client";

import { useState } from "react";
import { Settings, Copy, Check } from "lucide-react";

export function CRMProviderConfiguration() {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(key);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const configs = [
    {
      title: "OAuth Callback URL",
      value: "https://api.avenor.ai/api/v1/crm/{provider}/callback",
      description: "Generic OAuth callback URI configured in your CRM app portal.",
      key: "callback",
    },
    {
      title: "Webhook Ingestion Endpoint",
      value: "https://api.avenor.ai/api/v1/crm/{provider}/webhook/{workspace_id}",
      description: "Public endpoint for real-time change data capture & webhooks.",
      key: "webhook",
    },
    {
      title: "Connected Workspace",
      value: "Production Workspace (ID: ws_01h92k83)",
      description: "Target workspace for entity correlation & signal matching.",
      key: "workspace",
    },
    {
      title: "Environment & Region",
      value: "Production (us-east-1 / Multi-datacenter)",
      description: "Isolated cloud infrastructure with auto-scaling connection pool.",
      key: "env",
    },
  ];

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Settings className="h-5 w-5 text-indigo-500" />
            Provider Infrastructure Configuration
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            System configuration parameters and endpoint paths. API keys and secrets are securely masked.
          </p>
        </div>
        <span className="text-xs font-semibold text-slate-400">AES-128-CBC Encrypted</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {configs.map((c) => (
          <div
            key={c.key}
            className="rounded-xl border border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-950/40 p-4 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold text-slate-900 dark:text-white">{c.title}</p>
                <button
                  onClick={() => copyToClipboard(c.value, c.key)}
                  className="flex items-center gap-1 text-[11px] font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  {copiedField === c.key ? (
                    <>
                      <Check className="h-3 w-3 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
              <p className="font-mono text-xs text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 mt-2 truncate">
                {c.value}
              </p>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">{c.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
