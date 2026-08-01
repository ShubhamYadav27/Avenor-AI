import { apiClient } from "@/lib/api-client";
import Cookies from "js-cookie";

export interface CopilotMessage {
  id: string;
  thread_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  model_provider?: string;
  model_name?: string;
  token_count?: number;
  created_at: string;
}

export interface CopilotState {
  id: string;
  workspace_id: string;
  thread_id: string;
  current_company_id?: string;
  current_deal_id?: string;
  current_contact_id?: string;
  active_workspace_context?: Record<string, any>;
  active_recommendation?: Record<string, any>;
  token_budget?: number;
  last_tool_used?: string;
  updated_at: string;
}

export interface CopilotThread {
  id: string;
  workspace_id: string;
  user_id: string;
  title: string;
  status: "active" | "archived";
  created_at: string;
  updated_at: string;
  messages: CopilotMessage[];
  state?: CopilotState;
}

export interface HealthResponse {
  status: string;
  system: string;
  version: string;
  database: string;
  streaming: string;
  providers: {
    default: string;
    fallback: string;
  };
  feature_flags: Record<string, boolean>;
}

export async function fetchCopilotHealth(): Promise<HealthResponse> {
  const res = await apiClient.get<HealthResponse>("/copilot/health");
  return res.data;
}

export async function fetchThreads(): Promise<CopilotThread[]> {
  const res = await apiClient.get<CopilotThread[]>("/copilot/threads");
  return res.data;
}

export async function createThread(title?: string): Promise<CopilotThread> {
  const res = await apiClient.post<CopilotThread>("/copilot/threads", { title });
  return res.data;
}

export async function fetchThread(threadId: string): Promise<CopilotThread> {
  const res = await apiClient.get<CopilotThread>(`/copilot/threads/${threadId}`);
  return res.data;
}

export async function updateThread(threadId: string, data: { title?: string; status?: string }): Promise<CopilotThread> {
  const res = await apiClient.patch<CopilotThread>(`/copilot/threads/${threadId}`, data);
  return res.data;
}

export async function deleteThread(threadId: string): Promise<void> {
  await apiClient.delete(`/copilot/threads/${threadId}`);
}

export async function streamChatResponse(
  threadId: string,
  userMessage: string,
  onToken: (delta: string) => void,
  onDone: (data: any) => void,
  onError: (err: any) => void,
  options?: { provider?: string; model?: string; signal?: AbortSignal }
): Promise<void> {
  const token = Cookies.get("avenor_token");
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "https://backend-45395119059.asia-south1.run.app/api/v1";
  
  const queryParams = new URLSearchParams({ message: userMessage });
  if (options?.provider) queryParams.append("provider", options.provider);
  if (options?.model) queryParams.append("model", options.model);

  const url = `${baseUrl}/copilot/threads/${threadId}/chat/stream?${queryParams.toString()}`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token || ""}`,
        Accept: "text/event-stream",
      },
      signal: options?.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("Response body reader unavailable");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";

      for (const rawEvent of events) {
        if (!rawEvent.trim()) continue;
        const lines = rawEvent.split("\n");
        let eventName = "message";
        let dataStr = "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            eventName = line.replace("event: ", "").trim();
          } else if (line.startsWith("data: ")) {
            dataStr = line.replace("data: ", "").trim();
          }
        }

        if (dataStr) {
          try {
            const data = JSON.parse(dataStr);
            if (eventName === "token" && data.delta) {
              onToken(data.delta);
            } else if (eventName === "done") {
              onDone(data);
            } else if (eventName === "error") {
              onError(data);
            }
          } catch (e) {
            // Raw text fallback
            if (eventName === "token") onToken(dataStr);
          }
        }
      }
    }
  } catch (err: any) {
    if (err.name !== "AbortError") {
      onError(err);
    }
  }
}
