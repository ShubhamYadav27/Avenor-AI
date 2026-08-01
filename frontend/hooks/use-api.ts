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
  CompanyListResponse,
  CompanyStats,
  LogOutcomeRequest,
  ModelAccuracy,
  AttributionSummary,
  SignalEffectivenessResponse,
  PredictionAccuracy,
  HubSpotStatus,
  AdminStatus,
  HubSpotConnectResponse,
  ResearchResponse,
  EmailGenerateRequest,
  EmailListResponse,
  EmailResponse,
  BriefingGenerateRequest,
  BriefingListResponse,
  BriefingResponse,
  SalesCoachGenerateRequest,
  SalesCoachListResponse,
  SalesCoachResponse,
  CrmProvidersResponse,
  CrmConnectionsResponse,
  CrmOAuthStartResponse,
  CrmSyncResult,
  CrmDisconnectResult,
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

export function useCompanies(params?: { status?: string; buying_window?: string; limit?: number }) {
  return useQuery({
    queryKey: ["companies", params],
    queryFn: async () => {
      const res = await apiClient.get<CompanyListResponse>("/companies", { params });
      return res.data;
    },
  });
}

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

// ── AI Account Research (Phase 5.1) ───────────────────────────

/** Statuses where generation is finished and polling must stop. */
const RESEARCH_TERMINAL_STATUSES = ["completed", "failed", "none"];

const RESEARCH_POLL_INTERVAL_MS = 2500;

export function useCompanyResearch(companyId: string | null) {
  return useQuery({
    queryKey: ["research", companyId],
    queryFn: async () => {
      const res = await apiClient.get<ResearchResponse>(
        `/companies/${companyId}/research`
      );
      return res.data;
    },
    enabled: Boolean(companyId),
    // Poll only while generation is actually in flight, then stop. Returning
    // false ends the interval — otherwise a completed report would be refetched
    // every 2.5s forever.
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || RESEARCH_TERMINAL_STATUSES.includes(status)) return false;
      return RESEARCH_POLL_INTERVAL_MS;
    },
    refetchOnWindowFocus: false,
    staleTime: 0,
  });
}

export function useGenerateResearch(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (options?: { force_refresh?: boolean }) => {
      const res = await apiClient.post<ResearchResponse>(
        `/companies/${companyId}/research`,
        null,
        { params: { force_refresh: options?.force_refresh ?? false } }
      );
      return res.data;
    },
    onSuccess: (data) => {
      // Seed the cache with the POST result so the panel switches to its
      // pending/completed state immediately, before the first poll lands.
      qc.setQueryData(["research", companyId], data);
    },
  });
}

// ── Outcomes ──────────────────────────────────────────────────

// -- AI Email Generator (Phase 5.2) ------------------------------------------

const EMAIL_TERMINAL_STATUSES = ["completed", "failed", "none"];
const EMAIL_POLL_INTERVAL_MS = 2500;

export function useCompanyEmails(companyId: string | null) {
  return useQuery({
    queryKey: ["emails", companyId],
    queryFn: async () => {
      const res = await apiClient.get<EmailListResponse>(
        `/companies/${companyId}/emails`
      );
      return res.data;
    },
    enabled: Boolean(companyId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || EMAIL_TERMINAL_STATUSES.includes(status)) return false;
      return EMAIL_POLL_INTERVAL_MS;
    },
    refetchOnWindowFocus: false,
    staleTime: 0,
  });
}

export function useGenerateEmails(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: EmailGenerateRequest) => {
      const res = await apiClient.post<EmailListResponse>(
        `/companies/${companyId}/emails`,
        payload
      );
      return res.data;
    },
    onSuccess: (data) => {
      qc.setQueryData(["emails", companyId], data);
    },
  });
}

export function useCopyEmail(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (emailId: string) => {
      const res = await apiClient.post<EmailResponse>(`/emails/${emailId}/copy`);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["emails", companyId] }),
  });
}

export function useRegenerateEmail(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (emailId: string) => {
      const res = await apiClient.post<EmailResponse>(
        `/emails/${emailId}/regenerate`,
        { force_refresh: true }
      );
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["emails", companyId] }),
  });
}

export function useArchiveEmail(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (emailId: string) => {
      const res = await apiClient.post<EmailResponse>(`/emails/${emailId}/archive`);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["emails", companyId] }),
  });
}

// -- AI Sales Briefing (Phase 5.3) ------------------------------------------

const BRIEFING_TERMINAL_STATUSES = ["completed", "failed", "none"];
const BRIEFING_POLL_INTERVAL_MS = 2500;

