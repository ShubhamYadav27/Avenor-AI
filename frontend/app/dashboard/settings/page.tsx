"use client";

import { useState } from "react";
import { Settings, RefreshCw, CheckCircle2, Sun } from "lucide-react";
import { useMe, useAdminStatus, useModelAccuracy } from "@/hooks/use-api";
import { apiClient, getErrorMessage } from "@/lib/api-client";
import { TopBar } from "@/components/layout/top-bar";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { formatDate } from "@/lib/utils";

export default function SettingsPage() {
  const { data: me } = useMe();
  const { data: adminStatus } = useAdminStatus();
  const { data: modelAcc } = useModelAccuracy();
  const [triggering, setTriggering] = useState(false);
  const [triggered, setTriggered] = useState(false);
  const [triggerError, setTriggerError] = useState("");

  async function handleTriggerPipeline() {
    setTriggering(true);
    setTriggerError("");
    try {
      await apiClient.post("/admin/pipeline/trigger");
      setTriggered(true);
      setTimeout(() => setTriggered(false), 4000);
    } catch (err) {
      setTriggerError(getErrorMessage(err));
    } finally {
      setTriggering(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col w-full min-h-0 bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
      <TopBar title="Workspace Settings" subtitle="Workspace configuration, theme preferences, and prediction engine parameters" />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-2xl space-y-5">

          {/* Theme Preference Section */}
          <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs backdrop-blur-md">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Sun className="h-4 w-4 text-amber-500 dark:text-indigo-400" /> Interface Theme
                </h2>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  Choose your preferred theme appearance
                </p>
              </div>
              <ThemeToggle variant="compact" />
            </div>
          </div>

          {/* Workspace info */}
          <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs">
            <h2 className="mb-4 text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Settings className="h-4 w-4 text-slate-400" /> Workspace Account Details
            </h2>
            <dl className="space-y-2.5 text-xs">
              {[
                { label: "Workspace Name", value: me?.workspace_name },
                { label: "Account Owner", value: me?.full_name },
                { label: "Email Address", value: me?.email },
                { label: "Role", value: me?.role },
                { label: "Subscription Tier", value: me?.subscription_tier },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800/60 last:border-0">
                  <dt className="text-slate-500 dark:text-slate-400 font-semibold">{label}</dt>
                  <dd className="font-bold text-slate-900 dark:text-slate-100 capitalize">{value ?? "â€”"}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Model status */}
          <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs">
            <h2 className="mb-4 text-sm font-bold text-slate-900 dark:text-white">AI Prediction Engine Model</h2>
            <dl className="space-y-2.5 text-xs">
              {[
                {
                  label: "Outcomes Logged",
                  value: modelAcc?.total_outcomes != null ? String(modelAcc.total_outcomes) : "0",
                },
                {
                  label: "Model Confidence",
                  value: modelAcc?.model_confidence ?? "insufficient_data",
                },
                {
                  label: "Prediction Precision",
                  value: modelAcc?.precision_at_0_5 != null
                    ? `${Math.round(modelAcc.precision_at_0_5 * 100)}%`
                    : "â€”",
                },
                {
                  label: "Last Trained",
                  value: adminStatus?.model?.last_trained_at
                    ? formatDate(adminStatus.model.last_trained_at)
                    : "Not yet trained",
                },
                {
                  label: "Training Sample Size",
                  value: adminStatus?.model?.training_sample_size != null
                    ? String(adminStatus.model.training_sample_size)
                    : "0",
                },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800/60 last:border-0">
                  <dt className="text-slate-500 dark:text-slate-400 font-semibold">{label}</dt>
                  <dd className="font-bold text-slate-900 dark:text-slate-100">{value}</dd>
                </div>
              ))}
            </dl>
            <p className="mt-3.5 text-xs text-slate-400 font-medium">
              Model recalibrates automatically every Saturday at 2am UTC.
              Minimum 20 outcomes required before self-training loop activates.
            </p>
          </div>

          {/* Signal weights */}
          {adminStatus?.model?.current_weights &&
            Object.keys(adminStatus.model.current_weights).length > 0 && (
            <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs">
              <h2 className="mb-4 text-sm font-bold text-slate-900 dark:text-white">Active Signal Weights</h2>
              <div className="space-y-2.5">
                {Object.entries(adminStatus.model.current_weights)
                  .sort((a, b) => b[1] - a[1])
                  .map(([type, weight]) => (
                    <div key={type} className="flex items-center gap-3">
                      <span className="w-36 text-xs font-semibold text-slate-700 dark:text-slate-300 capitalize">
                        {type.replace(/_/g, " ")}
                      </span>
                      <div className="flex-1 rounded-full bg-slate-100 dark:bg-slate-800 h-2">
                        <div
                          className="rounded-full bg-indigo-600 dark:bg-indigo-500 h-2 transition-all"
                          style={{ width: `${Math.min((weight / 0.4) * 100, 100)}%` }}
                        />
                      </div>
                      <span className="w-12 text-right text-xs font-mono font-bold text-slate-900 dark:text-slate-100">
                        {weight.toFixed(3)}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Recent jobs */}
          {adminStatus?.recent_jobs && adminStatus.recent_jobs.length > 0 && (
            <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs">
              <h2 className="mb-4 text-sm font-bold text-slate-900 dark:text-white">Recent Background Signal Jobs</h2>
              <div className="space-y-1">
                {adminStatus.recent_jobs.slice(0, 8).map((job) => (
                  <div key={job.id} className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800/60 last:border-0">
                    <div className="flex items-center gap-2.5">
                      <span className={`h-2.5 w-2.5 rounded-full flex-shrink-0 ${
                        job.status === "completed" ? "bg-emerald-500"
                        : job.status === "failed" ? "bg-red-500"
                        : job.status === "running" ? "bg-indigo-500 animate-pulse"
                        : "bg-slate-300 dark:bg-slate-600"
                      }`} />
                      <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                        {job.type.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-400 font-medium">
                      {job.duration_seconds != null && (
                        <span>{job.duration_seconds.toFixed(1)}s</span>
                      )}
                      <span>{formatDate(job.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
              {(adminStatus.failed_jobs_count ?? 0) > 0 && (
                <p className="mt-2.5 text-xs font-semibold text-red-600 dark:text-red-400">
                  {adminStatus.failed_jobs_count} failed job{adminStatus.failed_jobs_count !== 1 ? "s" : ""} â€”
                  check backend logs.
                </p>
              )}
            </div>
          )}

          {/* Pipeline trigger */}
          <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-6 shadow-xs">
            <h2 className="mb-1.5 text-sm font-bold text-slate-900 dark:text-white">Manual Signal Pipeline Execution</h2>
            <p className="mb-4 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              Trigger signal collection â†’ score correlation â†’ feed generation for your workspace.
              Runs automatically every 6 hours in production.
            </p>
            {triggerError && (
              <p className="mb-2 text-xs font-semibold text-red-600 dark:text-red-400">{triggerError}</p>
            )}
            {triggered ? (
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 p-3 rounded-xl">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                Pipeline queued. View execution in job history above.
              </div>
            ) : (
              <button
                onClick={handleTriggerPipeline}
                disabled={triggering}
                className="flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 text-xs font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-slate-300 disabled:opacity-50 transition-all shadow-2xs cursor-pointer"
              >
                <RefreshCw className={`h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400 ${triggering ? "animate-spin" : ""}`} />
                {triggering ? "Queuing Pipelineâ€¦" : "Run Pipeline Now"}
              </button>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

