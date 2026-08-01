"use client";

import { useState } from "react";
import { X, CheckCircle } from "lucide-react";
import { useLogOutcome } from "@/hooks/use-api";
import { getErrorMessage } from "@/lib/api-client";
import { OUTCOME_OPTIONS } from "@/lib/utils";
import type { OutcomeType } from "@/types/api";

interface Props {
  companyId: string;
  companyName: string;
  onClose: () => void;
}

export function OutcomeModal({ companyId, companyName, onClose }: Props) {
  const logOutcome = useLogOutcome();
  const [selected, setSelected] = useState<OutcomeType | "">("");
  const [notes, setNotes] = useState("");
  const [dealValue, setDealValue] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selected) return;
    setError("");
    try {
      await logOutcome.mutateAsync({
        company_id: companyId,
        outcome_type: selected as OutcomeType,
        notes: notes || undefined,
        deal_value_usd: dealValue ? parseFloat(dealValue) : undefined,
      });
      setDone(true);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 dark:bg-slate-950/60 backdrop-blur-xs px-4"
      role="dialog"
      aria-modal="true"
      aria-label={`Log outcome for ${companyName}`}
    >
      <div className="w-full max-w-md rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl transition-colors">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 px-5 py-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">Log Outcome</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">{companyName}</p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 dark:text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
            aria-label="Close modal"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {done ? (
          <div className="flex flex-col items-center py-10">
            <CheckCircle className="mb-3 h-10 w-10 text-emerald-600 dark:text-emerald-400" />
            <p className="text-sm font-bold text-slate-900 dark:text-white">Outcome Logged</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">This data improves Avenor-AI engine prediction accuracy.</p>
            <button
              onClick={onClose}
              className="mt-5 rounded-xl bg-indigo-600 px-6 py-2 text-xs font-semibold text-white hover:bg-indigo-700 transition-colors shadow-xs cursor-pointer"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-5 space-y-4">
            {error && (
              <div className="rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 px-3 py-2 text-xs font-semibold text-red-700 dark:text-red-400">
                {error}
              </div>
            )}

            <div>
              <label className="mb-2 block text-xs font-semibold text-slate-700 dark:text-slate-300">
                What happened with this account?
              </label>
              <div className="grid grid-cols-2 gap-2">
                {OUTCOME_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setSelected(opt.value as OutcomeType)}
                    className={`rounded-lg border px-3 py-2 text-left text-xs font-medium transition-all cursor-pointer ${
                      selected === opt.value
                        ? opt.positive
                          ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-800 dark:text-emerald-300 font-semibold"
                          : "border-red-400 bg-red-50 dark:bg-red-500/10 text-red-800 dark:text-red-300 font-semibold"
                        : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {selected === "closed_won" && (
              <div>
                <label className="mb-1.5 block text-xs font-medium text-slate-700 dark:text-slate-300">
                  Deal Value (USD, optional)
                </label>
                <input
                  type="number"
                  value={dealValue}
                  onChange={(e) => setDealValue(e.target.value)}
                  placeholder="45000"
                  className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-xs text-slate-900 dark:text-white outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:border-indigo-600 dark:focus:border-indigo-400 focus:ring-1 focus:ring-indigo-100 dark:focus:ring-indigo-500/20 transition-colors"
                />
              </div>
            )}

            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-700 dark:text-slate-300">
                Notes (optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="What context is useful for future predictions?"
                rows={2}
                className="w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-3 py-2 text-xs text-slate-900 dark:text-white outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500 resize-none focus:border-indigo-600 dark:focus:border-indigo-400 focus:ring-1 focus:ring-indigo-100 dark:focus:ring-indigo-500/20 transition-colors"
              />
            </div>

            <div className="flex gap-2 pt-1">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 py-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!selected || logOutcome.isPending}
                className="flex-1 rounded-xl bg-indigo-600 py-2.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-xs cursor-pointer"
              >
                {logOutcome.isPending ? "Saving…" : "Log Outcome"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
