"use client";

import { useState } from "react";
import { Settings, RefreshCw, CheckCircle2 } from "lucide-react";
import { useMe, useAdminStatus, useModelAccuracy } from "@/hooks/use-api";
import { apiClient, getErrorMessage } from "@/lib/api-client";
import { TopBar } from "@/components/layout/top-bar";

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
    <div className="flex flex-1 flex-col overflow-hidden">
      <TopBar title="Settings" subtitle="Workspace configuration and system status" />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-2xl space-y-4">

          {/* Workspace info */}
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-4 text-sm font-semibold text-slate-800 flex items-center gap-2">
              <Settings className="h-4 w-4 text-slate-400" /> Workspace
            </h2>
            <dl className="space-y-2 text-sm">
              {[
                { label: "Workspace", value: me?.workspace_name },
                { label: "Your name", value: me?.full_name },
                { label: "Email", value: me?.email },
                { label: "Role", value: me?.role },
                { label: "Plan", value: me?.subscription_tier },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between py-1 border-b border-slate-50 last:border-0">
                  <dt className="text-slate-500">{label}</dt>
                  <dd className="font-medium text-slate-800 capitalize">{value ?? "—"}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Model status */}
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-4 text-sm font-semibold text-slate-800">Prediction model</h2>
            <dl className="space-y-2 text-sm">
              {[
                {
                  label: "Outcomes logged",
                  value: modelAcc?.total_outcomes != null ? String(modelAcc.total_outcomes) : "0",
                },
                {
                  label: "Model confidence",
                  value: modelAcc?.model_confidence ?? "insufficient_data",
                },
                {
                  label: "Prediction precision",
                  value: modelAcc?.precision_at_0_5 != null
                    ? `${Math.round(modelAcc.precision_at_0_5 * 100)}%`
                    : "—",
                },
                {
                  label: "Model last trained",
                  value: adminStatus?.model?.last_trained_at
                    ? formatDate(adminStatus.model.last_trained_at)
                    : "Not yet trained",
                },
                {
                  label: "Training sample size",
                  value: adminStatus?.model?.training_sample_size != null
                    ? String(adminStatus.model.training_sample_size)
                    : "0",
                },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between py-1 border-b border-slate-50 last:border-0">
                  <dt className="text-slate-500">{label}</dt>
                  <dd className="font-medium text-slate-800">{value}</dd>
                </div>
              ))}
            </dl>
            <p className="mt-3 text-xs text-slate-400">
              Model recalibrates automatically every Saturday at 2am UTC.
              Minimum 20 outcomes required before training begins.
            </p>
          </div>

          {/* Signal weights */}
          {adminStatus?.model?.current_weights &&
            Object.keys(adminStatus.model.current_weights).length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-4 text-sm font-semibold text-slate-800">Current signal weights</h2>
              <div className="space-y-2">
                {Object.entries(adminStatus.model.current_weights)
                  .sort((a, b) => b[1] - a[1])
                  .map(([type, weight]) => (
                    <div key={type} className="flex items-center gap-3">
                      <span className="w-36 text-xs text-slate-500 capitalize">
                        {type.replace(/_/g, " ")}
                      </span>
                      <div className="flex-1 rounded-full bg-slate-100 h-1.5">
                        <div
                          className="rounded-full bg-violet-500 h-1.5 transition-all"
                          style={{ width: `${Math.min((weight / 0.4) * 100, 100)}%` }}
                        />
                      </div>
                      <span className="w-10 text-right text-xs font-medium text-slate-700">
                        {weight.toFixed(3)}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Recent jobs */}
          {adminStatus?.recent_jobs && adminStatus.recent_jobs.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-4 text-sm font-semibold text-slate-800">Recent background jobs</h2>
              <div className="space-y-1">
                {adminStatus.recent_jobs.slice(0, 8).map((job) => (
                  <div key={job.id} className="flex items-center justify-between py-1.5 border-b border-slate-50 last:border-0">
                    <div className="flex items-center gap-2">
                      <span className={`h-2 w-2 rounded-full flex-shrink-0 ${
                        job.status === "completed" ? "bg-green-500"
                        : job.status === "failed" ? "bg-red-500"
                        : job.status === "running" ? "bg-blue-500"
                        : "bg-slate-300"
                      }`} />
                      <span className="text-xs font-medium text-slate-700">
                        {job.type.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-400">
                      {job.duration_seconds != null && (
                        <span>{job.duration_seconds.toFixed(1)}s</span>
                      )}
                      <span>{formatDate(job.created_at)}</span>
                    </div>
                  </div>
                ))}
              </div>
              {(adminStatus.failed_jobs_count ?? 0) > 0 && (
                <p className="mt-2 text-xs text-red-600">
                  {adminStatus.failed_jobs_count} failed job{adminStatus.failed_jobs_count !== 1 ? "s" : ""} —
                  check backend logs.
                </p>
              )}
            </div>
          )}

          {/* Pipeline trigger */}
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-2 text-sm font-semibold text-slate-800">Manual pipeline run</h2>
            <p className="mb-3 text-xs text-slate-500">
              Trigger signal collection → scoring → feed generation for your workspace.
              Normally runs automatically every 6 hours.
            </p>
            {triggerError && (
              <p className="mb-2 text-xs text-red-600">{triggerError}</p>
            )}
            {triggered ? (
              <div className="flex items-center gap-2 text-sm text-green-700">
                <CheckCircle2 className="h-4 w-4" />
                Pipeline queued. Check job history above.
              </div>
            ) : (
              <button
                onClick={handleTriggerPipeline}
                disabled={triggering}
                className="flex items-center gap-1.5 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:border-violet-300 hover:text-violet-700 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${triggering ? "animate-spin" : ""}`} />
                {triggering ? "Queuing…" : "Run pipeline now"}
              </button>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
