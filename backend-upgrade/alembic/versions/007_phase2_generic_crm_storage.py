"""Phase 2 - Generic CRM storage

Revision ID: 007_phase2_generic_crm_storage
Revises: 006_phase54_ai_sales_coaching

Creates the provider-agnostic CRM tables used by the generic sync engine and
backfills existing HubSpot records without removing legacy tables.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.mock import MockConnection

revision = "007_phase2_generic_crm_storage"
down_revision = "006_phase54_ai_sales_coaching"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    if isinstance(bind, MockConnection):
        return False
    return table_name in sa.inspect(bind).get_table_names()


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    return column_name in {col["name"] for col in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("workspaces", "crm_provider"):
        op.add_column("workspaces", sa.Column("crm_provider", sa.String(length=50), nullable=True))

    if not _has_table("crm_connections"):
        op.create_table(
            "crm_connections",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_account_id", sa.String(length=255), nullable=True),
            sa.Column("external_account_name", sa.String(length=255), nullable=True),
            sa.Column("access_token_encrypted", sa.Text(), nullable=False),
            sa.Column("refresh_token_encrypted", sa.Text(), nullable=False),
            sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
            sa.Column("webhook_secret_encrypted", sa.Text(), nullable=True),
            sa.Column("webhook_ids", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
            sa.Column("provider_metadata", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("sync_error", sa.Text(), nullable=True),
            sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("workspace_id", "provider", name="uq_crm_conn_workspace_provider"),
        )
        op.create_index("ix_crm_conn_workspace", "crm_connections", ["workspace_id"])
        op.create_index("ix_crm_conn_provider", "crm_connections", ["provider"])

    if not _has_table("crm_sync_states_v2"):
        op.create_table(
            "crm_sync_states_v2",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("connection_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("object_type", sa.String(length=30), nullable=False),
            sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("total_synced", sa.Integer(), server_default="0", nullable=False),
            sa.Column("last_run_status", sa.String(length=20), server_default="pending", nullable=False),
            sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_run_created", sa.Integer(), server_default="0", nullable=False),
            sa.Column("last_run_updated", sa.Integer(), server_default="0", nullable=False),
            sa.Column("last_run_error", sa.Text(), nullable=True),
            sa.Column("historical_import_completed", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("historical_import_completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("historical_records_imported", sa.Integer(), server_default="0", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["connection_id"], ["crm_connections.id"], ondelete="SET NULL"),
            sa.UniqueConstraint("workspace_id", "provider", "object_type", name="uq_crm_sync_v2_workspace_provider_type"),
        )
        op.create_index("ix_crm_sync_v2_workspace", "crm_sync_states_v2", ["workspace_id"])

    if not _has_table("crm_accounts"):
        op.create_table(
            "crm_accounts",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_id", sa.String(length=255), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=True),
            sa.Column("domain", sa.String(length=255), nullable=True),
            sa.Column("website", sa.String(length=500), nullable=True),
            sa.Column("industry", sa.String(length=100), nullable=True),
            sa.Column("employee_count", sa.Integer(), nullable=True),
            sa.Column("location_city", sa.String(length=100), nullable=True),
            sa.Column("location_state", sa.String(length=100), nullable=True),
            sa.Column("location_country", sa.String(length=100), nullable=True),
            sa.Column("annual_revenue", sa.Float(), nullable=True),
            sa.Column("phone", sa.String(length=50), nullable=True),
            sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
            sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
            sa.UniqueConstraint("workspace_id", "provider", "external_id", name="uq_crm_acc_workspace_provider_id"),
        )
        op.create_index("ix_crm_acc_workspace", "crm_accounts", ["workspace_id"])
        op.create_index("ix_crm_acc_domain", "crm_accounts", ["domain"])

    if not _has_table("crm_contacts"):
        op.create_table(
            "crm_contacts",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_id", sa.String(length=255), nullable=False),
            sa.Column("external_account_id", sa.String(length=255), nullable=True),
            sa.Column("first_name", sa.String(length=100), nullable=True),
            sa.Column("last_name", sa.String(length=100), nullable=True),
            sa.Column("full_name", sa.String(length=255), nullable=True),
            sa.Column("email", sa.String(length=255), nullable=True),
            sa.Column("phone", sa.String(length=50), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("department", sa.String(length=100), nullable=True),
            sa.Column("seniority", sa.String(length=50), nullable=True),
            sa.Column("linkedin_url", sa.String(length=500), nullable=True),
            sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
            sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
            sa.UniqueConstraint("workspace_id", "provider", "external_id", name="uq_crm_contact_workspace_provider_id"),
        )
        op.create_index("ix_crm_contact_workspace", "crm_contacts", ["workspace_id"])
        op.create_index("ix_crm_contact_email", "crm_contacts", ["email"])

    if not _has_table("crm_leads"):
        op.create_table(
            "crm_leads",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_id", sa.String(length=255), nullable=False),
            sa.Column("first_name", sa.String(length=100), nullable=True),
            sa.Column("last_name", sa.String(length=100), nullable=True),
            sa.Column("full_name", sa.String(length=255), nullable=True),
            sa.Column("email", sa.String(length=255), nullable=True),
            sa.Column("company_name", sa.String(length=255), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("phone", sa.String(length=50), nullable=True),
            sa.Column("status", sa.String(length=100), nullable=True),
            sa.Column("source", sa.String(length=100), nullable=True),
            sa.Column("external_owner_id", sa.String(length=255), nullable=True),
            sa.Column("converted", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("converted_account_id", sa.String(length=255), nullable=True),
            sa.Column("converted_contact_id", sa.String(length=255), nullable=True),
            sa.Column("converted_opportunity_id", sa.String(length=255), nullable=True),
            sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
            sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("workspace_id", "provider", "external_id", name="uq_crm_lead_workspace_provider_id"),
        )
        op.create_index("ix_crm_lead_workspace", "crm_leads", ["workspace_id"])
        op.create_index("ix_crm_lead_email", "crm_leads", ["email"])
        op.create_index("ix_crm_lead_status", "crm_leads", ["workspace_id", "provider", "status"])

    if not _has_table("crm_opportunities"):
        op.create_table(
            "crm_opportunities",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_id", sa.String(length=255), nullable=False),
            sa.Column("external_account_id", sa.String(length=255), nullable=True),
            sa.Column("external_contact_ids", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
            sa.Column("external_owner_id", sa.String(length=255), nullable=True),
            sa.Column("name", sa.String(length=500), nullable=True),
            sa.Column("stage", sa.String(length=100), nullable=True),
            sa.Column("pipeline", sa.String(length=100), nullable=True),
            sa.Column("amount_usd", sa.Float(), nullable=True),
            sa.Column("probability", sa.Float(), nullable=True),
            sa.Column("close_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("is_closed_won", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("is_closed_lost", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("days_to_close", sa.Integer(), nullable=True),
            sa.Column("avenor_predicted_score", sa.Float(), nullable=True),
            sa.Column("avenor_predicted_window", sa.String(length=10), nullable=True),
            sa.Column("avenor_first_detected_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("days_ahead_of_crm", sa.Integer(), nullable=True),
            sa.Column("is_historical", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
            sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
            sa.UniqueConstraint("workspace_id", "provider", "external_id", name="uq_crm_opp_workspace_provider_id"),
        )
        op.create_index("ix_crm_opp_workspace_stage", "crm_opportunities", ["workspace_id", "stage"])
        op.create_index("ix_crm_opp_company", "crm_opportunities", ["company_id"])
        op.create_index("ix_crm_opp_provider", "crm_opportunities", ["workspace_id", "provider"])

    if not _has_table("crm_users"):
        op.create_table(
            "crm_users",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("external_id", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=True),
            sa.Column("first_name", sa.String(length=100), nullable=True),
            sa.Column("last_name", sa.String(length=100), nullable=True),
            sa.Column("full_name", sa.String(length=255), nullable=True),
            sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("role", sa.String(length=100), nullable=True),
            sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
            sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("workspace_id", "provider", "external_id", name="uq_crm_user_workspace_provider_id"),
        )
        op.create_index("ix_crm_user_workspace", "crm_users", ["workspace_id"])

    if not _has_table("crm_audit_logs"):
        op.create_table(
            "crm_audit_logs",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("operation", sa.String(length=100), nullable=False),
            sa.Column("object_type", sa.String(length=30), nullable=True),
            sa.Column("external_id", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("detail", sa.Text(), nullable=True),
            sa.Column("error", sa.Text(), nullable=True),
            sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("duration_ms", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="SET NULL"),
        )
        op.create_index("ix_crm_audit_workspace", "crm_audit_logs", ["workspace_id", "created_at"])
        op.create_index("ix_crm_audit_provider", "crm_audit_logs", ["provider", "created_at"])
        op.create_index("ix_crm_audit_operation", "crm_audit_logs", ["operation"])

    _backfill_hubspot_data()


def _backfill_hubspot_data() -> None:
    op.execute(
        """
        INSERT INTO crm_connections (
            id, workspace_id, provider, external_account_id, external_account_name,
            access_token_encrypted, refresh_token_encrypted, token_expires_at,
            scopes, webhook_ids, provider_metadata, is_active, sync_error, last_sync_at, created_at, updated_at
        )
        SELECT
            id, workspace_id, 'hubspot', hub_id, hub_domain,
            access_token_encrypted, refresh_token_encrypted, token_expires_at,
            '[]'::jsonb,
            CASE WHEN webhook_id IS NULL THEN '[]'::jsonb ELSE jsonb_build_array(webhook_id) END,
            jsonb_build_object('hub_id', hub_id, 'hub_domain', hub_domain, 'source', 'legacy_hubspot_connections'),
            is_active, sync_error, last_sync_at, created_at, now()
        FROM hubspot_connections
        ON CONFLICT (workspace_id, provider) DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE workspaces
        SET crm_provider = 'hubspot'
        WHERE crm_provider IS NULL
          AND id IN (SELECT workspace_id FROM hubspot_connections WHERE is_active = true)
        """
    )
    op.execute(
        """
        INSERT INTO crm_opportunities (
            id, workspace_id, company_id, provider, external_id, external_account_id,
            external_contact_ids, external_owner_id, name, stage, pipeline, amount_usd,
            close_date, created_date, is_closed_won, is_closed_lost, closed_at,
            days_to_close, avenor_predicted_score, avenor_predicted_window,
            avenor_first_detected_at, days_ahead_of_crm, is_historical, raw_data,
            synced_at, updated_at
        )
        SELECT
            id, workspace_id, company_id, 'hubspot', hubspot_deal_id, hubspot_company_id,
            hubspot_contact_ids, hubspot_owner_id, deal_name, deal_stage, pipeline_id, amount_usd,
            close_date, created_date, is_closed_won, is_closed_lost, closed_at,
            days_to_close, avenor_predicted_score, avenor_predicted_window,
            avenor_first_detected_at, days_ahead_of_crm, is_historical, raw_properties,
            synced_at, updated_at
        FROM hubspot_deals
        ON CONFLICT (workspace_id, provider, external_id) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO crm_users (
            id, workspace_id, provider, external_id, email, first_name, last_name,
            full_name, is_active, raw_data, synced_at
        )
        SELECT
            id, workspace_id, 'hubspot', hubspot_owner_id, email, first_name, last_name,
            NULLIF(trim(coalesce(first_name, '') || ' ' || coalesce(last_name, '')), ''),
            is_active, jsonb_build_object('source', 'legacy_hubspot_owners'), synced_at
        FROM hubspot_owners
        ON CONFLICT (workspace_id, provider, external_id) DO NOTHING
        """
    )


def downgrade() -> None:
    for table_name in (
        "crm_audit_logs",
        "crm_users",
        "crm_opportunities",
        "crm_leads",
        "crm_contacts",
        "crm_accounts",
        "crm_sync_states_v2",
        "crm_connections",
    ):
        if _has_table(table_name):
            op.drop_table(table_name)
    if _has_column("workspaces", "crm_provider"):
        op.drop_column("workspaces", "crm_provider")


