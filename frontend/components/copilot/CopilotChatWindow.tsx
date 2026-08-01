"use client";

import React, { useState } from "react";
import { ProviderContextProvider } from "./context/ProviderContext";
import { ConversationContextProvider } from "./context/ConversationContext";
import { ThreadSidebar } from "./ThreadSidebar";
import { CopilotHeader } from "./CopilotHeader";
import { ChatMessageList } from "./ChatMessageList";
import { ChatInput } from "./ChatInput";
import { ToolDrawer } from "./ToolDrawer";
import { MemoryDrawer } from "./MemoryDrawer";

export const CopilotChatWindowInner: React.FC = () => {
  const [isToolsOpen, setIsToolsOpen] = useState(false);
  const [isMemoryOpen, setIsMemoryOpen] = useState(false);

  return (
    <div className="relative flex h-[calc(100vh-4rem)] w-full overflow-hidden bg-gray-950 rounded-xl border border-gray-800 shadow-2xl">
      <ThreadSidebar />

      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <CopilotHeader
          onOpenTools={() => {
            setIsMemoryOpen(false);
            setIsToolsOpen(true);
          }}
          onOpenMemory={() => {
            setIsToolsOpen(false);
            setIsMemoryOpen(true);
          }}
        />
        <ChatMessageList />
        <ChatInput />
      </div>

      <ToolDrawer isOpen={isToolsOpen} onClose={() => setIsToolsOpen(false)} />
      <MemoryDrawer isOpen={isMemoryOpen} onClose={() => setIsMemoryOpen(false)} />
    </div>
  );
};

export const CopilotChatWindow: React.FC = () => {
  return (
    <ProviderContextProvider>
      <ConversationContextProvider>
        <CopilotChatWindowInner />
      </ConversationContextProvider>
    </ProviderContextProvider>
  );
};
