import sys, os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import db_session
from app.models import Company, IntelligenceFeedItem, WorkspaceUser
from app.api.routes.feed import _serialize_feed_item

def verify():
    with db_session() as db:
        user = db.query(WorkspaceUser).filter_by(email="demo@avenor.ai").first()
        now = datetime.now(timezone.utc)
        
        all_companies = db.query(Company).filter_by(workspace_id=user.workspace_id).all()
        scored_companies = [c for c in all_companies if c.last_scored_at is not None]

        items = (
            db.query(IntelligenceFeedItem)
            .filter_by(workspace_id=user.workspace_id)
            .all()
        )
        
        active_items = (
            db.query(IntelligenceFeedItem)
            .filter(
                IntelligenceFeedItem.workspace_id == user.workspace_id,
                IntelligenceFeedItem.is_dismissed == False,
                IntelligenceFeedItem.expires_at > now,
            )
            .all()
        )
        
        print("==================================================")
        print("FINAL VERIFICATION METRICS")
        print("==================================================")
        print(f"Total Companies:                 {len(all_companies)}")
        print(f"Scored Companies:                {len(scored_companies)}")
        print(f"Total Feed Items:                {len(items)}")
        print(f"Active (Unexpired) Feed Items:   {len(active_items)}")
        print("--------------------------------------------------")
        print("Active Feed Accounts:")
        for item in active_items:
            comp = db.get(Company, item.company_id)
            print(f" - [{item.buying_window.upper()}] {comp.name:<25} | Composite Score: {item.composite_score:.3f} | Expires: {item.expires_at}")

if __name__ == "__main__":
    verify()
