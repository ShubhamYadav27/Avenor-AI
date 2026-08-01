"use client";

import React, { useState, useRef } from "react";
import { Send, Square, ChevronDown } from "lucide-react";
import { useConversation } from "./context/ConversationContext";
import { useCopilotProvider } from "./context/ProviderContext";

export const ChatInput: React.FC = () => {
  const { sendMessage, isStreaming, stopStreaming } = useConversation();
  const { selectedProvider, setSelectedProvider, selectedModel, setSelectedModel } = useCopilotProvider();
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    const msg = input;
    setInput("");
    sendMessage(msg);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="p-4 border-t border-gray-800 bg-gray-950">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-2">
        <div className="relative rounded-xl bg-gray-900 border border-gray-800 focus-within:border-indigo-500/50 transition-all p-2 shadow-xl">
          <textarea
            ref={textareaRef}
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Revenue Copilot (e.g., 'Which company should I contact today?')"
            className="w-full bg-transparent text-sm text-gray-100 placeholder-gray-500 focus:outline-none resize-none px-2 py-1"
          />

          <div className="flex items-center justify-between pt-2 border-t border-gray-800/40 px-2">
            <div className="flex items-center space-x-2">
              <select
                value={`${selectedProvider}:${selectedModel}`}
                onChange={(e) => {
                  const [p, m] = e.target.value.split(":");
                  setSelectedProvider(p);
                  setSelectedModel(m);
                }}
                className="bg-gray-800 text-xs text-gray-300 border border-gray-700 rounded-md px-2.5 py-1 focus:outline-none focus:border-indigo-500 cursor-pointer"
              >
                <option value="gemini:gemini-1.5-pro">Gemini 1.5 Pro</option>
                <option value="gemini:gemini-1.5-flash">Gemini 1.5 Flash</option>
                <option value="openai:gpt-4o">OpenAI GPT-4o</option>
                <option value="mock:mock-model">Mock Revenue Strategist</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              {isStreaming ? (
                <button
                  type="button"
                  onClick={stopStreaming}
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-red-600/20 text-red-400 border border-red-500/30 text-xs font-medium hover:bg-red-600/30 transition-colors"
                >
                  <Square className="w-3.5 h-3.5 fill-current" />
                  <span>Stop</span>
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="flex items-center justify-center p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white transition-colors shadow-md shadow-indigo-600/20"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};
