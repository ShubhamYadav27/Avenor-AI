"""Phase 4.2 — CRM Intelligence and Feedback Loop tables

Revision ID: 002_phase42_crm_intelligence
Revises: 001_initial_schema
Create Date: 2025-07-06

Adds:
  - crm_sync_states      : per-workspace per-object incremental sync cursor
  - hubspot_deals        : CRM deal records with Avenor attribution
  - hubspot_owners       : HubSpot deal owners / salespeople
  - outcome_attributions : links outcomes back to signals + feed recommendations
  - signal_effectiveness : aggregated signal → revenue correlation analytics

Also adds ENCRYPTION_KEY guidance (no schema change — token columns already exist
in hubspot_connections from 001; Phase 4.2 upgrades the encryption algorithm in
application code only).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_phase42_crm_intelligence"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── crm_sync_states ───────────────────────────────────────
    op.create_table(
        "crm_sync_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("object_type", sa.String(30), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_synced", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_run_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_run_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_run_error", sa.Text(), nullable=True),
        sa.Column("historical_import_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("historical_import_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("historical_deals_imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "object_type", name="uq_sync_state_workspace_type"),
    )

    # ── hubspot_owners ────────────────────────────────────────
    op.create_table(
        "hubspot_owners",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hubspot_owner_id", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "hubspot_owner_id", name="uq_hs_owner_workspace"),
    )

    # ── hubspot_deals ─────────────────────────────────────────
    op.create_table(
        "hubspot_deals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("hubspot_deal_id", sa.String(50), nullable=False),
        sa.Column("hubspot_company_id", sa.String(50), nullable=True),
        sa.Column("hubspot_contact_ids", postgresql.JSONB(), nullable=True, server_default="[]"),
        sa.Column("hubspot_owner_id", sa.String(50), nullable=True),
        sa.Column("deal_name", sa.String(500), nullable=True),
        sa.Column("deal_stage", sa.String(100), nullable=True),
        sa.Column("pipeline_id", sa.String(50), nullable=True),
        sa.Column("amount_usd", sa.Float(), nullable=True),
        sa.Column("close_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_closed_won", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_closed_lost", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("days_to_close", sa.Integer(), nullable=True),
        sa.Column("avenor_predicted_score", sa.Float(), nullable=True),
        sa.Column("avenor_predicted_window", sa.String(10), nullable=True),
        sa.Column("avenor_first_detected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("days_ahead_of_crm", sa.Integer(), nullable=True),
        sa.Column("is_historical", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("raw_properties", postgresql.JSONB(), nullable=True, server_default="{}"),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workspace_id", "hubspot_deal_id", name="uq_hs_deal_workspace"),
    )
    op.create_index(
        "ix_hubspot_deals_workspace_stage",
        "hubspot_deals", ["workspace_id", "deal_stage"],
    )
    op.create_index("ix_hubspot_deals_company", "hubspot_deals", ["company_id"])

    # ── outcome_attributions ──────────────────────────────────
    op.create_table(
        "outcome_attributions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("outcome_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("hubspot_deal_id", sa.String(50), nullable=True),
        sa.Column("feed_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("predicted_score_at_recommendation", sa.Float(), nullable=True),
        sa.Column("predicted_window_at_recommendation", sa.String(10), nullable=True),
        sa.Column("recommended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signals_at_recommendation", postgresql.JSONB(), nullable=True, server_default="[]"),
        sa.Column("outcome_type", sa.String(30), nullable=True),
        sa.Column("deal_value_usd", sa.Float(), nullable=True),
        sa.Column("days_from_recommendation_to_outcome", sa.Integer(), nullable=True),
        sa.Column("days_avenor_ahead_of_crm", sa.Integer(), nullable=True),
        sa.Column("prediction_was_correct", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["feed_item_id"], ["intelligence_feed_items.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["outcome_id"], ["outcomes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attribution_workspace", "outcome_attributions", ["workspace_id"])
    op.create_index("ix_attribution_company", "outcome_attributions", ["company_id"])

    # ── signal_effectiveness ──────────────────────────────────
    op.create_table(
        "signal_effectiveness",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("signal_type", sa.String(30), nullable=False),
        sa.Column("total_occurrences", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("positive_outcome_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversion_rate", sa.Float(), nullable=True),
        sa.Column("avg_deal_value_usd", sa.Float(), nullable=True),
        sa.Column("avg_days_to_close", sa.Float(), nullable=True),
        sa.Column("current_weight", sa.Float(), nullable=True),
        sa.Column("lift_over_baseline", sa.Float(), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workspace_id", "signal_type", name="uq_effectiveness_workspace_signal"
        ),
    )


def downgrade() -> None:
    op.drop_table("signal_effectiveness")
    op.drop_table("outcome_attributions")
    op.drop_table("hubspot_deals")
    op.drop_table("hubspot_owners")
    op.drop_table("crm_sync_states")
