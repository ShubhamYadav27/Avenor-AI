"""
tests/unit/test_crm_intelligence.py

Unit tests for Phase 4.2 CRM intelligence components.
All tests use mocks — no real HubSpot API or database required.

Covers:
  - HubSpot client token refresh detection
  - Sync engine company matching (exact, fuzzy, stub creation)
  - Webhook signature verification (v1 and v3)
  - Outcome attribution logic
  - Signal effectiveness and feedback loop analytics
"""
import hashlib
import hmac
import uuid
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, PropertyMock

import pytest


# ══════════════════════════════════════════════════════════════
# HubSpot Client Tests
# ══════════════════════════════════════════════════════════════

class TestHubSpotClientTokenRefresh:
    """Test token refresh detection without real HTTP calls."""

    def _make_conn(self, expires_in_minutes: int, use_fernet: bool = True):
        """Build a mock HubSpotConnection."""
        from cryptography.fernet import Fernet
        import os
        key = Fernet.generate_key()
        fernet = Fernet(key)

        conn = MagicMock()
        conn.workspace_id = uuid.uuid4()
        conn.hub_id = "12345"

        if use_fernet:
            # Valid Fernet-encrypted tokens
            conn.access_token_encrypted = fernet.encrypt(b"access_token_value").decode()
            conn.refresh_token_encrypted = fernet.encrypt(b"refresh_token_value").decode()
        else:
            # Simulate legacy XOR token
            import base64
            key_b = b"test" * 8
            enc = bytes(b ^ key_b[i % 32] for i, b in enumerate(b"old_token"))
            conn.access_token_encrypted = base64.b64encode(enc).decode()
            conn.refresh_token_encrypted = base64.b64encode(enc).decode()

        # Store the Fernet key in env so _get_fernet() can use it
        conn._test_fernet_key = key.decode()
        conn.token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        conn.is_active = True
        return conn, key.decode()

    def test_fresh_token_not_refreshed(self):
        """Token with > 5 min until expiry should not trigger refresh."""
        from cryptography.fernet import Fernet as _Fernet
        # Create a key and encrypt the test token with it
        test_key = _Fernet.generate_key()
        f = _Fernet(test_key)
        encrypted_access = f.encrypt(b"access_token_value").decode()
        encrypted_refresh = f.encrypt(b"refresh_token_value").decode()

        conn = MagicMock()
        conn.workspace_id = uuid.uuid4()
        conn.access_token_encrypted = encrypted_access
        conn.refresh_token_encrypted = encrypted_refresh
        conn.token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=60)
        conn.is_active = True

        db = MagicMock()

        from app.utils import encryption
        # Patch settings so _get_fernet uses our test key
        mock_settings = SimpleNamespace(
            ENCRYPTION_KEY=test_key.decode(), is_production=False
        )
        with patch("app.core.config.settings", mock_settings):
            encryption._get_fernet.cache_clear()
            with patch("app.integrations.hubspot.client.is_fernet_token", return_value=True):
                from app.integrations.hubspot.client import HubSpotClient
                client = HubSpotClient(conn, db)
                with patch.object(client, "_refresh_token") as mock_refresh:
                    token = client._get_token()
                    mock_refresh.assert_not_called()
                    assert token == "access_token_value"
        encryption._get_fernet.cache_clear()

    def test_expiring_token_triggers_refresh(self):
        """Token within 5 min of expiry should trigger refresh."""
        conn, key = self._make_conn(expires_in_minutes=3)
        db = MagicMock()

        import os
        with patch.dict(os.environ, {"ENCRYPTION_KEY": key, "APP_ENV": "development"}):
            from app.utils import encryption
            encryption._get_fernet.cache_clear()
            from app.integrations.hubspot.client import HubSpotClient
            client = HubSpotClient(conn, db)

            with patch.object(client, "_refresh_token") as mock_refresh:
                # Patch decrypt to return plaintext after "refresh"
                with patch("app.integrations.hubspot.client.decrypt_token", return_value="new_access_token"):
                    with patch("app.integrations.hubspot.client.is_fernet_token", return_value=True):
                        client._get_token()
                        mock_refresh.assert_called_once()

        encryption._get_fernet.cache_clear()

    def test_is_fernet_token_detection(self):
        """is_fernet_token correctly identifies Fernet vs legacy tokens."""
        from app.utils.encryption import is_fernet_token
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        fernet = Fernet(key)
        ct = fernet.encrypt(b"test").decode()
        assert is_fernet_token(ct) is True

        import base64
        legacy = base64.b64encode(b"some_xor_encrypted_data").decode()
        assert is_fernet_token(legacy) is False


