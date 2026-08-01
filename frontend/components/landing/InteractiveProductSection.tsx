"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Target,
  FileText,
  Compass,
  Sparkles,
  Check,
  Copy,
  Clock,
  Mail,
  Flame
} from "lucide-react";
import { INTERACTIVE_TABS } from "./constants";

export function InteractiveProductSection() {
  const [activeTabId, setActiveTabId] = useState(INTERACTIVE_TABS[0].id);
  const [copiedEmail, setCopiedEmail] = useState(false);

  const activeTab = INTERACTIVE_TABS.find((t) => t.id === activeTabId) || INTERACTIVE_TABS[0];

  const handleCopyEmail = () => {
    navigator.clipboard.writeText(
      `${activeTab.recommendedEmail.subject}\n\n${activeTab.recommendedEmail.body}`
    );
    setCopiedEmail(true);
    setTimeout(() => setCopiedEmail(false), 2000);
  };

  return (
    <section id="product" className="relative py-24 bg-[#F8FAFC] dark:bg-slate-950 overflow-hidden transition-colors">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14 space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 px-4 py-1.5 text-xs font-bold text-indigo-700 dark:text-indigo-300 shadow-2xs"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Interactive Product Experience</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 dark:text-white tracking-tight leading-tight"
          >
            Experience the Avenor-AI{" "}
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 dark:from-sky-400 dark:via-indigo-300 dark:to-purple-400 bg-clip-text text-transparent">
              Revenue Intelligence Engine
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-medium"
          >
            Click through the live preview below to explore how Avenor-AI continuously profiles accounts, tracks buying signals, and generates executive briefings.
          </motion.p>
        </div>

        {/* Interactive Workspace Container */}
        <div className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/80 p-4 sm:p-6 shadow-xl backdrop-blur-xl">
          
          {/* Top Tab Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-200/80 dark:border-slate-800/80 mb-6">
            <div className="flex flex-wrap items-center gap-2">
              {INTERACTIVE_TABS.map((tab) => {
                const isActive = tab.id === activeTabId;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTabId(tab.id)}
                    className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      isActive
                        ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                        : "bg-slate-100 dark:bg-slate-950/60 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200/60"
                    }`}
                  >
                    {tab.id === "account-feed" && <Activity className="h-3.5 w-3.5" />}
                    {tab.id === "buying-window" && <Target className="h-3.5 w-3.5" />}
                    {tab.id === "ai-briefing" && <FileText className="h-3.5 w-3.5" />}
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="hidden sm:flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Live Account Feed • 100% Real-Time</span>
            </div>
          </div>

          {/* Tab Body Grid */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-6"
            >
              {/* Left Column: Account Profile & Signals */}
              <div className="lg:col-span-5 space-y-4">
                <div className="rounded-xl border border-slate-200/90 dark:border-slate-800/80 bg-[#F8FAFC] dark:bg-slate-950/60 p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-600 dark:text-indigo-400 font-bold text-base">
                        {activeTab.companyName[0]}
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-slate-900 dark:text-white">{activeTab.companyName}</h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Series B SaaS • 120-250 Employees</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold">Intent Score</div>
                      <div className="text-xl font-black text-emerald-600 dark:text-emerald-400 flex items-center justify-end gap-1">
                        <Flame className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                        {activeTab.score}/100
                      </div>
                    </div>
                  </div>

                  <div className="rounded-lg bg-indigo-50 dark:bg-indigo-950/30 p-3 border border-indigo-200/80 dark:border-indigo-500/20 space-y-1">
                    <div className="text-[11px] font-bold text-indigo-700 dark:text-indigo-300 flex items-center gap-1.5">
                      <Clock className="h-3 w-3 text-indigo-600 dark:text-indigo-400" />
                      Buying Window Status
                    </div>
                    <p className="text-xs font-bold text-slate-900 dark:text-white">{activeTab.buyingWindow}</p>
                  </div>

                  <div className="space-y-1.5">
                    <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Detected Signal Summary
                    </span>
                    <p className="text-xs text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900/60 p-3 rounded-lg border border-slate-200 dark:border-slate-800/60 leading-relaxed font-medium">
                      {activeTab.signalSummary}
                    </p>
                  </div>
                </div>

                {/* AI Sales Coach Advice Box */}
                <div className="rounded-xl border border-slate-200/90 dark:border-slate-800/80 bg-[#F8FAFC] dark:bg-slate-950/60 p-4 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-amber-700 dark:text-amber-400">
                    <Compass className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                    <span>AI Sales Coach Playbook</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
                    {activeTab.coachAdvice}
                  </p>
                </div>
              </div>

              {/* Right Column: AI Briefing & Generated Email */}
              <div className="lg:col-span-7 space-y-4">
                {/* AI Executive Briefing */}
                <div className="rounded-xl border border-slate-200/90 dark:border-slate-800/80 bg-[#F8FAFC] dark:bg-slate-950/60 p-4 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-indigo-700 dark:text-indigo-300">
                    <FileText className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                    <span>AI Executive Deal Briefing</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed bg-white dark:bg-slate-900/60 p-3 rounded-lg border border-slate-200 dark:border-slate-800/60 font-medium">
                    {activeTab.aiBriefing}
                  </p>
                </div>

                {/* Signal-Based Outreach Email */}
                <div className="rounded-xl border border-slate-200/90 dark:border-slate-800/80 bg-[#F8FAFC] dark:bg-slate-950/60 p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white">
                      <Mail className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                      <span>Recommended Signal Outreach Draft</span>
                    </div>

                    <button
                      onClick={handleCopyEmail}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-1 text-[11px] font-bold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
                    >
                      {copiedEmail ? (
                        <>
                          <Check className="h-3 w-3 text-emerald-600 dark:text-emerald-400" />
                          <span className="text-emerald-600 dark:text-emerald-400 font-bold">Copied to Clipboard</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-3 w-3" />
                          <span>Copy Email Draft</span>
                        </>
                      )}
                    </button>
                  </div>

                  <div className="rounded-lg bg-white dark:bg-slate-900/90 p-4 border border-slate-200 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-300 space-y-2 font-mono shadow-2xs">
                    <div className="font-sans font-bold text-slate-900 dark:text-white border-b border-slate-200 dark:border-slate-800 pb-2">
                      <span className="text-slate-400 font-normal">Subject: </span>
                      {activeTab.recommendedEmail.subject}
                    </div>
                    <div className="font-sans whitespace-pre-wrap leading-relaxed pt-1 text-slate-700 dark:text-slate-200 text-[11px]">
                      {activeTab.recommendedEmail.body}
                    </div>
                  </div>
                </div>

              </div>
            </motion.div>
          </AnimatePresence>

        </div>

      </div>
    </section>
  );
}
