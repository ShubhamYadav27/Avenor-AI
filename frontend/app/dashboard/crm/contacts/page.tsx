"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Contact, Search, Download, RefreshCw, Building2, ExternalLink,
  ChevronLeft, ChevronRight, Filter, Mail, Phone, Briefcase
} from "lucide-react";
import { useCrmContacts, useCrmSyncStatus, CrmContactItem } from "@/hooks/use-api";
import { exportToCsv } from "@/lib/export-csv";
function formatDistanceToNow(dateInput: string | Date | number, opts?: { addSuffix?: boolean }): string {
  try {
    const d = new Date(dateInput);
    if (isNaN(d.getTime())) return "recently";
    const now = new Date();
    const diffSeconds = Math.floor((now.getTime() - d.getTime()) / 1000);
    const suffix = opts?.addSuffix ? " ago" : "";
    if (diffSeconds < 60) return `just now`;
    if (diffSeconds < 3600) return `${Math.floor(diffSeconds / 60)} minutes${suffix}`;
    if (diffSeconds < 86400) return `${Math.floor(diffSeconds / 3600)} hours${suffix}`;
    return `${Math.floor(diffSeconds / 86400)} days${suffix}`;
  } catch {
    return "recently";
  }
}

export default function CrmContactsPage() {

  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const [selectedContact, setSelectedContact] = useState<CrmContactItem | null>(null);
  const pageSize = 25;

  const { data, isLoading, isError, refetch } = useCrmContacts({
    q: searchTerm,
    limit: pageSize,
    offset: (page - 1) * pageSize,
  });

  const { data: syncStatus } = useCrmSyncStatus();

  const contacts = data?.contacts || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / pageSize) || 1;

  const handleExportCsv = () => {
    exportToCsv(
      "salesforce_contacts",
      contacts.map((c) => ({
        "Full Name": c.full_name,
        "Email": c.email || "",
        "Phone": c.phone || "",
        "Title": c.title || "",
        "Company": c.company_name || "",
        "Company Domain": c.company_domain || "",
        "Salesforce Contact ID": c.external_id || "",
        "Synced At": c.synced_at || "",
      }))
    );
  };

  return (
    <div className="p-6 pb-20 space-y-6 max-w-7xl mx-auto w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
              <Contact className="h-5 w-5" />
            </span>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">CRM Contacts</h1>
            <span className="ml-2 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2.5 py-0.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
              {total} Synced Records
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Synchronized Salesforce contact records associated with monitored accounts.
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
            disabled={contacts.length === 0}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white disabled:opacity-50 transition-colors shadow-sm"
          >
            <Download className="h-3.5 w-3.5" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Controls: Search & Stats */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search contacts, title, email or company..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="text-xs text-slate-500 dark:text-slate-400">
          Showing <span className="font-semibold text-slate-900 dark:text-slate-200">{contacts.length}</span> of {total} contacts
        </div>
      </div>

      {/* Table Content */}
      {isLoading ? (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 p-8 text-center space-y-3 bg-white dark:bg-slate-900">
          <div className="h-6 w-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-500 dark:text-slate-400">Loading Salesforce contacts from canonical database...</p>
        </div>
      ) : isError ? (
        <div className="rounded-xl border border-red-200 dark:border-red-900/50 p-6 text-center bg-red-50/50 dark:bg-red-950/20 text-red-600 dark:text-red-400 text-xs">
          Failed to load CRM contacts. Please try refreshing.
        </div>
      ) : contacts.length === 0 ? (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 p-12 text-center bg-white dark:bg-slate-900 space-y-3">
          <Contact className="h-10 w-10 text-slate-400 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">No Contacts Found</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            {searchTerm ? `No contacts matching "${searchTerm}". Try adjusting your search.` : "Run a Salesforce sync to populate contacts."}
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-3 px-4">Contact Name</th>
                  <th className="py-3 px-4">Title & Dept</th>
                  <th className="py-3 px-4">Associated Company</th>
                  <th className="py-3 px-4">Email</th>
                  <th className="py-3 px-4">Phone</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/80 text-slate-700 dark:text-slate-300">
                {contacts.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => setSelectedContact(c)}
                    className="hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors cursor-pointer"
                  >
                    <td className="py-3.5 px-4 font-semibold text-slate-900 dark:text-slate-100">
                      <div className="flex items-center gap-2.5">
                        <div className="h-7 w-7 rounded-full bg-indigo-100 dark:bg-indigo-950 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-400 flex items-center justify-center font-bold text-[11px]">
                          {c.first_name?.[0] || c.last_name?.[0] || "C"}
                        </div>
                        <div>
                          <p className="font-semibold">{c.full_name}</p>
                          {c.external_id && (
                            <p className="text-[10px] text-slate-400 font-mono">SF: {c.external_id}</p>
                          )}
                        </div>
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      <p className="font-medium text-slate-800 dark:text-slate-200">{c.title || "—"}</p>
                      <p className="text-[10px] text-slate-400">{c.department || c.seniority || ""}</p>
                    </td>

                    <td className="py-3.5 px-4">
                      {c.company_id ? (
                        <Link
                          href={`/dashboard/companies/${c.company_id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="inline-flex items-center gap-1.5 font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
                        >
                          <Building2 className="h-3.5 w-3.5" />
                          <span>{c.company_name}</span>
                        </Link>
                      ) : (
                        <span className="text-slate-400 italic">{c.company_name || "Unassigned"}</span>
                      )}
                    </td>

                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-600 dark:text-slate-400">
                      {c.email ? (
                        <a href={`mailto:${c.email}`} onClick={(e) => e.stopPropagation()} className="hover:underline flex items-center gap-1">
                          <Mail className="h-3 w-3 text-slate-400" />
                          {c.email}
                        </a>
                      ) : (
                        "—"
                      )}
                    </td>

                    <td className="py-3.5 px-4 font-mono text-[11px]">
                      {c.phone ? (
                        <span className="flex items-center gap-1 text-slate-600 dark:text-slate-400">
                          <Phone className="h-3 w-3 text-slate-400" />
                          {c.phone}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedContact(c);
                        }}
                        className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 hover:underline"
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

      {/* Contact Detail Modal Drawer */}
      {selectedContact && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/50 backdrop-blur-sm p-4">
          <div className="h-full w-full max-w-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 overflow-y-auto space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Contact Details</h2>
              <button
                onClick={() => setSelectedContact(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-indigo-100 dark:bg-indigo-950 border border-indigo-300 dark:border-indigo-800 text-indigo-700 dark:text-indigo-400 flex items-center justify-center font-bold text-lg">
                  {selectedContact.first_name?.[0] || "C"}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white">{selectedContact.full_name}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{selectedContact.title || "No title specified"}</p>
                </div>
              </div>

              <div className="space-y-3 pt-2">
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Company</p>
                  {selectedContact.company_id ? (
                    <Link
                      href={`/dashboard/companies/${selectedContact.company_id}`}
                      className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1.5"
                    >
                      <Building2 className="h-4 w-4" />
                      <span>{selectedContact.company_name}</span>
                      <ExternalLink className="h-3 w-3" />
                    </Link>
                  ) : (
                    <p className="text-xs text-slate-600 dark:text-slate-400">{selectedContact.company_name || "Unassigned"}</p>
                  )}
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Contact Info</p>
                  <p className="text-xs text-slate-700 dark:text-slate-300 flex items-center gap-2">
                    <Mail className="h-3.5 w-3.5 text-slate-400" />
                    <span>{selectedContact.email || "No email"}</span>
                  </p>
                  <p className="text-xs text-slate-700 dark:text-slate-300 flex items-center gap-2">
                    <Phone className="h-3.5 w-3.5 text-slate-400" />
                    <span>{selectedContact.phone || "No phone"}</span>
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Salesforce Metadata</p>
                  <p className="text-xs text-slate-600 dark:text-slate-400 font-mono">External ID: {selectedContact.external_id || "N/A"}</p>
                  <p className="text-xs text-slate-600 dark:text-slate-400">Synced: {selectedContact.synced_at ? new Date(selectedContact.synced_at).toLocaleString() : "N/A"}</p>
                </div>

                {selectedContact.raw_data && Object.keys(selectedContact.raw_data).length > 0 && (
                  <div className="p-3 rounded-xl bg-slate-900 text-slate-100 text-[11px] font-mono space-y-1 overflow-x-auto max-h-48">
                    <p className="text-slate-400 text-[10px] uppercase font-sans font-bold">Raw Salesforce Record</p>
                    <pre>{JSON.stringify(selectedContact.raw_data, null, 2)}</pre>
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
