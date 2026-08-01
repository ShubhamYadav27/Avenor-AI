"use client";

import { motion } from "framer-motion";
import { AlertTriangle, XCircle, CheckCircle2, ArrowRight, Zap } from "lucide-react";
import { PROBLEM_CARDS } from "./constants";

export function ProblemSection() {
  return (
    <section id="problem" className="relative py-24 bg-white dark:bg-slate-950 overflow-hidden transition-colors">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 rounded-full border border-red-200 dark:border-red-500/20 bg-red-50 dark:bg-red-500/10 px-4 py-1.5 text-xs font-bold text-red-700 dark:text-red-400 shadow-2xs"
          >
            <AlertTriangle className="h-3.5 w-3.5" />
            <span>The GTM Bottleneck</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-black text-[#0F172A] dark:text-white tracking-tight leading-tight"
          >
            Why Modern Sales Teams Miss{" "}
            <span className="bg-gradient-to-r from-red-600 via-indigo-600 to-purple-600 dark:from-red-400 dark:via-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
              70% of Buying Windows
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-base sm:text-lg text-[#475569] dark:text-slate-300 leading-relaxed font-medium"
          >
            CRMs were built 20 years ago as database logbooks to record past meetings. They do not tell you who is ready to buy today, leaving your reps pitching cold while competitors steal active deals.
          </motion.p>
        </div>

        {/* Problem Comparison Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {PROBLEM_CARDS.map((card, idx) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 25 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: idx * 0.15 }}
              className="relative flex flex-col justify-between rounded-2xl border border-[#E6EAF2] dark:border-slate-800/80 bg-[#F8FAFC] dark:bg-slate-900/50 p-6 backdrop-blur-xl hover:border-indigo-300 dark:hover:border-indigo-500/40 shadow-xs hover:shadow-md transition-all duration-300"
            >
              <div>
                {/* Badge */}
                <div className="flex items-center justify-between mb-4">
                  <span className="rounded-full bg-[#EEF2F8] dark:bg-indigo-500/10 border border-[#E6EAF2] dark:border-indigo-500/30 px-3 py-1 text-[11px] font-bold text-indigo-700 dark:text-indigo-400">
                    {card.badge}
                  </span>
                  <span className="text-xs font-bold text-emerald-800 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 px-2.5 py-0.5 rounded-full">
                    {card.impact}
                  </span>
                </div>

                <h3 className="text-lg font-black text-[#0F172A] dark:text-white mb-2 leading-snug">
                  {card.title}
                </h3>
                <p className="text-xs font-medium text-[#64748B] dark:text-slate-400 mb-6 leading-relaxed">
                  {card.subtitle}
                </p>

                {/* Legacy CRM Side */}
                <div className="rounded-xl bg-white dark:bg-slate-950/80 p-4 border border-[#E6EAF2] dark:border-slate-800/80 mb-3 space-y-1.5 shadow-2xs">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-red-600 dark:text-red-400">
                    <XCircle className="h-3.5 w-3.5 shrink-0" />
                    <span>Traditional CRM Limitations</span>
                  </div>
                  <p className="text-xs text-[#475569] dark:text-slate-400 leading-relaxed pl-5 font-medium">
                    {card.crmReality}
                  </p>
                </div>

                {/* Avenor AI Side */}
                <div className="rounded-xl bg-[#EEF2F8] dark:bg-indigo-950/30 p-4 border border-indigo-200/80 dark:border-indigo-500/30 space-y-1.5">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-700 dark:text-indigo-300">
                    <CheckCircle2 className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
                    <span>Avenor Predictive Solution</span>
                  </div>
                  <p className="text-xs text-[#0F172A] dark:text-slate-200 leading-relaxed pl-5 font-semibold">
                    {card.avenorPrediction}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom Callout Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 rounded-2xl border border-[#E6EAF2] dark:border-indigo-500/20 bg-[#F8FAFC] dark:bg-slate-900/60 p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-md"
        >
          <div className="space-y-1.5 text-center md:text-left">
            <h4 className="text-lg font-black text-[#0F172A] dark:text-white flex items-center justify-center md:justify-start gap-2">
              <Zap className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
              Transform your GTM stack from Reactive Record-Keeping to Predictive Intelligence
            </h4>
            <p className="text-xs sm:text-sm text-[#475569] dark:text-slate-400 max-w-2xl font-medium">
              Stop letting reps manually guess intent. Avenor connects intent detection directly to automated sales briefings.
            </p>
          </div>
          <a
            href="#how-it-works"
            className="shrink-0 inline-flex items-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 px-5 py-3 text-xs font-bold text-white transition-all shadow-md shadow-indigo-600/30 cursor-pointer"
          >
            <span>See How Avenor Works</span>
            <ArrowRight className="h-4 w-4" />
          </a>
        </motion.div>

      </div>
    </section>
  );
}


