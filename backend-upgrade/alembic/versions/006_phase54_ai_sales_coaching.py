"""Phase 5.4 - AI Sales Coach

Adds company-level AI revenue coaching derived from existing research,
briefings, generated emails, CRM context and buying signals.

Revision ID: 006_phase54_ai_sales_coaching
Revises: 005_phase53_ai_sales_briefing
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "006_phase54_ai_sales_coaching"
down_revision = "005_phase53_ai_sales_briefing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company_ai_sales_coaching",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("research_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("briefing_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("coaching_json", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("win_probability", sa.Float(), nullable=True),
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
        sa.ForeignKeyConstraint(["briefing_id"], ["company_ai_briefings.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_ai_sales_coaching_workspace_company",
        "company_ai_sales_coaching",
        ["workspace_id", "company_id"],
    )
    op.create_index(
        "ix_ai_sales_coaching_workspace_status",
        "company_ai_sales_coaching",
        ["workspace_id", "status"],
    )
    op.create_index(
        "ix_ai_sales_coaching_context_hash",
        "company_ai_sales_coaching",
        ["research_id", "briefing_id", "input_hash"],
    )


def downgrade() -> None:
    op.drop_index("ix_ai_sales_coaching_context_hash", table_name="company_ai_sales_coaching")
    op.drop_index("ix_ai_sales_coaching_workspace_status", table_name="company_ai_sales_coaching")
    op.drop_index("ix_ai_sales_coaching_workspace_company", table_name="company_ai_sales_coaching")
    op.drop_table("company_ai_sales_coaching")
