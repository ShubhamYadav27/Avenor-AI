from app.db.session import engine
from sqlalchemy import text

def verify():
    with engine.connect() as conn:
        tables = [
            'workspaces', 'workspace_users', 'icp_configs', 'signal_weights',
            'companies', 'contacts', 'signals', 'company_scores',
            'intelligence_feed_items', 'outcomes', 'jobs', 'hubspot_connections',
            'crm_sync_states', 'hubspot_owners', 'outcome_attributions',
            'signal_effectiveness', 'company_ai_research', 'company_ai_emails',
            'company_ai_briefings', 'company_ai_sales_coaching'
        ]
        print("=== Supabase Database Row Counts ===")
        for t in tables:
            cnt = conn.execute(text(f'SELECT count(*) FROM "{t}"')).scalar()
            print(f"{t:30s}: {cnt} rows")

if __name__ == "__main__":
    verify()
