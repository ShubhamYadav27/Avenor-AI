"""Initial schema — all tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-07-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('subscription_tier', sa.String(20), nullable=False, server_default='trial'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_monitored_companies', sa.Integer(), nullable=False, server_default='500'),
        sa.Column('max_users', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    # workspace_users
    op.create_table(
        'workspace_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('external_auth_id', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', 'email'),
        sa.UniqueConstraint('external_auth_id'),
    )

    # icp_configs
    op.create_table(
        'icp_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('industries', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('min_employees', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('max_employees', sa.Integer(), nullable=False, server_default='500'),
        sa.Column('locations', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('technologies', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('excluded_technologies', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('funding_stages', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('competitor_names', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('keywords', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('product_name', sa.String(255), nullable=True),
        sa.Column('product_description', sa.Text(), nullable=True),
        sa.Column('key_pain_points', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('customer_personas', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('active_score_threshold', sa.Float(), nullable=False, server_default='0.60'),
        sa.Column('watch_score_threshold', sa.Float(), nullable=False, server_default='0.30'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id'),
    )

    # signal_weights
    op.create_table(
        'signal_weights',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('weights', postgresql.JSONB(), nullable=False),
        sa.Column('training_sample_size', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('model_accuracy', sa.Float(), nullable=True),
        sa.Column('last_trained_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('combination_accuracy', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id'),
    )

    # companies
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('apollo_id', sa.String(100), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('sub_industry', sa.String(100), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('employee_range', sa.String(50), nullable=True),
        sa.Column('location_city', sa.String(100), nullable=True),
        sa.Column('location_state', sa.String(100), nullable=True),
        sa.Column('location_country', sa.String(100), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('funding_total_usd', sa.Float(), nullable=True),
        sa.Column('last_funding_stage', sa.String(50), nullable=True),
        sa.Column('last_funding_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_funding_amount_usd', sa.Float(), nullable=True),
        sa.Column('technologies', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('icp_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('signal_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('composite_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('buying_window', sa.String(10), nullable=False, server_default='cold'),
        sa.Column('buying_window_confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('last_scored_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='monitoring'),
        sa.Column('embedding', sa.Text(), nullable=True),  # stored as vector, text for migration compat
        sa.Column('raw_apollo_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id', 'domain', name='uq_workspace_company_domain'),
    )
    op.create_index('ix_companies_workspace_score', 'companies', ['workspace_id', 'composite_score'])
    op.create_index('ix_companies_workspace_status', 'companies', ['workspace_id', 'status'])
    op.create_index(op.f('ix_companies_apollo_id'), 'companies', ['apollo_id'])
    op.create_index(op.f('ix_companies_domain'), 'companies', ['domain'])
    op.create_index(op.f('ix_companies_composite_score'), 'companies', ['composite_score'])

    # Alter embedding column to use proper vector type (pgvector)
    op.execute("ALTER TABLE companies ALTER COLUMN embedding TYPE vector(1536) USING NULL")

    # contacts
    op.create_table(
        'contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('apollo_id', sa.String(100), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('seniority', sa.String(50), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('email_status', sa.String(50), nullable=True),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'email', name='uq_contact_email'),
    )
    op.create_index(op.f('ix_contacts_apollo_id'), 'contacts', ['apollo_id'])

    # signals
    op.create_table(
        'signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signal_type', sa.String(30), nullable=False),
        sa.Column('signal_source', sa.String(30), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(1000), nullable=True),
        sa.Column('base_strength', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('decayed_strength', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_signals_company_type_detected', 'signals', ['company_id', 'signal_type', 'detected_at'])
    op.create_index('ix_signals_workspace_detected', 'signals', ['workspace_id', 'detected_at'])

    # company_scores
    op.create_table(
        'company_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('icp_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('signal_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('composite_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('icp_breakdown', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('signal_breakdown', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('buying_window', sa.String(10), nullable=False, server_default='cold'),
        sa.Column('buying_window_confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('buying_window_reasoning', sa.Text(), nullable=True),
        sa.Column('scored_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id'),
    )

    # intelligence_feed_items
    op.create_table(
        'intelligence_feed_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('composite_score', sa.Float(), nullable=False),
        sa.Column('buying_window', sa.String(10), nullable=False),
        sa.Column('buying_window_confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('signal_summary', sa.Text(), nullable=False),
        sa.Column('buying_window_reasoning', sa.Text(), nullable=False),
        sa.Column('recommended_angle', sa.Text(), nullable=False),
        sa.Column('recommended_contact_title', sa.String(255), nullable=True),
        sa.Column('top_signals', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('similar_converted_companies', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_dismissed', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_feed_workspace_score', 'intelligence_feed_items', ['workspace_id', 'composite_score'])
    op.create_index('ix_feed_workspace_window', 'intelligence_feed_items', ['workspace_id', 'buying_window'])

    # outreach_messages
    op.create_table(
        'outreach_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sequence_step', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('angle', sa.String(50), nullable=True),
        sa.Column('tone_profile', sa.String(50), nullable=True),
        sa.Column('status', sa.String(30), nullable=False, server_default='draft'),
        sa.Column('quality_gate_passed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('quality_gate_notes', sa.Text(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('context_used', postgresql.JSONB(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('instantly_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # outcomes
    op.create_table(
        'outcomes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('outreach_message_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('outcome_type', sa.String(30), nullable=False),
        sa.Column('outcome_source', sa.String(20), nullable=False),
        sa.Column('predicted_composite_score', sa.Float(), nullable=True),
        sa.Column('predicted_buying_window', sa.String(10), nullable=True),
        sa.Column('active_signals_snapshot', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('days_from_first_signal', sa.Integer(), nullable=True),
        sa.Column('days_ahead_of_organic_discovery', sa.Integer(), nullable=True),
        sa.Column('hubspot_deal_id', sa.String(255), nullable=True),
        sa.Column('deal_value_usd', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['outreach_message_id'], ['outreach_messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_outcomes_workspace_type', 'outcomes', ['workspace_id', 'outcome_type'])
    op.create_index('ix_outcomes_workspace_created', 'outcomes', ['workspace_id', 'created_at'])

    # jobs
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('job_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_traceback', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_jobs_workspace_status', 'jobs', ['workspace_id', 'status'])
    op.create_index('ix_jobs_job_type_created', 'jobs', ['job_type', 'created_at'])

    # hubspot_connections
    op.create_table(
        'hubspot_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('hub_id', sa.String(50), nullable=False),
        sa.Column('hub_domain', sa.String(255), nullable=True),
        sa.Column('access_token_encrypted', sa.Text(), nullable=False),
        sa.Column('refresh_token_encrypted', sa.Text(), nullable=False),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('webhook_id', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_error', sa.Text(), nullable=True),
        sa.Column('deals_synced', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id'),
    )


def downgrade() -> None:
    op.drop_table('hubspot_connections')
    op.drop_table('jobs')
    op.drop_table('outcomes')
    op.drop_table('outreach_messages')
    op.drop_table('intelligence_feed_items')
    op.drop_table('company_scores')
    op.drop_table('signals')
    op.drop_table('contacts')
    op.drop_table('companies')
    op.drop_table('signal_weights')
    op.drop_table('icp_configs')
    op.drop_table('workspace_users')
    op.drop_table('workspaces')
