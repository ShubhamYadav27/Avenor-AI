"""
End-to-end integration test for Phase 5.1 AI Account Research.

Exercises the real service against real Postgres with a fake LLM provider:
cache hits, forced refresh, regeneration when intelligence changes, workspace
isolation, and graceful handling of every AI failure mode.

Requires a running Postgres instance (JSONB, pgvector, UUID types).
Run with: pytest tests/integration/test_ai_research_flow.py -v
Set TEST_DATABASE_URL environment variable to enable.
"""
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import NotFoundError, RateLimitError
from app.models import (
    Company,
    CompanyAIResearch,
    ResearchStatus,
    Signal,
    Workspace,
)
from app.modules.ai.provider import InvalidAIResponseError, ProviderUnavailableError
from app.modules.ai.research_service import (
    generate_research,
    get_latest_research,
    request_research,
)

from tests.unit.test_ai_research import FakeProvider, valid_payload

TEST_DB_URL = os.environ.get("TEST_DATABASE_URL", "")

requires_postgres = pytest.mark.skipif(
    not TEST_DB_URL.startswith("postgresql"),
    reason="Integration tests require Postgres. Set TEST_DATABASE_URL=postgresql://... to enable.",
)


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
    ws = Workspace(name="Research Test WS", slug=f"research-{uuid.uuid4().hex[:8]}")
    db.add(ws)
    db.commit()
    yield ws
    db.query(CompanyAIResearch).filter_by(workspace_id=ws.id).delete()
    db.query(Signal).filter_by(workspace_id=ws.id).delete()
    db.query(Company).filter_by(workspace_id=ws.id).delete()
    db.query(Workspace).filter_by(id=ws.id).delete()
    db.commit()


@pytest.fixture
def company(db, workspace):
    comp = Company(
        workspace_id=workspace.id,
        name="Acme Robotics",
        domain=f"acme-{uuid.uuid4().hex[:6]}.com",
        industry="Robotics",
        employee_count=180,
        composite_score=0.82,
        buying_window="hot",
    )
    db.add(comp)
    db.commit()
    return comp


@requires_postgres
class TestResearchGeneration:
    def test_generates_and_persists_report(self, db, workspace, company):
        provider = FakeProvider()
        stats = generate_research(db, str(company.id), workspace.id, provider=provider)

        assert stats["generated"] == 1
        assert stats["status"] == "completed"
        assert provider.call_count == 1

        row = db.query(CompanyAIResearch).filter_by(company_id=company.id).one()
        assert row.status == ResearchStatus.COMPLETED.value
        assert row.summary.startswith("Acme builds warehouse robotics")
        assert row.model_provider == "fake"
        assert row.model_version == "fake-model-1"
        assert row.prompt_version == "research.v1"
        assert len(row.input_hash) == 64
        assert row.generation_duration_ms >= 0
        assert row.outreach_strategy["recommended_channel"] == "email"
        assert row.buying_signals[0]["strength"] == "strong"
        assert row.error_message is None

    def test_response_exposes_all_eight_sections(self, db, workspace, company):
        generate_research(db, str(company.id), workspace.id, provider=FakeProvider())
        response = get_latest_research(db, str(company.id), workspace.id)

        assert response.status == "completed"
        assert response.summary
        assert response.buying_signals
        assert response.pain_points
        assert response.recommended_personas
        assert response.outreach_strategy is not None
        assert response.talking_points
        assert response.risks
        assert response.next_actions
        assert response.meta.prompt_version == "research.v1"


