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
    <div className={cn("flex flex-col items-center justify-center py-20 text-center", className)}>
      <div className="mb-4 rounded-full bg-slate-100 p-4">
        <Icon className="h-8 w-8 text-slate-400" />
      </div>
      <h3 className="mb-1 text-base font-semibold text-slate-800">{title}</h3>
      <p className="mb-4 max-w-sm text-sm text-slate-500">{description}</p>
      {action}
    </div>
  );
}
