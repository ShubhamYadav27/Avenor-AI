"use client";

import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from "recharts";
import {
  TrendingUp, Target, Zap, DollarSign, RefreshCw, Building2, Users,
  FolderKanban, Award, Lock, Sparkles, UserCheck, CheckCircle2, XCircle
} from "lucide-react";
import {
  useCrmAnalytics,
  useSignalEffectiveness,
  usePredictionAccuracy,
  useRunFeedbackLoop,
} from "@/hooks/use-api";
import { EmptyState } from "@/components/ui/empty-state";
import { StatsSkeleton, Skeleton } from "@/components/ui/skeleton";
import { TopBar } from "@/components/layout/top-bar";
import { formatCurrency, SIGNAL_TYPE_LABELS } from "@/lib/utils";

function StatCard({
  label, value, sub, color = "text-slate-900 dark:text-white", icon: Icon,
}: {
  label: string; value: string; sub?: string; color?: string; icon?: React.ElementType;
}) {
  return (
    <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-4 shadow-xs transition-colors">
      <div className="flex items-center justify-between">
        <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{label}</p>
        {Icon && <Icon className="h-4 w-4 text-slate-400 dark:text-slate-500" />}
      </div>
      <p className={`mt-1.5 text-2xl font-black tracking-tight ${color}`}>{value}</p>
      {sub && <p className="mt-0.5 text-xs text-slate-400 dark:text-slate-500 font-medium">{sub}</p>}
    </div>
  );
}

