"""
All database models in one file for MVP simplicity.
Split into separate files once codebase grows.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Text, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
import enum


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class LeadStatus(str, enum.Enum):
    NEW = "new"
    ENRICHED = "enriched"
    SCORED = "scored"
    QUEUED = "queued"
    IN_SEQUENCE = "in_sequence"
    REPLIED = "replied"
    MEETING_BOOKED = "meeting_booked"
    DISQUALIFIED = "disqualified"


class SignalType(str, enum.Enum):
    HIRING = "hiring"
    FUNDING = "funding"
    TECH_CHANGE = "tech_change"
    EXPANSION = "expansion"
    INTENT = "intent"


class OutreachStatus(str, enum.Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"


class ReplyType(str, enum.Enum):
    POSITIVE = "positive"
    SOFT_INTEREST = "soft_interest"
    OBJECTION = "objection"
    HARD_NO = "hard_no"
    OUT_OF_OFFICE = "out_of_office"
    UNKNOWN = "unknown"


# ─────────────────────────────────────────────
# Companies
# ─────────────────────────────────────────────

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    apollo_id = Column(String(100), unique=True, nullable=True, index=True)

    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    employee_count = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)
    founded_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, default=list)   # ["Snowflake", "Airflow", ...]
    funding_total = Column(Float, nullable=True)
    last_funding_round = Column(String(50), nullable=True)
    last_funding_date = Column(DateTime, nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)

    # Scoring
    icp_score = Column(Float, default=0.0)       # 0.0 – 1.0
    signal_score = Column(Float, default=0.0)    # 0.0 – 1.0
    composite_score = Column(Float, default=0.0) # final prioritization score

    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    raw_data = Column(JSON, nullable=True)       # full Apollo response

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contacts = relationship("Contact", back_populates="company")
    signals = relationship("Signal", back_populates="company")
    outreach_messages = relationship("OutreachMessage", back_populates="company")


# ─────────────────────────────────────────────
# Contacts
# ─────────────────────────────────────────────

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    apollo_id = Column(String(100), unique=True, nullable=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    full_name = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    seniority = Column(String(50), nullable=True)   # "vp", "director", "c_suite"
    email = Column(String(255), nullable=True, index=True)
    email_verified = Column(Boolean, default=False)
    linkedin_url = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)

    is_primary = Column(Boolean, default=False)     # main contact for outreach
    raw_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="contacts")
    outreach_messages = relationship("OutreachMessage", back_populates="contact")
    replies = relationship("Reply", back_populates="contact")


# ─────────────────────────────────────────────
# Signals
# ─────────────────────────────────────────────

class Signal(Base):
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    signal_type = Column(Enum(SignalType), nullable=False)
    signal_source = Column(String(100), nullable=True)  # "apollo", "crunchbase", etc.
    raw_value = Column(Text, nullable=True)              # e.g. "Head of Data Engineering"
    strength = Column(Float, default=0.5)                # 0.0 – 1.0 base weight
    decayed_score = Column(Float, default=0.5)           # after recency decay
    detected_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)   # extra context

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="signals")


# ─────────────────────────────────────────────
# Outreach Messages
# ─────────────────────────────────────────────

class OutreachMessage(Base):
    __tablename__ = "outreach_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)

    sequence_step = Column(Integer, default=1)
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)
    angle = Column(String(50), nullable=True)       # "pain_led", "outcome_led", "curiosity"
    tone_profile = Column(String(50), nullable=True) # "founder", "vp_eng", "cmo"

    status = Column(Enum(OutreachStatus), default=OutreachStatus.DRAFT)
    sent_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)

    # Tracking
    context_used = Column(JSON, nullable=True)       # what signals/context was passed to LLM
    instantly_id = Column(String(255), nullable=True) # external ID from Instantly
    word_count = Column(Integer, nullable=True)
    passed_quality_gate = Column(Boolean, default=False)
    quality_gate_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="outreach_messages")
    contact = relationship("Contact", back_populates="outreach_messages")
    reply = relationship("Reply", back_populates="outreach_message", uselist=False)


# ─────────────────────────────────────────────
# Replies
# ─────────────────────────────────────────────

class Reply(Base):
    __tablename__ = "replies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    outreach_message_id = Column(UUID(as_uuid=True), ForeignKey("outreach_messages.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)

    raw_body = Column(Text, nullable=False)
    reply_type = Column(Enum(ReplyType), default=ReplyType.UNKNOWN)
    classification_confidence = Column(Float, nullable=True)
    classification_reasoning = Column(Text, nullable=True)

    slack_notified = Column(Boolean, default=False)
    crm_synced = Column(Boolean, default=False)
    requires_human_action = Column(Boolean, default=False)

    received_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    outreach_message = relationship("OutreachMessage", back_populates="reply")
    contact = relationship("Contact", back_populates="replies")
