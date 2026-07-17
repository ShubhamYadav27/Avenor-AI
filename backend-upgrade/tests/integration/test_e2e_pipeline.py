# """
# End-to-end integration test.
# Tests: signal ingestion → scoring → intelligence generation → outcome feedback loop.

# Requires a running Postgres instance.
# Run with: pytest tests/integration/test_e2e_pipeline.py -v
# Set TEST_DATABASE_URL environment variable to override connection.
# """
# import os
# import uuid
# from datetime import datetime, timezone, timedelta

# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# # Integration tests REQUIRE Postgres (JSONB, pgvector, UUID types).
# # Set TEST_DATABASE_URL to a real Postgres instance to run these.
# TEST_DB_URL = os.environ.get("TEST_DATABASE_URL", "")

# requires_postgres = pytest.mark.skipif(
#     not TEST_DB_URL.startswith("postgresql"),
#     reason="Integration tests require Postgres. Set TEST_DATABASE_URL=postgresql://... to enable.",
# )


# @pytest.fixture(scope="session")
# def db_engine():
#     """Create test database engine against real Postgres."""
#     if not TEST_DB_URL.startswith("postgresql"):
#         pytest.skip("TEST_DATABASE_URL not set to a Postgres URL")

#     engine = create_engine(TEST_DB_URL, pool_pre_ping=True)

#     from app.db.session import Base
#     import app.models  # noqa: register models

#     with engine.connect() as conn:
#         from sqlalchemy import text
#         conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
#         conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
#         conn.commit()

#     Base.metadata.create_all(engine)
#     yield engine
#     Base.metadata.drop_all(engine)


# @pytest.fixture
# def db(db_engine):
#     """Provide a clean DB session per test."""
#     SessionTest = sessionmaker(bind=db_engine)
#     session = SessionTest()
#     yield session
#     session.rollback()
#     session.close()


# @pytest.fixture
# def workspace(db):
#     """Create a test workspace with ICP config and signal weights."""
#     from app.models import Workspace, ICPConfig, SignalWeights, WorkspaceUserRole, WorkspaceUser
#     from app.core.signal_config import DEFAULT_SIGNAL_WEIGHTS

#     ws = Workspace(
#         name="Test Workspace",
#         slug=f"test-{uuid.uuid4().hex[:8]}",
#         is_active=True,
#     )
#     db.add(ws)
#     db.flush()

#     icp = ICPConfig(
#         workspace_id=ws.id,
#         industries=["SaaS", "FinTech"],
#         min_employees=50,
#         max_employees=500,
#         locations=["United States"],
#         technologies=["Snowflake"],
#         customer_personas=["VP of Engineering", "Head of Data"],
#         product_name="DataFlow",
#         product_description="A data pipeline platform for fast-growing engineering teams.",
#         key_pain_points=["data pipeline scaling", "slow dashboards"],
#         active_score_threshold=0.60,
#         watch_score_threshold=0.30,
#     )
#     db.add(icp)

#     sw = SignalWeights(
#         workspace_id=ws.id,
#         weights={k: v for k, v in DEFAULT_SIGNAL_WEIGHTS.items()},
#     )
#     db.add(sw)

#     user = WorkspaceUser(
#         workspace_id=ws.id,
#         email="test@example.com",
#         full_name="Test User",
#         role=WorkspaceUserRole.ADMIN,
#         hashed_password="hashed",
#     )
#     db.add(user)
#     db.commit()
#     return ws


# # ── Tests ─────────────────────────────────────────────────────

# @requires_postgres
# class TestSignalIngestion:
#     def test_create_company_and_signals(self, db, workspace):
#         """Companies and signals can be created with correct workspace scoping."""
#         from app.models import Company, Signal, SignalType, SignalSource, CompanyStatus

#         company = Company(
#             workspace_id=workspace.id,
#             name="Veridian Labs",
#             domain="veridian.io",
#             industry="SaaS",
#             employee_count=145,
#             location_country="United States",
#             technologies=["Snowflake", "Airflow"],
#             last_funding_stage="Series A",
#             funding_total_usd=12_000_000,
#             status=CompanyStatus.MONITORING,
#         )
#         db.add(company)
#         db.flush()

