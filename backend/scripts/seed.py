#!/usr/bin/env python3
"""
scripts/seed.py — Demo seed script for Avenor.

Creates:
  - 1 workspace with full ICP config
  - 1 admin user (email: demo@avenor.ai, password: demo1234)
  - 5 realistic companies with signals
  - 25 mock outcomes (enables model training)
  - Runs scoring and feed generation

After running:
  - Login at POST /api/v1/auth/login
  - View feed at GET /api/v1/feed
  - Check model at GET /api/v1/outcomes/model-accuracy

Usage:
    python scripts/seed.py
    python scripts/seed.py --reset    # drops and recreates all data
"""
import sys
import os
import argparse
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.db.session import init_db, db_session
from app.models import (
    Workspace, WorkspaceUser, WorkspaceUserRole,
    ICPConfig, Company, Contact, Signal, Outcome, SignalWeights,
    SignalType, SignalSource, CompanyStatus, OutcomeType, OutcomeSource,
)
from app.core.signal_config import DEFAULT_SIGNAL_WEIGHTS
from app.api.auth import hash_password

DEMO_EMAIL = "demo@avenor.ai"
DEMO_PASSWORD = "demo1234"

# ── Sample data ────────────────────────────────────────────────

SAMPLE_COMPANIES = [
    {
        "name": "Veridian Labs",
        "domain": "veridian.io",
        "industry": "SaaS",
        "employee_count": 145,
        "location_city": "San Francisco",
        "location_state": "CA",
        "location_country": "United States",
        "description": "AI-powered analytics platform for modern data teams.",
        "technologies": ["Snowflake", "Airflow", "dbt", "AWS"],
        "funding_total_usd": 12_000_000,
        "last_funding_stage": "Series A",
        "signals": [
            {"type": SignalType.FUNDING, "title": "Series A — $12M", "age_days": 21, "strength": 0.35,
             "description": "Veridian Labs announced a $12M Series A led by Sequoia."},
            {"type": SignalType.HIRING, "title": "Hiring Head of Data Engineering", "age_days": 3, "strength": 0.28,
             "description": "Posted VP/Head of Data Engineering role — scaling their data team."},
            {"type": SignalType.TECH_CHANGE, "title": "Migrated to Snowflake", "age_days": 45, "strength": 0.15,
             "description": "Job postings confirm Snowflake adoption across the data stack."},
        ],
        "contact": {
            "first_name": "Priya", "last_name": "Nair", "full_name": "Priya Nair",
            "title": "VP of Engineering", "seniority": "vp",
            "email": "priya.nair@veridian.io", "email_status": "verified",
            "linkedin_url": "https://linkedin.com/in/priya-nair", "is_primary": True,
        },
    },
    {
        "name": "Meridian Health Tech",
        "domain": "meridianhealth.io",
        "industry": "FinTech",
        "employee_count": 280,
        "location_city": "New York",
        "location_state": "NY",
        "location_country": "United States",
        "description": "Healthcare payments infrastructure for mid-market providers.",
        "technologies": ["Databricks", "dbt", "Segment", "GCP"],
        "funding_total_usd": 45_000_000,
        "last_funding_stage": "Series B",
        "signals": [
            {"type": SignalType.HIRING, "title": "3 Senior Data Engineer openings", "age_days": 7, "strength": 0.25,
             "description": "Active hiring of data engineers for a platform rebuild initiative."},
            {"type": SignalType.LEADERSHIP_CHANGE, "title": "New CTO hired", "age_days": 14, "strength": 0.22,
             "description": "Hired new CTO from Stripe — signaling infrastructure investment."},
            {"type": SignalType.TECH_CHANGE, "title": "Evaluating Databricks", "age_days": 10, "strength": 0.18,
             "description": "Job descriptions mention Databricks evaluation for ML platform."},
        ],
        "contact": {
            "first_name": "James", "last_name": "Chen", "full_name": "James Chen",
            "title": "Head of Data", "seniority": "director",
            "email": "james.chen@meridianhealth.io", "email_status": "verified",
            "linkedin_url": "https://linkedin.com/in/james-chen", "is_primary": True,
        },
    },
    {
        "name": "Apex Revenue Co",
        "domain": "apexrevenue.com",
        "industry": "SaaS",
        "employee_count": 95,
        "location_city": "Austin",
        "location_state": "TX",
        "location_country": "United States",
        "description": "Revenue operations platform for B2B sales teams.",
        "technologies": ["Salesforce", "Fivetran", "Looker"],
        "funding_total_usd": 8_500_000,
        "last_funding_stage": "Series A",
        "signals": [
            {"type": SignalType.FUNDING, "title": "Series A — $8.5M", "age_days": 60, "strength": 0.35,
             "description": "Raised $8.5M to scale go-to-market capabilities."},
            {"type": SignalType.EXPANSION, "title": "Opening London office", "age_days": 20, "strength": 0.12,
             "description": "Job postings confirm UK expansion — hiring 10+ in London."},
        ],
        "contact": {
            "first_name": "Sarah", "last_name": "Kim", "full_name": "Sarah Kim",
            "title": "Co-Founder & CTO", "seniority": "c_suite",
            "email": "sarah@apexrevenue.com", "email_status": "likely to engage",
            "linkedin_url": "https://linkedin.com/in/sarah-kim", "is_primary": True,
        },
    },
    {
        "name": "NovaBuild Systems",
        "domain": "novabuild.io",
        "industry": "SaaS",
        "employee_count": 420,
        "location_city": "Chicago",
        "location_state": "IL",
        "location_country": "United States",
        "description": "Enterprise construction management software.",
        "technologies": ["AWS", "PostgreSQL", "React"],
        "funding_total_usd": 32_000_000,
        "last_funding_stage": "Series C",
        "signals": [
            {"type": SignalType.HIRING, "title": "Hiring VP Sales + 5 AEs", "age_days": 5, "strength": 0.25,
             "description": "Major sales expansion — building out enterprise team."},
        ],
        "contact": {
            "first_name": "Marcus", "last_name": "Webb", "full_name": "Marcus Webb",
            "title": "VP Engineering", "seniority": "vp",
            "email": "marcus.webb@novabuild.io", "email_status": "verified",
            "is_primary": True,
        },
    },
    {
        "name": "TinyMart Inc",
        "domain": "tinymart.com",
        "industry": "Retail",  # Not in ICP — should score low
        "employee_count": 15,
        "location_city": "Denver",
        "location_state": "CO",
        "location_country": "United States",
        "description": "Online marketplace for handmade goods.",
        "technologies": ["Shopify"],
        "funding_total_usd": None,
        "last_funding_stage": None,
        "signals": [],
        "contact": {
            "first_name": "Dave", "last_name": "Smith", "full_name": "Dave Smith",
            "title": "Founder", "seniority": "c_suite",
            "email": "dave@tinymart.com", "email_status": "likely to engage",
            "is_primary": True,
        },
    },
]


