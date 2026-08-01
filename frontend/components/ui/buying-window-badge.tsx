import { cn, WINDOW_CONFIG } from "@/lib/utils";
import type { BuyingWindow } from "@/types/api";

interface Props {
  window: BuyingWindow;
  size?: "sm" | "md";
}

export function BuyingWindowBadge({ window, size = "md" }: Props) {
  const cfg = WINDOW_CONFIG[window] ?? WINDOW_CONFIG.cold;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-semibold tracking-wide",
        cfg.bg,
        cfg.color,
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-xs"
      )}
    >
      <span className={cn("rounded-full", cfg.dot, "h-1.5 w-1.5")} />
      {cfg.label}
    </span>
  );
}
