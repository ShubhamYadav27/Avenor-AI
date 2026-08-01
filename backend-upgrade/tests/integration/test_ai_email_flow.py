"""Integration tests for Phase 5.2 AI Email Generator."""
import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

from app.core.exceptions import NotFoundError, ValidationError
from app.models import (
    AIEmailStatus,
    Company,
    CompanyAIEmail,
    CompanyAIResearch,
    Contact,
    ResearchStatus,
    Workspace,
)
from app.modules.ai.email_service import (
    archive_email,
    copy_email,
    generate_email_rows,
    list_company_emails,
    request_email_generation,
    request_regeneration,
)
from app.modules.ai.schemas import EmailGenerateRequest
from tests.unit.test_ai_research import FakeProvider

TEST_DB_URL = os.environ.get("TEST_DATABASE_URL", "")

requires_postgres = pytest.mark.skipif(
    not TEST_DB_URL.startswith("postgresql"),
    reason="Integration tests require Postgres. Set TEST_DATABASE_URL=postgresql://... to enable.",
)


def email_payload(variation: str = "A") -> dict[str, str]:
    return {
        "subject": f"Variation {variation}: timing after new buying signals",
        "body": "Hi Priya,\n\nAvenor flagged a few timing signals worth acting on.",
        "cta": "Worth a 15-minute conversation next week?",
        "reasoning": "Grounded in completed research and selected persona.",
        "variation": variation,
    }


@pytest.fixture(scope="module")
def db_engine():
    if not TEST_DB_URL.startswith("postgresql"):
        pytest.skip("TEST_DATABASE_URL not set to a Postgres URL")
    return create_engine(TEST_DB_URL)


