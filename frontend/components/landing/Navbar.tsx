"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, ArrowRight, LayoutDashboard, LogOut } from "lucide-react";
import { NAV_ITEMS } from "./constants";
import { Logo } from "@/components/common/Logo";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { auth } from "@/lib/auth";

interface NavbarProps {
  onOpenDemo: () => void;
}

export function Navbar({ onOpenDemo }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(() => auth.isAuthenticated());

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLogout = () => {
    auth.clearSession();
    setIsLoggedIn(false);
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        scrolled ? "glass-navbar py-3 shadow-xl" : "bg-transparent py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Logo Component matching Official Reference */}
          <Logo href="/" type="full" size="sm" />

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1 rounded-full border border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-900/60 px-4 py-1.5 backdrop-blur-md shadow-2xs">
            {NAV_ITEMS.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="px-3.5 py-1.5 text-xs font-semibold text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white transition-colors rounded-full hover:bg-slate-100 dark:hover:bg-slate-800/50"
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* Action Buttons & Theme Toggle */}
          <div className="hidden md:flex items-center gap-3">
            <ThemeToggle />

            {isLoggedIn ? (
              <>
                <button
                  onClick={handleLogout}
                  className="px-3 py-2 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  <span>Sign Out</span>
                </button>

                <Link
                  href="/dashboard/feed"
                  className="group relative inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-indigo-500/20 hover:shadow-indigo-500/35 hover:opacity-95 transition-all"
                >
                  <LayoutDashboard className="h-3.5 w-3.5" />
                  <span>Dashboard</span>
                  <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-3 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white transition-colors"
                >
                  Sign In
                </Link>

                <button
                  onClick={onOpenDemo}
                  className="px-4 py-2 text-xs font-semibold text-slate-800 dark:text-slate-200 rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-900/80 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all shadow-2xs cursor-pointer"
                >
                  Book Demo
                </button>

                <Link
                  href="/register"
                  className="group relative inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-indigo-500/20 hover:shadow-indigo-500/35 hover:opacity-95 transition-all"
                >
                  <span>Get Started</span>
                  <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Toggle Button */}
          <div className="flex items-center gap-2 md:hidden">
            <ThemeToggle />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="rounded-xl p-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60 focus:outline-none"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden overflow-hidden bg-white/95 dark:bg-slate-950/95 border-b border-slate-200 dark:border-slate-800 backdrop-blur-xl px-4 py-6"
          >
            <div className="flex flex-col space-y-4">
              {NAV_ITEMS.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-sm font-semibold text-slate-800 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-white py-1"
                >
                  {item.label}
                </a>
              ))}

              <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex flex-col space-y-2.5">
                {isLoggedIn ? (
                  <>
                    <Link
                      href="/dashboard/feed"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-indigo-600 text-xs font-semibold text-white"
                    >
                      <LayoutDashboard className="h-4 w-4" />
                      <span>Go to Dashboard</span>
                    </Link>

                    <button
                      onClick={() => {
                        setMobileMenuOpen(false);
                        handleLogout();
                      }}
                      className="w-full text-center py-2 text-xs font-medium text-slate-500 dark:text-slate-400"
                    >
                      Sign Out
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => {
                        setMobileMenuOpen(false);
                        onOpenDemo();
                      }}
                      className="w-full text-center py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs font-semibold text-slate-800 dark:text-slate-200"
                    >
                      Book Demo
                    </button>

                    <Link
                      href="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full text-center py-2.5 rounded-xl bg-indigo-600 text-xs font-semibold text-white"
                    >
                      Get Started
                    </Link>

                    <Link
                      href="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full text-center py-2 text-xs font-medium text-slate-500 dark:text-slate-400"
                    >
                      Sign In to Existing Workspace
                    </Link>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}


