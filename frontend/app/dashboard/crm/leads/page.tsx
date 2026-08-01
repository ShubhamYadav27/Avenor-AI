"use client";

import { useState } from "react";
import {
  UserCheck, Search, Download, RefreshCw, Mail, Phone, Building2,
  ChevronLeft, ChevronRight, Filter, ExternalLink
} from "lucide-react";
import { useCrmLeads, CrmLeadItem } from "@/hooks/use-api";
import { exportToCsv } from "@/lib/export-csv";

export default function CrmLeadsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const [selectedLead, setSelectedLead] = useState<CrmLeadItem | null>(null);
  const pageSize = 25;

  const { data, isLoading, isError, refetch } = useCrmLeads({
    q: searchTerm,
    limit: pageSize,
    offset: (page - 1) * pageSize,
  });

  const leads = data?.leads || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / pageSize) || 1;

  const handleExportCsv = () => {
    exportToCsv(
      "salesforce_leads",
      leads.map((l) => ({
        "Lead Name": l.full_name,
        "Company": l.company_name || "",
        "Title": l.title || "",
        "Email": l.email || "",
        "Phone": l.phone || "",
        "Status": l.status,
        "Source": l.source,
        "Salesforce Lead ID": l.external_id || "",
        "Synced At": l.synced_at || "",
      }))
    );
  };

  return (
    <div className="p-6 pb-20 space-y-6 max-w-7xl mx-auto w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-lg bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400">
              <UserCheck className="h-5 w-5" />
            </span>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">CRM Leads</h1>
            <span className="ml-2 rounded-full bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 px-2.5 py-0.5 text-xs font-semibold text-blue-700 dark:text-blue-400">
              {total} Synced Leads
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Unconverted prospecting leads synchronized from Salesforce.
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
            disabled={leads.length === 0}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 transition-colors shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Controls: Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search lead name, company, email or title..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="text-xs text-slate-500 dark:text-slate-400">
          Showing <span className="font-semibold text-slate-900 dark:text-slate-200">{leads.length}</span> of {total} leads
        </div>
      </div>

      {/* Table Content */}
      {isLoading ? (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 p-8 text-center space-y-3 bg-white dark:bg-slate-900">
          <div className="h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-500 dark:text-slate-400">Loading Salesforce leads from canonical database...</p>
        </div>
      ) : isError ? (
        <div className="rounded-xl border border-red-200 dark:border-red-900/50 p-6 text-center bg-red-50/50 dark:bg-red-950/20 text-red-600 dark:text-red-400 text-xs">
          Failed to load leads. Please try refreshing.
        </div>
      ) : leads.length === 0 ? (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 p-12 text-center bg-white dark:bg-slate-900 space-y-3">
          <UserCheck className="h-10 w-10 text-slate-400 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">No Leads Found</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            {searchTerm ? `No leads matching "${searchTerm}".` : "Run a Salesforce sync to populate leads."}
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Lead Name</th>
                  <th className="py-3 px-4">Company</th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Email</th>
                  <th className="py-3 px-4">Status & Source</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/80 text-slate-700 dark:text-slate-300">
                {leads.map((l) => (
                  <tr
                    key={l.id}
                    onClick={() => setSelectedLead(l)}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors cursor-pointer"
                  >
                    <td className="py-3.5 px-4 font-semibold text-slate-900 dark:text-slate-100">
                      <div>
                        <p className="font-semibold text-slate-900 dark:text-slate-100">{l.full_name}</p>
                        {l.external_id && (
                          <p className="text-[10px] text-slate-400 font-mono">SF: {l.external_id}</p>
                        )}
                      </div>
                    </td>

                    <td className="py-3.5 px-4 font-medium text-slate-800 dark:text-slate-200">
                      {l.company_name || "—"}
                    </td>

                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400">
                      {l.title || "—"}
                    </td>

                    <td className="py-3.5 px-4 font-mono text-[11px]">
                      {l.email ? (
                        <a href={`mailto:${l.email}`} onClick={(e) => e.stopPropagation()} className="hover:underline flex items-center gap-1 text-slate-600 dark:text-slate-400">
                          <Mail className="h-3 w-3 text-slate-400" />
                          {l.email}
                        </a>
                      ) : (
                        "—"
                      )}
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 px-2.5 py-0.5 text-[11px] font-semibold text-blue-700 dark:text-blue-400">
                        {l.status}
                      </span>
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedLead(l);
                        }}
                        className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
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

      {/* Lead Detail Modal */}
      {selectedLead && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/50 backdrop-blur-sm p-4">
          <div className="h-full w-full max-w-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 overflow-y-auto space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Lead Details</h2>
              <button
                onClick={() => setSelectedLead(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{selectedLead.full_name}</h3>
                <p className="text-xs text-slate-500">{selectedLead.title || "No title specified"}</p>
              </div>

              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Company</p>
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{selectedLead.company_name || "Unassigned"}</p>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Contact Info</p>
                  <p className="text-xs text-slate-700 dark:text-slate-300 flex items-center gap-2">
                    <Mail className="h-3.5 w-3.5 text-slate-400" />
                    <span>{selectedLead.email || "No email"}</span>
                  </p>
                  <p className="text-xs text-slate-700 dark:text-slate-300 flex items-center gap-2">
                    <Phone className="h-3.5 w-3.5 text-slate-400" />
                    <span>{selectedLead.phone || "No phone"}</span>
                  </p>
                </div>

                {selectedLead.raw_data && Object.keys(selectedLead.raw_data).length > 0 && (
                  <div className="p-3 rounded-xl bg-slate-900 text-slate-100 text-[11px] font-mono space-y-1 overflow-x-auto max-h-56">
                    <p className="text-slate-400 text-[10px] uppercase font-sans font-bold">Raw Salesforce Lead Record</p>
                    <pre>{JSON.stringify(selectedLead.raw_data, null, 2)}</pre>
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
