"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Target } from "lucide-react";
import { useRegister } from "@/hooks/use-api";
import { auth } from "@/lib/auth";
import { getErrorMessage } from "@/lib/api-client";

export default function RegisterPage() {
  const router = useRouter();
  const register = useRegister();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    workspace_name: "",
  });
  const [error, setError] = useState("");

  function setField(k: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((p) => ({ ...p, [k]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const data = await register.mutateAsync(form);
      auth.setSession(data);
      router.push("/dashboard/feed");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-violet-600">
            <Target className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-xl font-bold text-slate-900">Create your workspace</h1>
          <p className="mt-1 text-sm text-slate-500">Start predicting who will buy</p>
        </div>

        <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          {(
            [
              { key: "workspace_name", label: "Company / workspace name", placeholder: "Acme Sales" },
              { key: "full_name", label: "Your full name", placeholder: "Sarah Kim" },
              { key: "email", label: "Work email", placeholder: "you@company.com", type: "email" },
              { key: "password", label: "Password", placeholder: "••••••••", type: "password" },
            ] as Array<{ key: keyof typeof form; label: string; placeholder: string; type?: string }>
          ).map(({ key, label, placeholder, type = "text" }) => (
            <div key={key}>
              <label className="mb-1.5 block text-xs font-medium text-slate-700">{label}</label>
              <input
                type={type}
                value={form[key]}
                onChange={setField(key)}
                required
                placeholder={placeholder}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none placeholder:text-slate-400 focus:border-violet-500 focus:ring-2 focus:ring-violet-100"
              />
            </div>
          ))}

          <button
            type="submit"
            disabled={register.isPending}
            className="w-full rounded-lg bg-violet-600 py-2 text-sm font-semibold text-white hover:bg-violet-700 disabled:opacity-60 transition-colors"
          >
            {register.isPending ? "Creating workspace…" : "Create workspace"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-violet-600 hover:text-violet-700">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
