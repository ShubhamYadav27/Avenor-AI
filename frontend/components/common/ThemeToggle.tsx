"use client";

import { useSyncExternalStore } from "react";
import { useTheme } from "./ThemeProvider";
import { Sun, Moon, Laptop } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  className?: string;
  variant?: "icon" | "dropdown" | "compact";
}

const emptySubscribe = () => () => {};

function useMounted() {
  return useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  );
}

export function ThemeToggle({ className, variant = "icon" }: Props) {
  const { theme, resolvedTheme, setTheme, toggleTheme } = useTheme();
  const mounted = useMounted();

  if (!mounted) {
    if (variant === "compact") {
      return (
        <div className={cn("flex items-center gap-1 rounded-xl border border-slate-200 dark:border-slate-800/80 bg-slate-100/80 dark:bg-slate-900/60 p-1 backdrop-blur-md", className)}>
          <div className="h-7 w-7 rounded-lg" />
          <div className="h-7 w-7 rounded-lg" />
          <div className="h-7 w-7 rounded-lg" />
        </div>
      );
    }
    return (
      <div
        className={cn(
          "relative flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300",
          className
        )}
      >
        <span className="h-4 w-4" />
      </div>
    );
  }

  if (variant === "compact") {
    return (
      <div className={cn("flex items-center gap-1 rounded-xl border border-slate-200 dark:border-slate-800/80 bg-slate-100/80 dark:bg-slate-900/60 p-1 backdrop-blur-md", className)}>
        <button
          onClick={() => setTheme("light")}
          title="Light Theme"
          className={cn(
            "flex h-7 w-7 items-center justify-center rounded-lg text-xs transition-all cursor-pointer",
            resolvedTheme === "light" && theme !== "system"
              ? "bg-white text-indigo-600 shadow-xs font-bold"
              : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
          )}
        >
          <Sun className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={() => setTheme("dark")}
          title="Dark Theme"
          className={cn(
            "flex h-7 w-7 items-center justify-center rounded-lg text-xs transition-all cursor-pointer",
            resolvedTheme === "dark" && theme !== "system"
              ? "bg-slate-800 text-indigo-400 shadow-xs font-bold"
              : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
          )}
        >
          <Moon className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={() => setTheme("system")}
          title="System Default"
          className={cn(
            "flex h-7 w-7 items-center justify-center rounded-lg text-xs transition-all cursor-pointer",
            theme === "system"
              ? "bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-xs font-bold"
              : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
          )}
        >
          <Laptop className="h-3.5 w-3.5" />
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      title={`Switch to ${resolvedTheme === "dark" ? "Light" : "Dark"} Mode`}
      className={cn(
        "relative flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all cursor-pointer shadow-2xs",
        className
      )}
      aria-label="Toggle theme"
    >
      {resolvedTheme === "dark" ? (
        <Sun className="h-4 w-4 text-amber-400 transition-transform duration-300 hover:rotate-45" />
      ) : (
        <Moon className="h-4 w-4 text-indigo-600 transition-transform duration-300 hover:-rotate-12" />
      )}
    </button>
  );
}
