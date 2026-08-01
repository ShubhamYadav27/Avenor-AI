"""Phase 5.1 — AI Account Research

Adds the company_ai_research table backing the AI Revenue Copilot research
engine. Additive only: no Phase 4.1 or 4.2 table is altered.

Revision ID: 003_phase51_ai_research
Revises: 002_phase42_crm_intelligence
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "003_phase51_ai_research"
down_revision = "002_phase42_crm_intelligence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company_ai_research",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Report payload
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("buying_signals", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("pain_points", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("recommended_personas", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("outreach_strategy", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("talking_points", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("risks", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("next_actions", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        # Generation metadata
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("model_provider", sa.String(length=50), nullable=True),
        sa.Column("model_version", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=50), nullable=True),
        sa.Column("generation_duration_ms", sa.Integer(), nullable=True),
        sa.Column("input_hash", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("workspace_id", "company_id", name="uq_research_workspace_company"),
    )
    op.create_index(
        "ix_research_workspace_company", "company_ai_research", ["workspace_id", "company_id"]
    )
    op.create_index("ix_research_company_hash", "company_ai_research", ["company_id", "input_hash"])
    op.create_index("ix_research_workspace_status", "company_ai_research", ["workspace_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_research_workspace_status", table_name="company_ai_research")
    op.drop_index("ix_research_company_hash", table_name="company_ai_research")
    op.drop_index("ix_research_workspace_company", table_name="company_ai_research")
    op.drop_table("company_ai_research")
