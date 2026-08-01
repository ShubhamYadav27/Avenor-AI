"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { AuthGuard } from "@/components/layout/auth-guard";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex h-screen w-screen overflow-hidden font-sans antialiased">
        <Sidebar />
        <main className="flex flex-1 flex-col h-full min-w-0 min-h-0 overflow-y-auto overflow-x-hidden relative scroll-smooth">
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}
