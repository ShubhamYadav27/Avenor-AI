import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { auth } from "@/lib/auth";
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  MeResponse,
  FeedResponse,
  CompanyDetailResponse,
  CompanyStats,
  LogOutcomeRequest,
  ModelAccuracy,
  AttributionSummary,
  SignalEffectivenessResponse,
  PredictionAccuracy,
  HubSpotStatus,
  AdminStatus,
  HubSpotConnectResponse,
} from "@/types/api";

// ── Auth ──────────────────────────────────────────────────────

export function useLogin() {
  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      const res = await apiClient.post<TokenResponse>("/auth/login", data);
      return res.data;
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (data: RegisterRequest) => {
      const res = await apiClient.post<TokenResponse>("/auth/register", data);
      return res.data;
    },
  });
}

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await apiClient.get<MeResponse>("/auth/me");
      auth.cacheUser(res.data);
      return res.data;
    },
    enabled: auth.isAuthenticated(),
    staleTime: 5 * 60 * 1000,
  });
}

// ── Feed ──────────────────────────────────────────────────────

export function useFeed(params?: {
  buying_window?: string;
  min_score?: number;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ["feed", params],
    queryFn: async () => {
      const res = await apiClient.get<FeedResponse>("/feed", { params });
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useRefreshFeed() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await apiClient.post("/feed/refresh");
    },
    onSuccess: () => {
      setTimeout(() => qc.invalidateQueries({ queryKey: ["feed"] }), 3000);
    },
  });
}

export function useDismissCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (company_id: string) => {
      await apiClient.post("/feed/dismiss", { company_id });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["feed"] }),
  });
}

// ── Company ───────────────────────────────────────────────────

export function useCompanyDetail(companyId: string | null) {
  return useQuery({
    queryKey: ["company", companyId],
    queryFn: async () => {
      const res = await apiClient.get<CompanyDetailResponse>(
        `/feed/company/${companyId}`
      );
      return res.data;
    },
    enabled: Boolean(companyId),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCompanyStats() {
  return useQuery({
    queryKey: ["companies", "stats"],
    queryFn: async () => {
      const res = await apiClient.get<CompanyStats>("/companies/stats");
      return res.data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

// ── Outcomes ──────────────────────────────────────────────────

export function useLogOutcome() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: LogOutcomeRequest) => {
      await apiClient.post("/outcomes", data);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["model-accuracy"] });
      qc.invalidateQueries({ queryKey: ["attribution"] });
    },
  });
}

export function useModelAccuracy() {
  return useQuery({
    queryKey: ["model-accuracy"],
    queryFn: async () => {
      const res = await apiClient.get<ModelAccuracy>("/outcomes/model-accuracy");
      return res.data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

// ── Intelligence / Analytics ──────────────────────────────────

export function useAttributionSummary() {
  return useQuery({
    queryKey: ["attribution"],
    queryFn: async () => {
      const res = await apiClient.get<AttributionSummary>(
        "/intelligence/attribution"
      );
      return res.data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useSignalEffectiveness() {
  return useQuery({
    queryKey: ["signal-effectiveness"],
    queryFn: async () => {
      const res = await apiClient.get<SignalEffectivenessResponse>(
        "/intelligence/signal-effectiveness"
      );
      return res.data;
    },
    staleTime: 15 * 60 * 1000,
  });
}

export function usePredictionAccuracy() {
  return useQuery({
    queryKey: ["prediction-accuracy"],
    queryFn: async () => {
      const res = await apiClient.get<PredictionAccuracy>(
        "/intelligence/accuracy"
      );
      return res.data;
    },
    staleTime: 15 * 60 * 1000,
  });
}

export function useRunFeedbackLoop() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await apiClient.post("/intelligence/feedback-loop/run");
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["signal-effectiveness"] });
      qc.invalidateQueries({ queryKey: ["attribution"] });
      qc.invalidateQueries({ queryKey: ["prediction-accuracy"] });
    },
  });
}

// ── HubSpot ───────────────────────────────────────────────────

export function useHubSpotStatus() {
  return useQuery({
    queryKey: ["hubspot-status"],
    queryFn: async () => {
      const res = await apiClient.get<HubSpotStatus>(
        "/integrations/hubspot/status"
      );
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useHubSpotConnect() {
  return useMutation({
    mutationFn: async () => {
      const res = await apiClient.get<HubSpotConnectResponse>(
        "/integrations/hubspot/connect"
      );
      return res.data;
    },
    onSuccess: (data) => {
      window.location.href = data.auth_url;
    },
  });
}

export function useTriggerHubSpotSync() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await apiClient.post("/integrations/hubspot/sync/trigger");
    },
    onSuccess: () => {
      setTimeout(() => qc.invalidateQueries({ queryKey: ["hubspot-status"] }), 2000);
    },
  });
}

export function useDisconnectHubSpot() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await apiClient.delete("/integrations/hubspot/disconnect");
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["hubspot-status"] }),
  });
}

// ── Admin / Health ────────────────────────────────────────────

export function useAdminStatus() {
  return useQuery({
    queryKey: ["admin-status"],
    queryFn: async () => {
      const res = await apiClient.get<AdminStatus>("/admin/status");
      return res.data;
    },
    staleTime: 60 * 1000,
  });
}
