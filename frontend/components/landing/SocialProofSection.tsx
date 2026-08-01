"use client";

import { motion } from "framer-motion";
import { Building, TrendingUp, Users, Target, ShieldCheck, Zap } from "lucide-react";

export function SocialProofSection() {
  const audiences = [
    { title: "Series A–C SaaS", desc: "Scale GTM velocity post-funding", icon: Building },
    { title: "B2B Sales Teams", desc: "Zero manual account research", icon: Users },
    { title: "Revenue Operations", desc: "Clean signal-to-action routing", icon: Target },
    { title: "GTM Leadership", desc: "Predictable pipeline forecasting", icon: TrendingUp },
    { title: "Enterprise Growth", desc: "Multi-seat account intelligence", icon: Zap },
  ];

  return (
    <section className="relative py-16 border-y border-[#E6EAF2] dark:border-slate-800/80 bg-[#F8FAFC] dark:bg-slate-950/60 backdrop-blur-md transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Heading */}
        <div className="text-center mb-10">
          <p className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest mb-1.5">
            Engineered For High-Growth Revenue Teams
          </p>
          <h2 className="text-xl sm:text-2xl font-black text-[#0F172A] dark:text-white tracking-tight">
            Built for Modern Revenue & Sales Organizations
          </h2>
        </div>

        {/* Audience Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5 sm:gap-4">
          {audiences.map((aud, index) => {
            const Icon = aud.icon;
            return (
              <motion.div
                key={aud.title}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.08 }}
                className="group p-5 rounded-2xl border border-[#E6EAF2] dark:border-slate-800/80 bg-white dark:bg-slate-900/40 hover:bg-[#F3F6FC] dark:hover:bg-slate-900/80 hover:border-indigo-300 dark:hover:border-indigo-500/40 transition-all text-center flex flex-col items-center justify-center shadow-2xs hover:shadow-md"
              >
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-[#EEF2F8] dark:bg-indigo-500/10 border border-[#E6EAF2] dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 group-hover:scale-110 transition-transform">
                  <Icon className="h-4 w-4" />
                </div>
                <h3 className="text-xs font-bold text-[#0F172A] dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-white transition-colors">
                  {aud.title}
                </h3>
                <p className="text-[11px] font-medium text-[#64748B] dark:text-slate-400 mt-1 leading-snug">
                  {aud.desc}
                </p>
              </motion.div>
            );
          })}
        </div>

        {/* Subtle Trust Bar */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-6 sm:gap-10 text-[11px] font-bold text-[#64748B] dark:text-slate-400 pt-6 border-t border-[#E6EAF2] dark:border-slate-900">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
            99.8% Intent Correlation Accuracy
          </span>
          <span className="flex items-center gap-1.5">
            <Zap className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
            Real-time HubSpot CRM Sync
          </span>
          <span className="flex items-center gap-1.5">
            <Target className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
            Zero Manual Data Entry
          </span>
        </div>
      </div>
    </section>
  );
}
