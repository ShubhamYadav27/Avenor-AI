"use client";

import React, { useEffect, useRef } from "react";
import { Sparkles, User, Copy, Check } from "lucide-react";
import { useConversation } from "./context/ConversationContext";

export const ChatMessageList: React.FC = () => {
  const { activeThread, isStreaming, streamingDelta } = useConversation();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeThread?.messages, streamingDelta]);

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const messages = activeThread?.messages || [];

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-950">
      {messages.length === 0 && !isStreaming && (
        <div className="h-full flex flex-col items-center justify-center text-center p-8">
          <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8 text-indigo-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-200">Avenor AI Revenue Copilot</h2>
          <p className="text-sm text-gray-400 max-w-md mt-1">
            Ask strategic questions regarding your accounts, high-intent buying signals, CRM deal pipeline, or recommended outreach strategies.
          </p>
        </div>
      )}

      {messages.map((msg) => {
        const isUser = msg.role === "user";
        return (
          <div
            key={msg.id}
            className={`flex items-start space-x-3 ${isUser ? "justify-end" : "justify-start"}`}
          >
            {!isUser && (
              <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-xl p-4 text-sm leading-relaxed ${
                isUser
                  ? "bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-600/20"
                  : "bg-gray-900 border border-gray-800 text-gray-200 rounded-tl-none"
              }`}
            >
              <div className="whitespace-pre-wrap font-sans">{msg.content}</div>

              {!isUser && (
                <div className="mt-3 pt-2 border-t border-gray-800/60 flex items-center justify-between text-[11px] text-gray-500">
                  <div className="flex items-center space-x-2">
                    {msg.model_provider && (
                      <span className="uppercase font-mono text-[10px] bg-gray-800 px-1.5 py-0.5 rounded text-gray-400">
                        {msg.model_provider}
                      </span>
                    )}
                    {msg.model_name && <span>{msg.model_name}</span>}
                  </div>
                  <button
                    onClick={() => copyToClipboard(msg.id, msg.content)}
                    className="hover:text-gray-300 transition-colors flex items-center gap-1"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>

            {isUser && (
              <div className="w-8 h-8 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                <User className="w-4 h-4 text-gray-300" />
              </div>
            )}
          </div>
        );
      })}

      {/* Streaming Active Chunk Bubble */}
      {isStreaming && (
        <div className="flex items-start space-x-3 justify-start">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
            <Sparkles className="w-4 h-4 text-indigo-400 animate-spin" />
          </div>

          <div className="max-w-2xl rounded-xl p-4 text-sm leading-relaxed bg-gray-900 border border-gray-800 text-gray-200 rounded-tl-none">
            <div className="whitespace-pre-wrap font-sans">
              {streamingDelta || <span className="text-gray-500 italic">Thinking...</span>}
              <span className="inline-block w-2 h-4 ml-1 bg-indigo-500 animate-pulse" />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
