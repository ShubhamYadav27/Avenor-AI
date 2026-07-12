"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Zap, BarChart3, Building2, Link2, Settings, LogOut, Target,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { auth } from "@/lib/auth";
import { useMe } from "@/hooks/use-api";

const NAV = [
  { href: "/dashboard/feed", label: "Intelligence Feed", icon: Zap },
  { href: "/dashboard/companies", label: "Companies", icon: Building2 },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/hubspot", label: "HubSpot CRM", icon: Link2 },
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

  return (
    <aside className="flex h-full w-56 flex-col border-r border-slate-200 bg-white">
      {/* Logo */}
      <div className="flex h-14 items-center gap-2 border-b border-slate-200 px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-violet-600">
          <Target className="h-4 w-4 text-white" />
        </div>
        <span className="text-sm font-bold tracking-tight text-slate-900">Avenor</span>
      </div>

      {/* Workspace */}
      {me && (
        <div className="border-b border-slate-100 px-4 py-3">
          <p className="truncate text-xs font-medium text-slate-800">{me.workspace_name}</p>
          <p className="truncate text-xs text-slate-400 capitalize">{me.subscription_tier}</p>
        </div>
      )}

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 overflow-y-auto p-2">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-violet-50 text-violet-700"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <Icon className={cn("h-4 w-4 flex-shrink-0", active ? "text-violet-600" : "")} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* User */}
      <div className="border-t border-slate-200 p-3">
        <div className="mb-2 px-1">
          <p className="truncate text-xs font-medium text-slate-700">{me?.full_name}</p>
          <p className="truncate text-xs text-slate-400">{me?.email}</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-slate-500 hover:bg-red-50 hover:text-red-600 transition-colors"
        >
          <LogOut className="h-3.5 w-3.5" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
