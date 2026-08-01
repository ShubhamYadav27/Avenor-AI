"""Phase 5.2 - AI Email Generator

Adds generated outbound email drafts derived from company_ai_research.

Revision ID: 004_phase52_ai_email_generator
Revises: 003_phase51_ai_research
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "004_phase52_ai_email_generator"
down_revision = "003_phase51_ai_research"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company_ai_emails",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("research_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("email_type", sa.String(length=50), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("cta", sa.Text(), nullable=True),
        sa.Column("cta_type", sa.String(length=50), nullable=False),
        sa.Column("tone", sa.String(length=50), nullable=False),
        sa.Column("length", sa.String(length=20), nullable=False),
        sa.Column("variation", sa.String(length=1), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("copy_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("regeneration_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("model_provider", sa.String(length=50), nullable=True),
        sa.Column("model_version", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=50), nullable=True),
        sa.Column("generation_duration_ms", sa.Integer(), nullable=True),
        sa.Column("research_input_hash", sa.String(length=64), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["research_id"], ["company_ai_research.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_ai_emails_workspace_company", "company_ai_emails", ["workspace_id", "company_id"])
    op.create_index("ix_ai_emails_research_hash", "company_ai_emails", ["research_id", "research_input_hash"])
    op.create_index("ix_ai_emails_workspace_status", "company_ai_emails", ["workspace_id", "status"])
    op.create_index("ix_ai_emails_contact", "company_ai_emails", ["contact_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_emails_contact", table_name="company_ai_emails")
    op.drop_index("ix_ai_emails_workspace_status", table_name="company_ai_emails")
    op.drop_index("ix_ai_emails_research_hash", table_name="company_ai_emails")
    op.drop_index("ix_ai_emails_workspace_company", table_name="company_ai_emails")
    op.drop_table("company_ai_emails")
