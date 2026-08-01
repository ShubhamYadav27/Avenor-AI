import sys, os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import db_session
from app.models import Workspace, Company, IntelligenceFeedItem, Contact
from app.modules.scoring.engine import run_scoring_for_workspace
from app.modules.intelligence.engine import run_feed_generation_for_workspace

def regenerate():
    with db_session() as db:
        workspaces = db.query(Workspace).filter_by(is_active=True).all()
        for ws in workspaces:
            print(f"--- Running scoring for workspace {ws.name} ({ws.id}) ---")
            score_stats = run_scoring_for_workspace(db, str(ws.id))
            print(f"Scoring stats: {score_stats}")

            print(f"--- Running feed generation for workspace {ws.name} ({ws.id}) ---")
            feed_stats = run_feed_generation_for_workspace(db, str(ws.id), force_refresh=True)
            print(f"Feed stats: {feed_stats}")

        print("\n=== VERIFYING INTELLIGENCE FEED ITEMS ===")
        now = datetime.now(timezone.utc)
        items = db.query(IntelligenceFeedItem).all()
        print(f"Total feed items in DB: {len(items)}")
        active_items = [i for i in items if not i.is_dismissed and i.expires_at > now]
        print(f"Active (unexpired, non-dismissed) feed items: {len(active_items)}")
        
        for item in active_items:
            comp = db.get(Company, item.company_id)
            contacts = db.query(Contact).filter_by(company_id=item.company_id).all()
            primary = next((c for c in contacts if c.is_primary), contacts[0] if contacts else None)
            print(f"  Item ID: {item.id}")
            print(f"    Company: {comp.name} ({comp.domain})")
            print(f"    Composite Score: {item.composite_score}")
            print(f"    Buying Window: {item.buying_window}")
            print(f"    Signal Summary: {item.signal_summary[:80]}...")
            print(f"    Recommended Contact: {primary.full_name if primary else 'None'} ({item.recommended_contact_title})")
            print(f"    Expires At: {item.expires_at}")

if __name__ == "__main__":
    regenerate()
