// ── Auth ──────────────────────────────────────────────────────

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  workspace_name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  workspace_id: string;
  user_id: string;
}

export interface MeResponse {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  workspace_id: string;
  workspace_name: string;
  subscription_tier: string;
}

// ── Feed ──────────────────────────────────────────────────────

export type BuyingWindow = "hot" | "warm" | "watch" | "cold";

export interface TopSignal {
  type: string;
  title: string;
  detected_at: string;
  strength: number;
}

export interface SimilarCompany {
  name: string;
  industry: string;
  employee_count: number | null;
}

export interface FeedItemCompany {
  id: string;
  name: string;
  domain: string | null;
  industry: string | null;
  employee_count: number | null;
  employee_range: string | null;
  location: string;
  funding_stage: string | null;
  funding_total_usd: number | null;
  technologies: string[];
  linkedin_url: string | null;
  website: string | null;
}

export interface FeedItemIntelligence {
  composite_score: number;
  buying_window: BuyingWindow;
  buying_window_confidence: number;
  signal_summary: string;
  buying_window_reasoning: string;
  recommended_angle: string;
  top_signals: TopSignal[];
  similar_converted_companies: SimilarCompany[];
}

export interface RecommendedContact {
  title: string | null;
  name: string | null;
  email: string | null;
  linkedin_url: string | null;
}

export interface FeedItem {
  id: string;
  company: FeedItemCompany;
  intelligence: FeedItemIntelligence;
  recommended_contact: RecommendedContact | null;
  generated_at: string;
  expires_at: string;
  is_dismissed: boolean;
}

export interface BuyingWindowSummary {
  hot: number;
  warm: number;
  watch: number;
  cold: number;
}

export interface FeedResponse {
  total: number;
  offset: number;
  limit: number;
  items: FeedItem[];
  buying_window_summary: BuyingWindowSummary;
}

// ── Company detail ─────────────────────────────────────────────

export interface Signal {
  id: string;
  type: string;
  source: string;
  title: string;
  description: string | null;
  url: string | null;
  strength: number;
  detected_at: string;
}

export interface CompanyContact {
  id: string;
  name: string | null;
  title: string | null;
  email: string | null;
  email_status: string | null;
  linkedin_url: string | null;
  is_primary: boolean;
}

export interface CompanyDetailData {
  id: string;
  name: string;
  domain: string | null;
  industry: string | null;
  employee_count: number | null;
  location: string;
  description: string | null;
  technologies: string[];
  funding_stage: string | null;
  funding_total_usd: number | null;
  linkedin_url: string | null;
  website: string | null;
  status: string;
  composite_score: number;
  icp_score: number;
  signal_score: number | null;
  buying_window: BuyingWindow;
  last_scored_at: string | null;
}

export interface CompanyIntelligence {
  signal_summary: string | null;
  buying_window_reasoning: string | null;
  recommended_angle: string | null;
  similar_converted_companies: SimilarCompany[];
}

export interface CompanyDetailResponse {
  company: CompanyDetailData;
  intelligence: CompanyIntelligence;
  signals: Signal[];
  contacts: CompanyContact[];
}

// ── Companies list ─────────────────────────────────────────────

export interface CompanyListItem {
  id: string;
  name: string;
  domain: string | null;
  industry: string | null;
  employee_count: number | null;
  location: string;
  composite_score: number;
  buying_window: BuyingWindow;
  status: string;
  last_funding_stage: string | null;
  last_scored_at: string | null;
}

export interface CompanyStats {
  by_status: Record<string, number>;
  active_by_window: Record<string, number>;
  total: number;
}

// ── Outcomes ──────────────────────────────────────────────────

export type OutcomeType =
  | "became_opportunity"
  | "meeting_booked"
  | "replied_positive"
  | "replied_negative"
  | "no_response"
  | "wrong_timing"
  | "closed_won"
  | "closed_lost";

export interface LogOutcomeRequest {
  company_id: string;
  outcome_type: OutcomeType;
  notes?: string;
  deal_value_usd?: number;
  days_ahead_of_organic_discovery?: number;
}

export interface ModelAccuracy {
  total_outcomes: number;
  positive_outcomes: number;
  overall_conversion_rate: number;
  precision_at_0_5: number | null;
  recall_at_0_5: number | null;
  hot_warm_window_accuracy: number | null;
  avg_predicted_score_for_positives: number | null;
  avg_days_avenor_ahead: number | null;
  total_attributed_revenue_usd: number;
  by_outcome_type: Record<string, number>;
  model_confidence: string;
}

// ── Intelligence / Analytics ───────────────────────────────────

export interface AttributionSummary {
  total_attributions: number;
  positive_outcomes?: number;
  prediction_accuracy?: number | null;
  attributed_revenue_usd?: number | null;
  avg_deal_value_usd?: number | null;
  avg_days_avenor_ahead_of_crm?: number | null;
  message?: string;
}

export interface SignalEffectivenessRow {
  signal_type: string;
  total_occurrences: number;
  positive_outcomes: number;
  conversion_rate: number;
  lift_over_baseline: number | null;
  avg_deal_value_usd: number | null;
  current_weight: number | null;
  computed_at: string;
}

export interface WeightRecommendation {
  signal_type: string;
  action: "increase_weight" | "decrease_weight";
  current_weight: number;
  suggested_weight: number;
  reason: string;
  impact: "high" | "medium" | "low";
  evidence: {
    occurrences: number;
    conversion_rate: number;
    avg_deal_value_usd?: number | null;
  };
}

export interface SignalEffectivenessResponse {
  signal_effectiveness: SignalEffectivenessRow[];
  weight_recommendations: WeightRecommendation[];
  message?: string;
}

export interface PredictionAccuracy {
  total_outcomes: number;
  positive_outcomes?: number;
  overall_conversion_rate?: number;
  precision_at_0_5?: number | null;
  recall_at_0_5?: number | null;
  hot_warm_window_accuracy?: number | null;
  avg_predicted_score_for_positives?: number | null;
  avg_days_avenor_ahead?: number | null;
  total_attributed_revenue_usd?: number;
  model_confidence?: string;
  by_outcome_type?: Record<string, number>;
  message?: string;
}

// ── HubSpot ───────────────────────────────────────────────────

export interface SyncStateItem {
  object_type: string;
  status: string;
  last_synced_at: string | null;
  last_run_created: number;
  last_run_updated: number;
  last_run_error: string | null;
  historical_import_completed: boolean;
  historical_deals_imported: number;
  total_synced: number;
}

export interface HubSpotStatus {
  connected: boolean;
  hub_id?: string;
  hub_domain?: string;
  deals_synced?: number;
  last_sync_at?: string | null;
  sync_error?: string | null;
  token_expires_at?: string;
  sync_states?: SyncStateItem[];
}

export interface HubSpotConnectResponse {
  auth_url: string;
  redirect_uri: string;
}

// ── Health ────────────────────────────────────────────────────

export interface HealthResponse {
  status: "healthy" | "degraded";
  database: string;
  service: string;
  version: string;
}

export interface JobRecord {
  id: string;
  type: string;
  status: string;
  duration_seconds: number | null;
  records_processed: number;
  error: string | null;
  created_at: string;
}

export interface AdminStatus {
  workspace: {
    id: string;
    name: string;
    tier: string;
  };
  model: {
    accuracy: number | null;
    training_sample_size: number;
    last_trained_at: string | null;
    current_weights: Record<string, number>;
  };
  recent_jobs: JobRecord[];
  failed_jobs_count: number;
  alerts: string[];
}
