"use client";

import { useState } from "react";
import Link from "next/link";
import {
  DollarSign, Search, Download, RefreshCw, Building2, ExternalLink,
  ChevronLeft, ChevronRight, Filter, TrendingUp, CheckCircle, XCircle, Clock
} from "lucide-react";
import { useCrmDeals, CrmDealItem } from "@/hooks/use-api";
import { exportToCsv } from "@/lib/export-csv";

export default function CrmDealsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [stageFilter, setStageFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [selectedDeal, setSelectedDeal] = useState<CrmDealItem | null>(null);
  const pageSize = 25;

  const { data, isLoading, isError, refetch } = useCrmDeals({
    q: searchTerm,
    stage: stageFilter !== "all" ? stageFilter : undefined,
    limit: pageSize,
    offset: (page - 1) * pageSize,
  });

  const deals = data?.opportunities || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / pageSize) || 1;

  const totalPipelineValue = deals.reduce((sum, d) => sum + (d.amount_usd || 0), 0);

  const handleExportCsv = () => {
    exportToCsv(
      "salesforce_deals",
      deals.map((d) => ({
        "Deal Name": d.name,
        "Stage": d.stage || "Unspecified",
        "Amount (USD)": d.amount_usd || 0,
        "Close Date": d.close_date || "",
        "Company Name": d.company_name,
        "Company Domain": d.company_domain || "",
        "Salesforce Opportunity ID": d.external_id || "",
        "Closed Won": d.is_closed_won ? "Yes" : "No",
        "Closed Lost": d.is_closed_lost ? "Yes" : "No",
      }))
    );
  };

  const STAGES = [
    "all",
    "Value Proposition",
    "Prospecting",
    "Qualification",
    "Needs Analysis",
    "Proposal/Price Quote",
    "Negotiation/Review",
    "Closed Won",
    "Closed Lost",
  ];

  return (
    <div className="p-6 pb-20 space-y-6 max-w-7xl mx-auto w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <DollarSign className="h-5 w-5" />
            </span>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Deals & Opportunities</h1>
            <span className="ml-2 rounded-full bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/30 px-2.5 py-0.5 text-xs font-semibold text-emerald-700 dark:text-emerald-400">
              {total} Synced Deals
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Canonical pipeline synchronized from Salesforce Opportunities.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
          <button
            onClick={handleExportCsv}
            disabled={deals.length === 0}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white disabled:opacity-50 transition-colors shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Pipeline Summary Metrics Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Synced Deals</p>
            <p className="text-xl font-bold text-slate-900 dark:text-white mt-0.5">{total}</p>
          </div>
          <TrendingUp className="h-8 w-8 text-emerald-500/30" />
        </div>

        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Page Pipeline Value</p>
            <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">
              ${totalPipelineValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </div>
          <DollarSign className="h-8 w-8 text-emerald-500/30" />
        </div>

        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between">
          <div>
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Primary Data Source</p>
            <p className="text-sm font-bold text-slate-900 dark:text-white mt-1 flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              Salesforce CRM
            </p>
          </div>
          <Building2 className="h-8 w-8 text-indigo-500/30" />
        </div>
      </div>

      {/* Controls: Search & Stage Filter */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full sm:w-auto flex-1">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search deal name, stage or company..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(1);
              }}
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="h-3.5 w-3.5 text-slate-400" />
            <select
              value={stageFilter}
              onChange={(e) => {
                setStageFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 focus:outline-none"
            >
              {STAGES.map((s) => (
                <option key={s} value={s}>
                  {s === "all" ? "All Stages" : s}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="text-xs text-slate-500 dark:text-slate-400">
          Showing <span className="font-semibold text-slate-900 dark:text-slate-200">{deals.length}</span> of {total} deals
        </div>
      </div>

      {/* Table Content */}
      {isLoading ? (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 p-8 text-center space-y-3 bg-white dark:bg-slate-900">
          <div className="h-6 w-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-500 dark:text-slate-400">Loading Salesforce opportunities from canonical database...</p>
        </div>
      ) : isError ? (
        <div className="rounded-xl border border-red-200 dark:border-red-900/50 p-6 text-center bg-red-50/50 dark:bg-red-950/20 text-red-600 dark:text-red-400 text-xs">
          Failed to load deals. Please try refreshing.
        </div>
      ) : deals.length === 0 ? (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 p-12 text-center bg-white dark:bg-slate-900 space-y-3">
          <DollarSign className="h-10 w-10 text-slate-400 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">No Deals Found</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            {searchTerm || stageFilter !== "all"
              ? "No deals matching your filter criteria."
              : "Run a Salesforce sync to populate deals."}
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Opportunity Name</th>
                  <th className="py-3 px-4">Stage</th>
                  <th className="py-3 px-4">Amount (USD)</th>
                  <th className="py-3 px-4">Associated Company</th>
                  <th className="py-3 px-4">Close Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/80 text-slate-700 dark:text-slate-300">
                {deals.map((d) => (
                  <tr
                    key={d.id}
                    onClick={() => setSelectedDeal(d)}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors cursor-pointer"
                  >
                    <td className="py-3.5 px-4 font-semibold text-slate-900 dark:text-slate-100">
                      <div>
                        <p className="font-semibold text-slate-900 dark:text-slate-100">{d.name}</p>
                        {d.external_id && (
                          <p className="text-[10px] text-slate-400 font-mono">SF: {d.external_id}</p>
                        )}
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      {d.is_closed_won ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/30 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400">
                          <CheckCircle className="h-3 w-3" />
                          Closed Won
                        </span>
                      ) : d.is_closed_lost ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 px-2.5 py-0.5 text-[11px] font-semibold text-red-700 dark:text-red-400">
                          <XCircle className="h-3 w-3" />
                          Closed Lost
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 px-2.5 py-0.5 text-[11px] font-semibold text-blue-700 dark:text-blue-400">
                          <Clock className="h-3 w-3" />
                          {d.stage || "In Progress"}
                        </span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 font-bold text-slate-900 dark:text-slate-100">
                      {d.amount_usd !== null && d.amount_usd !== undefined
                        ? `$${d.amount_usd.toLocaleString()}`
                        : "—"}
                    </td>

                    <td className="py-3.5 px-4">
                      {d.company_id ? (
                        <Link
                          href={`/dashboard/companies/${d.company_id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="inline-flex items-center gap-1.5 font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
                        >
                          <Building2 className="h-3.5 w-3.5" />
                          <span>{d.company_name}</span>
                        </Link>
                      ) : (
                        <span className="text-slate-400 italic">{d.company_name || "Unassigned"}</span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400">
                      {d.close_date ? new Date(d.close_date).toLocaleDateString() : "—"}
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedDeal(d);
                        }}
                        className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-xs">
            <span className="text-slate-500">
              Page {page} of {totalPages}
            </span>
            <div className="flex items-center gap-1">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="p-1.5 rounded border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="p-1.5 rounded border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Deal Detail Drawer Modal */}
      {selectedDeal && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/50 backdrop-blur-sm p-4">
          <div className="h-full w-full max-w-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 overflow-y-auto space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Opportunity Details</h2>
              <button
                onClick={() => setSelectedDeal(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{selectedDeal.name}</h3>
                <p className="text-xs text-slate-500 font-mono">External ID: {selectedDeal.external_id || "N/A"}</p>
              </div>

              <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 space-y-1">
                <p className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Opportunity Value</p>
                <p className="text-2xl font-extrabold text-emerald-700 dark:text-emerald-300">
                  {selectedDeal.amount_usd !== null ? `$${selectedDeal.amount_usd.toLocaleString()}` : "Unspecified"}
                </p>
              </div>

              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Stage & Status</p>
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{selectedDeal.stage || "Unspecified"}</p>
                  <p className="text-xs text-slate-500">
                    Close Date: {selectedDeal.close_date ? new Date(selectedDeal.close_date).toLocaleDateString() : "N/A"}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Associated Company</p>
                  {selectedDeal.company_id ? (
                    <Link
                      href={`/dashboard/companies/${selectedDeal.company_id}`}
                      className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1.5"
                    >
                      <Building2 className="h-4 w-4" />
                      <span>{selectedDeal.company_name}</span>
                      <ExternalLink className="h-3 w-3" />
                    </Link>
                  ) : (
                    <p className="text-xs text-slate-600 dark:text-slate-400">{selectedDeal.company_name || "Unassigned"}</p>
                  )}
                </div>

                {selectedDeal.raw_data && Object.keys(selectedDeal.raw_data).length > 0 && (
                  <div className="p-3 rounded-xl bg-slate-900 text-slate-100 text-[11px] font-mono space-y-1 overflow-x-auto max-h-56">
                    <p className="text-slate-400 text-[10px] uppercase font-sans font-bold">Raw Salesforce Record</p>
                    <pre>{JSON.stringify(selectedDeal.raw_data, null, 2)}</pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
