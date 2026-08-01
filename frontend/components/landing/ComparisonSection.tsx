"use client";

import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Sparkles, Layers } from "lucide-react";
import { COMPARISON_DATA } from "./constants";

export function ComparisonSection() {
  return (
    <section id="comparison" className="relative py-24 bg-white dark:bg-slate-950/80 border-t border-slate-200/90 dark:border-slate-900 overflow-hidden transition-colors">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 px-4 py-1.5 text-xs font-bold text-indigo-700 dark:text-indigo-300 shadow-2xs"
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Architecture Breakdown</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 dark:text-white tracking-tight leading-tight"
          >
            How Avenor-AI Unifies the{" "}
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 dark:from-sky-400 dark:via-indigo-300 dark:to-purple-400 bg-clip-text text-transparent">
              Modern GTM Stack
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-medium"
          >
            CRMs record history. Contact databases provide emails. Intent tools track isolated web spikes. Avenor unifies all three into predictive revenue action.
          </motion.p>
        </div>

        {/* Comparison Matrix Table */}
        <div className="overflow-x-auto rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-slate-900/60 backdrop-blur-xl shadow-md">
          <table className="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr className="border-b border-slate-200/80 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/80 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                <th className="p-4 sm:p-5 w-1/3">Capability / Dimension</th>
                <th className="p-4 sm:p-5 text-center">Legacy CRMs</th>
                <th className="p-4 sm:p-5 text-center">Prospecting Databases</th>
                <th className="p-4 sm:p-5 text-center">Isolated Intent Tools</th>
                <th className="p-4 sm:p-5 text-center bg-indigo-50/80 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border-x border-indigo-200 dark:border-indigo-500/30">
                  <span className="flex items-center justify-center gap-1 font-extrabold text-slate-900 dark:text-white">
                    <Sparkles className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                    Avenor-AI
                  </span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 text-xs sm:text-sm">
              {COMPARISON_DATA.map((row) => (
                <tr
                  key={row.capability}
                  className="hover:bg-slate-50/60 dark:hover:bg-slate-900/40 transition-colors"
                >
                  <td className="p-4 sm:p-5 font-bold text-slate-900 dark:text-slate-200">
                    {row.capability}
                    <div className="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 mt-0.5">
                      {row.highlight}
                    </div>
                  </td>

                  {/* CRM Column */}
                  <td className="p-4 sm:p-5 text-center text-slate-500 dark:text-slate-400 font-medium">
                    {typeof row.crm === "boolean" ? (
                      row.crm ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mx-auto" />
                      ) : (
                        <XCircle className="h-4 w-4 text-slate-300 dark:text-slate-600 mx-auto" />
                      )
                    ) : (
                      <span className="text-slate-500 dark:text-slate-400 text-xs">{row.crm}</span>
                    )}
                  </td>

                  {/* Prospecting Tools Column */}
                  <td className="p-4 sm:p-5 text-center text-slate-500 dark:text-slate-400 font-medium">
                    {typeof row.prospectingTools === "boolean" ? (
                      row.prospectingTools ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mx-auto" />
                      ) : (
                        <XCircle className="h-4 w-4 text-slate-300 dark:text-slate-600 mx-auto" />
                      )
                    ) : (
                      <span className="text-slate-500 dark:text-slate-400 text-xs">{row.prospectingTools}</span>
                    )}
                  </td>

                  {/* Intent Tools Column */}
                  <td className="p-4 sm:p-5 text-center text-slate-500 dark:text-slate-400 font-medium">
                    {typeof row.intentTools === "boolean" ? (
                      row.intentTools ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mx-auto" />
                      ) : (
                        <XCircle className="h-4 w-4 text-slate-300 dark:text-slate-600 mx-auto" />
                      )
                    ) : (
                      <span className="text-slate-500 dark:text-slate-400 text-xs">{row.intentTools}</span>
                    )}
                  </td>

                  {/* Avenor Column */}
                  <td className="p-4 sm:p-5 text-center bg-indigo-50/50 dark:bg-indigo-950/30 border-x border-indigo-200/80 dark:border-indigo-500/30 font-extrabold text-slate-900 dark:text-white">
                    {typeof row.avenor === "boolean" ? (
                      row.avenor ? (
                        <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400 mx-auto" />
                      ) : (
                        <XCircle className="h-4 w-4 text-slate-300 dark:text-slate-600 mx-auto" />
                      )
                    ) : (
                      <span className="text-indigo-700 dark:text-indigo-300 text-xs font-bold">{row.avenor}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </section>
  );
}

