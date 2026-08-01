"use client";

import React from "react";
import Link from "next/link";

export interface LogoProps {
  type?: "full" | "icon" | "symbol" | "wordmark";
  size?: "xs" | "sm" | "md" | "lg" | "xl" | "2xl";
  href?: string;
  className?: string;
  wordmarkClassName?: string;
  iconClassName?: string;
}

export function AvenorSymbolIcon({
  size = "md",
  className = "",
}: {
  size?: LogoProps["size"];
  className?: string;
}) {
  const dimensions = {
    xs: "h-5 w-5",
    sm: "h-7 w-7",
    md: "h-9 w-9",
    lg: "h-12 w-12",
    xl: "h-16 w-16",
    "2xl": "h-14 w-14 sm:h-18 sm:w-18 md:h-22 md:w-22 lg:h-26 lg:w-26",
  };

  const dimClass = dimensions[size] || dimensions.md;

  return (
    <div className={`relative inline-flex items-center justify-center shrink-0 ${dimClass} ${className}`}>
      <svg
        viewBox="0 0 52 52"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full drop-shadow-[0_0_16px_rgba(99,102,241,0.5)]"
        role="img"
        aria-label="Avenor-AI Logo"
      >
        <defs>
          {/* Cyan to Electric Blue Gradient for Left Stem */}
          <linearGradient id="logo-left-stem" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="50%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#1D4ED8" />
          </linearGradient>

          {/* Electric Blue to Purple/Magenta Gradient for Right Stem */}
          <linearGradient id="logo-right-stem" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#60A5FA" />
            <stop offset="35%" stopColor="#818CF8" />
            <stop offset="75%" stopColor="#A855F7" />
            <stop offset="100%" stopColor="#D946EF" />
          </linearGradient>

          {/* Revenue Analytics Bar Gradients */}
          <linearGradient id="logo-bar-1" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor="#0284C7" />
            <stop offset="100%" stopColor="#38BDF8" />
          </linearGradient>

          <linearGradient id="logo-bar-2" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor="#4338CA" />
            <stop offset="100%" stopColor="#818CF8" />
          </linearGradient>

          <linearGradient id="logo-bar-3" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor="#7E22CE" />
            <stop offset="100%" stopColor="#C084FC" />
          </linearGradient>

          {/* Soft Glow */}
          <filter id="logo-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Circuit Traces extending on Left Side */}
        <g opacity="0.95">
          {/* Top Trace */}
          <path d="M7 16 H16 L21 21" stroke="#38BDF8" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="6" cy="16" r="2.5" fill="#38BDF8" />

          {/* Middle Trace */}
          <path d="M3 26 H13 L19 32" stroke="#38BDF8" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="2" cy="26" r="2.5" fill="#38BDF8" />

          {/* Bottom Trace */}
          <path d="M9 36 H17 L21 40" stroke="#38BDF8" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="8" cy="36" r="2.5" fill="#38BDF8" />
        </g>

        {/* Outer Left Stem of 'A' */}
        <path
          d="M29 5 L16 45 H23.5 L27.5 32 L29 27 L29 5 Z"
          fill="url(#logo-left-stem)"
        />

        {/* Outer Right Stem of 'A' */}
        <path
          d="M29 5 L29 27 L30.5 32 L34.5 45 H42 L29 5 Z"
          fill="url(#logo-right-stem)"
        />

        {/* Inner Dark Cutout of 'A' — always dark for contrast */}
        <path
          d="M29 13.5 L22.5 33.5 H35.5 L29 13.5 Z"
          fill="#0F172A"
        />

        {/* 3 Rising Revenue Analytics Bars in bottom cutout of 'A' */}
        {/* Bar 1 (Short / Left) */}
        <rect x="23" y="35" width="3.2" height="7.5" rx="1.2" fill="url(#logo-bar-1)" filter="url(#logo-glow)" />

        {/* Bar 2 (Medium / Center) */}
        <rect x="27.4" y="29.5" width="3.2" height="13" rx="1.2" fill="url(#logo-bar-2)" filter="url(#logo-glow)" />

        {/* Bar 3 (Tall / Right) */}
        <rect x="31.8" y="24" width="3.2" height="18.5" rx="1.2" fill="url(#logo-bar-3)" filter="url(#logo-glow)" />

        {/* Apex Cap Accent */}
        <polygon points="29,4.5 25,13.5 33,13.5" fill="url(#logo-right-stem)" opacity="0.95" />
      </svg>
    </div>
  );
}

export function LogoWordmark({
  size = "md",
  className = "",
}: {
  size?: LogoProps["size"];
  className?: string;
}) {
  const textSizes = {
    xs: "text-xs tracking-[0.16em]",
    sm: "text-sm sm:text-base tracking-[0.18em]",
    md: "text-base sm:text-lg tracking-[0.2em]",
    lg: "text-xl sm:text-2xl tracking-[0.22em]",
    xl: "text-2xl sm:text-3xl tracking-[0.25em]",
    "2xl": "text-3xl sm:text-4xl md:text-5xl lg:text-6xl tracking-[0.22em]",
  };

  const textClass = textSizes[size] || textSizes.md;

  return (
    <div className={`inline-flex items-center font-sans font-black uppercase ${textClass} ${className}`}>
      {/* AVENOR — themed gradient for visibility on both light and dark */}
      <span className="bg-gradient-to-r from-slate-800 via-slate-700 to-slate-500 dark:from-white dark:via-slate-100 dark:to-slate-400 bg-clip-text text-transparent drop-shadow-sm font-extrabold">
        AVENOR
      </span>

      {/* -AI in electric blue to purple gradient */}
      <span className="bg-gradient-to-r from-sky-500 via-indigo-500 to-purple-600 dark:from-sky-400 dark:via-indigo-400 dark:to-purple-500 bg-clip-text text-transparent ml-0.5 font-black">
        -AI
      </span>
    </div>
  );
}

export function Logo({
  type = "full",
  size = "md",
  href,
  className = "",
  wordmarkClassName = "",
  iconClassName = "",
}: LogoProps) {
  const showIcon = type === "full" || type === "icon" || type === "symbol";
  const showWordmark = type === "full" || type === "wordmark";

  const gapClasses = {
    xs: "gap-1.5",
    sm: "gap-2",
    md: "gap-2.5",
    lg: "gap-3",
    xl: "gap-3.5",
    "2xl": "gap-3.5 sm:gap-4 md:gap-5",
  };
  const gapClass = gapClasses[size] || gapClasses.md;

  const content = (
    <div className={`inline-flex items-center ${gapClass} group cursor-pointer ${className}`}>
      {showIcon && <AvenorSymbolIcon size={size} className={iconClassName} />}
      {showWordmark && <LogoWordmark size={size} className={wordmarkClassName} />}
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="inline-flex items-center" aria-label="Avenor-AI - Go to homepage">
        {content}
      </Link>
    );
  }

  return content;
}
