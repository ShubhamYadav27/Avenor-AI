import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface Props {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, action, className }: Props) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 text-center p-8 glass-card", className)}>
      <div className="mb-4 rounded-full bg-slate-100 dark:bg-slate-800 p-4 border border-slate-200/60 dark:border-slate-700">
        <Icon className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
      </div>
      <h3 className="mb-1 text-base font-bold text-slate-900 dark:text-white">{title}</h3>
      <p className="mb-4 max-w-sm text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{description}</p>
      {action}
    </div>
  );
}
