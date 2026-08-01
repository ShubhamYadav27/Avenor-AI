import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { BuyingWindow } from "@/types/api";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(score: number): string {
  return (score * 100).toFixed(0) + "%";
}

export function formatCurrency(usd: number | null | undefined): string {
  if (usd == null) return "—";
  if (usd >= 1_000_000) return `$${(usd / 1_000_000).toFixed(1)}M`;
  if (usd >= 1_000) return `$${(usd / 1_000).toFixed(0)}K`;
  return `$${usd.toFixed(0)}`;
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;

  const days = Math.floor(hours / 24);
  if (days === 1) return "yesterday";
  if (days < 7) return `${days} days ago`;
  if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
  return `${Math.floor(days / 30)} months ago`;
}

export const WINDOW_CONFIG: Record<
  BuyingWindow,
  { label: string; color: string; bg: string; dot: string }
> = {
  hot: {
    label: "HOT WINDOW",
    color: "text-emerald-700",
    bg: "bg-emerald-50 border-emerald-200",
    dot: "bg-emerald-500 animate-pulse",
  },
  warm: {
    label: "WARM INTENT",
    color: "text-amber-700",
    bg: "bg-amber-50 border-amber-200",
    dot: "bg-amber-500",
  },
  watch: {
    label: "EVALUATING",
    color: "text-sky-700",
    bg: "bg-sky-50 border-sky-200",
    dot: "bg-sky-500",
  },
  cold: {
    label: "MONITORING",
    color: "text-slate-600",
    bg: "bg-slate-100 border-slate-200",
    dot: "bg-slate-400",
  },
};

export const SIGNAL_TYPE_LABELS: Record<string, string> = {
  hiring: "Hiring",
  funding: "Funding",
  tech_change: "Tech Change",
  expansion: "Expansion",
  intent: "Intent",
  leadership_change: "Leadership Change",
  product_launch: "Product Launch",
  news: "News",
};

export const OUTCOME_OPTIONS: Array<{
  value: string;
  label: string;
  positive: boolean;
}> = [
  { value: "replied_positive", label: "Replied (positive)", positive: true },
  { value: "meeting_booked", label: "Meeting booked", positive: true },
  { value: "became_opportunity", label: "Opportunity created", positive: true },
  { value: "closed_won", label: "Closed won", positive: true },
  { value: "replied_negative", label: "Replied (negative)", positive: false },
  { value: "no_response", label: "No response", positive: false },
  { value: "wrong_timing", label: "Wrong timing", positive: false },
  { value: "closed_lost", label: "Closed lost", positive: false },
];
