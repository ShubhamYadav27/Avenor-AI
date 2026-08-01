import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.session import db_session
from app.models import Company, Signal, IntelligenceFeedItem, ICPConfig, Workspace

def main():
    with db_session() as db:
        companies = db.query(Company).filter(~Company.name.like('Historical Co%')).all()
        print("=== NON-HISTORICAL COMPANIES ===")
        for c in companies:
            signals = db.query(Signal).filter_by(company_id=c.id).all()
            print(f"Name: {c.name:<25} | Status: {c.status:<12} | Composite Score: {c.composite_score:.4f} | Window: {c.buying_window:<5} | Signals: {len(signals)}")
            for s in signals:
                print(f"    Signal: {s.title} (decayed strength: {s.decayed_strength})")

if __name__ == "__main__":
    main()