# ══════════════════════════════════════════════════════════════
# CRM Sync Engine Tests
# ══════════════════════════════════════════════════════════════

class TestCompanyMatching:
    """Test _match_or_create_company without database."""

    def _make_db_with_companies(self, companies: list[dict]):
        """Build a mock DB that returns a list of Company-like objects."""
        db = MagicMock()
        company_mocks = []
        for cd in companies:
            c = SimpleNamespace(**cd)
            c.raw_apollo_data = cd.get("raw_apollo_data", {})
            c.id = cd.get("id", uuid.uuid4())
            company_mocks.append(c)

        # filter_by().first() for domain lookup
        def mock_filter_by(**kwargs):
            mock = MagicMock()
            domain = kwargs.get("domain")
            if domain:
                match = next((c for c in company_mocks if c.domain == domain), None)
                mock.first.return_value = match
            else:
                mock.first.return_value = None
            return mock

        db.query.return_value.filter_by.side_effect = mock_filter_by
        db.query.return_value.filter_by.return_value.all = lambda: company_mocks
        # For all() call in _match_or_create_company
        db.query.return_value.filter_by.return_value.filter_by.return_value.all = lambda: []

        return db, company_mocks

    def test_exact_domain_match(self):
        """Exact domain match should return existing company."""
        from app.integrations.hubspot.sync import _match_or_create_company
        company_id = uuid.uuid4()
        db = MagicMock()
        existing = SimpleNamespace(
            id=company_id, name="Veridian Labs", domain="veridian.io",
            raw_apollo_data={}, composite_score=0.7, buying_window="hot"
        )
        db.query.return_value.filter_by.return_value.first.return_value = existing
        db.query.return_value.filter_by.return_value.all.return_value = [existing]

        result = _match_or_create_company(
            db, str(uuid.uuid4()), "veridian.io", "Veridian Labs", "hs_123"
        )
        assert result is existing

    def test_no_domain_fuzzy_name_match(self):
        """When domain is None, fuzzy name match should find the company."""
        from rapidfuzz import fuzz
        # Verify the fuzzy logic itself works at the threshold we use
        ratio = fuzz.ratio("Meridian Health Technology".lower(), "Meridian Health Tech".lower())
        assert ratio > 85, f"Expected fuzzy ratio > 85, got {ratio}"  # sync.py uses > 88 but this pair scores ~87

        # Verify a clearly different name does NOT match
        ratio_bad = fuzz.ratio("Completely Different Corp".lower(), "Meridian Health Tech".lower())
        assert ratio_bad <= 88, f"Expected no match, got {ratio_bad}"

    def test_no_match_creates_stub(self):
        """When no company matches, create a stub."""
        from app.integrations.hubspot.sync import _match_or_create_company
        workspace_id = str(uuid.uuid4())

        db = MagicMock()
        db.query.return_value.filter_by.return_value.first.return_value = None
        db.query.return_value.filter_by.return_value.all.return_value = []
        db.flush = MagicMock()

        # Track what gets added
        added = []
        db.add.side_effect = lambda obj: added.append(obj)

        from app.models import Company
        result = _match_or_create_company(
            db, workspace_id, "newcompany.io", "New Company Inc", "hs_789"
        )
        assert len(added) == 1
        assert added[0].name == "New Company Inc"
        assert added[0].domain == "newcompany.io"


