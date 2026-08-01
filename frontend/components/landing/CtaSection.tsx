"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Play, Sparkles, Target, ShieldCheck, LayoutDashboard } from "lucide-react";
import { auth } from "@/lib/auth";

interface CtaSectionProps {
  onOpenDemo: () => void;
}

export function CtaSection({ onOpenDemo }: CtaSectionProps) {
  const [isLoggedIn] = useState(() => auth.isAuthenticated());

  return (
    <section className="relative py-24 bg-[#F8FAFC] dark:bg-slate-950 overflow-hidden transition-colors">
      <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 z-10 text-center">
        
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 20 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="rounded-3xl border border-[#E6EAF2] dark:border-indigo-500/30 bg-white dark:bg-slate-900/70 p-8 sm:p-14 backdrop-blur-2xl shadow-xl space-y-6 transition-colors"
        >
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 px-4 py-1.5 backdrop-blur-md shadow-2xs">
            <Target className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
            <span className="text-xs font-bold text-indigo-700 dark:text-indigo-300 tracking-wide">
              Transform Your GTM Pipeline Today
            </span>
          </div>

          {/* Main Headline */}
          <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black text-slate-900 dark:text-white tracking-tight leading-tight">
            Start Predicting Revenue <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 dark:from-sky-400 dark:via-indigo-300 dark:to-purple-400 bg-clip-text text-transparent">
              Opportunities Today
            </span>
          </h2>

          {/* Subtext */}
          <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto font-medium leading-relaxed">
            Join forward-thinking B2B sales and revenue teams using Avenor-AI to know who is buying, when to engage, and how to win every deal.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            {isLoggedIn ? (
              <Link
                href="/dashboard/feed"
                className="group relative w-full sm:w-auto inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 px-8 py-4 text-base font-semibold text-white shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:opacity-95 active:scale-[0.98] transition-all cursor-pointer"
              >
                <LayoutDashboard className="h-4 w-4" />
                <span>Go to Dashboard</span>
                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            ) : (
              <Link
                href="/register"
                className="group relative w-full sm:w-auto inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 px-8 py-4 text-base font-semibold text-white shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:opacity-95 active:scale-[0.98] transition-all cursor-pointer"
              >
                <span>Get Started Free</span>
                <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            )}

            <button
              onClick={onOpenDemo}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950/80 px-8 py-4 text-base font-semibold text-slate-800 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 hover:border-slate-300 active:scale-[0.98] transition-all shadow-2xs cursor-pointer"
            >
              <Play className="h-4 w-4 text-indigo-600 dark:text-indigo-400 fill-indigo-600 dark:fill-indigo-400" />
              <span>Book Executive Demo</span>
            </button>
          </div>

          {/* Trust points */}
          <div className="pt-6 border-t border-[#E6EAF2] dark:border-slate-800/80 flex flex-wrap items-center justify-center gap-6 text-xs font-bold text-slate-600 dark:text-slate-400 transition-colors">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              No credit card required
            </span>
            <span className="flex items-center gap-1.5">
              <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              Includes 14-day full intent audit
            </span>
            <span className="flex items-center gap-1.5">
              <Target className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              Native HubSpot CRM integration
            </span>
          </div>

        </motion.div>

      </div>
    </section>
  );
}

