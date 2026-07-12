"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, Search } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { BuyingWindowBadge } from "@/components/ui/buying-window-badge";
import { ScoreRing } from "@/components/ui/score-ring";
import { EmptyState } from "@/components/ui/empty-state";
import { FeedSkeleton } from "@/components/ui/skeleton";
import { TopBar } from "@/components/layout/top-bar";
import { useCompanyStats } from "@/hooks/use-api";
import { formatDate } from "@/lib/utils";
import type { CompanyListItem } from "@/types/api";

function useCompanies(status?: string) {
  return useQuery({
    queryKey: ["companies", status],
    queryFn: async () => {
      const res = await apiClient.get<{ total: number; companies: CompanyListItem[] }>(
        "/companies",
        { params: { status, limit: 100 } }
      );
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

const STATUS_TABS = [
  { label: "Active", value: "active" },
  { label: "Monitoring", value: "monitoring" },
  { label: "Converted", value: "converted" },
  { label: "All", value: undefined },
];

export default function CompaniesPage() {
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string | undefined>("active");
  const [search, setSearch] = useState("");
  const { data: statsData } = useCompanyStats();
  const { data, isLoading, isError } = useCompanies(statusFilter);

  const filtered = data?.companies.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    (c.domain ?? "").toLowerCase().includes(search.toLowerCase())
  ) ?? [];

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <TopBar title="Companies" subtitle="All accounts in your monitored universe" />

      {/* Stats strip */}
      {statsData && (
        <div className="flex gap-6 border-b border-slate-200 bg-white px-6 py-3">
          {[
            { label: "Total", value: statsData.total },
            { label: "Active", value: statsData.by_status?.active ?? 0 },
            { label: "Hot", value: statsData.active_by_window?.hot ?? 0, color: "text-red-600" },
            { label: "Warm", value: statsData.active_by_window?.warm ?? 0, color: "text-amber-600" },
            { label: "Converted", value: statsData.by_status?.converted ?? 0, color: "text-green-600" },
          ].map(({ label, value, color }) => (
            <div key={label} className="text-center">
              <p className={`text-lg font-bold ${color ?? "text-slate-800"}`}>{value}</p>
              <p className="text-xs text-slate-400">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-3 border-b border-slate-200 bg-white px-6 py-2">
        <div className="flex gap-1">
          {STATUS_TABS.map(({ label, value }) => (
            <button
              key={label}
              onClick={() => setStatusFilter(value)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                statusFilter === value
                  ? "bg-violet-100 text-violet-700"
                  : "text-slate-500 hover:bg-slate-100"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="relative ml-auto">
          <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search companies…"
            className="rounded-lg border border-slate-200 bg-slate-50 py-1.5 pl-8 pr-3 text-xs outline-none focus:border-violet-400 focus:bg-white w-48"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {isLoading && <FeedSkeleton />}

        {isError && (
          <EmptyState
            icon={Building2}
            title="Failed to load companies"
            description="Check that the backend API is running."
          />
        )}

        {!isLoading && !isError && filtered.length === 0 && (
          <EmptyState
            icon={Building2}
            title="No companies found"
            description="Companies appear here after the signal ingestion pipeline runs."
          />
        )}

        {!isLoading && filtered.length > 0 && (
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50 text-xs font-medium text-slate-500">
                  <th className="px-4 py-3 text-left">Company</th>
                  <th className="px-4 py-3 text-left">Industry</th>
                  <th className="px-4 py-3 text-center">Score</th>
                  <th className="px-4 py-3 text-center">Window</th>
                  <th className="px-4 py-3 text-left">Funding</th>
                  <th className="px-4 py-3 text-left">Last scored</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {filtered.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => router.push(`/dashboard/companies/${c.id}`)}
                    className="cursor-pointer hover:bg-violet-50 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-900">{c.name}</p>
                      {c.domain && <p className="text-xs text-slate-400">{c.domain}</p>}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">{c.industry ?? "—"}</td>
                    <td className="px-4 py-3">
                      <div className="flex justify-center">
                        <ScoreRing score={c.composite_score} size={36} />
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-center">
                        <BuyingWindowBadge window={c.buying_window} size="sm" />
                      </div>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {c.last_funding_stage ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {c.last_scored_at ? formatDate(c.last_scored_at) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="border-t border-slate-100 px-4 py-2 text-xs text-slate-400">
              {filtered.length} of {data?.total ?? 0} companies
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
