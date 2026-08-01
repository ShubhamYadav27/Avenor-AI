"use client";

import React, { createContext, useContext, useEffect, useState, useRef } from "react";
import {
  CopilotMessage,
  CopilotThread,
  createThread,
  deleteThread,
  fetchThread,
  fetchThreads,
  streamChatResponse,
  updateThread,
} from "@/lib/api/copilot";
import { useCopilotProvider } from "./ProviderContext";

interface ConversationContextType {
  threads: CopilotThread[];
  activeThread: CopilotThread | null;
  activeThreadId: string | null;
  setActiveThreadId: (id: string | null) => void;
  isLoadingThreads: boolean;
  isLoadingActiveThread: boolean;
  isStreaming: boolean;
  streamingDelta: string;
  loadThreads: () => Promise<void>;
  selectThread: (id: string) => Promise<void>;
  handleCreateThread: (title?: string) => Promise<CopilotThread>;
  handleDeleteThread: (id: string) => Promise<void>;
  handleRenameThread: (id: string, title: string) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  stopStreaming: () => void;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export const ConversationContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { selectedProvider, selectedModel } = useCopilotProvider();
  const [threads, setThreads] = useState<CopilotThread[]>([]);
  const [activeThread, setActiveThread] = useState<CopilotThread | null>(null);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);

  const [isLoadingThreads, setIsLoadingThreads] = useState<boolean>(true);
  const [isLoadingActiveThread, setIsLoadingActiveThread] = useState<boolean>(false);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [streamingDelta, setStreamingDelta] = useState<string>("");

  const abortControllerRef = useRef<AbortController | null>(null);

  const loadThreads = async () => {
    setIsLoadingThreads(true);
    try {
      const data = await fetchThreads();
      setThreads(data);
      if (data.length > 0 && !activeThreadId) {
        await selectThread(data[0].id);
      }
    } catch (err) {
      console.error("Failed to load threads:", err);
    } finally {
      setIsLoadingThreads(false);
    }
  };

  const selectThread = async (threadId: string) => {
    setActiveThreadId(threadId);
    setIsLoadingActiveThread(true);
    try {
      const fullThread = await fetchThread(threadId);
      setActiveThread(fullThread);
    } catch (err) {
      console.error("Failed to load thread detail:", err);
    } finally {
      setIsLoadingActiveThread(false);
    }
  };

  const handleCreateThread = async (title?: string) => {
    const newThread = await createThread(title);
    setThreads((prev) => [newThread, ...prev]);
    setActiveThread(newThread);
    setActiveThreadId(newThread.id);
    return newThread;
  };

  const handleDeleteThread = async (threadId: string) => {
    await deleteThread(threadId);
    setThreads((prev) => prev.filter((t) => t.id !== threadId));
    if (activeThreadId === threadId) {
      const remaining = threads.filter((t) => t.id !== threadId);
      if (remaining.length > 0) {
        await selectThread(remaining[0].id);
      } else {
        setActiveThread(null);
        setActiveThreadId(null);
      }
    }
  };

  const handleRenameThread = async (threadId: string, title: string) => {
    const updated = await updateThread(threadId, { title });
    setThreads((prev) => prev.map((t) => (t.id === threadId ? { ...t, title } : t)));
    if (activeThreadId === threadId && activeThread) {
      setActiveThread({ ...activeThread, title });
    }
  };

  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || isStreaming) return;

    let targetThreadId = activeThreadId;
    let currentActive = activeThread;

    if (!targetThreadId || !currentActive) {
      const created = await handleCreateThread(content.slice(0, 40) + "...");
      targetThreadId = created.id;
      currentActive = created;
    }

    // Optimistic user message
    const userMsg: CopilotMessage = {
      id: "temp-user-" + Date.now(),
      thread_id: targetThreadId,
      role: "user",
      content: content,
      created_at: new Date().toISOString(),
    };

    setActiveThread({
      ...currentActive,
      messages: [...(currentActive.messages || []), userMsg],
    });

    setIsStreaming(true);
    setStreamingDelta("");

    abortControllerRef.current = new AbortController();

    let accumulatedDelta = "";

    await streamChatResponse(
      targetThreadId,
      content,
      (delta) => {
        accumulatedDelta += delta;
        setStreamingDelta(accumulatedDelta);
      },
      async (doneData) => {
        setIsStreaming(false);
        setStreamingDelta("");
        abortControllerRef.current = null;

        // Refresh thread from backend for full persistence sync
        try {
          const freshThread = await fetchThread(targetThreadId!);
          setActiveThread(freshThread);
          setThreads((prev) => prev.map((t) => (t.id === targetThreadId ? freshThread : t)));
        } catch (e) {
          console.error("Failed to reload thread after stream:", e);
        }
      },
      (err) => {
        console.error("Streaming error:", err);
        setIsStreaming(false);
        setStreamingDelta("");
        abortControllerRef.current = null;
      },
      {
        provider: selectedProvider,
        model: selectedModel,
        signal: abortControllerRef.current.signal,
      }
    );
  };

  useEffect(() => {
    loadThreads();
  }, []);

  return (
    <ConversationContext.Provider
      value={{
        threads,
        activeThread,
        activeThreadId,
        setActiveThreadId,
        isLoadingThreads,
        isLoadingActiveThread,
        isStreaming,
        streamingDelta,
        loadThreads,
        selectThread,
        handleCreateThread,
        handleDeleteThread,
        handleRenameThread,
        sendMessage,
        stopStreaming,
      }}
    >
      {children}
    </ConversationContext.Provider>
  );
};

export const useConversation = () => {
  const ctx = useContext(ConversationContext);
  if (!ctx) throw new Error("useConversation must be used within ConversationContextProvider");
  return ctx;
};
