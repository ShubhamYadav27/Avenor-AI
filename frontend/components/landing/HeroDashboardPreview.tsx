"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Sparkles,
  TrendingUp,
  Zap,
  Clock,
  ChevronRight,
  ShieldCheck,
  Flame
} from "lucide-react";
import { HERO_SIGNALS } from "./constants";

export function HeroDashboardPreview() {
  const [activeSignalIndex, setActiveSignalIndex] = useState(0);
  const [activeTab, setActiveTab] = useState<"live" | "intelligence" | "email">("live");

  const currentSignal = HERO_SIGNALS[activeSignalIndex];

  return (
    <div className="relative w-full rounded-2xl border border-slate-800/80 bg-slate-900/80 p-3 sm:p-5 shadow-2xl backdrop-blur-xl glow-indigo">
      {/* Top Glass Mac-style Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/60 mb-4">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <div className="h-3 w-3 rounded-full bg-red-500/80" />
            <div className="h-3 w-3 rounded-full bg-amber-500/80" />
            <div className="h-3 w-3 rounded-full bg-emerald-500/80" />
          </div>
          <span className="ml-2 text-xs font-medium text-slate-400 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Avenor Engine v2.4 â€¢ Live Intent Stream
          </span>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1 bg-slate-950/60 p-1 rounded-lg border border-slate-800/80 text-[11px]">
          <button
            onClick={() => setActiveTab("live")}
            className={`px-2.5 py-1 rounded-md font-medium transition-all ${
              activeTab === "live"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Signals Feed
          </button>
          <button
            onClick={() => setActiveTab("intelligence")}
            className={`px-2.5 py-1 rounded-md font-medium transition-all ${
              activeTab === "intelligence"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Intent Score
          </button>
          <button
            onClick={() => setActiveTab("email")}
            className={`px-2.5 py-1 rounded-md font-medium transition-all ${
              activeTab === "email"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            AI Draft
          </button>
        </div>
      </div>

      {/* Main Preview Content */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
        {/* Left Side Feed Column */}
        <div className="md:col-span-5 space-y-2.5">
          <div className="flex items-center justify-between px-1">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Activity className="h-3 w-3 text-indigo-400" />
              High-Intent Accounts
            </span>
            <span className="text-[10px] text-slate-500">4 New</span>
          </div>

          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
            {HERO_SIGNALS.map((sig, idx) => {
              const isSelected = idx === activeSignalIndex;
              return (
                <button
                  key={sig.id}
                  onClick={() => setActiveSignalIndex(idx)}
                  className={`w-full text-left p-3 rounded-xl border transition-all ${
                    isSelected
                      ? "border-indigo-500/50 bg-indigo-950/30 shadow-md shadow-indigo-500/10"
                      : "border-slate-800/60 bg-slate-950/40 hover:bg-slate-800/40 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <div className="flex items-center gap-2">
                      <div className="h-6 w-6 rounded-md bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-xs font-bold text-indigo-300">
                        {sig.company[0]}
                      </div>
                      <div>
                        <span className="text-xs font-bold text-slate-100">{sig.company}</span>
                        <span className="text-[10px] text-slate-400 ml-1.5">{sig.domain}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 border border-emerald-500/20">
                      <Flame className="h-2.5 w-2.5 text-emerald-400" />
                      <span className="text-[10px] font-bold text-emerald-400">{sig.score}</span>
                    </div>
                  </div>

                  <p className="text-[11px] font-medium text-slate-300 line-clamp-1">
                    {sig.title}
                  </p>
                  <div className="flex items-center justify-between mt-2 text-[10px] text-slate-500">
                    <span className="inline-flex items-center gap-1 text-indigo-400 font-medium">
                      <Zap className="h-2.5 w-2.5" />
                      {sig.signalType}
                    </span>
                    <span>{sig.timeAgo}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Side Intelligence Detail Column */}
        <div className="md:col-span-7 rounded-xl border border-slate-800/80 bg-slate-950/60 p-4 flex flex-col justify-between">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentSignal.id + activeTab}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className="space-y-3"
            >
              {/* Account Header */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-800/60">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-white">{currentSignal.company}</h4>
                    <span className="rounded-md bg-indigo-500/10 px-2 py-0.5 text-[10px] font-semibold text-indigo-400 border border-indigo-500/30">
                      {currentSignal.buyingStage}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">{currentSignal.description}</p>
                </div>
              </div>

              {/* Dynamic View by activeTab */}
              {activeTab === "live" && (
                <div className="space-y-2.5">
                  <div className="rounded-lg bg-indigo-950/40 p-3 border border-indigo-500/20">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-300 mb-1">
                      <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
                      Avenor AI Predictive Analysis
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      High-probability buying window detected. Signal correlation indicates an active vendor evaluation cycle. Expected outreach conversion is <span className="font-semibold text-emerald-400">3.4x baseline</span>.
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                      Recent Signal Timeline
                    </span>
                    <div className="space-y-1 text-[11px]">
                      <div className="flex items-center gap-2 text-slate-300 bg-slate-900/60 px-2.5 py-1.5 rounded-md border border-slate-800/40">
                        <Clock className="h-3 w-3 text-indigo-400 shrink-0" />
                        <span>VP of Sales hired from Tier-1 SaaS SaaS company</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-300 bg-slate-900/60 px-2.5 py-1.5 rounded-md border border-slate-800/40">
                        <TrendingUp className="h-3 w-3 text-emerald-400 shrink-0" />
                        <span>Job board: Added 6 new Enterprise AE requisitions</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "intelligence" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/90 border border-slate-800">
                    <div>
                      <div className="text-xs text-slate-400 font-medium">Revenue Opportunity Score</div>
                      <div className="text-2xl font-black text-white mt-0.5 flex items-baseline gap-1">
                        {currentSignal.score}
                        <span className="text-xs text-slate-400 font-normal">/ 100</span>
                      </div>
                    </div>
                    <div className="h-12 w-12 rounded-full border-4 border-indigo-500 border-t-emerald-400 flex items-center justify-center font-bold text-xs text-indigo-300">
                      Top 1%
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px]">
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                      <div className="text-slate-400 text-[10px]">Intent Horizon</div>
                      <div className="text-emerald-400 font-semibold mt-0.5">Next 14 Days</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
                      <div className="text-slate-400 text-[10px]">ICP Fit Match</div>
                      <div className="text-indigo-400 font-semibold mt-0.5">99.4% Match</div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "email" && (
                <div className="space-y-2">
                  <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                    <span>Generated Signal-Based Outreach</span>
                    <span className="text-indigo-400">Persona: VP Sales</span>
                  </div>
                  <div className="rounded-lg bg-slate-900/90 p-3 border border-slate-800 text-[11px] font-mono text-slate-300 leading-relaxed">
                    <p className="font-sans font-semibold text-white mb-1.5 border-b border-slate-800 pb-1">
                      Subject: Quick note on {currentSignal.company}&apos;s AE team expansion
                    </p>
                    <p className="font-sans text-slate-300 text-[11px]">
                      Hi Marcus, saw the news on expanding your GTM team! When adding 6 new AEs post-Series B, ramp time is usually the biggest pipeline bottleneck. Avenor predicts intent windows so your new AEs book meetings in week 2.
                    </p>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          {/* Action Bar Footer */}
          <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs">
            <span className="text-[11px] text-slate-400 flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-indigo-400" />
              Auto-synced with HubSpot CRM
            </span>
            <button
              onClick={() => setActiveSignalIndex((activeSignalIndex + 1) % HERO_SIGNALS.length)}
              className="inline-flex items-center gap-1 font-semibold text-indigo-400 hover:text-indigo-300 transition-colors text-[11px]"
            >
              <span>Next Signal</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

