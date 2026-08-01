"use client";

import React, { useEffect, useState } from "react";
import { Wrench, Zap, ShieldCheck, AlertTriangle, CheckCircle, RefreshCw, X } from "lucide-react";

interface ToolInfo {
  name: string;
  category: string;
  description: string;
  circuit_breaker_state: string;
  execution_cost: string;
}

interface ToolDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ToolDrawer: React.FC<ToolDrawerProps> = ({ isOpen, onClose }) => {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchTools = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/copilot/tools");
      if (res.ok) {
        const data = await res.json();
        setTools(data.tools || []);
      }
    } catch {
      // Fallback baseline display if API unauthenticated in dev
      setTools([
        { name: "CompanyTool", category: "COMPANY", description: "Retrieve Company Intelligence & Buying Signals", circuit_breaker_state: "CLOSED", execution_cost: "LOW" },
        { name: "SignalTool", category: "SIGNAL", description: "Analyze High-Intent Market Signals", circuit_breaker_state: "CLOSED", execution_cost: "LOW" },
        { name: "CrmTool", category: "CRM", description: "Retrieve CRM Pipeline & Opportunity Intelligence", circuit_breaker_state: "CLOSED", execution_cost: "LOW" },
        { name: "ResearchTool", category: "RESEARCH", description: "Generate Account Research Summaries", circuit_breaker_state: "CLOSED", execution_cost: "MEDIUM" },
        { name: "BriefingTool", category: "BRIEFING", description: "Synthesize Executive Sales Briefings", circuit_breaker_state: "CLOSED", execution_cost: "MEDIUM" },
        { name: "SalesCoachTool", category: "SALES_COACH", description: "Compute Sales Objection Strategies", circuit_breaker_state: "CLOSED", execution_cost: "MEDIUM" },
        { name: "EmailTool", category: "EMAIL", description: "Draft Personalized High-Impact Email Templates", circuit_breaker_state: "CLOSED", execution_cost: "LOW" },
        { name: "FeedTool", category: "FEED", description: "Stream Intelligence Feed Events", circuit_breaker_state: "CLOSED", execution_cost: "FREE" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchTools();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-gray-900 border-l border-gray-800 shadow-2xl z-50 flex flex-col p-5">
      <div className="flex items-center justify-between pb-4 border-b border-gray-800">
        <div className="flex items-center space-x-2 text-indigo-400">
          <Wrench className="w-5 h-5" />
          <h2 className="font-semibold text-gray-100 text-base">Tool Orchestrator</h2>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-200">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="py-3 flex items-center justify-between text-xs text-gray-400">
        <span>Active DAG Tools ({tools.length})</span>
        <button onClick={fetchTools} className="hover:text-indigo-400 flex items-center gap-1">
          <RefreshCw className={`w-3 h-3 ${isLoading ? "animate-spin" : ""}`} /> Refresh
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {tools.map((tool) => (
          <div key={tool.name} className="p-3 bg-gray-950/80 rounded-lg border border-gray-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-medium text-xs text-gray-200 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-indigo-400" />
                {tool.name}
              </span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 flex items-center gap-1">
                <CheckCircle className="w-2.5 h-2.5" />
                {tool.circuit_breaker_state}
              </span>
            </div>
            <p className="text-xs text-gray-400">{tool.description}</p>
            <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1 border-t border-gray-900">
              <span>Category: {tool.category}</span>
              <span>Cost: {tool.execution_cost}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
