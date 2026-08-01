"use client";

import { motion } from "framer-motion";
import { ShieldCheck, Lock, Server, UserCheck, Zap, Cpu } from "lucide-react";
import { ENTERPRISE_FEATURES } from "./constants";

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  ShieldCheck,
  Lock,
  Server,
  UserCheck,
  Zap,
  Cpu,
};

export function EnterpriseSection() {
  return (
    <section id="enterprise" className="relative py-24 bg-[#F8FAFC] dark:bg-slate-950 border-t border-slate-200/90 dark:border-slate-900 overflow-hidden transition-colors">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 px-4 py-1.5 text-xs font-bold text-indigo-700 dark:text-indigo-300 shadow-2xs"
          >
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>Enterprise Security & Architecture</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 dark:text-white tracking-tight leading-tight"
          >
            Built for Enterprise Trust, Security &{" "}
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 dark:from-sky-400 dark:via-indigo-300 dark:to-purple-400 bg-clip-text text-transparent">
              High-Scale GTM
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-medium"
          >
            Designed from day one to protect your customer data, enforce strict tenant isolation, and deliver resilient real-time pipeline automation.
          </motion.p>
        </div>

        {/* Enterprise Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {ENTERPRISE_FEATURES.map((item, idx) => {
            const Icon = ICON_MAP[item.iconName] || ShieldCheck;
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.08 }}
                className="p-6 rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/40 backdrop-blur-xl hover:border-indigo-300 dark:hover:border-indigo-500/30 hover:shadow-md transition-all shadow-2xs"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200/80 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">{item.title}</h3>
                <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-medium">
                  {item.description}
                </p>
              </motion.div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
