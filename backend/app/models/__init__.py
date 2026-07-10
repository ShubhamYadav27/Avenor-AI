"""
Complete database schema for Avenor.
All models in one file for MVP — split by module once the team grows.
"""
import uuid
import enum
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint,
    Index, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class SubscriptionTier(str, enum.Enum):
    TRIAL = "trial"
    STARTER = "starter"
    GROWTH = "growth"
    SCALE = "scale"

class WorkspaceUserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"

class SignalType(str, enum.Enum):
    HIRING = "hiring"
    FUNDING = "funding"
    TECH_CHANGE = "tech_change"
    EXPANSION = "expansion"
    INTENT = "intent"
    LEADERSHIP_CHANGE = "leadership_change"
    PRODUCT_LAUNCH = "product_launch"
    NEWS = "news"

class SignalSource(str, enum.Enum):
    APOLLO = "apollo"
    CRUNCHBASE = "crunchbase"
    BUILTWITH = "builtwith"
    NEWS = "news"
    SEC = "sec"
    MANUAL = "manual"

class CompanyStatus(str, enum.Enum):
    MONITORING = "monitoring"
    ACTIVE = "active"
    IN_SEQUENCE = "in_sequence"
    CONVERTED = "converted"
    DISQUALIFIED = "disqualified"

class BuyingWindowLabel(str, enum.Enum):
    HOT = "hot"
    WARM = "warm"
    WATCH = "watch"
    COLD = "cold"

