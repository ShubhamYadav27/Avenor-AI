"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { TrendingUp, Target, Zap, DollarSign, RefreshCw } from "lucide-react";
import {
  useSignalEffectiveness,
  usePredictionAccuracy,
  useAttributionSummary,
  useRunFeedbackLoop,
} from "@/hooks/use-api";
import { EmptyState } from "@/components/ui/empty-state";
import { StatsSkeleton, Skeleton } from "@/components/ui/skeleton";
import { TopBar } from "@/components/layout/top-bar";
import { formatCurrency, SIGNAL_TYPE_LABELS } from "@/lib/utils";

function StatCard({
  label, value, sub, color = "text-slate-800",
}: {
  label: string; value: string; sub?: string; color?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${color}`}>{value}</p>
      {sub && <p className="mt-0.5 text-xs text-slate-400">{sub}</p>}
    </div>
  );
}

export default function AnalyticsPage() {
  const { data: accuracy, isLoading: loadingAccuracy } = usePredictionAccuracy();
  const { data: effectiveness, isLoading: loadingEffectiveness } = useSignalEffectiveness();
  const { data: attribution } = useAttributionSummary();
  const feedbackLoop = useRunFeedbackLoop();

  // Chart data for signal effectiveness
  const chartData = (effectiveness?.signal_effectiveness ?? [])
    .filter((r) => r.total_occurrences >= 5)
    .sort((a, b) => (b.conversion_rate ?? 0) - (a.conversion_rate ?? 0))
    .map((r) => ({
      name: SIGNAL_TYPE_LABELS[r.signal_type] ?? r.signal_type,
      conversion: Math.round((r.conversion_rate ?? 0) * 100),
      lift: r.lift_over_baseline ?? 1,
      occurrences: r.total_occurrences,
    }));

  // Outcome type breakdown for win/loss chart
  const outcomeData = accuracy?.by_outcome_type
    ? Object.entries(accuracy.by_outcome_type)
        .sort((a, b) => b[1] - a[1])
        .map(([type, count]) => ({
          name: type.replace(/_/g, " "),
          count,
        }))
    : [];

  const hasEffectivenessData = chartData.length > 0;
  const hasAccuracyData = accuracy && accuracy.total_outcomes > 0;

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <TopBar
        title="Analytics"
        subtitle="Signal effectiveness, prediction accuracy, and revenue attribution"
        action={
          <button
            onClick={() => feedbackLoop.mutate()}
            disabled={feedbackLoop.isPending}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-slate-300 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-3 w-3 ${feedbackLoop.isPending ? "animate-spin" : ""}`} />
            Recompute
          </button>
        }
      />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-5xl space-y-6">

          {/* Top stats */}
          {loadingAccuracy ? (
            <StatsSkeleton />
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatCard
                label="Total outcomes logged"
                value={String(accuracy?.total_outcomes ?? 0)}
                sub="Needed for model training"
              />
              <StatCard
                label="Prediction precision"
                value={accuracy?.precision_at_0_5 != null
                  ? `${Math.round(accuracy.precision_at_0_5 * 100)}%`
                  : "—"}
                sub="At score ≥ 50%"
                color="text-violet-700"
              />
              <StatCard
                label="Hot/warm accuracy"
                value={accuracy?.hot_warm_window_accuracy != null
                  ? `${Math.round(accuracy.hot_warm_window_accuracy * 100)}%`
                  : "—"}
                sub="Of flagged accounts that converted"
                color="text-amber-700"
              />
              <StatCard
                label="Avg days ahead"
                value={accuracy?.avg_days_avenor_ahead != null
                  ? `${Math.round(accuracy.avg_days_avenor_ahead as number)}d`
                  : "—"}
                sub="Before organic CRM discovery"
                color="text-green-700"
              />
            </div>
          )}

          {/* Attribution summary */}
          {attribution && attribution.total_attributions > 0 && (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              <StatCard
                label="Attributed outcomes"
                value={String(attribution.total_attributions)}
              />
              <StatCard
                label="Attributed revenue"
                value={formatCurrency(attribution.attributed_revenue_usd ?? 0)}
                color="text-green-700"
              />
              <StatCard
                label="Avg deal value"
                value={formatCurrency(attribution.avg_deal_value_usd)}
              />
            </div>
          )}

          {/* Model confidence */}
          {accuracy?.model_confidence && (
            <div className={`rounded-xl border p-4 flex items-center gap-3 ${
              accuracy.model_confidence === "high"
                ? "bg-green-50 border-green-200"
                : accuracy.model_confidence === "medium"
                ? "bg-amber-50 border-amber-200"
                : accuracy.model_confidence === "insufficient_data"
                ? "bg-slate-50 border-slate-200"
                : "bg-red-50 border-red-200"
            }`}>
              <Target className={`h-5 w-5 flex-shrink-0 ${
                accuracy.model_confidence === "high" ? "text-green-600"
                : accuracy.model_confidence === "medium" ? "text-amber-600"
                : "text-slate-400"
              }`} />
              <div>
                <p className="text-sm font-semibold text-slate-800 capitalize">
                  Model confidence: {accuracy.model_confidence.replace(/_/g, " ")}
                </p>
                <p className="text-xs text-slate-500">
                  {accuracy.model_confidence === "insufficient_data"
                    ? `${accuracy.total_outcomes} outcomes logged — need 10+ for meaningful accuracy`
                    : `Based on ${accuracy.total_outcomes} outcome${accuracy.total_outcomes !== 1 ? "s" : ""}`}
                </p>
              </div>
            </div>
          )}

          {/* Signal effectiveness chart */}
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-1 text-sm font-semibold text-slate-800 flex items-center gap-2">
              <Zap className="h-4 w-4 text-violet-500" /> Signal effectiveness
            </h2>
            <p className="mb-4 text-xs text-slate-500">
              Conversion rate when each signal type is present (requires 5+ outcomes per signal)
            </p>

            {loadingEffectiveness && <Skeleton className="h-48 rounded-lg" />}

            {!loadingEffectiveness && !hasEffectivenessData && (
              <EmptyState
                icon={Zap}
                title="Not enough data yet"
                description="Log at least 5 outcomes per signal type to see effectiveness data."
                className="py-10"
              />
            )}

            {!loadingEffectiveness && hasEffectivenessData && (
              <>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={chartData} margin={{ top: 4, right: 8, left: -8, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} />
                    <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11, fill: "#64748b" }} />
                    <Tooltip
                      formatter={(v: unknown) => [`${Math.round(Number(v))}%`, "Conversion rate"]}
                      contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
                    />
                    <Bar dataKey="conversion" radius={[4, 4, 0, 0]}>
                      {chartData.map((entry, i) => (
                        <Cell
                          key={i}
                          fill={entry.lift >= 1.5 ? "#7c3aed" : entry.lift >= 1 ? "#a78bfa" : "#cbd5e1"}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>

                {/* Recommendations */}
                {(effectiveness?.weight_recommendations ?? []).length > 0 && (
                  <div className="mt-4 space-y-2">
                    <p className="text-xs font-medium text-slate-500">Scoring recommendations</p>
                    {effectiveness!.weight_recommendations.slice(0, 3).map((rec, i) => (
                      <div key={i} className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-xs ${
                        rec.impact === "high"
                          ? "border-violet-200 bg-violet-50"
                          : "border-slate-100 bg-slate-50"
                      }`}>
                        <TrendingUp className={`mt-0.5 h-3 w-3 flex-shrink-0 ${
                          rec.action === "increase_weight" ? "text-green-600" : "text-slate-400"
                        }`} />
                        <div>
                          <span className="font-medium text-slate-700">
                            {SIGNAL_TYPE_LABELS[rec.signal_type] ?? rec.signal_type}
                          </span>
                          <span className="text-slate-500"> — {rec.reason}</span>
                          <span className="ml-2 text-slate-400">
                            {rec.current_weight.toFixed(2)} → {rec.suggested_weight.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>

          {/* Win/loss breakdown */}
          {hasAccuracyData && outcomeData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-1 text-sm font-semibold text-slate-800 flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-green-500" /> Outcome breakdown
              </h2>
              <p className="mb-4 text-xs text-slate-500">Distribution of logged outcomes</p>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={outcomeData} layout="vertical" margin={{ top: 0, right: 20, left: 80, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 11, fill: "#64748b" }} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fontSize: 11, fill: "#64748b" }}
                    width={76}
                  />
                  <Tooltip
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {outcomeData.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={
                          entry.name.includes("won") ? "#22c55e"
                          : entry.name.includes("meeting") || entry.name.includes("opportunity") ? "#7c3aed"
                          : entry.name.includes("positive") ? "#a78bfa"
                          : "#e2e8f0"
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* No data CTA */}
          {!hasAccuracyData && !loadingAccuracy && (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
              <Target className="mx-auto mb-3 h-8 w-8 text-slate-300" />
              <p className="text-sm font-semibold text-slate-700">No outcome data yet</p>
              <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
                Log outcomes from the Intelligence Feed — contacted, meetings booked, deals won/lost — to see analytics here.
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