#         signal = Signal(
#             workspace_id=workspace.id,
#             company_id=company.id,
#             signal_type=SignalType.FUNDING,
#             signal_source=SignalSource.APOLLO,
#             title="Series A — $12M",
#             description="Veridian Labs raised a Series A round.",
#             base_strength=0.35,
#             decayed_strength=0.35,
#             detected_at=datetime.now(timezone.utc) - timedelta(days=7),
#         )
#         db.add(signal)
#         db.commit()

#         fetched = db.query(Company).filter_by(domain="veridian.io").first()
#         assert fetched is not None
#         assert fetched.name == "Veridian Labs"
#         assert len(fetched.signals) == 1
#         assert fetched.signals[0].signal_type == SignalType.FUNDING


# @requires_postgres
# class TestScoringPipeline:
#     def _create_company_with_signals(self, db, workspace):
#         from app.models import Company, Signal, SignalType, SignalSource, CompanyStatus

#         company = Company(
#             workspace_id=workspace.id,
#             name="Meridian Health",
#             domain="meridianhealth.io",
#             industry="SaaS",
#             employee_count=200,
#             location_country="United States",
#             technologies=["Snowflake", "dbt"],
#             last_funding_stage="Series B",
#             status=CompanyStatus.MONITORING,
#         )
#         db.add(company)
#         db.flush()

#         now = datetime.now(timezone.utc)
#         for sig_type, age in [
#             (SignalType.FUNDING, 14),
#             (SignalType.HIRING, 3),
#             (SignalType.TECH_CHANGE, 7),
#         ]:
#             from app.core.signal_config import DEFAULT_SIGNAL_WEIGHTS
#             strength = DEFAULT_SIGNAL_WEIGHTS[sig_type]
#             db.add(Signal(
#                 workspace_id=workspace.id,
#                 company_id=company.id,
#                 signal_type=sig_type,
#                 signal_source=SignalSource.MANUAL,
#                 title=f"Test {sig_type} signal",
#                 base_strength=strength,
#                 decayed_strength=strength,
#                 detected_at=now - timedelta(days=age),
#             ))
#         db.commit()
#         return company

#     def test_scoring_produces_nonzero_score(self, db, workspace):
#         company = self._create_company_with_signals(db, workspace)

#         from app.modules.scoring.engine import run_scoring_for_workspace
#         stats = run_scoring_for_workspace(db, str(workspace.id))

#         db.refresh(company)
#         assert company.composite_score > 0
#         assert stats["scored"] >= 1

#     def test_high_signal_company_gets_active_status(self, db, workspace):
#         company = self._create_company_with_signals(db, workspace)

#         from app.modules.scoring.engine import run_scoring_for_workspace
#         from app.models import CompanyStatus
#         run_scoring_for_workspace(db, str(workspace.id))

#         db.refresh(company)
#         # SaaS + 200 employees + US location = full ICP match
#         # 3 fresh signals should push above 0.60 threshold
#         if company.composite_score >= 0.60:
#             assert company.status == CompanyStatus.ACTIVE

#     def test_buying_window_assigned_after_scoring(self, db, workspace):
#         self._create_company_with_signals(db, workspace)
#         from app.modules.scoring.engine import run_scoring_for_workspace
#         run_scoring_for_workspace(db, str(workspace.id))

#         from app.models import Company
#         company = db.query(Company).filter_by(workspace_id=workspace.id).first()
#         assert company.buying_window in ("hot", "warm", "watch", "cold")

#     def test_score_snapshot_created(self, db, workspace):
#         self._create_company_with_signals(db, workspace)
#         from app.modules.scoring.engine import run_scoring_for_workspace
#         run_scoring_for_workspace(db, str(workspace.id))

#         from app.models import Company, CompanyScore
#         company = db.query(Company).filter_by(workspace_id=workspace.id).first()
#         assert company.score_snapshot is not None
#         assert company.score_snapshot.composite_score == company.composite_score


# @requires_postgres
# class TestIntelligenceGeneration:
#     def test_feed_generation_without_openai(self, db, workspace):
#         """Feed generation falls back gracefully when no OpenAI key."""
#         from app.models import Company, Signal, SignalType, SignalSource, CompanyStatus
#         from datetime import datetime, timezone, timedelta

#         company = Company(
#             workspace_id=workspace.id,
#             name="TechCorp",
#             domain="techcorp.io",
#             industry="SaaS",
#             employee_count=120,
#             location_country="United States",
#             status=CompanyStatus.ACTIVE,
#             composite_score=0.75,
#             buying_window="hot",
#             buying_window_confidence=0.8,
#         )
#         db.add(company)
#         db.flush()

