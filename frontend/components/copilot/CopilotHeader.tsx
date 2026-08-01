"use client";

import React from "react";
import { Sparkles, Cpu, Activity, Wrench, Brain } from "lucide-react";
import { useConversation } from "./context/ConversationContext";
import { useCopilotProvider } from "./context/ProviderContext";

interface CopilotHeaderProps {
  onOpenTools?: () => void;
  onOpenMemory?: () => void;
}

export const CopilotHeader: React.FC<CopilotHeaderProps> = ({ onOpenTools, onOpenMemory }) => {
  const { activeThread } = useConversation();
  const { selectedProvider, selectedModel } = useCopilotProvider();

  return (
    <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-gray-950/80 backdrop-blur-md">
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-base font-semibold text-gray-100 flex items-center gap-2">
            {activeThread?.title || "Revenue Strategy Session"}
          </h1>
          <p className="text-xs text-gray-400">
            Avenor Predictive Revenue Intelligence Orchestrator
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3 text-xs">
        <button
          onClick={onOpenTools}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-gray-900 border border-gray-800 text-indigo-300 hover:border-indigo-500/50 hover:bg-gray-850 transition-colors"
        >
          <Wrench className="w-3.5 h-3.5 text-indigo-400" />
          <span className="font-medium">Tools Engine</span>
        </button>

        <button
          onClick={onOpenMemory}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-gray-900 border border-gray-800 text-indigo-300 hover:border-indigo-500/50 hover:bg-gray-850 transition-colors"
        >
          <Brain className="w-3.5 h-3.5 text-indigo-400" />
          <span className="font-medium">Enterprise Memory</span>
        </button>

        <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-gray-900 border border-gray-800 text-gray-300">
          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
          <span className="font-mono text-gray-200 uppercase">{selectedProvider}</span>
          <span className="text-gray-500">/</span>
          <span className="text-gray-400">{selectedModel}</span>
        </div>

        <div className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-full bg-emerald-950/40 border border-emerald-800/40 text-emerald-400">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span className="font-medium">Ready</span>
        </div>
      </div>
    </div>
  );
};
