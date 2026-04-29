"""
All API endpoints.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Company, Contact, OutreachMessage, LeadStatus
from app.services.apollo_fetcher import fetch_and_store_leads
from app.services.scoring_engine import score_all_unscored, score_company, get_top_leads
from app.services.message_generator import generate_and_store_message
from app.services.outreach_sender import send_outreach_message, send_batch
from app.services.reply_classifier import handle_reply
from app.core.pipeline import run_pipeline, pipeline_status

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────

class IngestLeadsRequest(BaseModel):
    industries: Optional[list[str]] = None
    min_employees: Optional[int] = None
    max_employees: Optional[int] = None
    locations: Optional[list[str]] = None
    limit: int = 25


class ScoreLeadsRequest(BaseModel):
    company_id: Optional[str] = None  # score just one if provided


class GenerateMessageRequest(BaseModel):
    company_id: str
    contact_id: str
    sender_name: str = "Alex"
    sender_company: str = "Nexus"
    product_description: str = "an AI-powered data pipeline tool"
    angle: str = "pain_led"
    sequence_step: int = 1


class SendOutreachRequest(BaseModel):
    message_id: str
    from_name: str = "Alex"
    dry_run: bool = False


class SendBatchRequest(BaseModel):
    message_ids: Optional[list[str]] = None  # None = send all approved drafts
    from_name: str = "Alex"
    dry_run: bool = False
    limit: int = 10


class HandleReplyRequest(BaseModel):
    outreach_message_id: str
    reply_text: str


class RunPipelineRequest(BaseModel):
    industries: Optional[list[str]] = None
    min_employees: Optional[int] = None
    max_employees: Optional[int] = None
    locations: Optional[list[str]] = None
    fetch_limit: int = 25
    max_leads_to_contact: int = 10
    sender_name: str = "Alex"
    sender_company: str = "Nexus"
    product_description: str = "an AI-powered data pipeline tool"
    dry_run: bool = True       # safe default — require explicit dry_run=false to actually send
    skip_fetch: bool = False


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "nexus-outbound"}


@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    """Pipeline health snapshot — lead counts, messages sent, etc."""
    return pipeline_status(db)


@router.post("/ingest-leads")
def ingest_leads(req: IngestLeadsRequest, db: Session = Depends(get_db)):
    """
    Fetch leads from Apollo and store them.
    Uses ICP defaults from config if filters not provided.
    """
    try:
        result = fetch_and_store_leads(
            db=db,
            industries=req.industries,
            min_employees=req.min_employees,
            max_employees=req.max_employees,
            locations=req.locations,
            limit=req.limit,
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"/ingest-leads failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score-leads")
def score_leads(req: ScoreLeadsRequest, db: Session = Depends(get_db)):
    """
    Score leads. If company_id provided, scores just that one.
    Otherwise scores all unscored/enriched leads.
    """
    try:
        if req.company_id:
            company = db.query(Company).get(req.company_id)
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            result = score_company(db, company)
            return {"success": True, "result": result}
        else:
            results = score_all_unscored(db)
            return {
                "success": True,
                "total_scored": len(results),
                "queued_for_outreach": sum(1 for r in results if r["status"] == "queued"),
                "results": results,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/score-leads failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-message")
def generate_message(req: GenerateMessageRequest, db: Session = Depends(get_db)):
    """
    Generate a personalized message for a specific company + contact.
    Stores the draft and returns it with quality gate result.
    """
    company = db.query(Company).get(req.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    contact = db.query(Contact).get(req.contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    try:
        message = generate_and_store_message(
            db=db,
            company=company,
            contact=contact,
            sender_name=req.sender_name,
            sender_company=req.sender_company,
            product_description=req.product_description,
            angle=req.angle,
            sequence_step=req.sequence_step,
        )
        return {
            "success": True,
            "message_id": str(message.id),
            "subject": message.subject,
            "body": message.body,
            "word_count": message.word_count,
            "angle": message.angle,
            "tone_profile": message.tone_profile,
            "quality_gate_passed": message.passed_quality_gate,
            "quality_gate_notes": message.quality_gate_notes,
        }
    except Exception as e:
        logger.error(f"/generate-message failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-outreach")
def send_outreach(req: SendOutreachRequest, db: Session = Depends(get_db)):
    """Send a single approved message."""
    message = db.query(OutreachMessage).get(req.message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        result = send_outreach_message(db, message, from_name=req.from_name)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"/send-outreach failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-batch")
def send_outreach_batch(req: SendBatchRequest, db: Session = Depends(get_db)):
    """
    Send multiple approved messages.
    If message_ids not specified, sends all approved drafts (up to limit).
    """
    if req.message_ids:
        messages = [db.query(OutreachMessage).get(mid) for mid in req.message_ids]
        messages = [m for m in messages if m is not None]
    else:
        messages = (
            db.query(OutreachMessage)
            .filter(
                OutreachMessage.status == __import__(
                    'app.models', fromlist=['OutreachStatus']
                ).OutreachStatus.DRAFT,
                OutreachMessage.passed_quality_gate == True,
            )
            .limit(req.limit)
            .all()
        )

    if not messages:
        return {"success": True, "message": "No messages to send", "results": []}

    results = send_batch(db, messages, from_name=req.from_name, dry_run=req.dry_run)
    return {
        "success": True,
        "attempted": len(messages),
        "dry_run": req.dry_run,
        "results": results,
    }


@router.post("/handle-reply")
def handle_incoming_reply(req: HandleReplyRequest, db: Session = Depends(get_db)):
    """
    Process an incoming reply. Classifies intent and notifies if hot.
    Webhook endpoint — hook this up to Instantly or your email provider.
    """
    try:
        reply = handle_reply(
            db=db,
            outreach_message_id=req.outreach_message_id,
            reply_text=req.reply_text,
        )
        return {
            "success": True,
            "reply_id": str(reply.id),
            "classification": reply.reply_type.value,
            "confidence": reply.classification_confidence,
            "reasoning": reply.classification_reasoning,
            "requires_human_action": reply.requires_human_action,
            "slack_notified": reply.slack_notified,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"/handle-reply failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-pipeline")
def trigger_pipeline(req: RunPipelineRequest, db: Session = Depends(get_db)):
    """
    Trigger the full pipeline: fetch → score → generate → send.
    dry_run=True (default) — stages everything but doesn't send.
    Set dry_run=False when you're ready to go live.
    """
    try:
        summary = run_pipeline(
            db=db,
            industries=req.industries,
            min_employees=req.min_employees,
            max_employees=req.max_employees,
            locations=req.locations,
            fetch_limit=req.fetch_limit,
            sender_name=req.sender_name,
            sender_company=req.sender_company,
            product_description=req.product_description,
            max_leads_to_contact=req.max_leads_to_contact,
            dry_run=req.dry_run,
            skip_fetch=req.skip_fetch,
        )
        return {"success": True, "summary": summary}
    except Exception as e:
        logger.error(f"/run-pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads")
def list_leads(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List leads, optionally filtered by status."""
    query = db.query(Company)
    if status:
        try:
            status_enum = LeadStatus(status)
            query = query.filter(Company.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    companies = query.order_by(Company.composite_score.desc()).limit(limit).all()

    return {
        "leads": [
            {
                "id": str(c.id),
                "name": c.name,
                "domain": c.domain,
                "industry": c.industry,
                "employees": c.employee_count,
                "location": c.location,
                "composite_score": c.composite_score,
                "status": c.status.value,
                "signal_count": len(c.signals),
            }
            for c in companies
        ]
    }


@router.get("/messages")
def list_messages(
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List outreach messages with their status."""
    from app.models import OutreachStatus
    query = db.query(OutreachMessage)
    if status:
        try:
            status_enum = OutreachStatus(status)
            query = query.filter(OutreachMessage.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    messages = query.order_by(OutreachMessage.created_at.desc()).limit(limit).all()

    return {
        "messages": [
            {
                "id": str(m.id),
                "company_id": str(m.company_id),
                "subject": m.subject,
                "body": m.body[:100] + "..." if m.body and len(m.body) > 100 else m.body,
                "word_count": m.word_count,
                "angle": m.angle,
                "status": m.status.value,
                "quality_gate_passed": m.passed_quality_gate,
                "sent_at": m.sent_at.isoformat() if m.sent_at else None,
            }
            for m in messages
        ]
    }
