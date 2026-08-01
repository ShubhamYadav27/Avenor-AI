"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { fetchCopilotHealth, HealthResponse } from "@/lib/api/copilot";

interface ProviderContextType {
  selectedProvider: string;
  setSelectedProvider: (p: string) => void;
  selectedModel: string;
  setSelectedModel: (m: string) => void;
  health: HealthResponse | null;
  isLoadingHealth: boolean;
  refetchHealth: () => Promise<void>;

}

const ProviderContext = createContext<ProviderContextType | undefined>(undefined);

export const ProviderContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedProvider, setSelectedProvider] = useState<string>("gemini");
  const [selectedModel, setSelectedModel] = useState<string>("gemini-1.5-pro");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState<boolean>(true);

  const refetchHealth = async () => {
    setIsLoadingHealth(true);
    try {
      const data = await fetchCopilotHealth();
      setHealth(data);
      if (data.providers.default) {
        setSelectedProvider(data.providers.default);
      }
    } catch (e) {
      console.warn("Could not fetch Copilot health status:", e);
    } finally {
      setIsLoadingHealth(false);
    }
  };

  useEffect(() => {
    refetchHealth();
  }, []);

  return (
    <ProviderContext.Provider
      value={{
        selectedProvider,
        setSelectedProvider,
        selectedModel,
        setSelectedModel,
        health,
        isLoadingHealth,
        refetchHealth,
      }}
    >
      {children}
    </ProviderContext.Provider>
  );
};

export const useCopilotProvider = () => {
  const ctx = useContext(ProviderContext);
  if (!ctx) throw new Error("useCopilotProvider must be used within ProviderContextProvider");
  return ctx;
};