class OutcomeType(str, enum.Enum):
    BECAME_OPPORTUNITY = "became_opportunity"
    MEETING_BOOKED = "meeting_booked"
    REPLIED_POSITIVE = "replied_positive"
    REPLIED_NEGATIVE = "replied_negative"
    NO_RESPONSE = "no_response"
    WRONG_TIMING = "wrong_timing"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class OutcomeSource(str, enum.Enum):
    HUBSPOT = "hubspot"
    MANUAL = "manual"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    subscription_tier: Mapped[str] = mapped_column(String(20), default=SubscriptionTier.TRIAL, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_monitored_companies: Mapped[int] = mapped_column(Integer, default=500)
    max_users: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users: Mapped[list["WorkspaceUser"]] = relationship(back_populates="workspace")
    icp_config: Mapped["ICPConfig"] = relationship(back_populates="workspace", uselist=False)
    companies: Mapped[list["Company"]] = relationship(back_populates="workspace")
    outcomes: Mapped[list["Outcome"]] = relationship(back_populates="workspace")
    signal_weights: Mapped["SignalWeights"] = relationship(back_populates="workspace", uselist=False)
    hubspot_connection: Mapped["HubSpotConnection"] = relationship(back_populates="workspace", uselist=False)
    jobs: Mapped[list["Job"]] = relationship(back_populates="workspace")


class WorkspaceUser(Base):
    __tablename__ = "workspace_users"
    __table_args__ = (UniqueConstraint("workspace_id", "email"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    external_auth_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=WorkspaceUserRole.MEMBER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    hashed_password: Mapped[str | None] = mapped_column(String(255))

    workspace: Mapped["Workspace"] = relationship(back_populates="users")


class ICPConfig(Base):
    __tablename__ = "icp_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True)
    industries: Mapped[list] = mapped_column(JSONB, default=list)
    min_employees: Mapped[int] = mapped_column(Integer, default=50)
    max_employees: Mapped[int] = mapped_column(Integer, default=500)
    locations: Mapped[list] = mapped_column(JSONB, default=list)
    technologies: Mapped[list] = mapped_column(JSONB, default=list)
    excluded_technologies: Mapped[list] = mapped_column(JSONB, default=list)
    funding_stages: Mapped[list] = mapped_column(JSONB, default=list)
    competitor_names: Mapped[list] = mapped_column(JSONB, default=list)
    keywords: Mapped[list] = mapped_column(JSONB, default=list)
    product_name: Mapped[str | None] = mapped_column(String(255))
    product_description: Mapped[str | None] = mapped_column(Text)
    key_pain_points: Mapped[list] = mapped_column(JSONB, default=list)
    customer_personas: Mapped[list] = mapped_column(JSONB, default=list)
    active_score_threshold: Mapped[float] = mapped_column(Float, default=0.60)
    watch_score_threshold: Mapped[float] = mapped_column(Float, default=0.30)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="icp_config")


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        Index("ix_companies_workspace_score", "workspace_id", "composite_score"),
        Index("ix_companies_workspace_status", "workspace_id", "status"),
        UniqueConstraint("workspace_id", "domain", name="uq_workspace_company_domain"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    apollo_id: Mapped[str | None] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255), index=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    website: Mapped[str | None] = mapped_column(String(500))
    industry: Mapped[str | None] = mapped_column(String(100))
    sub_industry: Mapped[str | None] = mapped_column(String(100))
    employee_count: Mapped[int | None] = mapped_column(Integer)
    employee_range: Mapped[str | None] = mapped_column(String(50))
    location_city: Mapped[str | None] = mapped_column(String(100))
    location_state: Mapped[str | None] = mapped_column(String(100))
    location_country: Mapped[str | None] = mapped_column(String(100))
    founded_year: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    funding_total_usd: Mapped[float | None] = mapped_column(Float)
    last_funding_stage: Mapped[str | None] = mapped_column(String(50))
    last_funding_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_funding_amount_usd: Mapped[float | None] = mapped_column(Float)
    technologies: Mapped[list] = mapped_column(JSONB, default=list)
    icp_score: Mapped[float] = mapped_column(Float, default=0.0)
    signal_score: Mapped[float] = mapped_column(Float, default=0.0)
    composite_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    buying_window: Mapped[str] = mapped_column(String(10), default=BuyingWindowLabel.COLD)
    buying_window_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    last_scored_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default=CompanyStatus.MONITORING)
    embedding: Mapped[list | None] = mapped_column(Vector(1536))
    raw_apollo_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="companies")
    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")
    signals: Mapped[list["Signal"]] = relationship(back_populates="company")
    score_snapshot: Mapped["CompanyScore"] = relationship(back_populates="company", uselist=False)
    intelligence_items: Mapped[list["IntelligenceFeedItem"]] = relationship(back_populates="company")
    outcomes: Mapped[list["Outcome"]] = relationship(back_populates="company")
    outreach_messages: Mapped[list["OutreachMessage"]] = relationship(back_populates="company")


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("company_id", "email", name="uq_contact_email"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    apollo_id: Mapped[str | None] = mapped_column(String(100), index=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    full_name: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(String(255))
    seniority: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
    email_status: Mapped[str | None] = mapped_column(String(50))
    linkedin_url: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(50))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company"] = relationship(back_populates="contacts")
    outreach_messages: Mapped[list["OutreachMessage"]] = relationship(back_populates="contact")


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (
        Index("ix_signals_company_type_detected", "company_id", "signal_type", "detected_at"),
        Index("ix_signals_workspace_detected", "workspace_id", "detected_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    signal_source: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(String(1000))
    base_strength: Mapped[float] = mapped_column(Float, default=0.5)
    decayed_strength: Mapped[float] = mapped_column(Float, default=0.5)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # 'metadata' is reserved by SQLAlchemy — use signal_metadata mapped to 'metadata' column
    signal_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    company: Mapped["Company"] = relationship(back_populates="signals")


class CompanyScore(Base):
    __tablename__ = "company_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True)
    icp_score: Mapped[float] = mapped_column(Float, default=0.0)
    signal_score: Mapped[float] = mapped_column(Float, default=0.0)
    composite_score: Mapped[float] = mapped_column(Float, default=0.0)
    icp_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict)
    signal_breakdown: Mapped[list] = mapped_column(JSONB, default=list)
    buying_window: Mapped[str] = mapped_column(String(10), default="cold")
    buying_window_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    buying_window_reasoning: Mapped[str | None] = mapped_column(Text)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company"] = relationship(back_populates="score_snapshot")


class SignalWeights(Base):
    __tablename__ = "signal_weights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True)
    weights: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    training_sample_size: Mapped[int] = mapped_column(Integer, default=0)
    model_accuracy: Mapped[float | None] = mapped_column(Float)
    last_trained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    combination_accuracy: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="signal_weights")


class IntelligenceFeedItem(Base):
    __tablename__ = "intelligence_feed_items"
    __table_args__ = (
        Index("ix_feed_workspace_score", "workspace_id", "composite_score"),
        Index("ix_feed_workspace_window", "workspace_id", "buying_window"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    composite_score: Mapped[float] = mapped_column(Float, nullable=False)
    buying_window: Mapped[str] = mapped_column(String(10), nullable=False)
    buying_window_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    signal_summary: Mapped[str] = mapped_column(Text, nullable=False)
    buying_window_reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_angle: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_contact_title: Mapped[str | None] = mapped_column(String(255))
    top_signals: Mapped[list] = mapped_column(JSONB, default=list)
    similar_converted_companies: Mapped[list] = mapped_column(JSONB, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)

    company: Mapped["Company"] = relationship(back_populates="intelligence_items")


class OutreachMessage(Base):
    __tablename__ = "outreach_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id", ondelete="SET NULL"))
    sequence_step: Mapped[int] = mapped_column(Integer, default=1)
    subject: Mapped[str | None] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    angle: Mapped[str | None] = mapped_column(String(50))
    tone_profile: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="draft")
    quality_gate_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    quality_gate_notes: Mapped[str | None] = mapped_column(Text)
    word_count: Mapped[int | None] = mapped_column(Integer)
    context_used: Mapped[dict | None] = mapped_column(JSONB)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    instantly_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped["Company"] = relationship(back_populates="outreach_messages")
    contact: Mapped["Contact"] = relationship(back_populates="outreach_messages")