export default function AnalyticsPage() {
  const { data: crmData, isLoading: loadingCrm } = useCrmAnalytics();
  const { data: accuracy, isLoading: loadingAccuracy } = usePredictionAccuracy();
  const { data: effectiveness, isLoading: loadingEffectiveness } = useSignalEffectiveness();
  const feedbackLoop = useRunFeedbackLoop();

  const crmSummary = crmData?.summary;
  const stageData = crmData?.stage_distribution ?? [];
  const ownerData = crmData?.owner_performance ?? [];

  // Chart data for signal effectiveness
  const chartData = useMemo(() => {
    return (effectiveness?.signal_effectiveness ?? [])
      .filter((r) => r.total_occurrences >= 5)
      .sort((a, b) => (b.conversion_rate ?? 0) - (a.conversion_rate ?? 0))
      .map((r) => ({
        name: SIGNAL_TYPE_LABELS[r.signal_type] ?? r.signal_type,
        conversion: Math.round((r.conversion_rate ?? 0) * 100),
        lift: r.lift_over_baseline ?? 1,
        occurrences: r.total_occurrences,
      }));
  }, [effectiveness]);

  const hasEffectivenessData = chartData.length > 0;
  const hasAccuracyData = accuracy && accuracy.total_outcomes > 0;

  const statusPieData = useMemo(() => {
    if (!crmSummary) return [];
    return [
      { name: "Open Opportunities", value: crmSummary.open_count, color: "#6366f1" },
      { name: "Closed Won", value: crmSummary.won_count, color: "#10b981" },
      { name: "Closed Lost", value: crmSummary.lost_count, color: "#ef4444" },
    ].filter(d => d.value > 0);
  }, [crmSummary]);

  return (
    <div className="flex flex-1 flex-col w-full min-h-0 bg-[#F5F7FB] dark:bg-[#050816] transition-colors">
      <TopBar
        title="CRM & Intelligence Analytics"
        subtitle="Live CRM pipeline metrics and AI predictive model performance"
        action={
          <button
            onClick={() => feedbackLoop.mutate()}
            disabled={feedbackLoop.isPending}
            className="flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-50 transition-all shadow-2xs cursor-pointer"
          >
            <RefreshCw className={`h-3 w-3 text-indigo-600 dark:text-indigo-400 ${feedbackLoop.isPending ? "animate-spin" : ""}`} />
            Recalibrate Models
          </button>
        }
      />

      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-6xl space-y-8">

          {/* ========================================================= */}
          {/* SECTION 1: LIVE CRM ANALYTICS                             */}
          {/* ========================================================= */}
          <section className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-indigo-500/10 p-2 text-indigo-600 dark:text-indigo-400">
                  <FolderKanban className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">CRM Pipeline & Sales Analytics</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Calculated directly from synced Salesforce records</p>
                </div>
              </div>
              <span className="rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                Live CRM Data
              </span>
            </div>

            {loadingCrm ? (
              <StatsSkeleton />
            ) : (
              <>
                {/* 4 Record Count KPIs */}
                <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
                  <StatCard
                    label="Synced Accounts"
                    value={String(crmSummary?.total_accounts ?? 0)}
                    sub="crm_accounts"
                    icon={Building2}
                  />
                  <StatCard
                    label="Synced Contacts"
                    value={String(crmSummary?.total_contacts ?? 0)}
                    sub="crm_contacts"
                    icon={Users}
                  />
                  <StatCard
                    label="Synced Leads"
                    value={String(crmSummary?.total_leads ?? 0)}
                    sub="crm_leads"
                    icon={Target}
                  />
                  <StatCard
                    label="Synced Opportunities"
                    value={String(crmSummary?.total_opportunities ?? 0)}
                    sub="crm_opportunities"
                    icon={FolderKanban}
                    color="text-indigo-600 dark:text-indigo-400"
                  />
                </div>

                {/* 4 Revenue & Pipeline KPIs */}
                <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
                  <StatCard
                    label="Open Pipeline Value"
                    value={formatCurrency(crmSummary?.pipeline_value ?? 0)}
                    sub="Active open deals"
                    color="text-indigo-700 dark:text-indigo-400"
                    icon={DollarSign}
                  />
                  <StatCard
                    label="Average Deal Size"
                    value={formatCurrency(crmSummary?.avg_deal_size ?? 0)}
                    sub="Across all opportunities"
                    color="text-emerald-700 dark:text-emerald-400"
                  />
                  <StatCard
                    label="Won Revenue"
                    value={formatCurrency(crmSummary?.won_revenue ?? 0)}
                    sub={`${crmSummary?.won_count ?? 0} Closed-Won deals`}
                    color="text-emerald-600 dark:text-emerald-500"
                  />
                  <StatCard
                    label="Lost Revenue"
                    value={formatCurrency(crmSummary?.lost_revenue ?? 0)}
                    sub={`${crmSummary?.lost_count ?? 0} Closed-Lost deals`}
                    color="text-slate-500 dark:text-slate-400"
                  />
                </div>

                {/* Opportunity Breakdown & Stage Distribution */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

                  {/* Stage Distribution Chart */}
                  <div className="lg:col-span-2 rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs transition-colors">
                    <h3 className="mb-1 text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Revenue & Opportunities by Stage
                    </h3>
                    <p className="mb-4 text-xs text-slate-500 dark:text-slate-400">Total pipeline value ($) mapped to CRM stage</p>

                    {stageData.length === 0 ? (
                      <EmptyState icon={FolderKanban} title="No opportunity stages found" description="Sync Salesforce opportunities to see pipeline stage distribution." className="py-8" />
                    ) : (
                      <ResponsiveContainer width="100%" height={240}>
                        <BarChart data={stageData} margin={{ top: 8, right: 12, left: 12, bottom: 24 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" className="opacity-50 dark:opacity-10" />
                          <XAxis dataKey="stage" tick={{ fontSize: 10, fill: "#64748b" }} interval={0} angle={-15} textAnchor="end" />
                          <YAxis tickFormatter={(v) => `$${v >= 1000 ? `${Math.round(v / 1000)}k` : v}`} tick={{ fontSize: 11, fill: "#64748b" }} />
                          <Tooltip
                            formatter={(v: unknown) => [formatCurrency(Number(v)), "Pipeline Value"]}
                            contentStyle={{ fontSize: 12, borderRadius: 12, border: "1px solid #e2e8f0", backgroundColor: "#0f172a", color: "#fff" }}
                          />
                          <Bar dataKey="value" fill="#6366f1" radius={[6, 6, 0, 0]}>
                            {stageData.map((entry, index) => (
                              <Cell key={index} fill={entry.stage.toLowerCase().includes("won") ? "#10b981" : "#6366f1"} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>

                  {/* Opportunity Status Ratio */}
                  <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs flex flex-col justify-between transition-colors">
                    <div>
                      <h3 className="mb-1 text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <Award className="h-4 w-4 text-emerald-600 dark:text-emerald-400" /> Deal Status Ratio
                      </h3>
                      <p className="mb-4 text-xs text-slate-500 dark:text-slate-400">Open vs Closed opportunities</p>

                      {statusPieData.length > 0 ? (
                        <div className="flex flex-col items-center">
                          <ResponsiveContainer width="100%" height={160}>
                            <PieChart>
                              <Pie
                                data={statusPieData}
                                cx="50%"
                                cy="50%"
                                innerRadius={45}
                                outerRadius={65}
                                paddingAngle={4}
                                dataKey="value"
                              >
                                {statusPieData.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                              </Pie>
                              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 12, backgroundColor: "#0f172a", color: "#fff" }} />
                            </PieChart>
                          </ResponsiveContainer>
                          <div className="w-full space-y-2 text-xs border-t border-slate-100 dark:border-slate-800 pt-3">
                            <div className="flex justify-between items-center">
                              <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300 font-semibold">
                                <span className="h-2 w-2 rounded-full bg-indigo-500" /> Open Deals
                              </span>
                              <span className="font-bold text-slate-900 dark:text-white">{crmSummary?.open_count ?? 0}</span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300 font-semibold">
                                <CheckCircle2 className="h-3 w-3 text-emerald-500" /> Closed Won
                              </span>
                              <span className="font-bold text-slate-900 dark:text-white">{crmSummary?.won_count ?? 0}</span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300 font-semibold">
                                <XCircle className="h-3 w-3 text-red-500" /> Closed Lost
                              </span>
                              <span className="font-bold text-slate-900 dark:text-white">{crmSummary?.lost_count ?? 0}</span>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <EmptyState icon={FolderKanban} title="No deal status data" description="Sync Salesforce opportunities to view status ratios." className="py-6" />
                      )}
                    </div>
                  </div>
                </div>

                {/* Sales Rep / Owner Performance Table */}
                {ownerData.length > 0 && (
                  <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs transition-colors">
                    <h3 className="mb-1 text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                      <UserCheck className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Opportunity Owner Performance
                    </h3>
                    <p className="mb-4 text-xs text-slate-500 dark:text-slate-400">Total pipeline value managed per CRM rep</p>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left">
                        <thead>
                          <tr className="border-b border-slate-200/80 dark:border-slate-800/80 text-slate-500 dark:text-slate-400 uppercase tracking-wider font-bold">
                            <th className="pb-3">Opportunity Owner</th>
                            <th className="pb-3 text-center">Managed Deals</th>
                            <th className="pb-3 text-right">Total Pipeline Value</th>
                            <th className="pb-3 text-right">Closed Won Value</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-semibold">
                          {ownerData.map((owner, i) => (
                            <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                              <td className="py-3 text-slate-900 dark:text-white font-bold">{owner.owner}</td>
                              <td className="py-3 text-center text-slate-600 dark:text-slate-300">{owner.count}</td>
                              <td className="py-3 text-right text-indigo-600 dark:text-indigo-400 font-bold">{formatCurrency(owner.total_value)}</td>
                              <td className="py-3 text-right text-emerald-600 dark:text-emerald-400 font-bold">{formatCurrency(owner.won_value)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}
          </section>

          {/* ========================================================= */}
          {/* SECTION 2: AI PREDICTIVE MODEL & LEARNING ANALYTICS        */}
          {/* ========================================================= */}
          <section className="space-y-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="flex items-center justify-between border-b border-slate-200/80 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-lg bg-indigo-500/10 p-2 text-indigo-600 dark:text-indigo-400">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-base font-black text-slate-900 dark:text-white">AI Learning & Predictive Performance</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Model accuracy, signal effectiveness, and outcome attribution calibration</p>
                </div>
              </div>
              <span className={`rounded-full border px-3 py-1 text-xs font-bold flex items-center gap-1.5 ${
                hasAccuracyData
                  ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-600 dark:text-indigo-400"
                  : "bg-amber-500/10 border-amber-500/20 text-amber-600 dark:text-amber-400"
              }`}>
                {hasAccuracyData ? <Sparkles className="h-3 w-3" /> : <Lock className="h-3 w-3" />}
                {hasAccuracyData ? "Model Active" : "Outcome Feedback Required"}
              </span>
            </div>

            {/* AI Learning Notification Banner if no outcomes */}
            {!hasAccuracyData && !loadingAccuracy && (
              <div className="rounded-2xl border border-indigo-200/80 dark:border-indigo-500/30 bg-indigo-50/50 dark:bg-indigo-950/20 p-5 shadow-xs flex items-start gap-3.5 transition-colors">
                <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 flex-shrink-0">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">AI Learning Engine Standing By</h4>
                  <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
                    AI learning metrics (prediction precision, signal conversion lift, and days-ahead accuracy) will activate automatically as Salesforce opportunities transition to Closed-Won or Closed-Lost.
                  </p>
                </div>
              </div>
            )}

            {/* AI Stat Cards */}
            {loadingAccuracy ? (
              <StatsSkeleton />
            ) : (
              <div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">
                <StatCard
                  label="Prediction Precision"
                  value={accuracy?.precision_at_0_5 != null ? `${Math.round(accuracy.precision_at_0_5 * 100)}%` : "Standby"}
                  sub="At score ≥ 50%"
                  color="text-indigo-600 dark:text-indigo-400"
                />
                <StatCard
                  label="Hot/Warm Window Accuracy"
                  value={accuracy?.hot_warm_window_accuracy != null ? `${Math.round(accuracy.hot_warm_window_accuracy * 100)}%` : "Standby"}
                  sub="Flagged intent accounts"
                  color="text-amber-600 dark:text-amber-500"
                />
                <StatCard
                  label="Avg Days Ahead"
                  value={accuracy?.avg_days_avenor_ahead != null ? `${Math.round(accuracy.avg_days_avenor_ahead as number)}d` : "Standby"}
                  sub="Before organic discovery"
                  color="text-emerald-600 dark:text-emerald-500"
                />
                <StatCard
                  label="Total Outcomes Logged"
                  value={String(accuracy?.total_outcomes ?? 0)}
                  sub="Outcome feedback dataset"
                />
              </div>
            )}

            {/* Signal Effectiveness Matrix */}
            <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/90 p-5 shadow-xs transition-colors">
              <h3 className="mb-1 text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Zap className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Signal Effectiveness Matrix
              </h3>
              <p className="mb-4 text-xs text-slate-500 dark:text-slate-400">Conversion rate when each signal type is detected across synced accounts</p>

              {loadingEffectiveness && <Skeleton className="h-40 rounded-2xl" />}

              {!loadingEffectiveness && !hasEffectivenessData && (
                <div className="py-8 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-xl bg-slate-50/50 dark:bg-slate-950/40">
                  <Zap className="mx-auto h-6 w-6 text-slate-400 mb-2" />
                  <p className="text-xs font-bold text-slate-700 dark:text-slate-300">Awaiting Outcome Signal Data</p>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 max-w-md mx-auto mt-1">
                    Signal effectiveness matrix requires at least 5 outcome records per signal type to display conversion lift benchmarks.
                  </p>
                </div>
              )}

              {!loadingEffectiveness && hasEffectivenessData && (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={chartData} margin={{ top: 4, right: 8, left: -8, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" className="opacity-50 dark:opacity-10" />
                    <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} />
                    <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11, fill: "#64748b" }} />
                    <Tooltip formatter={(v: unknown) => [`${Math.round(Number(v))}%`, "Conversion Rate"]} />
                    <Bar dataKey="conversion" radius={[6, 6, 0, 0]}>
                      {chartData.map((entry, i) => (
                        <Cell key={i} fill={entry.lift >= 1.5 ? "#4f46e5" : "#6366f1"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>

          </section>

        </div>
      </div>
    </div>
  );
}