def seed(reset: bool = False):
    print("\n" + "═" * 60)
    print("  Avenor — Demo Seed Script")
    print("═" * 60)

    init_db()
    print("✓ Database initialized")

    with db_session() as db:
        if reset:
            # Clear existing demo data
            db.query(Workspace).filter_by(slug="avenor-demo").delete()
            db.commit()
            print("✓ Previous demo data cleared")

        # Check if already seeded
        existing = db.query(Workspace).filter_by(slug="avenor-demo").first()
        if existing:
            print(f"\n⚠  Demo workspace already exists.")
            print(f"   Run with --reset to clear and re-seed.")
            print(f"   Login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
            print(f"   Workspace ID: {existing.id}")
            return

        # ── Create workspace ──────────────────────────────────
        workspace = Workspace(
            name="Avenor Demo",
            slug="avenor-demo",
            is_active=True,
        )
        db.add(workspace)
        db.flush()
        print(f"\n✓ Workspace created: {workspace.name} ({workspace.id})")

        # ── Create admin user ─────────────────────────────────
        user = WorkspaceUser(
            workspace_id=workspace.id,
            email=DEMO_EMAIL,
            full_name="Demo User",
            hashed_password=hash_password(DEMO_PASSWORD),
            role=WorkspaceUserRole.ADMIN,
        )
        db.add(user)
        db.flush()
        print(f"✓ Admin user: {DEMO_EMAIL} / {DEMO_PASSWORD}")

        # ── Create ICP config ─────────────────────────────────
        icp = ICPConfig(
            workspace_id=workspace.id,
            industries=["SaaS", "FinTech", "B2B Software"],
            min_employees=50,
            max_employees=500,
            locations=["United States", "United Kingdom", "Canada"],
            technologies=["Snowflake", "Databricks", "dbt", "Fivetran"],
            funding_stages=["Series A", "Series B", "Series C"],
            competitor_names=["Fivetran", "Airbyte", "Matillion"],
            product_name="DataFlow",
            product_description=(
                "A managed data pipeline platform that helps engineering teams "
                "scale their data infrastructure without breaking. We handle "
                "reliability, monitoring, and transformation so your team can "
                "focus on building products, not plumbing."
            ),
            key_pain_points=[
                "data pipelines breaking at scale",
                "engineering time wasted on data infra",
                "slow analytics due to unreliable pipelines",
                "no visibility into pipeline health",
            ],
            customer_personas=[
                "VP of Engineering", "Head of Data", "Director of Data Engineering",
                "CTO", "Data Engineering Manager",
            ],
            active_score_threshold=0.55,
            watch_score_threshold=0.25,
        )
        db.add(icp)

        # ── Create signal weights ─────────────────────────────
        sw = SignalWeights(
            workspace_id=workspace.id,
            weights={k: v for k, v in DEFAULT_SIGNAL_WEIGHTS.items()},
        )
        db.add(sw)
        db.flush()
        print("✓ ICP configuration and signal weights created")

        # ── Create companies, contacts, signals ────────────────
        created_companies = []
        now = datetime.now(timezone.utc)

        for cd in SAMPLE_COMPANIES:
            company = Company(
                workspace_id=workspace.id,
                name=cd["name"],
                domain=cd["domain"],
                industry=cd["industry"],
                employee_count=cd["employee_count"],
                location_city=cd["location_city"],
                location_state=cd["location_state"],
                location_country=cd["location_country"],
                description=cd["description"],
                technologies=cd["technologies"],
                funding_total_usd=cd["funding_total_usd"],
                last_funding_stage=cd["last_funding_stage"],
                status=CompanyStatus.MONITORING,
            )
            db.add(company)
            db.flush()

            # Contact
            contact = Contact(
                company_id=company.id,
                **cd["contact"],
            )
            db.add(contact)

            # Signals
            for sd in cd["signals"]:
                signal = Signal(
                    workspace_id=workspace.id,
                    company_id=company.id,
                    signal_type=sd["type"],
                    signal_source=SignalSource.MANUAL,
                    title=sd["title"],
                    description=sd.get("description"),
                    base_strength=sd["strength"],
                    decayed_strength=sd["strength"],
                    detected_at=now - timedelta(days=sd["age_days"]),
                )
                db.add(signal)

            created_companies.append(company)
            sig_count = len(cd["signals"])
            print(f"  + {cd['name']} ({cd['industry']}, {cd['employee_count']} emp, {sig_count} signals)")

        db.commit()
        print(f"\n✓ {len(created_companies)} companies created with contacts and signals")

        # ── Run scoring ────────────────────────────────────────
        print("\n⏳ Running scoring engine...")
        from app.modules.scoring.engine import run_scoring_for_workspace
        score_stats = run_scoring_for_workspace(db, str(workspace.id))
        print(f"✓ Scoring complete: {score_stats}")

        # ── Create historical outcomes for model training ─────
        print("\n⏳ Creating 30 historical outcomes for model training...")
        import uuid as uuid_lib
        for i in range(30):
            # Create a historical company (already closed)
            hist_company = Company(
                workspace_id=workspace.id,
                name=f"Historical Co {i:02d}",
                domain=f"historical{i:02d}.com",
                industry="SaaS",
                employee_count=100 + (i * 10),
                location_country="United States",
                status=CompanyStatus.CONVERTED if i % 3 == 0 else CompanyStatus.MONITORING,
                composite_score=0.40 + (i * 0.015),
                buying_window="hot" if i % 3 == 0 else "warm",
            )
            db.add(hist_company)
            db.flush()

            # Signals at time of prediction
            hist_signal = Signal(
                workspace_id=workspace.id,
                company_id=hist_company.id,
                signal_type=SignalType.HIRING if i % 2 == 0 else SignalType.FUNDING,
                signal_source=SignalSource.MANUAL,
                title="Historical signal",
                base_strength=0.25,
                decayed_strength=0.20,
                detected_at=now - timedelta(days=30 + i),
            )
            db.add(hist_signal)
            db.flush()

            # Outcome
            if i % 3 == 0:
                otype = OutcomeType.CLOSED_WON
            elif i % 4 == 0:
                otype = OutcomeType.MEETING_BOOKED
            elif i % 5 == 0:
                otype = OutcomeType.REPLIED_POSITIVE
            else:
                otype = OutcomeType.NO_RESPONSE

            outcome = Outcome(
                workspace_id=workspace.id,
                company_id=hist_company.id,
                outcome_type=otype,
                outcome_source=OutcomeSource.MANUAL,
                predicted_composite_score=hist_company.composite_score,
                predicted_buying_window=hist_company.buying_window,
                active_signals_snapshot=[
                    {"type": hist_signal.signal_type, "strength": 0.20}
                ],
                days_from_first_signal=15 + i,
                days_ahead_of_organic_discovery=7 if i % 3 == 0 else None,
                deal_value_usd=45000 if otype == OutcomeType.CLOSED_WON else None,
                occurred_at=now - timedelta(days=i),
            )
            db.add(outcome)

        db.commit()
        print("✓ 30 historical outcomes created")

        # ── Run model training ─────────────────────────────────
        print("\n⏳ Running model recalibration...")
        from app.modules.scoring.trainer import recalibrate_weights
        train_result = recalibrate_weights(db, str(workspace.id))
        if train_result.get("skipped"):
            print(f"  ⚠  Training skipped: {train_result.get('reason')}")
        else:
            print(f"✓ Model trained on {train_result['outcomes_used']} outcomes")
            if train_result.get("model_accuracy"):
                print(f"  Model accuracy: {train_result['model_accuracy']:.1%}")

        # ── Generate intelligence feed ─────────────────────────
        print("\n⏳ Generating intelligence feed (no LLM — using fallback summaries)...")
        from app.modules.intelligence.engine import run_feed_generation_for_workspace
        feed_stats = run_feed_generation_for_workspace(db, str(workspace.id))
        print(f"✓ Feed generated: {feed_stats}")

        # ── Summary ────────────────────────────────────────────
        from app.models import IntelligenceFeedItem
        feed_items = db.query(IntelligenceFeedItem).filter_by(workspace_id=workspace.id).all()

        print("\n" + "═" * 60)
        print("  SEED COMPLETE")
        print("═" * 60)
        print(f"\n  Login:        POST /api/v1/auth/login")
        print(f"  Email:        {DEMO_EMAIL}")
        print(f"  Password:     {DEMO_PASSWORD}")
        print(f"  Workspace ID: {workspace.id}")
        print(f"\n  Feed items generated: {len(feed_items)}")
        print(f"\n  Quick test commands:")
        print(f"""
  # 1. Login
  curl -s -X POST http://localhost:8000/api/v1/auth/login \\
    -H 'Content-Type: application/json' \\
    -d '{{"email":"{DEMO_EMAIL}","password":"{DEMO_PASSWORD}"}}' | python3 -m json.tool

  # 2. Get feed (use token from step 1)
  curl -s http://localhost:8000/api/v1/feed \\
    -H 'Authorization: Bearer <YOUR_TOKEN>' | python3 -m json.tool

  # 3. Company stats
  curl -s http://localhost:8000/api/v1/companies/stats \\
    -H 'Authorization: Bearer <YOUR_TOKEN>' | python3 -m json.tool

  # 4. Model accuracy
  curl -s http://localhost:8000/api/v1/outcomes/model-accuracy \\
    -H 'Authorization: Bearer <YOUR_TOKEN>' | python3 -m json.tool
        """)
        print("  Docs: http://localhost:8000/docs")
        print("═" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Avenor demo data")
    parser.add_argument("--reset", action="store_true", help="Clear existing demo data first")
    args = parser.parse_args()
    seed(reset=args.reset)
