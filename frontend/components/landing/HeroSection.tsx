"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Play, LayoutDashboard } from "lucide-react";
import { HeroDashboardPreview } from "./HeroDashboardPreview";
import { Logo } from "@/components/common/Logo";
import { auth } from "@/lib/auth";

interface HeroSectionProps {
  onOpenDemo: () => void;
}

export function HeroSection({ onOpenDemo }: HeroSectionProps) {
  const [isLoggedIn] = useState(() => auth.isAuthenticated());

  return (
    <section className="relative min-h-screen pt-28 pb-20 md:pt-36 md:pb-28 flex flex-col items-center justify-center overflow-hidden bg-[#F5F7FB] dark:bg-[#030712] transition-colors">
      {/* Ambient Background Glow & Soft Lighting */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-tr from-indigo-200/30 via-purple-200/20 to-blue-200/20 dark:from-indigo-600/20 dark:via-purple-600/15 dark:to-blue-500/10 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute inset-0 bg-grid-line-pattern opacity-30 dark:opacity-30 pointer-events-none" />

      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 z-10 w-full flex flex-col items-center text-center">
        
        {/* 1. Official Brand Label (Small, Elegant, Premium, Minimal) */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-4"
        >
          <Logo href="/" type="full" size="sm" className="opacity-90 hover:opacity-100 transition-opacity" />
        </motion.div>

        {/* 2. Product Badge */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="inline-flex items-center gap-2 rounded-full border border-[#E6EAF2] dark:border-indigo-500/30 bg-white/80 dark:bg-indigo-500/10 px-4 py-1.5 backdrop-blur-md shadow-2xs mb-6"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-500 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-600 dark:bg-indigo-400"></span>
          </span>
          <span className="text-xs font-bold text-indigo-700 dark:text-indigo-300 tracking-wide">
            AI Predictive Revenue Intelligence Platform
          </span>
        </motion.div>

        {/* 3. Hero Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-black tracking-tight text-[#0F172A] dark:text-white leading-[1.06] max-w-4xl mb-6"
        >
          Know Who Will Buy{" "}
          <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 dark:from-sky-400 dark:via-indigo-300 dark:to-purple-400 bg-clip-text text-transparent">
            Before They Do.
          </span>
        </motion.h1>

        {/* 4. Supporting Description (Max 2â€“3 lines, readable width) */}
        <motion.p
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-base sm:text-lg md:text-xl text-[#475569] dark:text-slate-300 max-w-2xl leading-relaxed font-medium mb-8"
        >
          Avenor-AI continuously monitors buying signals across the market and predicts which companies are entering an active buying windowâ€”weeks before your competitors know they exist.
        </motion.p>

        {/* 5. CTA Row */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-3.5 w-full sm:w-auto mb-16"
        >
          {isLoggedIn ? (
            <Link
              href="/dashboard/feed"
              className="group relative inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 px-7 py-3.5 text-sm font-semibold text-white shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:opacity-95 active:scale-[0.98] transition-all cursor-pointer w-full sm:w-auto min-h-[48px]"
            >
              <LayoutDashboard className="h-4 w-4" />
              <span>Go to Dashboard</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          ) : (
            <Link
              href="/register"
              className="group relative inline-flex items-center justify-center gap-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 px-7 py-3.5 text-sm font-semibold text-white shadow-xl shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:opacity-95 active:scale-[0.98] transition-all cursor-pointer w-full sm:w-auto min-h-[48px]"
            >
              <span>Get Started Free</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          )}

          <button
            onClick={onOpenDemo}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-[#E6EAF2] dark:border-slate-800 bg-white dark:bg-slate-900/80 px-7 py-3.5 text-sm font-semibold text-[#0F172A] dark:text-slate-200 hover:bg-[#F3F6FC] dark:hover:bg-slate-800 transition-all shadow-2xs cursor-pointer w-full sm:w-auto min-h-[48px]"
          >
            <Play className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400 fill-indigo-600 dark:fill-indigo-400" />
            <span>Book Demo</span>
          </button>
        </motion.div>

        {/* 6. Interactive Dashboard Preview (~10% larger visual anchor) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 25 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="w-full max-w-5xl mb-14"
        >
          <HeroDashboardPreview />
        </motion.div>

        {/* 7. Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="w-full max-w-3xl pt-8 border-t border-[#E6EAF2] dark:border-slate-800/80 grid grid-cols-3 gap-6 text-center"
        >
          <div>
            <div className="text-2xl sm:text-3xl font-black text-[#0F172A] dark:text-white">$4.2B+</div>
            <div className="text-xs text-[#64748B] dark:text-slate-400 font-semibold mt-1">Pipeline Analyzed</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-black text-indigo-600 dark:text-indigo-400">3.4x</div>
            <div className="text-xs text-[#64748B] dark:text-slate-400 font-semibold mt-1">Conversion Lift</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-black text-[#0F172A] dark:text-white">40+</div>
            <div className="text-xs text-[#64748B] dark:text-slate-400 font-semibold mt-1">Signal Indicators</div>
          </div>
        </motion.div>

      </div>
    </section>
  );
}