export function useCompanyBriefings(companyId: string | null) {
  return useQuery({
    queryKey: ["briefings", companyId],
    queryFn: async () => {
      const res = await apiClient.get<BriefingListResponse>(
        `/companies/${companyId}/briefings`
      );
      return res.data;
    },
    enabled: Boolean(companyId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || BRIEFING_TERMINAL_STATUSES.includes(status)) return false;
      return BRIEFING_POLL_INTERVAL_MS;
    },
    refetchOnWindowFocus: false,
    staleTime: 0,
  });
}

export function useGenerateBriefing(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: BriefingGenerateRequest = {}) => {
      const res = await apiClient.post<BriefingResponse>(
        `/companies/${companyId}/briefings`,
        payload
      );
      return res.data;
    },
    onSuccess: (data) => {
      qc.setQueryData<BriefingListResponse>(["briefings", companyId], (old) => ({
        company_id: data.company_id,
        status: data.status === "archived" ? old?.status ?? "none" : data.status,
        cached: data.cached,
        briefings: [
          data,
          ...(old?.briefings.filter((briefing) => briefing.id !== data.id) ?? []),
        ],
        error_message: data.error_message,
      }));
    },
  });
}

export function useRegenerateBriefing(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (briefingId: string) => {
      const res = await apiClient.post<BriefingResponse>(
        `/briefings/${briefingId}/regenerate`,
        { force_refresh: true }
      );
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["briefings", companyId] }),
  });
}

export function useArchiveBriefing(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (briefingId: string) => {
      const res = await apiClient.post<BriefingResponse>(
        `/briefings/${briefingId}/archive`
      );
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["briefings", companyId] }),
  });
}

// -- AI Sales Coach (Phase 5.4) ---------------------------------------------

const SALES_COACH_TERMINAL_STATUSES = ["completed", "failed", "none"];
const SALES_COACH_POLL_INTERVAL_MS = 2500;

export function useCompanySalesCoaching(companyId: string | null) {
  return useQuery({
    queryKey: ["sales-coaching", companyId],
    queryFn: async () => {
      const res = await apiClient.get<SalesCoachListResponse>(
        `/companies/${companyId}/sales-coaching`
      );
      return res.data;
    },
    enabled: Boolean(companyId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || SALES_COACH_TERMINAL_STATUSES.includes(status)) return false;
      return SALES_COACH_POLL_INTERVAL_MS;
    },
    refetchOnWindowFocus: false,
    staleTime: 0,
  });
}

export function useGenerateSalesCoaching(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: SalesCoachGenerateRequest = {}) => {
      const res = await apiClient.post<SalesCoachResponse>(
        `/companies/${companyId}/sales-coaching`,
        payload
      );
      return res.data;
    },
    onSuccess: (data) => {
      qc.setQueryData<SalesCoachListResponse>(["sales-coaching", companyId], (old) => ({
        company_id: data.company_id,
        status: data.status === "archived" ? old?.status ?? "none" : data.status,
        cached: data.cached,
        coaching: [
          data,
          ...(old?.coaching.filter((coaching) => coaching.id !== data.id) ?? []),
        ],
        error_message: data.error_message,
      }));
    },
  });
}

export function useRegenerateSalesCoaching(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (coachingId: string) => {
      const res = await apiClient.post<SalesCoachResponse>(
        `/sales-coaching/${coachingId}/regenerate`,
        { force_refresh: true }
      );
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sales-coaching", companyId] }),
  });
}

export function useArchiveSalesCoaching(companyId: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (coachingId: string) => {
      const res = await apiClient.post<SalesCoachResponse>(
        `/sales-coaching/${coachingId}/archive`
      );
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sales-coaching", companyId] }),
  });
}

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

// ── Generic CRM ───────────────────────────────────────────────

