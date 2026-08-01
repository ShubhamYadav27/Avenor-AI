from app.db.session import engine
from sqlalchemy import text
from datetime import datetime, timezone

def debug_feed():
    with engine.connect() as conn:
        u_ws = conn.execute(text("SELECT workspace_id FROM workspace_users WHERE email='demo@avenor.ai'")).scalar()
        print('User demo@avenor.ai workspace_id:', u_ws)
        
        feed_ws = conn.execute(text("SELECT DISTINCT workspace_id FROM intelligence_feed_items")).scalars().all()
        print('Feed items workspace_ids in DB:', feed_ws)
        
        now = datetime.now(timezone.utc)
        print('Current UTC time:', now)
        
        feed_count_total = conn.execute(text("SELECT count(*) FROM intelligence_feed_items")).scalar()
        print('Total feed items in DB:', feed_count_total)

        valid_count = conn.execute(text("SELECT count(*) FROM intelligence_feed_items WHERE expires_at > :now"), {'now': now}).scalar()
        print('Feed items where expires_at > now:', valid_count)

        matches_user_ws = conn.execute(text("SELECT count(*) FROM intelligence_feed_items WHERE workspace_id = :ws"), {'ws': u_ws}).scalar()
        print('Feed items matching user workspace_id:', matches_user_ws)

if __name__ == "__main__":
    debug_feed()