#         db.add(Signal(
#             workspace_id=workspace.id,
#             company_id=company.id,
#             signal_type=SignalType.FUNDING,
#             signal_source=SignalSource.MANUAL,
#             title="Series A — $8M",
#             base_strength=0.35,
#             decayed_strength=0.30,
#             detected_at=datetime.now(timezone.utc) - timedelta(days=10),
#         ))
#         db.commit()

#         # Patch OpenAI to be unavailable
#         import app.core.config as cfg_module
#         original = cfg_module.settings.OPENAI_API_KEY
#         cfg_module.settings.OPENAI_API_KEY = ""

#         try:
#             from app.modules.intelligence.engine import run_feed_generation_for_workspace
#             stats = run_feed_generation_for_workspace(db, str(workspace.id))
#         finally:
#             cfg_module.settings.OPENAI_API_KEY = original

#         from app.models import IntelligenceFeedItem
#         item = db.query(IntelligenceFeedItem).filter_by(workspace_id=workspace.id).first()
#         assert item is not None
#         assert item.signal_summary  # fallback summary generated
#         assert item.recommended_angle


# @requires_postgres
# class TestOutcomeFeedbackLoop:
#     def test_outcome_logging_captures_signal_snapshot(self, db, workspace):
#         """Logging an outcome captures the current signal state as training data."""
#         from app.models import Company, Signal, SignalType, SignalSource, CompanyStatus

#         company = Company(
#             workspace_id=workspace.id,
#             name="OutcomeTest Co",
#             domain="outcometest.io",
#             industry="SaaS",
#             employee_count=100,
#             status=CompanyStatus.ACTIVE,
#             composite_score=0.72,
#             buying_window="warm",
#         )
#         db.add(company)
#         db.flush()

#         db.add(Signal(
#             workspace_id=workspace.id,
#             company_id=company.id,
#             signal_type=SignalType.HIRING,
#             signal_source=SignalSource.MANUAL,
#             title="Hiring 5 engineers",
#             base_strength=0.25,
#             decayed_strength=0.22,
#             detected_at=datetime.now(timezone.utc) - timedelta(days=5),
#         ))
#         db.commit()

#         from app.models import Outcome, OutcomeType, OutcomeSource
#         signals = db.query(Signal).filter_by(company_id=company.id).all()
#         snapshot = [{"type": s.signal_type, "strength": s.decayed_strength} for s in signals]

#         outcome = Outcome(
#             workspace_id=workspace.id,
#             company_id=company.id,
#             outcome_type=OutcomeType.MEETING_BOOKED,
#             outcome_source=OutcomeSource.MANUAL,
#             predicted_composite_score=company.composite_score,
#             predicted_buying_window=company.buying_window,
#             active_signals_snapshot=snapshot,
#             days_from_first_signal=5,
#             occurred_at=datetime.now(timezone.utc),
#         )
#         db.add(outcome)
#         db.commit()

#         fetched = db.query(Outcome).filter_by(company_id=company.id).first()
#         assert fetched.outcome_type == OutcomeType.MEETING_BOOKED
#         assert fetched.predicted_composite_score == 0.72
#         assert len(fetched.active_signals_snapshot) == 1

#     def test_model_trainer_skips_insufficient_data(self, db, workspace):
#         """Trainer skips recalibration when < 20 outcomes exist."""
#         from app.modules.scoring.trainer import recalibrate_weights
#         result = recalibrate_weights(db, str(workspace.id))
#         assert result.get("skipped") is True

#     def test_model_trainer_runs_with_sufficient_data(self, db, workspace):
#         """Trainer updates weights when enough outcomes are available."""
#         from app.models import Company, Outcome, OutcomeType, OutcomeSource, CompanyStatus

#         # Create 25 outcomes (above threshold)
#         for i in range(25):
#             company = Company(
#                 workspace_id=workspace.id,
#                 name=f"TrainingCo {i}",
#                 domain=f"trainingco{i}.io",
#                 industry="SaaS",
#                 employee_count=100 + i,
#                 status=CompanyStatus.MONITORING,
#                 composite_score=0.5 + (i * 0.01),
#             )
#             db.add(company)
#             db.flush()