/** GET /crm/providers — lists all registered CRM providers with enabled/configured flags */
export function useCrmProviders() {
  return useQuery({
    queryKey: ["crm-providers"],
    queryFn: async () => {
      const res = await apiClient.get<CrmProvidersResponse>("/crm/providers");
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

/** GET /crm/connections — returns all CRM connections for the current workspace */
export function useCrmConnections() {
  return useQuery({
    queryKey: ["crm-connections"],
    queryFn: async () => {
      const res = await apiClient.get<CrmConnectionsResponse>("/crm/connections");
      return res.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

/** POST /crm/{provider}/oauth/start — generates OAuth authorization URL for a specific provider */
export function useCrmStartOAuth() {
  return useMutation({
    mutationFn: async (provider: string) => {
      const res = await apiClient.post<CrmOAuthStartResponse>(
        `/crm/${provider}/oauth/start`
      );
      return res.data;
    },
    onSuccess: (data) => {
      // Redirect to provider OAuth page
      window.location.href = data.auth_url;
    },
  });
}

/** POST /crm/{provider}/disconnect — disconnects a specific provider connection */
export function useCrmDisconnect() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (provider: string) => {
      const res = await apiClient.post<CrmDisconnectResult>(
        `/crm/${provider}/disconnect`
      );
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["crm-connections"] });
      qc.invalidateQueries({ queryKey: ["crm-providers"] });
    },
  });
}

/** POST /crm/{provider}/sync — triggers incremental sync for a specific provider */
export function useCrmSyncProvider() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (provider: string) => {
      const res = await apiClient.post<CrmSyncResult>(`/crm/${provider}/sync`);
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["crm-connections"] });
      qc.invalidateQueries({ queryKey: ["crm-providers"] });
      qc.invalidateQueries({ queryKey: ["crm-sync-status"] });
      qc.invalidateQueries({ queryKey: ["crm-analytics"] });
      qc.invalidateQueries({ queryKey: ["crm-deals"] });
      qc.invalidateQueries({ queryKey: ["crm-contacts"] });
      qc.invalidateQueries({ queryKey: ["crm-leads"] });
      qc.invalidateQueries({ queryKey: ["crm-users"] });
      qc.invalidateQueries({ queryKey: ["admin-status"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["feed"] });
      qc.invalidateQueries({ queryKey: ["hubspot-status"] });
      setTimeout(() => {
        qc.invalidateQueries({ queryKey: ["crm-connections"] });
        qc.invalidateQueries({ queryKey: ["crm-sync-status"] });
        qc.invalidateQueries({ queryKey: ["crm-analytics"] });
        qc.invalidateQueries({ queryKey: ["crm-deals"] });
        qc.invalidateQueries({ queryKey: ["crm-contacts"] });
        qc.invalidateQueries({ queryKey: ["crm-leads"] });
        qc.invalidateQueries({ queryKey: ["crm-users"] });
        qc.invalidateQueries({ queryKey: ["admin-status"] });
        qc.invalidateQueries({ queryKey: ["companies"] });
        qc.invalidateQueries({ queryKey: ["feed"] });
      }, 1500);
    },
  });
}

/** POST /crm/sync — triggers incremental sync for the workspace active CRM provider */
export function useCrmSyncActive() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const res = await apiClient.post<CrmSyncResult>("/crm/sync");
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["crm-connections"] });
      qc.invalidateQueries({ queryKey: ["crm-providers"] });
      qc.invalidateQueries({ queryKey: ["crm-sync-status"] });
      qc.invalidateQueries({ queryKey: ["crm-analytics"] });
      qc.invalidateQueries({ queryKey: ["crm-deals"] });
      qc.invalidateQueries({ queryKey: ["crm-contacts"] });
      qc.invalidateQueries({ queryKey: ["crm-leads"] });
      qc.invalidateQueries({ queryKey: ["crm-users"] });
      qc.invalidateQueries({ queryKey: ["admin-status"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["feed"] });
      qc.invalidateQueries({ queryKey: ["hubspot-status"] });
      setTimeout(() => {
        qc.invalidateQueries({ queryKey: ["crm-connections"] });
        qc.invalidateQueries({ queryKey: ["crm-sync-status"] });
        qc.invalidateQueries({ queryKey: ["crm-analytics"] });
        qc.invalidateQueries({ queryKey: ["crm-deals"] });
        qc.invalidateQueries({ queryKey: ["crm-contacts"] });
        qc.invalidateQueries({ queryKey: ["crm-leads"] });
        qc.invalidateQueries({ queryKey: ["crm-users"] });
        qc.invalidateQueries({ queryKey: ["admin-status"] });
        qc.invalidateQueries({ queryKey: ["companies"] });
        qc.invalidateQueries({ queryKey: ["feed"] });
      }, 1500);
    },
  });
}

/** Imperatively refresh all CRM-related queries without a network mutation */
export function useRefreshCrmStatus() {
  const qc = useQueryClient();
  return () => {
    qc.invalidateQueries({ queryKey: ["crm-connections"] });
    qc.invalidateQueries({ queryKey: ["crm-providers"] });
    qc.invalidateQueries({ queryKey: ["crm-sync-status"] });
    qc.invalidateQueries({ queryKey: ["crm-analytics"] });
    qc.invalidateQueries({ queryKey: ["crm-deals"] });
    qc.invalidateQueries({ queryKey: ["crm-contacts"] });
    qc.invalidateQueries({ queryKey: ["crm-leads"] });
    qc.invalidateQueries({ queryKey: ["crm-users"] });
    qc.invalidateQueries({ queryKey: ["admin-status"] });
    qc.invalidateQueries({ queryKey: ["companies"] });
    qc.invalidateQueries({ queryKey: ["feed"] });
    qc.invalidateQueries({ queryKey: ["hubspot-status"] });
  };
}