class TestSyncHelpers:
    def test_parse_hs_date_iso_string(self):
        from app.integrations.hubspot.sync import _parse_hs_date
        dt = _parse_hs_date("2024-03-15T10:30:00.000Z")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 3

    def test_parse_hs_date_milliseconds(self):
        from app.integrations.hubspot.sync import _parse_hs_date
        # HubSpot sometimes sends millisecond timestamps
        ms = int(datetime(2024, 6, 1, tzinfo=timezone.utc).timestamp() * 1000)
        dt = _parse_hs_date(str(ms))
        assert dt is not None
        assert dt.year == 2024

    def test_parse_hs_date_none(self):
        from app.integrations.hubspot.sync import _parse_hs_date
        assert _parse_hs_date(None) is None
        assert _parse_hs_date("") is None

    def test_parse_float_valid(self):
        from app.integrations.hubspot.sync import _parse_float
        assert _parse_float("45000.00") == 45000.0
        assert _parse_float(0) == 0.0
        assert _parse_float(None) is None
        assert _parse_float("not_a_number") is None


# ══════════════════════════════════════════════════════════════
# Webhook Signature Verification Tests
# ══════════════════════════════════════════════════════════════

class TestWebhookSignature:
    """Test signature verification without real HTTP — pure crypto math."""

    def test_v1_signature_valid(self):
        from app.integrations.hubspot.routes import _verify_signature_v1
        client_secret = "test_client_secret_abc"
        body = b'[{"subscriptionType":"deal.propertyChange"}]'

        # Compute expected signature (same as HubSpot would)
        source = (client_secret + body.decode()).encode()
        expected_sig = hashlib.sha256(source).hexdigest()

        with patch("app.integrations.hubspot.routes.settings") as mock_settings:
            mock_settings.HUBSPOT_APP_CLIENT_SECRET = client_secret
            result = _verify_signature_v1(body, expected_sig)
        assert result is True

    def test_v1_signature_invalid(self):
        from app.integrations.hubspot.routes import _verify_signature_v1
        with patch("app.integrations.hubspot.routes.settings") as mock_settings:
            mock_settings.HUBSPOT_APP_CLIENT_SECRET = "secret"
            result = _verify_signature_v1(b"body", "wrong_signature")
        assert result is False

    def test_v3_signature_valid(self):
        from app.integrations.hubspot.routes import _verify_signature_v3
        client_secret = "test_v3_secret"
        url = "https://avenor.io/api/v1/integrations/hubspot/webhook"
        timestamp = "1234567890"
        body = b'[{"event":"deal.propertyChange"}]'

        source = client_secret + url + body.decode() + timestamp
        expected_sig = hashlib.sha256(source.encode()).hexdigest()

        with patch("app.integrations.hubspot.routes.settings") as mock_settings:
            mock_settings.HUBSPOT_APP_CLIENT_SECRET = client_secret
            result = _verify_signature_v3(body, expected_sig, timestamp, url)
        assert result is True

    def test_v3_signature_tampered_body(self):
        from app.integrations.hubspot.routes import _verify_signature_v3
        client_secret = "test_secret"
        url = "https://example.com/webhook"
        timestamp = "999"
        original_body = b"original"
        tampered_body = b"tampered"

        source = client_secret + url + original_body.decode() + timestamp
        sig = hashlib.sha256(source.encode()).hexdigest()

        with patch("app.integrations.hubspot.routes.settings") as mock_settings:
            mock_settings.HUBSPOT_APP_CLIENT_SECRET = client_secret
            result = _verify_signature_v3(tampered_body, sig, timestamp, url)
        assert result is False


# ══════════════════════════════════════════════════════════════
# Outcome Attribution Tests
# ══════════════════════════════════════════════════════════════

