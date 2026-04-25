"""
Pipeline orchestrator.
run_pipeline() is the single entry point that executes the full MVP flow:
fetch → score → generate → send → log
"""
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import Company, Contact, OutreachMessage, OutreachStatus, LeadStatus
from app.services.apollo_fetcher import fetch_and_store_leads
from app.services.scoring_engine import score_all_unscored, get_top_leads
from app.services.message_generator import generate_and_store_message
from app.services.outreach_sender import send_batch

logger = logging.getLogger(__name__)


def run_pipeline(
    db: Session,
    # Ingest config
    industries: list[str] = None,
    min_employees: int = None,
    max_employees: int = None,
    locations: list[str] = None,
    fetch_limit: int = 25,
    # Outreach config
    sender_name: str = "Alex",
    sender_company: str = "Nexus",
    product_description: str = "an AI-powered data pipeline tool that helps engineering teams scale without breaking",
    max_leads_to_contact: int = 10,
    dry_run: bool = False,
    skip_fetch: bool = False,
) -> dict:
    """
    Full MVP pipeline.

    Args:
        db: Database session
        dry_run: If True, generate messages but don't send
        skip_fetch: If True, skip Apollo fetch (use existing leads in DB)

    Returns:
        Pipeline run summary dict
    """
    run_start = datetime.now(timezone.utc)
    logger.info(f"{'[DRY RUN] ' if dry_run else ''}Pipeline starting at {run_start.isoformat()}")

    summary = {
        "run_at": run_start.isoformat(),
        "dry_run": dry_run,
        "steps": {},
    }

    # ─── STEP 1: Fetch Leads ─────────────────
    if not skip_fetch:
        logger.info("Step 1: Fetching leads from Apollo")
        try:
            ingest_result = fetch_and_store_leads(
                db=db,
                industries=industries,
                min_employees=min_employees,
                max_employees=max_employees,
                locations=locations,
                limit=fetch_limit,
            )
            summary["steps"]["fetch"] = ingest_result
            logger.info(f"Step 1 complete: {ingest_result}")
        except Exception as e:
            logger.error(f"Step 1 failed: {e}")
            summary["steps"]["fetch"] = {"error": str(e)}
    else:
        logger.info("Step 1: Skipped (skip_fetch=True)")
        summary["steps"]["fetch"] = {"skipped": True}

    # ─── STEP 2: Score Leads ─────────────────
    logger.info("Step 2: Scoring leads")
    try:
        scores = score_all_unscored(db)
        queued_count = sum(1 for s in scores if s["status"] == LeadStatus.QUEUED.value)
        summary["steps"]["score"] = {
            "total_scored": len(scores),
            "queued_for_outreach": queued_count,
            "top_5": scores[:5],
        }
        logger.info(f"Step 2 complete: {queued_count}/{len(scores)} leads queued for outreach")
    except Exception as e:
        logger.error(f"Step 2 failed: {e}")
        summary["steps"]["score"] = {"error": str(e)}

    # ─── STEP 3: Pick Top Leads ─────────────────
    logger.info(f"Step 3: Selecting top {max_leads_to_contact} leads")
    top_companies = get_top_leads(db, limit=max_leads_to_contact)
    summary["steps"]["selection"] = {"selected": len(top_companies)}
    logger.info(f"Step 3 complete: {len(top_companies)} leads selected")

    if not top_companies:
        logger.warning("No leads qualified for outreach — pipeline ending early")
        summary["steps"]["generate"] = {"skipped": "no qualified leads"}
        summary["steps"]["send"] = {"skipped": "no qualified leads"}
        return summary

    # ─── STEP 4: Generate Messages ─────────────────
    logger.info("Step 4: Generating personalized messages")
    generated_messages = []
    generation_errors = []

    for company in top_companies:
        # Get primary contact
        contact = (
            db.query(Contact)
            .filter_by(company_id=company.id, is_primary=True)
            .first()
        )

        if not contact:
            # Fall back to first available contact
            contact = db.query(Contact).filter_by(company_id=company.id).first()

        if not contact or not contact.email:
            logger.warning(f"No usable contact for {company.name} — skipping")
            generation_errors.append({"company": company.name, "error": "no contact"})
            continue

        try:
            message = generate_and_store_message(
                db=db,
                company=company,
                contact=contact,
                sender_name=sender_name,
                sender_company=sender_company,
                product_description=product_description,
                angle="pain_led",
                sequence_step=1,
            )
            generated_messages.append(message)
            logger.info(
                f"Generated for {company.name} → quality_gate={'✓' if message.passed_quality_gate else '✗'}"
            )
        except Exception as e:
            logger.error(f"Generation failed for {company.name}: {e}")
            generation_errors.append({"company": company.name, "error": str(e)})

    # Only send messages that passed the quality gate
    approved_messages = [m for m in generated_messages if m.passed_quality_gate]

    summary["steps"]["generate"] = {
        "total_attempted": len(top_companies),
        "generated": len(generated_messages),
        "quality_approved": len(approved_messages),
        "quality_rejected": len(generated_messages) - len(approved_messages),
        "errors": generation_errors,
    }

    logger.info(
        f"Step 4 complete: {len(approved_messages)}/{len(generated_messages)} messages approved"
    )

    # ─── STEP 5: Send ─────────────────
    logger.info(f"Step 5: {'[DRY RUN] ' if dry_run else ''}Sending {len(approved_messages)} messages")
    try:
        send_results = send_batch(
            db=db,
            messages=approved_messages,
            from_name=sender_name,
            dry_run=dry_run,
        )
        sent_count = sum(
            1 for r in send_results
            if r.get("status") in ("mock_sent", "success", "dry_run")
        )
        summary["steps"]["send"] = {
            "attempted": len(approved_messages),
            "sent": sent_count,
            "results": send_results,
        }
        logger.info(f"Step 5 complete: {sent_count} messages {'would be sent (dry run)' if dry_run else 'sent'}")
    except Exception as e:
        logger.error(f"Step 5 failed: {e}")
        summary["steps"]["send"] = {"error": str(e)}

    # ─── Final Summary ─────────────────
    run_end = datetime.now(timezone.utc)
    duration_s = (run_end - run_start).total_seconds()
    summary["duration_seconds"] = round(duration_s, 1)
    summary["completed_at"] = run_end.isoformat()

    logger.info(
        f"Pipeline complete in {duration_s:.1f}s — "
        f"leads fetched, scored, {len(approved_messages)} messages "
        f"{'staged (dry run)' if dry_run else 'sent'}"
    )

    return summary


def pipeline_status(db: Session) -> dict:
    """Quick status snapshot of the pipeline — no side effects."""
    from sqlalchemy import func

    counts = (
        db.query(Company.status, func.count(Company.id))
        .group_by(Company.status)
        .all()
    )

    messages_sent = (
        db.query(func.count(OutreachMessage.id))
        .filter(OutreachMessage.status == OutreachStatus.SENT)
        .scalar()
    )

    messages_pending = (
        db.query(func.count(OutreachMessage.id))
        .filter(OutreachMessage.status == OutreachStatus.DRAFT,
                OutreachMessage.passed_quality_gate == True)
        .scalar()
    )

    return {
        "lead_pipeline": {status.value: count for status, count in counts},
        "messages_sent": messages_sent,
        "messages_pending_send": messages_pending,
    }
