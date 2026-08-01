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

export interface CompanyOpportunity {
  id: string;
  name: string;
  stage: string | null;
  amount_usd: number | null;
  close_date: string | null;
  is_closed_won: boolean;
  is_closed_lost: boolean;
}

export interface CompanyDetailResponse {
  company: CompanyDetailData;
  intelligence: CompanyIntelligence;
  signals: Signal[];
  contacts: CompanyContact[];
  opportunities?: CompanyOpportunity[];
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
  buying_window_reasoning?: string | null;
}

export interface CompanyListResponse {
  total: number;
  companies: CompanyListItem[];
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

// ── Generic CRM ──────────────────────────────────────────────

export interface CrmProvider {
  name: string;
  display_name: string;
  description: string;
  enabled: boolean;
  configured: boolean;
}

export interface CrmProvidersResponse {
  providers: CrmProvider[];
}

export interface CrmConnection {
  id: string;
  provider: string;
  external_account_id: string | null;
  external_account_name: string | null;
  is_active: boolean;
  last_sync_at: string | null;
  sync_error: string | null;
  created_at: string | null;
}

export interface CrmConnectionsResponse {
  connections: CrmConnection[];
}

export interface CrmOAuthStartResponse {
  auth_url: string;
  redirect_uri?: string;
  state?: string;
}

export interface CrmSyncResult {
  provider: string;
  status: string;
  records_synced?: number;
  error?: string | null;
  [key: string]: unknown;
}

export interface CrmDisconnectResult {
  status: string;
  provider: string;
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
  current_sync_records: number;
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

// ── AI Account Research (Phase 5.1) ───────────────────────────

export type ResearchStatus =
  | "none"
  | "pending"
  | "running"
  | "completed"
  | "failed";

export type SignalStrength = "strong" | "moderate" | "weak";
export type PriorityLevel = "high" | "medium" | "low";
export type RiskSeverity = "high" | "medium" | "low";

export interface ResearchBuyingSignal {
  title: string;
  evidence: string;
  why_it_matters: string;
  strength: SignalStrength;
}

export interface ResearchPainPoint {
  title: string;
  description: string;
  evidence: string | null;
  priority: PriorityLevel;
}

export interface ResearchPersona {
  title: string;
  rationale: string;
  matched_contact_name: string | null;
  priority: PriorityLevel;
}

export interface ResearchOutreachStrategy {
  recommended_channel: string;
  timing: string;
  angle: string;
  opening_hook: string;
}

export interface ResearchTalkingPoint {
  point: string;
  supporting_detail: string;
}

export interface ResearchRisk {
  title: string;
  description: string;
  mitigation: string | null;
  severity: RiskSeverity;
}

export interface ResearchNextAction {
  action: string;
  rationale: string;
  priority: PriorityLevel;
  suggested_timeframe: string | null;
}

export interface ResearchMeta {
  model_provider: string | null;
  model_version: string | null;
  prompt_version: string | null;
  generation_duration_ms: number | null;
  input_hash: string | null;
}

export interface ResearchResponse {
  company_id: string;
  status: ResearchStatus;
  cached: boolean;
  is_stale: boolean;
  error_message: string | null;
  summary: string | null;
  buying_signals: ResearchBuyingSignal[];
  pain_points: ResearchPainPoint[];
  recommended_personas: ResearchPersona[];
  outreach_strategy: ResearchOutreachStrategy | null;
  talking_points: ResearchTalkingPoint[];
  risks: ResearchRisk[];
  next_actions: ResearchNextAction[];
  meta: ResearchMeta;
  generated_at: string | null;
  updated_at: string | null;
}

// -- AI Email Generator (Phase 5.2) ------------------------------------------

export type EmailStatus = "pending" | "running" | "completed" | "failed" | "archived";
export type EmailListStatus = "none" | "pending" | "running" | "completed" | "failed";
export type EmailType =
  | "cold_email"
  | "follow_up_email"
  | "re_engagement_email"
  | "meeting_request"
  | "product_demo_invitation"
  | "value_proposition_email";
export type EmailTone = "professional" | "friendly" | "executive" | "technical" | "consultative";
export type EmailLength = "short" | "medium" | "long";
export type EmailCTA = "book_meeting" | "demo" | "quick_call" | "reply" | "learn_more";
export type EmailVariation = "A" | "B" | "C";

export interface EmailGenerateRequest {
  email_type: EmailType;
  tone: EmailTone;
  length: EmailLength;
  cta_type: EmailCTA;
  contact_id?: string | null;
  force_refresh?: boolean;
}

export interface EmailMeta {
  model_provider: string | null;
  model_version: string | null;
  prompt_version: string | null;
  generation_duration_ms: number | null;
  research_input_hash: string | null;
}

export interface EmailResponse {
  id: string;
  workspace_id: string;
  company_id: string;
  research_id: string;
  contact_id: string | null;
  email_type: EmailType;
  subject: string | null;
  body: string | null;
  cta: string | null;
  cta_type: EmailCTA;
  tone: EmailTone;
  length: EmailLength;
  variation: EmailVariation;
  reasoning: string | null;
  status: EmailStatus;
  copy_count: number;
  regeneration_count: number;
  version: number;
  error_message: string | null;
  meta: EmailMeta;
  created_at: string | null;
  updated_at: string | null;
  archived_at: string | null;
}

export interface EmailListResponse {
  company_id: string;
  status: EmailListStatus;
  cached: boolean;
  emails: EmailResponse[];
  error_message: string | null;
}

// -- AI Sales Briefing (Phase 5.3) ------------------------------------------

export type BriefingStatus = "none" | "pending" | "running" | "completed" | "failed" | "archived";
export type BriefingListStatus = "none" | "pending" | "running" | "completed" | "failed";

export interface BriefingGenerateRequest {
  force_refresh?: boolean;
  source_email_id?: string | null;
}

export interface BriefingSignal {
  title: string;
  evidence: string;
  strength: SignalStrength;
}

export interface BriefingStakeholder {
  name: string | null;
  title: string;
  priority: PriorityLevel;
  rationale: string;
}

export interface BriefingContactPriority {
  contact_or_persona: string;
  priority: PriorityLevel;
  reason: string;
}

export interface BriefingPreviousEmail {
  subject: string;
  variation: string;
  summary: string;
  cta: string | null;
}

export interface BriefingOpportunity {
  title: string;
  rationale: string;
  priority: PriorityLevel;
}

export interface BriefingSuggestedResponse {
  objection: string;
  response: string;
}

export interface BriefingRisk {
  title: string;
  description: string;
  severity: RiskSeverity;
  mitigation: string | null;
}

export interface BriefingPayload {
  executive_summary: string;
  company_overview: string;
  current_buying_signals: BriefingSignal[];
  why_buy_now: string[];
  recent_company_changes: string[];
  existing_relationship_summary: string;
  crm_activity_summary: string;
  key_stakeholders: BriefingStakeholder[];
  recommended_contact_priority: BriefingContactPriority[];
  existing_ai_research_summary: string;
  previous_generated_emails: BriefingPreviousEmail[];
  pain_points: ResearchPainPoint[];
  business_opportunities: BriefingOpportunity[];
  suggested_value_proposition: string;
  competitive_landscape: string;
  discovery_questions: string[];
  technical_questions: string[];
  business_questions: string[];
  executive_questions: string[];
  possible_customer_objections: string[];
  suggested_responses: BriefingSuggestedResponse[];
  recommended_meeting_agenda: string[];
  meeting_goals: string[];
  recommended_demo_focus: string[];
  recommended_pricing_strategy: string;
  recommended_follow_up_timeline: string[];
  next_best_action: string;
  risk_factors: BriefingRisk[];
  confidence_score: number;
  confidence_explanation: string;
}

export interface BriefingMeta {
  model_provider: string | null;
  model_version: string | null;
  prompt_version: string | null;
  generation_duration_ms: number | null;
  input_hash: string | null;
}

export interface BriefingResponse {
  id: string;
  workspace_id: string;
  company_id: string;
  research_id: string;
  source_email_id: string | null;
  summary: string | null;
  briefing_json: BriefingPayload | null;
  confidence_score: number | null;
  status: BriefingStatus;
  cached: boolean;
  error_message: string | null;
  meta: BriefingMeta;
  created_at: string | null;
  updated_at: string | null;
  archived_at: string | null;
}

export interface BriefingListResponse {
  company_id: string;
  status: BriefingListStatus;
  cached: boolean;
  briefings: BriefingResponse[];
  error_message: string | null;
}

// -- AI Sales Coach (Phase 5.4) ---------------------------------------------

export type SalesCoachStatus = "none" | "pending" | "running" | "completed" | "failed" | "archived";
export type SalesCoachListStatus = "none" | "pending" | "running" | "completed" | "failed";
export type DealStage =
  | "prospecting"
  | "discovery"
  | "qualification"
  | "demo"
  | "proposal"
  | "negotiation"
  | "closing"
  | "expansion";
export type DealHealth = "strong" | "healthy" | "at_risk" | "blocked" | "unknown";
export type ObjectionSeverity = "critical" | "high" | "medium" | "low";
export type StakeholderInfluence =
  | "decision_maker"
  | "influencer"
  | "champion"
  | "blocker"
  | "unknown";

export interface SalesCoachGenerateRequest {
  force_refresh?: boolean;
  deal_stage?: DealStage | null;
  briefing_id?: string | null;
}

export interface SalesCoachEvidence {
  buying_signals: string[];
  research_findings: string[];
  crm_information: string[];
  briefing_insights: string[];
}

export interface SalesCoachSignal {
  title: string;
  evidence: string;
  impact: string;
  strength: SignalStrength;
}

export interface SalesCoachRisk {
  title: string;
  description: string;
  severity: RiskSeverity;
  mitigation: string | null;
  evidence: SalesCoachEvidence;
}

export interface SalesCoachStakeholder {
  name: string | null;
  title: string;
  influence: StakeholderInfluence;
  priority: PriorityLevel;
  likely_motivation: string;
  recommended_approach: string;
}

export interface SalesCoachObjection {
  objection: string;
  severity: ObjectionSeverity;
  customer_statement: string;
  why_customer_may_say_this: string;
  recommended_response: string;
  follow_up_question: string;
  goal_of_response: string;
  evidence: SalesCoachEvidence;
}

export interface SalesCoachBattleCard {
  competitor_or_alternative: string;
  likely_positioning: string;
  avenor_advantage: string;
  risk: string;
  recommended_talk_track: string;
}

export interface SalesCoachStageGuidance {
  stage: DealStage;
  objective: string;
  coaching: string;
  questions: string[];
}

export interface SalesCoachActionItem {
  action: string;
  rationale: string;
  priority: PriorityLevel;
  owner: string | null;
  timeframe: string | null;
}

export interface SalesCoachPayload {
  executive_coaching_summary: string;
  deal_health_assessment: DealHealth;
  win_probability: number;
  win_probability_explanation: string;
  positive_buying_signals: SalesCoachSignal[];
  risk_factors: SalesCoachRisk[];
  deal_blockers: SalesCoachRisk[];
  decision_maker_analysis: string;
  stakeholder_influence_map: SalesCoachStakeholder[];
  likely_customer_objections: SalesCoachObjection[];
  competitive_battle_cards: SalesCoachBattleCard[];
  competitor_comparison: string;
  pricing_negotiation_strategy: string;
  discovery_coaching: SalesCoachStageGuidance;
  demo_coaching: SalesCoachStageGuidance;
  negotiation_coaching: SalesCoachStageGuidance;
  closing_coaching: SalesCoachStageGuidance;
  expansion_opportunity: string;
  recommended_next_best_action: string;
  immediate_action_plan: SalesCoachActionItem[];
  follow_up_strategy: SalesCoachActionItem[];
  long_term_action_plan: SalesCoachActionItem[];
  escalation_recommendation: string | null;
  confidence_score: number;
  confidence_explanation: string;
  explainability: SalesCoachEvidence;
}

export interface SalesCoachMeta {
  model_provider: string | null;
  model_version: string | null;
  prompt_version: string | null;
  generation_duration_ms: number | null;
  input_hash: string | null;
}

export interface SalesCoachResponse {
  id: string;
  workspace_id: string;
  company_id: string;
  research_id: string;
  briefing_id: string | null;
  summary: string | null;
  coaching_json: SalesCoachPayload | null;
  win_probability: number | null;
  confidence_score: number | null;
  status: SalesCoachStatus;
  cached: boolean;
  error_message: string | null;
  meta: SalesCoachMeta;
  created_at: string | null;
  updated_at: string | null;
  archived_at: string | null;
}

export interface SalesCoachListResponse {
  company_id: string;
  status: SalesCoachListStatus;
  cached: boolean;
  coaching: SalesCoachResponse[];
  error_message: string | null;
}