class Outcome(Base):
    __tablename__ = "outcomes"
    __table_args__ = (
        Index("ix_outcomes_workspace_type", "workspace_id", "outcome_type"),
        Index("ix_outcomes_workspace_created", "workspace_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    outreach_message_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("outreach_messages.id", ondelete="SET NULL"))
    outcome_type: Mapped[str] = mapped_column(String(30), nullable=False)
    outcome_source: Mapped[str] = mapped_column(String(20), nullable=False)
    predicted_composite_score: Mapped[float | None] = mapped_column(Float)
    predicted_buying_window: Mapped[str | None] = mapped_column(String(10))
    active_signals_snapshot: Mapped[list] = mapped_column(JSONB, default=list)
    days_from_first_signal: Mapped[int | None] = mapped_column(Integer)
    days_ahead_of_organic_discovery: Mapped[int | None] = mapped_column(Integer)
    hubspot_deal_id: Mapped[str | None] = mapped_column(String(255))
    deal_value_usd: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="outcomes")
    company: Mapped["Company"] = relationship(back_populates="outcomes")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_workspace_status", "workspace_id", "status"),
        Index("ix_jobs_job_type_created", "job_type", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"))
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=JobStatus.PENDING)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    error_traceback: Mapped[str | None] = mapped_column(Text)
    job_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="jobs")


class HubSpotConnection(Base):
    __tablename__ = "hubspot_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True)
    hub_id: Mapped[str] = mapped_column(String(50), nullable=False)
    hub_domain: Mapped[str | None] = mapped_column(String(255))
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    webhook_id: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sync_error: Mapped[str | None] = mapped_column(Text)
    deals_synced: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    workspace: Mapped["Workspace"] = relationship(back_populates="hubspot_connection")
