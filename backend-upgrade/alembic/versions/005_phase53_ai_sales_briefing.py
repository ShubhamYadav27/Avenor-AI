"""Phase 5.3 - AI Sales Briefing

Adds company-level AI sales briefings derived from existing research, emails,
CRM context and buying signals.

Revision ID: 005_phase53_ai_sales_briefing
Revises: 004_phase52_ai_email_generator
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "005_phase53_ai_sales_briefing"
down_revision = "004_phase52_ai_email_generator"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company_ai_briefings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("research_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_email_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("briefing_json", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("model_provider", sa.String(length=50), nullable=True),
        sa.Column("model_version", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=50), nullable=True),
        sa.Column("generation_duration_ms", sa.Integer(), nullable=True),
        sa.Column("input_hash", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["research_id"], ["company_ai_research.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_email_id"], ["company_ai_emails.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ai_briefings_workspace_company", "company_ai_briefings", ["workspace_id", "company_id"])
    op.create_index("ix_ai_briefings_workspace_status", "company_ai_briefings", ["workspace_id", "status"])
    op.create_index("ix_ai_briefings_research_hash", "company_ai_briefings", ["research_id", "input_hash"])


def downgrade() -> None:
    op.drop_index("ix_ai_briefings_research_hash", table_name="company_ai_briefings")
    op.drop_index("ix_ai_briefings_workspace_status", table_name="company_ai_briefings")
    op.drop_index("ix_ai_briefings_workspace_company", table_name="company_ai_briefings")
    op.drop_table("company_ai_briefings")
