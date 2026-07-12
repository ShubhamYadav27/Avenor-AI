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
    pct >= 65 ? "#ef4444" : pct >= 45 ? "#f59e0b" : pct >= 25 ? "#3b82f6" : "#94a3b8";

  return (
    <div
      className={cn("relative flex items-center justify-center", className)}
      style={{ width: size, height: size }}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={4}
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
        className="absolute text-xs font-bold"
        style={{ color, fontSize: size * 0.22 }}
      >
        {pct}
      </span>
    </div>
  );
}