@pytest.fixture
def db(db_engine):
    session = sessionmaker(bind=db_engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def workspace(db):
    ws = Workspace(name="Email Test WS", slug=f"email-{uuid.uuid4().hex[:8]}")
    db.add(ws)
    db.commit()
    yield ws
    db.query(CompanyAIEmail).filter_by(workspace_id=ws.id).delete()
    db.query(CompanyAIResearch).filter_by(workspace_id=ws.id).delete()
    db.query(Contact).filter(Contact.company_id.in_(db.query(Company.id).filter_by(workspace_id=ws.id))).delete(
        synchronize_session=False
    )
    db.query(Company).filter_by(workspace_id=ws.id).delete()
    db.query(Workspace).filter_by(id=ws.id).delete()
    db.commit()


@pytest.fixture
def company(db, workspace):
    comp = Company(
        workspace_id=workspace.id,
        name="Veridian Labs",
        domain=f"veridian-{uuid.uuid4().hex[:6]}.io",
        industry="Data Infrastructure",
        employee_count=220,
        composite_score=0.81,
        buying_window="hot",
    )
    db.add(comp)
    db.commit()
    return comp


@pytest.fixture
def contact(db, company):
    row = Contact(
        company_id=company.id,
        full_name="Priya Nair",
        title="VP Revenue Operations",
        email="priya@example.com",
        is_primary=True,
    )
    db.add(row)
    db.commit()
    return row


@pytest.fixture
def research(db, workspace, company):
    row = CompanyAIResearch(
        workspace_id=workspace.id,
        company_id=company.id,
        status=ResearchStatus.COMPLETED.value,
        summary="Veridian is scaling revenue operations after several buying signals.",
        buying_signals=[
            {
                "title": "GTM scaling",
                "evidence": "Hiring signal",
                "why_it_matters": "More pipeline requires better prioritization.",
                "strength": "strong",
            }
        ],
        pain_points=[],
        recommended_personas=[],
        outreach_strategy={
            "recommended_channel": "email",
            "timing": "This week",
            "angle": "Prioritize accounts already showing buying windows.",
            "opening_hook": "Saw Veridian is scaling GTM.",
        },
        talking_points=[],
        risks=[],
        next_actions=[],
        model_provider="fake",
        model_version="fake-model-1",
        prompt_version="research.v1",
        input_hash="a" * 64,
    )
    db.add(row)
    db.commit()
    return row


@requires_postgres
class TestEmailService:
    def test_generation_request_creates_three_pending_variations(self, db, workspace, company, contact, research):
        result, should_dispatch = request_email_generation(
            db,
            str(company.id),
            workspace.id,
            EmailGenerateRequest(contact_id=str(contact.id)),
            provider=FakeProvider(),
        )

        assert should_dispatch is True
        assert result.status == "pending"
        assert [email.variation for email in result.emails] == ["A", "B", "C"]
        assert {email.status for email in result.emails} == {AIEmailStatus.PENDING.value}
        assert {email.research_id for email in result.emails} == {str(research.id)}

    def test_generation_requires_completed_research(self, db, workspace, company):
        with pytest.raises(ValidationError):
            request_email_generation(
                db,
                str(company.id),
                workspace.id,
                EmailGenerateRequest(),
                provider=FakeProvider(),
            )

    def test_worker_populates_email_rows(self, db, workspace, company, research):
        result, _ = request_email_generation(
            db,
            str(company.id),
            workspace.id,
            EmailGenerateRequest(),
            provider=FakeProvider(),
        )

        provider = FakeProvider(response=email_payload("A"))
        stats = generate_email_rows(db, [result.emails[0].id], workspace.id, provider=provider)

        assert stats["generated"] == 1
        row = db.get(CompanyAIEmail, uuid.UUID(result.emails[0].id))
        assert row.status == AIEmailStatus.COMPLETED.value
        assert row.subject.startswith("Variation")
        assert row.model_provider == "fake"
        assert row.prompt_version == "email.v1"

    def test_cache_hit_returns_completed_variations_without_dispatch(self, db, workspace, company, research):
        request = EmailGenerateRequest()
        result, _ = request_email_generation(db, str(company.id), workspace.id, request, provider=FakeProvider())
        for email in result.emails:
            generate_email_rows(db, [email.id], workspace.id, provider=FakeProvider(response=email_payload(email.variation)))

        cached, should_dispatch = request_email_generation(
            db,
            str(company.id),
            workspace.id,
            request,
            provider=FakeProvider(),
        )

        assert should_dispatch is False
        assert cached.cached is True
        assert cached.status == "completed"
        assert len(cached.emails) == 3

    def test_copy_regenerate_and_archive_are_workspace_scoped(self, db, workspace, company, research):
        result, _ = request_email_generation(
            db,
            str(company.id),
            workspace.id,
            EmailGenerateRequest(),
            provider=FakeProvider(),
        )
        email_id = result.emails[0].id

        copied = copy_email(db, email_id, workspace.id)
        assert copied.copy_count == 1

        regenerated, should_dispatch = request_regeneration(db, email_id, workspace.id, provider=FakeProvider())
        assert should_dispatch is True
        assert regenerated.version == 2
        assert regenerated.regeneration_count == 1

        archived = archive_email(db, email_id, workspace.id)
        assert archived.status == "archived"
        assert archived.archived_at is not None

        with pytest.raises(NotFoundError):
            copy_email(db, regenerated.id, uuid.uuid4())

    def test_list_excludes_archived_emails(self, db, workspace, company, research):
        result, _ = request_email_generation(
            db,
            str(company.id),
            workspace.id,
            EmailGenerateRequest(),
            provider=FakeProvider(),
        )
        archive_email(db, result.emails[0].id, workspace.id)

        listed = list_company_emails(db, str(company.id), workspace.id)

        assert all(email.status != "archived" for email in listed.emails)
        assert len(listed.emails) == 2


@requires_postgres
class TestEmailAPI:
    @pytest.fixture
    def client(self, db, workspace, monkeypatch):
        from fastapi.testclient import TestClient

        from app.api.auth import AuthenticatedUser, get_current_user
        from app.db.session import get_db
        from app.main import app
        from app.modules.ai.provider import get_provider

        dispatched: list[tuple[str, list[str]]] = []

        class _FakeTask:
            def delay(self, workspace_id: str, email_ids: list[str]):
                dispatched.append((workspace_id, email_ids))

        monkeypatch.setattr("app.workers.tasks.generate_company_ai_emails", _FakeTask(), raising=False)

        user = MagicMock()
        user.id = uuid.uuid4()
        user.is_active = True
        user.role = "admin"
        authed = AuthenticatedUser.__new__(AuthenticatedUser)
        authed.user = user
        authed.workspace = workspace
        authed.workspace_id = workspace.id
        authed.user_id = user.id
        authed.role = "admin"

        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_current_user] = lambda: authed
        app.dependency_overrides[get_provider] = lambda: FakeProvider()

        test_client = TestClient(app)
        test_client.dispatched = dispatched  # type: ignore[attr-defined]
        yield test_client
        app.dependency_overrides.clear()

    def test_get_returns_none_status_when_no_emails(self, client, company):
        res = client.get(f"/api/v1/companies/{company.id}/emails")

        assert res.status_code == 200
        assert res.json()["status"] == "none"

    def test_post_starts_email_generation_and_returns_202(self, client, company, research):
        res = client.post(f"/api/v1/companies/{company.id}/emails", json={"email_type": "cold_email"})

        assert res.status_code == 202
        body = res.json()
        assert body["status"] == "pending"
        assert len(body["emails"]) == 3
        assert len(client.dispatched) == 1

    def test_post_fallback_to_background_task_when_celery_unavailable(self, client, company, research, monkeypatch):
        class _FailingTask:
            def delay(self, *args, **kwargs):
                raise Exception("Celery unreachable")

        monkeypatch.setattr("app.workers.tasks.generate_company_ai_emails", _FailingTask(), raising=False)

        res = client.post(f"/api/v1/companies/{company.id}/emails", json={"email_type": "cold_email"})
        assert res.status_code == 202
        body = res.json()
        assert body["status"] == "pending"
        assert len(body["emails"]) == 3

    def test_endpoints_require_authentication(self, db, company):
        from fastapi.testclient import TestClient

        from app.db.session import get_db
        from app.main import app

        app.dependency_overrides.clear()
        app.dependency_overrides[get_db] = lambda: db
        anon = TestClient(app)
        try:
            assert anon.get(f"/api/v1/companies/{company.id}/emails").status_code == 401
            assert anon.post(f"/api/v1/companies/{company.id}/emails", json={}).status_code == 401
        finally:
            app.dependency_overrides.clear()