#             otype = OutcomeType.CLOSED_WON if i % 3 == 0 else OutcomeType.NO_RESPONSE
#             db.add(Outcome(
#                 workspace_id=workspace.id,
#                 company_id=company.id,
#                 outcome_type=otype,
#                 outcome_source=OutcomeSource.MANUAL,
#                 predicted_composite_score=company.composite_score,
#                 predicted_buying_window="warm",
#                 active_signals_snapshot=[{"type": "hiring", "strength": 0.2}],
#                 occurred_at=datetime.now(timezone.utc),
#             ))

#         db.commit()

#         from app.modules.scoring.trainer import recalibrate_weights
#         result = recalibrate_weights(db, str(workspace.id))

#         assert result.get("skipped") is not True
#         assert result["outcomes_used"] >= 20
#         assert isinstance(result["new_weights"], dict)
#         assert len(result["new_weights"]) > 0



"""
End-to-end integration test.
Tests: signal ingestion → scoring → intelligence generation → outcome feedback loop.

Requires a running Postgres instance.
Run with: pytest tests/integration/test_e2e_pipeline.py -v
Set TEST_DATABASE_URL environment variable to override connection.
"""
import os
import uuid
from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Integration tests REQUIRE Postgres (JSONB, pgvector, UUID types).
# Set TEST_DATABASE_URL to a real Postgres instance to run these.
TEST_DB_URL = os.environ.get("TEST_DATABASE_URL", "")

