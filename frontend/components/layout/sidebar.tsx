"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Zap, BarChart3, Building2, Link2, Settings, LogOut, ChevronRight,
  Users, UserCheck, DollarSign, Contact, Layers, Sparkles
} from "lucide-react";
import { cn } from "@/lib/utils";
import { auth } from "@/lib/auth";
import { useMe } from "@/hooks/use-api";
import { Logo } from "@/components/common/Logo";

const MAIN_NAV = [
  { href: "/dashboard/copilot", label: "Revenue Copilot", icon: Sparkles },
  { href: "/dashboard/feed", label: "Intelligence Feed", icon: Zap },
  { href: "/dashboard/companies", label: "Companies", icon: Building2 },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
];


const CRM_NAV = [
  { href: "/dashboard/crm/contacts", label: "Contacts", icon: Contact },
  { href: "/dashboard/crm/deals", label: "Deals (Opportunities)", icon: DollarSign },
  { href: "/dashboard/crm/leads", label: "Leads", icon: UserCheck },
  { href: "/dashboard/crm/users", label: "CRM Users", icon: Users },
];

const SYSTEM_NAV = [
  { href: "/dashboard/crm", label: "CRM Integrations", icon: Link2, exact: true },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { data: me } = useMe();

  function handleLogout() {
    auth.clearSession();
    router.push("/login");
  }

  const isNavActive = (href: string, exact: boolean = false) => {
    if (exact) return pathname === href;
    return pathname.startsWith(href);
  };

  return (
    <aside className="flex h-full w-64 flex-col glass-sidebar select-none transition-colors">
      {/* Brand Header */}
      <div className="flex h-16 items-center border-b border-slate-200 dark:border-slate-800/80 px-4">
        <Logo href="/" type="full" size="sm" />
      </div>

      {/* Workspace Indicator */}
      {me && (
        <div className="border-b border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-900/40 px-4 py-3">
          <div className="flex items-center justify-between">
            <p className="truncate text-xs font-bold text-slate-800 dark:text-slate-200">{me.workspace_name}</p>
            <span className="rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/30 px-2 py-0.5 text-[10px] font-semibold text-indigo-700 dark:text-indigo-400 capitalize">
              {me.subscription_tier}
            </span>
          </div>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse" />
            AI Predictive Engine Active
          </p>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 space-y-4 overflow-y-auto p-3 custom-scrollbar" aria-label="Dashboard navigation">
        {/* Main Platform Section */}
        <div className="space-y-1">
          <div className="px-2 pb-1.5 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
            Platform Workspace
          </div>
          {MAIN_NAV.map(({ href, label, icon: Icon }) => {
            const active = isNavActive(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "relative flex items-center justify-between rounded-xl px-3 py-2 text-xs font-semibold transition-all duration-200",
                  active
                    ? "bg-indigo-50 dark:bg-gradient-to-r dark:from-indigo-950/80 dark:to-slate-900/90 text-indigo-700 dark:text-white border border-indigo-200 dark:border-indigo-500/30 shadow-sm dark:shadow-md dark:shadow-indigo-500/10"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900/60 hover:text-slate-900 dark:hover:text-slate-200"
                )}
                aria-current={active ? "page" : undefined}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={cn(
                      "h-4 w-4 shrink-0 transition-colors",
                      active ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400 dark:text-slate-500"
                    )}
                  />
                  <span>{label}</span>
                </div>
                {active && (
                  <div className="h-1.5 w-1.5 rounded-full bg-indigo-600 dark:bg-indigo-400 shadow-[0_0_8px_rgba(99,102,241,0.5)]" />
                )}
              </Link>
            );
          })}
        </div>

        {/* CRM Data Objects Section */}
        <div className="space-y-1">
          <div className="px-2 pb-1.5 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center justify-between">
            <span>CRM Data Records</span>
            <span className="text-[9px] bg-slate-100 dark:bg-slate-800 text-slate-500 px-1.5 py-0.5 rounded font-mono">Live</span>
          </div>
          {CRM_NAV.map(({ href, label, icon: Icon }) => {
            const active = isNavActive(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "relative flex items-center justify-between rounded-xl px-3 py-2 text-xs font-semibold transition-all duration-200 pl-4",
                  active
                    ? "bg-indigo-50 dark:bg-gradient-to-r dark:from-indigo-950/80 dark:to-slate-900/90 text-indigo-700 dark:text-white border border-indigo-200 dark:border-indigo-500/30 shadow-sm dark:shadow-md dark:shadow-indigo-500/10"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900/60 hover:text-slate-900 dark:hover:text-slate-200"
                )}
                aria-current={active ? "page" : undefined}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={cn(
                      "h-3.5 w-3.5 shrink-0 transition-colors",
                      active ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400 dark:text-slate-500"
                    )}
                  />
                  <span>{label}</span>
                </div>
                {active && (
                  <div className="h-1.5 w-1.5 rounded-full bg-indigo-600 dark:bg-indigo-400" />
                )}
              </Link>
            );
          })}
        </div>

        {/* System & Integrations Section */}
        <div className="space-y-1">
          <div className="px-2 pb-1.5 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
            Configuration
          </div>
          {SYSTEM_NAV.map(({ href, label, icon: Icon, exact }) => {
            const active = isNavActive(href, exact);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "relative flex items-center justify-between rounded-xl px-3 py-2 text-xs font-semibold transition-all duration-200",
                  active
                    ? "bg-indigo-50 dark:bg-gradient-to-r dark:from-indigo-950/80 dark:to-slate-900/90 text-indigo-700 dark:text-white border border-indigo-200 dark:border-indigo-500/30 shadow-sm dark:shadow-md dark:shadow-indigo-500/10"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900/60 hover:text-slate-900 dark:hover:text-slate-200"
                )}
                aria-current={active ? "page" : undefined}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={cn(
                      "h-4 w-4 shrink-0 transition-colors",
                      active ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400 dark:text-slate-500"
                    )}
                  />
                  <span>{label}</span>
                </div>
                {active && (
                  <div className="h-1.5 w-1.5 rounded-full bg-indigo-600 dark:bg-indigo-400" />
                )}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* User Profile & Logout */}
      <div className="border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-950 p-3 transition-colors">
        <div className="mb-2 px-2 py-1.5 rounded-lg bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800/60">
          <p className="truncate text-xs font-semibold text-slate-800 dark:text-slate-200">{me?.full_name}</p>
          <p className="truncate text-[11px] text-slate-500 dark:text-slate-400">{me?.email}</p>
        </div>

        <button
          onClick={handleLogout}
          className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-xs font-medium text-slate-500 dark:text-slate-400 hover:bg-red-50 dark:hover:bg-red-500/10 hover:text-red-600 dark:hover:text-red-400 border border-transparent hover:border-red-200 dark:hover:border-red-500/20 transition-all cursor-pointer"
          aria-label="Sign out of your account"
        >
          <span className="flex items-center gap-2">
            <LogOut className="h-3.5 w-3.5" />
            <span>Sign Out</span>
          </span>
          <ChevronRight className="h-3 w-3 opacity-60" />
        </button>
      </div>
    </aside>
  );
}
