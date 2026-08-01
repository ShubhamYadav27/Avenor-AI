"use client";

import Link from "next/link";
import { Mail, Headphones, ShieldCheck } from "lucide-react";
import { FOOTER_LINKS, COMPANY_INFO } from "./constants";

export function Footer() {
  return (
    <footer className="relative bg-[#F5F7FB] dark:bg-slate-950 border-t border-[#E6EAF2] dark:border-slate-900 text-slate-900 dark:text-slate-400 text-xs transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-14">
        
        {/* 1. Navigation Links */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pb-8 border-b border-[#E6EAF2]/80 dark:border-slate-900">
          {/* Product Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-900 dark:text-slate-200">Product</h4>
            <ul className="space-y-2.5 font-medium text-slate-600 dark:text-slate-400">
              {FOOTER_LINKS.product.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="hover:text-indigo-600 dark:hover:text-white transition-colors">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Solutions Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-900 dark:text-slate-200">Solutions</h4>
            <ul className="space-y-2.5 font-medium text-slate-600 dark:text-slate-400">
              {FOOTER_LINKS.solutions.map((link) => (
                <li key={link.label}>
                  <a href={link.href} className="hover:text-indigo-600 dark:hover:text-white transition-colors">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-900 dark:text-slate-200">Resources</h4>
            <ul className="space-y-2.5 font-medium text-slate-600 dark:text-slate-400">
              {FOOTER_LINKS.resources.map((link) => (
                <li key={link.label}>
                  <Link href={link.href} className="hover:text-indigo-600 dark:hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-900 dark:text-slate-200">Legal</h4>
            <ul className="space-y-2.5 font-medium text-slate-600 dark:text-slate-400">
              {FOOTER_LINKS.legal.map((link) => (
                <li key={link.label}>
                  <Link href={link.href} className="hover:text-indigo-600 dark:hover:text-white transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* 2. Contact Row */}
        <div className="py-6 flex flex-wrap items-center gap-6 sm:gap-10 text-xs font-semibold text-slate-700 dark:text-slate-300">
          <a
            href={`mailto:${COMPANY_INFO.primaryEmail}`}
            className="flex items-center gap-2.5 hover:text-indigo-600 dark:hover:text-white transition-colors group"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-xl border border-[#E6EAF2] dark:border-slate-800 bg-white dark:bg-slate-900 group-hover:border-indigo-300 dark:group-hover:border-indigo-500/40 transition-colors shadow-2xs">
              <Mail className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            </span>
            <span>{COMPANY_INFO.primaryEmail}</span>
          </a>

          <a
            href={`mailto:${COMPANY_INFO.supportEmail}`}
            className="flex items-center gap-2.5 hover:text-indigo-600 dark:hover:text-white transition-colors group"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-xl border border-[#E6EAF2] dark:border-slate-800 bg-white dark:bg-slate-900 group-hover:border-indigo-300 dark:group-hover:border-indigo-500/40 transition-colors shadow-2xs">
              <Headphones className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            </span>
            <span>{COMPANY_INFO.supportEmail}</span>
          </a>

          <a
            href={COMPANY_INFO.linkedInUrl}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2.5 hover:text-indigo-600 dark:hover:text-white transition-colors group"
            aria-label="Official Avenor-AI LinkedIn Page"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-xl border border-[#E6EAF2] dark:border-slate-800 bg-white dark:bg-slate-900 group-hover:border-indigo-300 dark:group-hover:border-indigo-500/40 transition-colors shadow-2xs">
              <svg className="h-4 w-4 fill-indigo-600 dark:fill-indigo-400" viewBox="0 0 24 24">
                <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.25V10.9H6.46M7.86 6.74a1.63 1.63 0 1 0 0 3.26 1.63 1.63 0 0 0 0-3.26z"/>
              </svg>
            </span>
            <span>LinkedIn</span>
          </a>
        </div>

        {/* 3. Copyright Bar */}
        <div className="pt-6 border-t border-[#E6EAF2] dark:border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] font-semibold text-slate-500 dark:text-slate-500">
          <p>© 2026 Avenor-AI. All rights reserved.</p>

          <div className="flex items-center gap-6">
            <Link href="/login" className="hover:text-indigo-600 dark:hover:text-slate-300 transition-colors">
              Privacy
            </Link>
            <Link href="/login" className="hover:text-indigo-600 dark:hover:text-slate-300 transition-colors">
              Terms
            </Link>
            <Link href="/login" className="hover:text-indigo-600 dark:hover:text-slate-300 transition-colors">
              Status
            </Link>
            <div className="flex items-center gap-1.5 ml-2 text-slate-400 dark:text-slate-600">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
              <span>Production System Operational</span>
            </div>
          </div>
        </div>

      </div>
    </footer>
  );
}
