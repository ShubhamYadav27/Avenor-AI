import { cn } from "@/lib/utils";

interface Props {
  score: number; // 0–1
  size?: number;
  className?: string;
}

export function ScoreRing({ score, size = 48, className }: Props) {
  const pct = Math.round(score * 100);
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;

  const color =
    pct >= 65 ? "#059669" : pct >= 45 ? "#d97706" : pct >= 25 ? "#0284c7" : "#64748b";

  return (
    <div
      className={cn("relative flex items-center justify-center shrink-0", className)}
      style={{ width: size, height: size }}
      role="meter"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Score: ${pct}%`}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth={4}
          className="text-slate-200 dark:text-slate-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={4}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
        />
      </svg>
      <span
        className="absolute text-xs font-bold text-slate-900 dark:text-white"
        style={{ fontSize: size * 0.24 }}
      >
        {pct}
      </span>
    </div>
  );
}