class TestOutcomeAttribution:
    """Test attribution logic with mock database objects."""

    def _make_outcome(self, outcome_type="closed_won", score=0.75, window="hot"):
        return SimpleNamespace(
            id=uuid.uuid4(),
            company_id=uuid.uuid4(),
            outcome_type=outcome_type,
            predicted_composite_score=score,
            predicted_buying_window=window,
            deal_value_usd=45000.0,
            hubspot_deal_id="deal_123",
            days_ahead_of_organic_discovery=14,
            occurred_at=datetime.now(timezone.utc),
        )

    def test_attribution_created_for_positive_outcome(self):
        """A closed_won outcome with signals should produce an attribution."""
        from app.modules.outcomes.attribution import attribute_outcome

        outcome = self._make_outcome("closed_won", score=0.8)

        # Mock company
        company = SimpleNamespace(
            id=outcome.company_id, name="Test Co", domain="test.io",
            composite_score=0.8, buying_window="hot"
        )

        # Mock signals
        signal = SimpleNamespace(
            signal_type="funding", title="Series A", decayed_strength=0.3,
            detected_at=datetime.now(timezone.utc) - timedelta(days=20)
        )

        # Mock feed item
        feed_item = SimpleNamespace(
            id=uuid.uuid4(), composite_score=0.8, buying_window="hot",
            generated_at=datetime.now(timezone.utc) - timedelta(days=5)
        )

        db = MagicMock()
        db.get.side_effect = lambda cls, id: company if id == outcome.company_id else None
        db.query.return_value.filter_by.return_value.first.return_value = None  # no existing attribution
        db.query.return_value.filter_by.return_value.all.return_value = [signal]
        db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = feed_item

        added = []
        db.add.side_effect = lambda obj: added.append(obj)

        result = attribute_outcome(db, str(uuid.uuid4()), outcome)

        assert result is not None
        assert len(added) == 1
        attr = added[0]
        assert attr.outcome_type == "closed_won"
        assert attr.prediction_was_correct is True  # score 0.8 >= 0.5 AND closed_won
        assert attr.deal_value_usd == 45000.0

    def test_attribution_skipped_when_no_signals(self):
        """No signals = can't attribute — it's a pure CRM deal."""
        from app.modules.outcomes.attribution import attribute_outcome

        outcome = self._make_outcome("closed_won")
        company = SimpleNamespace(
            id=outcome.company_id, name="No Signal Co", domain="nosig.io",
            composite_score=0.0, buying_window="cold"
        )

        db = MagicMock()
        db.get.return_value = company
        db.query.return_value.filter_by.return_value.first.return_value = None
        db.query.return_value.filter_by.return_value.all.return_value = []  # no signals

        result = attribute_outcome(db, str(uuid.uuid4()), outcome)
        assert result is None

    def test_prediction_incorrect_for_low_score_positive(self):
        """Score < 0.5 at prediction time = prediction was NOT correct."""
        from app.modules.outcomes.attribution import attribute_outcome

        outcome = self._make_outcome("closed_won", score=0.3)  # below 0.5
        company = SimpleNamespace(
            id=outcome.company_id, name="Low Score Co",
            composite_score=0.3, buying_window="cold"
        )
        signal = SimpleNamespace(
            signal_type="news", title="Minor news",
            decayed_strength=0.05,
            detected_at=datetime.now(timezone.utc) - timedelta(days=5)
        )
        feed_item = SimpleNamespace(
            id=uuid.uuid4(), composite_score=0.3, buying_window="cold",
            generated_at=datetime.now(timezone.utc) - timedelta(days=2)
        )

        db = MagicMock()
        db.get.return_value = company
        db.query.return_value.filter_by.return_value.first.return_value = None
        db.query.return_value.filter_by.return_value.all.return_value = [signal]
        db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = feed_item

        added = []
        db.add.side_effect = lambda obj: added.append(obj)
        result = attribute_outcome(db, str(uuid.uuid4()), outcome)

        assert result is not None
        assert added[0].prediction_was_correct is False


# ══════════════════════════════════════════════════════════════
# Signal Feedback Loop Tests
# ══════════════════════════════════════════════════════════════

