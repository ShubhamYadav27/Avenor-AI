"""
scripts/test_pipeline.py

Runs the full pipeline with MOCK DATA (no Apollo API key needed).
Use this to verify everything works locally before connecting real APIs.

Usage:
    python scripts/test_pipeline.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import datetime, timezone, timedelta

# Load env
from dotenv import load_dotenv
load_dotenv()

from app.db.session import init_db, SessionLocal
from app.models import (
    Company, Contact, Signal,
    SignalType, LeadStatus,
)
from app.services.scoring_engine import score_company, score_all_unscored
from app.services.message_generator import generate_and_store_message, build_context
from app.services.outreach_sender import send_batch
from app.services.reply_classifier import classify_reply


def seed_mock_data(db):
    """Insert realistic mock companies + contacts + signals."""
    print("\n── Seeding mock data ──")

    companies_data = [
        {
            "name": "Veridian Labs",
            "domain": "veridian.io",
            "industry": "FinTech",
            "employee_count": 145,
            "location": "San Francisco, CA, United States",
            "funding_total": 12_000_000,
            "last_funding_round": "Series A",
            "technologies": [{"name": "Snowflake"}, {"name": "Airflow"}, {"name": "AWS"}],
            "signals": [
                {"type": SignalType.FUNDING, "value": "Series A", "age_days": 21, "strength": 0.35},
                {"type": SignalType.HIRING, "value": "Head of Data Engineering", "age_days": 3, "strength": 0.25},
            ],
        },
        {
            "name": "Meridian Health",
            "domain": "meridianhealth.com",
            "industry": "B2B Software",
            "employee_count": 280,
            "location": "New York, NY, United States",
            "funding_total": 45_000_000,
            "last_funding_round": "Series B",
            "technologies": [{"name": "Databricks"}, {"name": "dbt"}],
            "signals": [
                {"type": SignalType.HIRING, "value": "Senior Data Engineer x3", "age_days": 7, "strength": 0.25},
                {"type": SignalType.TECH_CHANGE, "value": "Databricks, dbt", "age_days": 14, "strength": 0.20},
            ],
        },
        {
            "name": "TinyMart",
            "domain": "tinymart.com",
            "industry": "Retail",  # Not in ICP
            "employee_count": 12,  # Too small
            "location": "Austin, TX, United States",
            "funding_total": 0,
            "last_funding_round": None,
            "technologies": [],
            "signals": [],
        },
    ]

    contacts_data = {
        "Veridian Labs": {
            "first_name": "Priya",
            "last_name": "Nair",
            "full_name": "Priya Nair",
            "title": "VP of Engineering",
            "seniority": "vp",
            "email": "priya.nair@veridian.io",
            "email_verified": True,
        },
        "Meridian Health": {
            "first_name": "James",
            "last_name": "Chen",
            "full_name": "James Chen",
            "title": "Head of Data",
            "seniority": "director",
            "email": "james.chen@meridianhealth.com",
            "email_verified": True,
        },
        "TinyMart": {
            "first_name": "Dave",
            "last_name": "Smith",
            "full_name": "Dave Smith",
            "title": "Owner",
            "seniority": "c_suite",
            "email": "dave@tinymart.com",
            "email_verified": False,
        },
    }

    created_companies = []
    for cd in companies_data:
        company = Company(
            name=cd["name"],
            domain=cd["domain"],
            industry=cd["industry"],
            employee_count=cd["employee_count"],
            location=cd["location"],
            funding_total=cd["funding_total"],
            last_funding_round=cd["last_funding_round"],
            technologies=cd["technologies"],
            status=LeadStatus.ENRICHED,
        )
        db.add(company)
        db.flush()

        # Add contact
        ct = contacts_data[cd["name"]]
        contact = Contact(
            company_id=company.id,
            is_primary=True,
            **ct,
        )
        db.add(contact)

        # Add signals
        for sig_data in cd["signals"]:
            signal = Signal(
                company_id=company.id,
                signal_type=sig_data["type"],
                signal_source="mock",
                raw_value=sig_data["value"],
                strength=sig_data["strength"],
                decayed_score=sig_data["strength"],
                detected_at=datetime.now(timezone.utc) - timedelta(days=sig_data["age_days"]),
            )
            db.add(signal)

        created_companies.append(company)
        print(f"  ✓ Created {company.name} ({company.industry}, {company.employee_count} emp)")

    db.commit()
    return created_companies


def test_scoring(db, companies):
    print("\n── Testing scoring engine ──")
    for company in companies:
        result = score_company(db, company)
        print(
            f"  {company.name:20} → score={result['composite_score']:.3f}  "
            f"ICP×{result['icp_multiplier']:.1f}  "
            f"status={result['status']:15}  {result['priority']}"
        )


def test_generation(db):
    print("\n── Testing message generation ──")
    from openai import OpenAI
    from app.config import settings

    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-..."):
        print("  ⚠ No OpenAI key set — skipping live generation")
        print("  Set OPENAI_API_KEY in .env to test message generation")
        return []

    queued = db.query(Company).filter_by(status=LeadStatus.QUEUED).all()
    messages = []

    for company in queued[:2]:  # test with first 2 to save API calls
        contact = db.query(Contact).filter_by(company_id=company.id, is_primary=True).first()
        if not contact:
            continue

        print(f"  Generating for {company.name} ({contact.title})...")
        msg = generate_and_store_message(
            db=db,
            company=company,
            contact=contact,
            sender_name="Alex",
            sender_company="DataFlow",
            product_description="a data pipeline platform that helps engineering teams scale their data infrastructure without breaking",
        )
        messages.append(msg)
        gate = "✓ PASSED" if msg.passed_quality_gate else f"✗ FAILED: {msg.quality_gate_notes}"
        print(f"  Subject: {msg.subject}")
        print(f"  Body ({msg.word_count} words): {msg.body[:120]}...")
        print(f"  Quality gate: {gate}\n")

    return messages


def test_send(db, messages):
    print("\n── Testing send (mock) ──")
    approved = [m for m in messages if m.passed_quality_gate]
    if not approved:
        print("  No approved messages to send")
        return

    results = send_batch(db, approved, dry_run=True)
    for r in results:
        print(f"  {r}")


def test_reply_classifier():
    print("\n── Testing reply classifier ──")
    from app.config import settings

    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-..."):
        print("  ⚠ No OpenAI key — skipping")
        return

    test_replies = [
        "Yes, this is actually perfect timing for us. Let's find 15 minutes.",
        "Please remove me from your mailing list.",
        "Interesting — can you send over a case study?",
        "We already have a vendor for this, but thanks.",
        "I'm on vacation until Jan 20th. Contact my colleague at ops@company.com for urgent matters.",
    ]

    for reply in test_replies:
        reply_type, conf, reasoning = classify_reply(reply)
        print(f"  [{reply_type.value:15}] ({conf:.0%} conf) '{reply[:60]}...' ")


def main():
    print("=" * 60)
    print("NEXUS — End-to-End Pipeline Test")
    print("=" * 60)

    # Initialize DB
    init_db()
    db = SessionLocal()

    try:
        companies = seed_mock_data(db)
        test_scoring(db, companies)
        messages = test_generation(db)
        test_send(db, messages)
        test_reply_classifier()

        print("\n" + "=" * 60)
        print("✓ All tests complete")
        print("Check mock_sent_emails.jsonl for mock sends")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()