export interface CrmAnalyticsSummary {
  summary: {
    total_accounts: number;
    total_contacts: number;
    total_leads: number;
    total_opportunities: number;
    pipeline_value: number;
    won_revenue: number;
    lost_revenue: number;
    avg_deal_size: number;
    open_count: number;
    won_count: number;
    lost_count: number;
  };
  stage_distribution: Array<{ stage: string; count: number; value: number }>;
  owner_performance: Array<{ owner: string; count: number; total_value: number; won_value: number }>;
}

export function useCrmAnalytics() {
  return useQuery({
    queryKey: ["crm-analytics"],
    queryFn: async () => {
      const res = await apiClient.get<CrmAnalyticsSummary>("/crm/analytics");
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export interface CrmSyncObjectState {
  last_synced_at: string | null;
  last_run_at: string | null;
  last_run_status: "completed" | "failed" | "pending" | string;
  last_run_created: number;
  last_run_updated: number;
  last_run_error: string | null;
  total_synced: number;
  current_sync_records: number;
  historical_completed: boolean;
}

export interface CrmSyncStatus {
  connected: boolean;
  provider: string | null;
  last_sync_at: string | null;
  sync_error: string | null;
  is_syncing: boolean;
  objects: Record<string, CrmSyncObjectState>;
}

/** Poll GET /crm/sync/status — used to display sync progress on the CRM page. */
export function useCrmSyncStatus(enabled: boolean = true) {
  return useQuery({
    queryKey: ["crm-sync-status"],
    queryFn: async () => {
      const res = await apiClient.get<CrmSyncStatus>("/crm/sync/status");
      return res.data;
    },
    enabled,
    // Poll every 8 seconds while a sync may be in progress
    refetchInterval: 8000,
    staleTime: 0,
  });
}

export interface CrmContactItem {
  id: string;
  external_id: string | null;
  first_name: string | null;
  last_name: string | null;
  full_name: string;
  email: string | null;
  phone: string | null;
  title: string | null;
  department: string | null;
  seniority: string | null;
  company_id: string | null;
  company_name: string;
  company_domain: string;
  synced_at: string | null;
  raw_data?: Record<string, any>;
}

export function useCrmContacts(params?: { q?: string; company_id?: string; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["crm-contacts", params],
    queryFn: async () => {
      const res = await apiClient.get<{ total: number; contacts: CrmContactItem[] }>("/crm/contacts", { params });
      return res.data;
    },
  });
}

export interface CrmDealItem {
  id: string;
  external_id: string | null;
  name: string;
  stage: string | null;
  amount_usd: number | null;
  probability: number | null;
  close_date: string | null;
  created_date: string | null;
  is_closed_won: boolean;
  is_closed_lost: boolean;
  company_id: string | null;
  company_name: string;
  company_domain: string;
  provider: string;
  raw_data?: Record<string, any>;
}

export function useCrmDeals(params?: { q?: string; stage?: string; company_id?: string; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["crm-deals", params],
    queryFn: async () => {
      const res = await apiClient.get<{ total: number; opportunities: CrmDealItem[] }>("/crm/opportunities", { params });
      return res.data;
    },
  });
}

export interface CrmLeadItem {
  id: string;
  external_id: string | null;
  first_name: string | null;
  last_name: string | null;
  full_name: string;
  company_name: string | null;
  title: string | null;
  email: string | null;
  phone: string | null;
  status: string;
  source: string;
  provider: string;
  synced_at: string | null;
  raw_data?: Record<string, any>;
}

export function useCrmLeads(params?: { q?: string; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["crm-leads", params],
    queryFn: async () => {
      const res = await apiClient.get<{ total: number; leads: CrmLeadItem[] }>("/crm/leads", { params });
      return res.data;
    },
  });
}

export interface CrmUserItem {
  id: string;
  external_id: string | null;
  name: string | null;
  email: string | null;
  provider: string;
  is_active: boolean;
  synced_at: string | null;
}

export function useCrmUsers(params?: { q?: string; limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["crm-users", params],
    queryFn: async () => {
      const res = await apiClient.get<{ total: number; users: CrmUserItem[] }>("/crm/users", { params });
      return res.data;
    },
  });
}