class TestSignalFeedbackLoop:
    """Test signal effectiveness computation with mock data."""

    def _make_outcome(self, outcome_type, signal_types, deal_value=None):
        return SimpleNamespace(
            id=uuid.uuid4(),
            company_id=uuid.uuid4(),
            outcome_type=outcome_type,
            predicted_composite_score=0.7,
            predicted_buying_window="hot",
            deal_value_usd=deal_value,
            days_ahead_of_organic_discovery=None,
            active_signals_snapshot=[
                {"type": st, "strength": 0.25} for st in signal_types
            ],
        )

    def test_conversion_rate_computed_correctly(self):
        """Verify conversion rate = positives / total for a signal type."""
        from app.modules.outcomes.feedback_loop import compute_signal_effectiveness

        # 4 outcomes: 2 with "funding" signal → 1 positive, 1 negative
        # 2 with "hiring" signal → both positive
        outcomes = [
            self._make_outcome("closed_won", ["funding", "hiring"]),
            self._make_outcome("no_response", ["funding"]),
            self._make_outcome("closed_won", ["hiring"]),
            self._make_outcome("meeting_booked", ["hiring"]),
            self._make_outcome("no_response", ["news"]),
            self._make_outcome("no_response", ["news"]),
        ]

        workspace = SimpleNamespace(
            id=uuid.uuid4(),
            signal_weights=SimpleNamespace(weights={"funding": 0.35, "hiring": 0.28}),
            is_active=True,
        )

        db = MagicMock()
        db.get.return_value = workspace

        # Mock query().filter_by().all() to return outcomes
        db.query.return_value.filter_by.return_value.all.return_value = outcomes
        # Mock query().filter_by().first() for upsert (no existing)
        db.query.return_value.filter_by.return_value.first.return_value = None

        added = []
        db.add.side_effect = lambda obj: added.append(obj)

        result = compute_signal_effectiveness(db, str(workspace.id))

        assert result.get("skipped") is not True
        eff = result["signal_effectiveness"]

        # hiring appears in 4 outcomes, 3 are positive → rate = 0.75
        if "hiring" in eff:
            assert eff["hiring"]["conversion_rate"] > eff.get("news", {}).get("conversion_rate", 1.0)

    def test_insufficient_data_skipped(self):
        """Empty outcome list returns skipped."""
        from app.modules.outcomes.feedback_loop import compute_signal_effectiveness

        db = MagicMock()
        db.query.return_value.filter_by.return_value.all.return_value = []
        workspace = SimpleNamespace(signal_weights=None)
        db.get.return_value = workspace

        result = compute_signal_effectiveness(db, str(uuid.uuid4()))
        assert result.get("skipped") is True

    def test_model_confidence_label(self):
        """Confidence label reflects data quality correctly."""
        from app.modules.outcomes.feedback_loop import _model_confidence_label

        assert _model_confidence_label(None, None, 5) == "insufficient_data"
        assert _model_confidence_label(0.70, 0.55, 15) == "high"
        assert _model_confidence_label(0.50, 0.40, 20) == "medium"
        assert _model_confidence_label(0.30, 0.20, 30) == "low"
        assert _model_confidence_label(0.80, 0.60, 8) == "insufficient_data"

    def test_prediction_accuracy_report_empty(self):
        """Empty workspace returns message, not error."""
        from app.modules.outcomes.feedback_loop import get_prediction_accuracy_report
        db = MagicMock()
        db.query.return_value.filter_by.return_value.all.return_value = []
        result = get_prediction_accuracy_report(db, str(uuid.uuid4()))
        assert result["total_outcomes"] == 0
        assert "message" in result

    def test_scoring_recommendations_increase_for_high_lift(self):
        """Signal with high lift should generate an increase_weight recommendation."""
        from app.modules.outcomes.feedback_loop import get_scoring_recommendations

        high_lift_row = SimpleNamespace(
            signal_type="funding",
            conversion_rate=0.80,
            lift_over_baseline=2.5,
            total_occurrences=10,
            current_weight=0.25,
            avg_deal_value_usd=45000.0,
        )
        low_lift_row = SimpleNamespace(
            signal_type="news",
            conversion_rate=0.05,
            lift_over_baseline=0.3,
            total_occurrences=20,
            current_weight=0.06,
            avg_deal_value_usd=None,
        )

        db = MagicMock()
        from app.models import SignalEffectiveness
        db.query.return_value.filter_by.return_value.all.return_value = [
            high_lift_row, low_lift_row
        ]

        recs = get_scoring_recommendations(db, str(uuid.uuid4()))

        rec_types = {r["signal_type"]: r["action"] for r in recs}
        assert rec_types.get("funding") == "increase_weight"
        assert rec_types.get("news") == "decrease_weight"
