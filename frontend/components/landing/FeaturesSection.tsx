"use client";

import { motion } from "framer-motion";
import {
  BrainCircuit,
  Sparkles,
  Radio,
  MailCheck,
  FileSpreadsheet,
  Compass,
  Layers,
  RefreshCw,
  TrendingUp,
  Bot,
  ArrowRight
} from "lucide-react";
import { CAPABILITIES } from "./constants";

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  BrainCircuit,
  Sparkles,
  Radio,
  MailCheck,
  FileSpreadsheet,
  Compass,
  Layers,
  RefreshCw,
  TrendingUp,
  Bot,
};

export function FeaturesSection() {
  return (
    <section id="capabilities" className="relative py-24 bg-white dark:bg-slate-950/90 border-t border-slate-200/90 dark:border-slate-900 overflow-hidden transition-colors">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 px-4 py-1.5 text-xs font-bold text-indigo-700 dark:text-indigo-300 shadow-2xs"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Complete Intelligence Suite</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 dark:text-white tracking-tight leading-tight"
          >
            Every AI Capability Needed to{" "}
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 dark:from-sky-400 dark:via-indigo-300 dark:to-purple-400 bg-clip-text text-transparent">
              Dominate Your Market
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-medium"
          >
            A unified suite of AI GTM capabilities engineered to eliminate guesswork and replace static lead lists with real-time buying intelligence.
          </motion.p>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {CAPABILITIES.map((cap, idx) => {
            const Icon = ICON_MAP[cap.iconName] || Sparkles;
            const isWide = cap.size === "wide";

            return (
              <motion.div
                key={cap.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.07 }}
                className={`group relative flex flex-col justify-between rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-[#F8FAFC] dark:bg-slate-900/40 p-6 backdrop-blur-xl hover:bg-white dark:hover:bg-slate-900/80 hover:border-indigo-300 dark:hover:border-indigo-500/40 shadow-2xs hover:shadow-md transition-all duration-300 ${
                  isWide ? "lg:col-span-2" : ""
                }`}
              >
                <div>
                  {/* Top Bar with Icon & Badge */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200/80 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-500/20 transition-all">
                      <Icon className="h-5 w-5" />
                    </div>

                    {cap.badge && (
                      <span className="rounded-full bg-purple-50 dark:bg-purple-500/20 border border-purple-200 dark:border-purple-500/40 px-3 py-0.5 text-[10px] font-black text-purple-700 dark:text-purple-300 uppercase tracking-wider">
                        {cap.badge}
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-black text-slate-900 dark:text-white mb-2 group-hover:text-indigo-600 dark:group-hover:text-indigo-300 transition-colors">
                    {cap.title}
                  </h3>

                  <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-medium">
                    {cap.description}
                  </p>
                </div>

                <div className="pt-6 mt-4 border-t border-slate-200/80 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  <span className="font-bold text-[11px]">Avenor-AI Capability</span>
                  <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </motion.div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
