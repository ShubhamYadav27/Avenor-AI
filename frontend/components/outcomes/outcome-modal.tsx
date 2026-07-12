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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Log outcome</h2>
            <p className="text-xs text-slate-500">{companyName}</p>
          </div>
          <button onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:text-slate-600">
            <X className="h-4 w-4" />
          </button>
        </div>

        {done ? (
          <div className="flex flex-col items-center py-10">
            <CheckCircle className="mb-3 h-10 w-10 text-green-500" />
            <p className="text-sm font-semibold text-slate-800">Outcome logged</p>
            <p className="mt-1 text-xs text-slate-500">This data improves your model accuracy.</p>
            <button
              onClick={onClose}
              className="mt-4 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-5 space-y-4">
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
                {error}
              </div>
            )}

            <div>
              <label className="mb-2 block text-xs font-medium text-slate-700">
                What happened with this account?
              </label>
              <div className="grid grid-cols-2 gap-2">
                {OUTCOME_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setSelected(opt.value as OutcomeType)}
                    className={`rounded-lg border px-3 py-2 text-left text-xs font-medium transition-colors ${
                      selected === opt.value
                        ? opt.positive
                          ? "border-green-500 bg-green-50 text-green-700"
                          : "border-red-400 bg-red-50 text-red-700"
                        : "border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {selected === "closed_won" && (
              <div>
                <label className="mb-1.5 block text-xs font-medium text-slate-700">
                  Deal value (USD, optional)
                </label>
                <input
                  type="number"
                  value={dealValue}
                  onChange={(e) => setDealValue(e.target.value)}
                  placeholder="45000"
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-100"
                />
              </div>
            )}

            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-700">
                Notes (optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="What context is useful for future predictions?"
                rows={2}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none resize-none focus:border-violet-500 focus:ring-2 focus:ring-violet-100"
              />
            </div>

            <div className="flex gap-2 pt-1">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 rounded-lg border border-slate-200 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!selected || logOutcome.isPending}
                className="flex-1 rounded-lg bg-violet-600 py-2 text-sm font-semibold text-white hover:bg-violet-700 disabled:opacity-50"
              >
                {logOutcome.isPending ? "Saving…" : "Log outcome"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
