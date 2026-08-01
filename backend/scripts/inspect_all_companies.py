import sys, os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import db_session
from app.models import Company, Signal, IntelligenceFeedItem, ICPConfig, Workspace

def inspect_all():
    with db_session() as db:
        companies = db.query(Company).all()
        print("=== ALL COMPANIES ===")
        for c in companies:
            signals = db.query(Signal).filter_by(company_id=c.id).all()
            print(f"Name: {c.name:<25} | Status: {c.status:<12} | Composite Score: {c.composite_score:.4f} | Window: {c.buying_window:<5} | Signals: {len(signals)}")
            
        print("\n=== ICP CONFIG THRESHOLDS ===")
        icps = db.query(ICPConfig).all()
        for icp in icps:
            print(f"Workspace: {icp.workspace_id} | Active Threshold: {icp.active_score_threshold} | Watch Threshold: {icp.watch_score_threshold}")

if __name__ == "__main__":
    inspect_all()
