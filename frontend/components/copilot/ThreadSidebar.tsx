"use client";

import React, { useState } from "react";
import { Plus, MessageSquare, Trash2, Search, Sparkles } from "lucide-react";
import { useConversation } from "./context/ConversationContext";

export const ThreadSidebar: React.FC = () => {
  const {
    threads,
    activeThreadId,
    selectThread,
    handleCreateThread,
    handleDeleteThread,
    isLoadingThreads,
  } = useConversation();

  const [search, setSearch] = useState("");

  const filtered = threads.filter((t) =>
    t.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <aside className="w-64 border-r border-gray-800 bg-gray-950 flex flex-col h-full">
      {/* Header & New Session Button */}
      <div className="p-4 border-b border-gray-800/80">
        <button
          onClick={() => handleCreateThread()}
          className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-600 hover:from-indigo-500 hover:to-indigo-500 text-white font-medium text-sm transition-all shadow-md shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4" />
          <span>New Session</span>
        </button>

        <div className="mt-3 relative">
          <Search className="w-4 h-4 text-gray-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search sessions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-gray-900 border border-gray-800 rounded-md text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Threads List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {isLoadingThreads ? (
          <div className="p-4 text-center text-xs text-gray-500">Loading sessions...</div>
        ) : filtered.length === 0 ? (
          <div className="p-4 text-center text-xs text-gray-500">No sessions found</div>
        ) : (
          filtered.map((t) => {
            const isActive = t.id === activeThreadId;
            return (
              <div
                key={t.id}
                onClick={() => selectThread(t.id)}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer text-xs font-medium transition-colors ${
                  isActive
                    ? "bg-indigo-600/10 text-indigo-300 border border-indigo-500/20"
                    : "text-gray-400 hover:bg-gray-900 hover:text-gray-200"
                }`}
              >
                <div className="flex items-center space-x-2.5 truncate">
                  <MessageSquare
                    className={`w-3.5 h-3.5 flex-shrink-0 ${
                      isActive ? "text-indigo-400" : "text-gray-500"
                    }`}
                  />
                  <span className="truncate">{t.title}</span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteThread(t.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity"
                  title="Delete thread"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer info */}
      <div className="p-3 border-t border-gray-900 text-[10px] text-gray-500 text-center">
        Avenor Revenue Copilot Foundation v1.0
      </div>
    </aside>
  );
};