@requires_postgres
class TestCacheStrategy:
    def test_second_request_hits_cache_without_llm_call(self, db, workspace, company):
        provider = FakeProvider()
        generate_research(db, str(company.id), workspace.id, provider=provider)
        assert provider.call_count == 1

        result, should_dispatch = request_research(
            db, str(company.id), workspace.id, provider=provider
        )
        assert result.cached is True
        assert result.status == "completed"
        assert should_dispatch is False
        assert provider.call_count == 1  # no regeneration

    def test_force_refresh_bypasses_cache(self, db, workspace, company):
        provider = FakeProvider()
        generate_research(db, str(company.id), workspace.id, provider=provider)

        result, should_dispatch = request_research(
            db, str(company.id), workspace.id, force_refresh=True, provider=provider
        )
        assert should_dispatch is True
        assert result.status == "pending"

    def test_changed_intelligence_triggers_regeneration(self, db, workspace, company):
        provider = FakeProvider()
        generate_research(db, str(company.id), workspace.id, provider=provider)

        _, cached_dispatch = request_research(
            db, str(company.id), workspace.id, provider=provider
        )
        assert cached_dispatch is False

        # A new signal changes the company's intelligence -> hash moves.
        db.add(
            Signal(
                workspace_id=workspace.id,
                company_id=company.id,
                signal_type="funding",
                signal_source="crunchbase",
                title="Series C raised",
                base_strength=0.9,
                decayed_strength=0.9,
                detected_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        _, should_dispatch = request_research(
            db, str(company.id), workspace.id, provider=provider
        )
        assert should_dispatch is True, "new signal must invalidate the cached report"

    def test_completed_report_marked_stale_after_change(self, db, workspace, company):
        provider = FakeProvider()
        generate_research(db, str(company.id), workspace.id, provider=provider)

        fresh = get_latest_research(db, str(company.id), workspace.id, provider=provider)
        assert fresh.is_stale is False

        db.add(
            Signal(
                workspace_id=workspace.id,
                company_id=company.id,
                signal_type="hiring",
                signal_source="apollo",
                title="20 new ops roles",
                base_strength=0.6,
                decayed_strength=0.6,
                detected_at=datetime.now(timezone.utc),
            )
        )
        db.commit()

        stale = get_latest_research(db, str(company.id), workspace.id, provider=provider)
        assert stale.is_stale is True

    def test_in_progress_request_does_not_dispatch_twice(self, db, workspace, company):
        db.add(
            CompanyAIResearch(
                workspace_id=workspace.id,
                company_id=company.id,
                status=ResearchStatus.RUNNING.value,
            )
        )
        db.commit()

        result, should_dispatch = request_research(
            db, str(company.id), workspace.id, provider=FakeProvider()
        )
        assert should_dispatch is False
        assert result.status == "running"

    def test_stale_running_row_is_reaped(self, db, workspace, company):
        row = CompanyAIResearch(
            workspace_id=workspace.id,
            company_id=company.id,
            status=ResearchStatus.RUNNING.value,
        )
        db.add(row)
        db.commit()

        # Simulate a worker that died 30 minutes ago.
        row.updated_at = datetime.now(timezone.utc) - timedelta(minutes=30)
        db.commit()

        response = get_latest_research(db, str(company.id), workspace.id)
        assert response.status == "failed"
        assert "try again" in (response.error_message or "").lower()


@requires_postgres
class TestWorkspaceIsolation:
    def test_other_workspace_cannot_read_research(self, db, workspace, company):
        generate_research(db, str(company.id), workspace.id, provider=FakeProvider())
        intruder = uuid.uuid4()

        with pytest.raises(NotFoundError):
            get_latest_research(db, str(company.id), intruder)

    def test_other_workspace_cannot_trigger_research(self, db, workspace, company):
        with pytest.raises(NotFoundError):
            request_research(db, str(company.id), uuid.uuid4(), provider=FakeProvider())

    def test_unknown_company_raises_not_found(self, db, workspace):
        with pytest.raises(NotFoundError):
            get_latest_research(db, str(uuid.uuid4()), workspace.id)

    def test_malformed_company_id_raises_not_found_not_500(self, db, workspace):
        with pytest.raises(NotFoundError):
            get_latest_research(db, "not-a-uuid", workspace.id)


@requires_postgres
class TestErrorHandling:
    """Every AI failure mode must land on the row, never crash the caller."""

    def _assert_failed(self, db, company, stats, fragment: str):
        assert stats["failed"] == 1
        assert stats["status"] == "failed"
        row = db.query(CompanyAIResearch).filter_by(company_id=company.id).one()
        assert row.status == ResearchStatus.FAILED.value
        assert fragment.lower() in (row.error_message or "").lower()

    def test_rate_limit_is_captured(self, db, workspace, company):
        provider = FakeProvider(raises=RateLimitError(service="fake"))
        stats = generate_research(db, str(company.id), workspace.id, provider=provider)
        self._assert_failed(db, company, stats, "rate limited")

    def test_provider_unavailable_is_captured(self, db, workspace, company):
        provider = FakeProvider(raises=ProviderUnavailableError("no credentials"))
        stats = generate_research(db, str(company.id), workspace.id, provider=provider)
        self._assert_failed(db, company, stats, "unavailable")

    def test_invalid_ai_response_is_captured(self, db, workspace, company):
        provider = FakeProvider(raises=InvalidAIResponseError("not json"))
        stats = generate_research(db, str(company.id), workspace.id, provider=provider)
        self._assert_failed(db, company, stats, "unusable")

    def test_schema_violation_is_captured(self, db, workspace, company):
        bad = valid_payload()
        del bad["summary"]
        stats = generate_research(
            db, str(company.id), workspace.id, provider=FakeProvider(response=bad)
        )
        self._assert_failed(db, company, stats, "schema validation")

    def test_unexpected_exception_is_captured(self, db, workspace, company):
        provider = FakeProvider(raises=RuntimeError("boom"))
        stats = generate_research(db, str(company.id), workspace.id, provider=provider)
        self._assert_failed(db, company, stats, "unexpected")

    def test_failed_report_can_be_retried_successfully(self, db, workspace, company):
        generate_research(
            db, str(company.id), workspace.id, provider=FakeProvider(raises=RuntimeError("boom"))
        )
        stats = generate_research(db, str(company.id), workspace.id, provider=FakeProvider())

        assert stats["status"] == "completed"
        row = db.query(CompanyAIResearch).filter_by(company_id=company.id).one()
        assert row.status == ResearchStatus.COMPLETED.value
        assert row.error_message is None

    def test_failed_row_is_not_served_as_cached_content(self, db, workspace, company):
        generate_research(
            db, str(company.id), workspace.id, provider=FakeProvider(raises=RuntimeError("boom"))
        )
        response = get_latest_research(db, str(company.id), workspace.id)
        assert response.status == "failed"
        assert response.summary is None
        assert response.buying_signals == []


# ══════════════════════════════════════════════════════════════
# HTTP layer
# ══════════════════════════════════════════════════════════════


@requires_postgres
class TestResearchAPI:
    """
    Exercises the real FastAPI stack: routing, auth, status codes and
    workspace isolation. The Celery dispatch is stubbed so no broker is needed.
    """

    @pytest.fixture
    def client(self, db, workspace, monkeypatch):
        from fastapi.testclient import TestClient

        from app.api.auth import AuthenticatedUser, get_current_user
        from app.db.session import get_db
        from app.main import app
        from app.modules.ai.provider import get_provider

        dispatched: list[tuple[str, str]] = []

        class _FakeTask:
            def delay(self, workspace_id: str, company_id: str):
                dispatched.append((workspace_id, company_id))

        monkeypatch.setattr(
            "app.workers.tasks.generate_company_research", _FakeTask(), raising=False
        )

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

    def test_get_returns_none_status_when_no_research(self, client, company):
        res = client.get(f"/api/v1/companies/{company.id}/research")
        assert res.status_code == 200
        assert res.json()["status"] == "none"

    def test_get_unknown_company_returns_404(self, client):
        res = client.get(f"/api/v1/companies/{uuid.uuid4()}/research")
        assert res.status_code == 404

    def test_get_malformed_id_returns_404_not_500(self, client):
        res = client.get("/api/v1/companies/not-a-uuid/research")
        assert res.status_code == 404

    def test_post_starts_generation_and_returns_202(self, client, company):
        res = client.post(f"/api/v1/companies/{company.id}/research")
        assert res.status_code == 202
        body = res.json()
        assert body["status"] == "pending"
        assert body["cached"] is False
        assert client.dispatched == [(str(company.workspace_id), str(company.id))]

    def test_post_returns_200_and_no_dispatch_on_cache_hit(
        self, client, db, workspace, company
    ):
        generate_research(db, str(company.id), workspace.id, provider=FakeProvider())

        res = client.post(f"/api/v1/companies/{company.id}/research")
        assert res.status_code == 200
        body = res.json()
        assert body["cached"] is True
        assert body["status"] == "completed"
        assert body["summary"]
        assert client.dispatched == [], "cache hit must not queue a job"

    def test_post_force_refresh_dispatches_despite_cache(
        self, client, db, workspace, company
    ):
        generate_research(db, str(company.id), workspace.id, provider=FakeProvider())

        res = client.post(
            f"/api/v1/companies/{company.id}/research", params={"force_refresh": True}
        )
        assert res.status_code == 202
        assert len(client.dispatched) == 1

    def test_post_unknown_company_returns_404(self, client):
        res = client.post(f"/api/v1/companies/{uuid.uuid4()}/research")
        assert res.status_code == 404

    def test_response_exposes_full_report_contract(self, client, db, workspace, company):
        generate_research(db, str(company.id), workspace.id, provider=FakeProvider())
        body = client.get(f"/api/v1/companies/{company.id}/research").json()

        for key in (
            "summary",
            "buying_signals",
            "pain_points",
            "recommended_personas",
            "outreach_strategy",
            "talking_points",
            "risks",
            "next_actions",
            "meta",
            "status",
            "cached",
            "is_stale",
        ):
            assert key in body, f"missing `{key}` in API response"
        assert body["meta"]["prompt_version"] == "research.v1"

    def test_endpoints_require_authentication(self, db, company):
        """With no auth override in place, the routes must reject anonymous calls."""
        from fastapi.testclient import TestClient

        from app.db.session import get_db
        from app.main import app

        app.dependency_overrides.clear()
        app.dependency_overrides[get_db] = lambda: db
        anon = TestClient(app)
        try:
            assert anon.get(f"/api/v1/companies/{company.id}/research").status_code == 401
            assert anon.post(f"/api/v1/companies/{company.id}/research").status_code == 401
        finally:
            app.dependency_overrides.clear()
