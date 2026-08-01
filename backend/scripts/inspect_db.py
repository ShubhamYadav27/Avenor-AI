import sys, os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import db_session
from app.models import (
    Workspace, WorkspaceUser, ICPConfig, Company, Contact, Signal,
    CompanyScore, IntelligenceFeedItem
)

def inspect():
    with db_session() as db:
        workspaces = db.query(Workspace).all()
        print(f"Workspaces count: {len(workspaces)}")
        for ws in workspaces:
            print(f"  Workspace ID: {ws.id}, Name: {ws.name}, Slug: {ws.slug}, Active: {ws.is_active}")
        
        users = db.query(WorkspaceUser).all()
        print(f"\nWorkspace Users count: {len(users)}")
        for u in users:
            print(f"  User: {u.email}, Workspace ID: {u.workspace_id}, Role: {u.role}")

        companies = db.query(Company).all()
        print(f"\nCompanies count: {len(companies)}")
        for c in companies[:10]:
            print(f"  Company ID: {c.id}, Name: {c.name}, Status: {c.status}, Composite Score: {c.composite_score}, Buying Window: {c.buying_window}, Last Scored: {c.last_scored_at}")

        contacts = db.query(Contact).all()
        print(f"\nContacts count: {len(contacts)}")

        signals = db.query(Signal).all()
        print(f"\nSignals count: {len(signals)}")

        scores = db.query(CompanyScore).all()
        print(f"\nCompany Scores count: {len(scores)}")
        for s in scores[:10]:
            print(f"  Company ID: {s.company_id}, Composite Score: {s.composite_score}, Buying Window: {s.buying_window}, Scored At: {s.scored_at}")

        feed_items = db.query(IntelligenceFeedItem).all()
        print(f"\nIntelligence Feed Items count: {len(feed_items)}")
        now = datetime.now(timezone.utc)
        for f in feed_items:
            # handle tz info
            exp = f.expires_at
            if exp and exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            is_expired = exp <= now if exp else True
            print(f"  Feed Item ID: {f.id}, Company ID: {f.company_id}, Score: {f.composite_score}, Window: {f.buying_window}, Generated: {f.generated_at}, Expires: {f.expires_at}, Is Dismissed: {f.is_dismissed}, Is Expired: {is_expired}")

if __name__ == "__main__":
    inspect()
