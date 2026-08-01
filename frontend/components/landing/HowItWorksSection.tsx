"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Radar, Cpu, TrendingUp, Zap, CheckCircle2, ArrowRight } from "lucide-react";
import { HOW_IT_WORKS_STEPS } from "./constants";

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  Radar,
  Cpu,
  TrendingUp,
  Zap,
};

export function HowItWorksSection() {
  const [activeStep, setActiveStep] = useState(0);

  return (
    <section id="how-it-works" className="relative py-24 bg-[#F5F7FB] dark:bg-slate-950/80 border-t border-slate-200/90 dark:border-slate-900 overflow-hidden transition-colors">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 rounded-full border border-indigo-200 dark:border-indigo-500/30 bg-indigo-50 dark:bg-indigo-500/10 px-4 py-1.5 text-xs font-bold text-indigo-700 dark:text-indigo-300 shadow-2xs"
          >
            <Zap className="h-3.5 w-3.5" />
            <span>4-Step Predictive Engine</span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 dark:text-white tracking-tight leading-tight"
          >
            How Avenor Predicts & Converts{" "}
            <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600 dark:from-sky-400 dark:via-indigo-300 dark:to-purple-400 bg-clip-text text-transparent">
              Revenue Intent
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-base sm:text-lg text-slate-600 dark:text-slate-300 leading-relaxed font-medium"
          >
            From raw global market signals to closed-won deals. Avenor automates the entire revenue intelligence lifecycle in real time.
          </motion.p>
        </div>

        {/* 4 Steps Navigation Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 mb-8">
          {HOW_IT_WORKS_STEPS.map((step, idx) => {
            const IconComponent = ICON_MAP[step.iconName] || Radar;
            const isActive = idx === activeStep;
            return (
              <button
                key={step.step}
                onClick={() => setActiveStep(idx)}
                className={`relative text-left p-5 rounded-2xl border transition-all duration-300 cursor-pointer shadow-2xs ${
                  isActive
                    ? "border-indigo-500 bg-white dark:bg-indigo-950/40 shadow-md shadow-indigo-500/10 font-bold"
                    : "border-slate-200/90 dark:border-slate-800/80 bg-white/70 dark:bg-slate-900/40 hover:bg-white dark:hover:bg-slate-900/80 hover:border-slate-300 dark:hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span
                    className={`text-xs font-black px-2.5 py-0.5 rounded-lg ${
                      isActive ? "bg-indigo-600 text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                    }`}
                  >
                    {step.step}
                  </span>
                  <IconComponent className={`h-4 w-4 ${isActive ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400"}`} />
                </div>
                <h3 className={`text-sm font-bold ${isActive ? "text-slate-900 dark:text-white" : "text-slate-700 dark:text-slate-300"}`}>
                  {step.title}
                </h3>
                <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1">{step.subtitle}</p>

                {/* Progress bar line */}
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-b-2xl"
                  />
                )}
              </button>
            );
          })}
        </div>

        {/* Step Detail Active Panel */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeStep}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.3 }}
            className="rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900/60 p-6 md:p-10 backdrop-blur-xl shadow-md"
          >
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              
              {/* Left Column Description */}
              <div className="lg:col-span-6 space-y-5">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-black text-indigo-700 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/30 px-3 py-1 rounded-lg">
                    Step {HOW_IT_WORKS_STEPS[activeStep].step}
                  </span>
                  <span className="text-xs font-bold text-slate-500 dark:text-slate-400">
                    {HOW_IT_WORKS_STEPS[activeStep].subtitle}
                  </span>
                </div>

                <h3 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
                  {HOW_IT_WORKS_STEPS[activeStep].title}
                </h3>

                <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
                  {HOW_IT_WORKS_STEPS[activeStep].description}
                </p>

                <div className="space-y-2.5 pt-2">
                  {HOW_IT_WORKS_STEPS[activeStep].details.map((item, i) => (
                    <div key={i} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-800 dark:text-slate-200 font-semibold">
                      <CheckCircle2 className="h-4 w-4 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right Column Interactive Visual Box */}
              <div className="lg:col-span-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-[#F8FAFC] dark:bg-slate-950 p-6 space-y-4 shadow-inner">
                <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                    <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span>Pipeline Stage Execution</span>
                  </div>
                  <span className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400">
                    Automated Task
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="p-4 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 space-y-1 shadow-2xs">
                    <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center justify-between">
                      <span>Target Account Matched</span>
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold text-[11px]">Score: 98/100</span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                      High intent velocity detected across 3 distinct signal channels.
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-500/30 text-xs text-indigo-900 dark:text-indigo-200 space-y-1 shadow-2xs">
                    <div className="font-bold flex items-center gap-1.5 text-indigo-700 dark:text-indigo-300">
                      <Zap className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                      Recommended AE Action
                    </div>
                    <p className="text-[11px] text-slate-700 dark:text-slate-300 font-medium">
                      Send personalized signal outreach to VP of Sales within 24 hours.
                    </p>
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 font-semibold">
                  <span>Step {activeStep + 1} of 4</span>
                  <button
                    onClick={() => setActiveStep((activeStep + 1) % HOW_IT_WORKS_STEPS.length)}
                    className="inline-flex items-center gap-1 font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 cursor-pointer"
                  >
                    <span>Next Pipeline Stage</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

            </div>
          </motion.div>
        </AnimatePresence>

      </div>
    </section>
  );
}