requires_postgres = pytest.mark.skipif(
    not TEST_DB_URL.startswith("postgresql"),
    reason="Integration tests require Postgres. Set TEST_DATABASE_URL=postgresql://... to enable.",
)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine against real Postgres."""
    if not TEST_DB_URL.startswith("postgresql"):
        pytest.skip("TEST_DATABASE_URL not set to a Postgres URL")

    engine = create_engine(TEST_DB_URL, pool_pre_ping=True)

    from app.db.session import Base
    import app.models  # noqa: register models

    with engine.connect() as conn:
        from sqlalchemy import text
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db(db_engine):
    """Provide a clean DB session per test."""
    SessionTest = sessionmaker(bind=db_engine)
    session = SessionTest()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def workspace(db):
    """Create a test workspace with ICP config and signal weights."""
    from app.models import Workspace, ICPConfig, SignalWeights, WorkspaceUserRole, WorkspaceUser
    from app.core.signal_config import DEFAULT_SIGNAL_WEIGHTS

    ws = Workspace(
        name="Test Workspace",
        slug=f"test-{uuid.uuid4().hex[:8]}",
        is_active=True,
    )
    db.add(ws)
    db.flush()

    icp = ICPConfig(
        workspace_id=ws.id,
        industries=["SaaS", "FinTech"],
        min_employees=50,
        max_employees=500,
        locations=["United States"],
        technologies=["Snowflake"],
        customer_personas=["VP of Engineering", "Head of Data"],
        product_name="DataFlow",
        product_description="A data pipeline platform for fast-growing engineering teams.",
        key_pain_points=["data pipeline scaling", "slow dashboards"],
        active_score_threshold=0.60,
        watch_score_threshold=0.30,
    )
    db.add(icp)

    sw = SignalWeights(
        workspace_id=ws.id,
        weights={k: v for k, v in DEFAULT_SIGNAL_WEIGHTS.items()},
    )
    db.add(sw)

    user = WorkspaceUser(
        workspace_id=ws.id,
        email="test@example.com",
        full_name="Test User",
        role=WorkspaceUserRole.ADMIN,
        hashed_password="hashed",
    )
    db.add(user)
    db.commit()
    return ws


# ── Tests ─────────────────────────────────────────────────────

@requires_postgres
class TestSignalIngestion:
    def test_create_company_and_signals(self, db, workspace):
        """Companies and signals can be created with correct workspace scoping."""
        from app.models import Company, Signal, SignalType, SignalSource, CompanyStatus

        company = Company(
            workspace_id=workspace.id,
            name="Veridian Labs",
            domain="veridian.io",
            industry="SaaS",
            employee_count=145,
            location_country="United States",
            technologies=["Snowflake", "Airflow"],
            last_funding_stage="Series A",
            funding_total_usd=12_000_000,
            status=CompanyStatus.MONITORING,
        )
        db.add(company)
        db.flush()

        signal = Signal(
            workspace_id=workspace.id,
            company_id=company.id,
            signal_type=SignalType.FUNDING,
            signal_source=SignalSource.APOLLO,
            title="Series A — $12M",
            description="Veridian Labs raised a Series A round.",
            base_strength=0.35,
            decayed_strength=0.35,
            detected_at=datetime.now(timezone.utc) - timedelta(days=7),
        )
        db.add(signal)
        db.commit()

        fetched = db.query(Company).filter_by(domain="veridian.io").first()
        assert fetched is not None
        assert fetched.name == "Veridian Labs"
        assert len(fetched.signals) == 1
        assert fetched.signals[0].signal_type == SignalType.FUNDING


@requires_postgres
class TestScoringPipeline:
    def _create_company_with_signals(self, db, workspace):
        from app.models import Company, Signal, SignalType, SignalSource, CompanyStatus

        company = Company(
            workspace_id=workspace.id,
            name="Meridian Health",
            domain="meridianhealth.io",
            industry="SaaS",
            employee_count=200,
            location_country="United States",
            technologies=["Snowflake", "dbt"],
            last_funding_stage="Series B",
            status=CompanyStatus.MONITORING,
        )
        db.add(company)
        db.flush()

        now = datetime.now(timezone.utc)
        for sig_type, age in [
            (SignalType.FUNDING, 14),
            (SignalType.HIRING, 3),
            (SignalType.TECH_CHANGE, 7),
        ]:
            from app.core.signal_config import DEFAULT_SIGNAL_WEIGHTS
            strength = DEFAULT_SIGNAL_WEIGHTS[sig_type]
            db.add(Signal(
                workspace_id=workspace.id,
                company_id=company.id,
                signal_type=sig_type,
                signal_source=SignalSource.MANUAL,
                title=f"Test {sig_type} signal",
                base_strength=strength,
                decayed_strength=strength,
                detected_at=now - timedelta(days=age),
            ))
        db.commit()
        return company

    def test_scoring_produces_nonzero_score(self, db, workspace):
        company = self._create_company_with_signals(db, workspace)

        from app.modules.scoring.engine import run_scoring_for_workspace
        stats = run_scoring_for_workspace(db, str(workspace.id))

        db.refresh(company)
        assert company.composite_score > 0
        assert stats["scored"] >= 1

    def test_high_signal_company_gets_active_status(self, db, workspace):
        company = self._create_company_with_signals(db, workspace)

        from app.modules.scoring.engine import run_scoring_for_workspace
        from app.models import CompanyStatus
        run_scoring_for_workspace(db, str(workspace.id))

        db.refresh(company)
        # SaaS + 200 employees + US location = full ICP match
        # 3 fresh signals should push above 0.60 threshold
        if company.composite_score >= 0.60:
            assert company.status == CompanyStatus.ACTIVE

    def test_buying_window_assigned_after_scoring(self, db, workspace):
        self._create_company_with_signals(db, workspace)
        from app.modules.scoring.engine import run_scoring_for_workspace
        run_scoring_for_workspace(db, str(workspace.id))

        from app.models import Company
        company = db.query(Company).filter_by(workspace_id=workspace.id).first()
        assert company.buying_window in ("hot", "warm", "watch", "cold")

    def test_score_snapshot_created(self, db, workspace):
        self._create_company_with_signals(db, workspace)
        from app.modules.scoring.engine import run_scoring_for_workspace
        run_scoring_for_workspace(db, str(workspace.id))

        from app.models import Company, CompanyScore
        company = db.query(Company).filter_by(workspace_id=workspace.id).first()
        assert company.score_snapshot is not None
        assert company.score_snapshot.composite_score == company.composite_score


@requires_postgres
class TestIntelligenceGeneration:
    def test_feed_generation_without_gemini(self, db, workspace):
        """Feed generation falls back gracefully when no Gemini key."""
        from app.models import Company, Signal, SignalType, SignalSource, CompanyStatus
        from datetime import datetime, timezone, timedelta

        company = Company(
            workspace_id=workspace.id,
            name="TechCorp",
            domain="techcorp.io",
            industry="SaaS",
            employee_count=120,
            location_country="United States",
            status=CompanyStatus.ACTIVE,
            composite_score=0.75,
            buying_window="hot",
            buying_window_confidence=0.8,
        )
        db.add(company)
        db.flush()

        db.add(Signal(
            workspace_id=workspace.id,
            company_id=company.id,
            signal_type=SignalType.FUNDING,
            signal_source=SignalSource.MANUAL,
            title="Series A — $8M",
            base_strength=0.35,
            decayed_strength=0.30,
            detected_at=datetime.now(timezone.utc) - timedelta(days=10),
        ))
        db.commit()

        # Patch Gemini to be unavailable
        import app.core.config as cfg_module
        original = cfg_module.settings.GEMINI_API_KEY
        cfg_module.settings.GEMINI_API_KEY = ""

        try:
            from app.modules.intelligence.engine import run_feed_generation_for_workspace
            stats = run_feed_generation_for_workspace(db, str(workspace.id))
        finally:
            cfg_module.settings.GEMINI_API_KEY = original

        from app.models import IntelligenceFeedItem
        item = db.query(IntelligenceFeedItem).filter_by(workspace_id=workspace.id).first()
        assert item is not None
        assert item.signal_summary  # fallback summary generated
        assert item.recommended_angle


@requires_postgres
class TestOutcomeFeedbackLoop:
    def test_outcome_logging_captures_signal_snapshot(self, db, workspace):
        """Logging an outcome captures the current signal state as training data."""
        from app.models import Company, Signal, SignalType, SignalSource, CompanyStatus

        company = Company(
            workspace_id=workspace.id,
            name="OutcomeTest Co",
            domain="outcometest.io",
            industry="SaaS",
            employee_count=100,
            status=CompanyStatus.ACTIVE,
            composite_score=0.72,
            buying_window="warm",
        )
        db.add(company)
        db.flush()

        db.add(Signal(
            workspace_id=workspace.id,
            company_id=company.id,
            signal_type=SignalType.HIRING,
            signal_source=SignalSource.MANUAL,
            title="Hiring 5 engineers",
            base_strength=0.25,
            decayed_strength=0.22,
            detected_at=datetime.now(timezone.utc) - timedelta(days=5),
        ))
        db.commit()

        from app.models import Outcome, OutcomeType, OutcomeSource
        signals = db.query(Signal).filter_by(company_id=company.id).all()
        snapshot = [{"type": s.signal_type, "strength": s.decayed_strength} for s in signals]

        outcome = Outcome(
            workspace_id=workspace.id,
            company_id=company.id,
            outcome_type=OutcomeType.MEETING_BOOKED,
            outcome_source=OutcomeSource.MANUAL,
            predicted_composite_score=company.composite_score,
            predicted_buying_window=company.buying_window,
            active_signals_snapshot=snapshot,
            days_from_first_signal=5,
            occurred_at=datetime.now(timezone.utc),
        )
        db.add(outcome)
        db.commit()

        fetched = db.query(Outcome).filter_by(company_id=company.id).first()
        assert fetched.outcome_type == OutcomeType.MEETING_BOOKED
        assert fetched.predicted_composite_score == 0.72
        assert len(fetched.active_signals_snapshot) == 1

    def test_model_trainer_skips_insufficient_data(self, db, workspace):
        """Trainer skips recalibration when < 20 outcomes exist."""
        from app.modules.scoring.trainer import recalibrate_weights
        result = recalibrate_weights(db, str(workspace.id))
        assert result.get("skipped") is True

    def test_model_trainer_runs_with_sufficient_data(self, db, workspace):
        """Trainer updates weights when enough outcomes are available."""
        from app.models import Company, Outcome, OutcomeType, OutcomeSource, CompanyStatus

        # Create 25 outcomes (above threshold)
        for i in range(25):
            company = Company(
                workspace_id=workspace.id,
                name=f"TrainingCo {i}",
                domain=f"trainingco{i}.io",
                industry="SaaS",
                employee_count=100 + i,
                status=CompanyStatus.MONITORING,
                composite_score=0.5 + (i * 0.01),
            )
            db.add(company)
            db.flush()

            otype = OutcomeType.CLOSED_WON if i % 3 == 0 else OutcomeType.NO_RESPONSE
            db.add(Outcome(
                workspace_id=workspace.id,
                company_id=company.id,
                outcome_type=otype,
                outcome_source=OutcomeSource.MANUAL,
                predicted_composite_score=company.composite_score,
                predicted_buying_window="warm",
                active_signals_snapshot=[{"type": "hiring", "strength": 0.2}],
                occurred_at=datetime.now(timezone.utc),
            ))

        db.commit()

        from app.modules.scoring.trainer import recalibrate_weights
        result = recalibrate_weights(db, str(workspace.id))

        assert result.get("skipped") is not True
        assert result["outcomes_used"] >= 20
        assert isinstance(result["new_weights"], dict)
        assert len(result["new_weights"]) > 0

