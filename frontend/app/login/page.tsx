"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Eye, EyeOff } from "lucide-react";
import { useLogin } from "@/hooks/use-api";
import { auth } from "@/lib/auth";
import { getErrorMessage } from "@/lib/api-client";
import { Logo } from "@/components/common/Logo";

export default function LoginPage() {
  const router = useRouter();
  const login = useLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (auth.isAuthenticated()) {
      router.replace("/dashboard/feed");
    }
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const data = await login.mutateAsync({ email, password });
      auth.setSession(data);
      router.push("/dashboard/feed");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-[#F5F7FB] dark:bg-slate-950 px-4 py-12 text-slate-900 dark:text-slate-100 overflow-hidden transition-colors">
      {/* Ambient Radial Background Mesh */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-tr from-indigo-200/20 via-purple-200/15 to-blue-200/10 dark:from-indigo-600/20 dark:via-purple-600/15 dark:to-blue-500/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute inset-0 bg-grid-line-pattern opacity-30 pointer-events-none" />

      <div className="relative w-full max-w-md z-10">
        {/* Official Logo */}
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl glow-indigo">
            <Logo type="icon" size="md" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Sign in to Avenor-AI</h1>
          <p className="mt-1.5 text-sm text-slate-500 dark:text-slate-400">Predictive revenue intelligence for B2B sales teams</p>
        </div>

        <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/80 p-6 sm:p-8 shadow-2xl backdrop-blur-xl space-y-4">
          {error && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-3.5 py-2.5 text-xs font-semibold text-red-400">
              {error}
            </div>
          )}

          <div>
            <label className="mb-1.5 block text-xs font-medium text-slate-700 dark:text-slate-300">
              Work Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@company.com"
              className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-[#F8FAFC] dark:bg-slate-950 px-3.5 py-2.5 text-sm text-slate-900 dark:text-white outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-slate-700 dark:text-slate-300">
              Password
            </label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full rounded-lg border border-slate-200 dark:border-slate-800 bg-[#F8FAFC] dark:bg-slate-950 px-3.5 py-2.5 pr-10 text-sm text-slate-900 dark:text-white outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
              >
                {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={login.isPending}
            className="w-full mt-2 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:opacity-95 disabled:opacity-60 transition-all cursor-pointer"
          >
            {login.isPending ? "Signing In…" : "Sign In"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
          No account?{" "}
          <Link href="/register" className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300 transition-colors">
            Create workspace
          </Link>
        </p>
      </div>
    </div>
  );
}
