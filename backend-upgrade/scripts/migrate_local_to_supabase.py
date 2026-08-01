"""
Migrate complete database from local PostgreSQL to Supabase PostgreSQL.
Preserves all primary keys, foreign keys, vectors, JSONB columns, and relationships.
"""
from sqlalchemy import create_engine, text, MetaData, inspect
from app.core.config import settings

LOCAL_DB_URL = "postgresql://avenor_user:avenor_pass@localhost:5432/avenor_db"
SUPABASE_DB_URL = settings.DATABASE_URL

TABLE_ORDER = [
    "workspaces",
    "workspace_users",
    "icp_configs",
    "signal_weights",
    "companies",
    "contacts",
    "signals",
    "company_scores",
    "intelligence_feed_items",
    "outreach_messages",
    "outcomes",
    "jobs",
    "hubspot_connections",
    "crm_sync_states",
    "hubspot_owners",
    "hubspot_deals",
    "outcome_attributions",
    "signal_effectiveness",
    "company_ai_research",
    "company_ai_emails",
    "company_ai_briefings",
    "company_ai_sales_coaching",
]

def run_migration():
    print("Connecting to Source (Local DB)...")
    src_engine = create_engine(LOCAL_DB_URL)
    
    print("Connecting to Destination (Supabase DB)...")
    dst_engine = create_engine(SUPABASE_DB_URL)

    src_meta = MetaData()
    src_meta.reflect(bind=src_engine)

    # 1. Truncate destination tables in reverse order to avoid FK constraint issues
    print("\n--- Truncating existing destination tables in Supabase ---")
    with dst_engine.begin() as dst_conn:
        for table_name in reversed(TABLE_ORDER):
            if table_name in dst_meta_tables(dst_engine):
                print(f"Truncating Supabase table: {table_name}")
                dst_conn.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE;'))

    # 2. Copy data table by table in dependency order
    print("\n--- Copying data from Local DB -> Supabase DB ---")
    total_rows_copied = 0
    with src_engine.connect() as src_conn:
        with dst_engine.begin() as dst_conn:
            for table_name in TABLE_ORDER:
                if table_name not in src_meta.tables:
                    print(f"Skipping {table_name} (not present in source)")
                    continue
                
                table = src_meta.tables[table_name]
                rows = src_conn.execute(table.select()).mappings().all()
                count = len(rows)
                print(f"Migrating {table_name}: {count} rows")
                
                if count > 0:
                    # Insert in chunks of 500
                    chunk_size = 500
                    for i in range(0, count, chunk_size):
                        chunk = [dict(row) for row in rows[i:i+chunk_size]]
                        dst_conn.execute(table.insert(), chunk)
                    total_rows_copied += count

    print(f"\n[SUCCESS] Migration Complete! Total rows copied to Supabase: {total_rows_copied}")

def dst_meta_tables(engine):
    inspector = inspect(engine)
    return set(inspector.get_table_names())

if __name__ == "__main__":
    run_migration()
