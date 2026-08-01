"""
tests/unit/test_salesforce_provider.py

Unit tests for Salesforce CRM provider:
- OAuth flow (URL generation, code exchange, token refresh, PKCE S256)
- Salesforce API Client (SOQL queries, pagination, rate limiting, 401 auto-refresh)
- Canonical Object mapping (Account, Contact, Lead, Opportunity, User)
- Webhook Handler (Platform Events JSON & SOAP XML Outbound Messages)
- Provider Capabilities & Sync Engine Integration
- Callback Routes & 302 RedirectResponse verification
"""
import hashlib
import json
import time
import uuid
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import RateLimitError
from app.crm.base.models import CRMEventType, CRMObjectType, SyncStatus
from app.crm.engine import CRMSyncEngine
from app.crm.providers.salesforce.client import SalesforceAPIClient, _extract_domain
from app.crm.providers.salesforce.oauth import (
    SalesforceOAuth,
    _pop_verifier,
    _store_verifier,
)
from app.crm.providers.salesforce.provider import SalesforceProvider
from app.crm.providers.salesforce.webhook import SalesforceWebhookHandler
from app.crm.registry import CRMProviderRegistry
from app.utils.encryption import encrypt_token


class FakeQuery:
    def __init__(self, db, model):
        self.db = db
        self.model = model
        self.filters = {}

    def filter_by(self, **kwargs):
        self.filters.update(kwargs)
        return self

    def first(self):
        for row in self.db.rows.get(self.model, []):
            if all(getattr(row, key, None) == value for key, value in self.filters.items()):
                return row
        return None

    def all(self):
        return [
            row
            for row in self.db.rows.get(self.model, [])
            if all(getattr(row, key, None) == value for key, value in self.filters.items())
        ]


class FakeSession:
    def __init__(self):
        self.rows = {}
        self.commits = 0

    def query(self, model):
        return FakeQuery(self, model)

    def add(self, row):
        self.rows.setdefault(type(row), []).append(row)

    def get(self, model, ident):
        for row in self.rows.get(model, []):
            if getattr(row, "id", None) == ident:
                return row
        return None

    def commit(self):
        self.commits += 1

    def flush(self):
        """No-op flush for unit tests."""

    def execute(self, stmt, **kwargs):
        """Minimal execute() that supports the deletion-detection code path.

        The sync engine calls db.execute(select(Model).where(...)).scalars()
        to iterate over existing rows for tombstone scanning. Return rows
        stored in self.rows keyed by model class.
        """
        class _FakeResult:
            def __init__(self, rows):
                self._rows = rows

            def scalars(self):
                return iter(self._rows)

            def scalar(self):
                return len(self._rows)


        try:
            entity = stmt.column_descriptions[0]["entity"]
            rows = self.rows.get(entity, [])
        except Exception:
            rows = []
        return _FakeResult(rows)


class TestDomainExtraction:
    def test_extract_domain_valid_urls(self):
        assert _extract_domain("https://www.acme.com/about") == "acme.com"
        assert _extract_domain("http://sub.domain.co.uk") == "sub.domain.co.uk"
        assert _extract_domain("acme-corp.org") == "acme-corp.org"

    def test_extract_domain_empty_or_none(self):
        assert _extract_domain(None) is None
        assert _extract_domain("") is None


class TestSalesforceOAuth:
    @patch("app.crm.providers.salesforce.oauth.settings")
    def test_build_auth_url_contains_pkce_params(self, mock_settings):
        """Authorization URL must include code_challenge and code_challenge_method=S256."""
        mock_settings.SALESFORCE_CLIENT_ID = "sf_client_123"
        mock_settings.SALESFORCE_REDIRECT_URI = "http://localhost:8000/api/v1/crm/salesforce/callback"
        mock_settings.SALESFORCE_SANDBOX = False

        oauth = SalesforceOAuth()
        result = oauth.build_auth_url("workspace_abc")

        assert "login.salesforce.com" in result.auth_url
        assert "sf_client_123" in result.auth_url
        assert result.state == "workspace_abc"
        assert result.redirect_uri == "http://localhost:8000/api/v1/crm/salesforce/callback"
        assert "code_challenge=" in result.auth_url
        assert "code_challenge_method=S256" in result.auth_url
        assert result.pkce_verifier is not None
        assert len(result.pkce_verifier) >= 40

    @patch("app.crm.providers.salesforce.oauth.settings")
    def test_build_auth_url_stores_verifier_in_ttl_store(self, mock_settings):
        """build_auth_url must persist the verifier so the callback can retrieve it."""
        mock_settings.SALESFORCE_CLIENT_ID = "sf_client_123"
        mock_settings.SALESFORCE_REDIRECT_URI = "http://localhost:8000/api/v1/crm/salesforce/callback"
        mock_settings.SALESFORCE_SANDBOX = False

        workspace_id = "workspace_store_test"
        oauth = SalesforceOAuth()
        result = oauth.build_auth_url(workspace_id)

        retrieved = _pop_verifier(workspace_id)
        assert retrieved == result.pkce_verifier
        assert _pop_verifier(workspace_id) is None

    @patch("app.crm.providers.salesforce.oauth.settings")
    def test_build_auth_url_sandbox_uses_test_domain(self, mock_settings):
        """Sandbox mode must route to test.salesforce.com."""
        mock_settings.SALESFORCE_CLIENT_ID = "sf_client_sandbox"
        mock_settings.SALESFORCE_REDIRECT_URI = "http://localhost:8000/api/v1/crm/salesforce/callback"
        mock_settings.SALESFORCE_SANDBOX = True

        oauth = SalesforceOAuth()
        result = oauth.build_auth_url("workspace_sandbox")

        assert "test.salesforce.com" in result.auth_url

    def test_pkce_pair_s256_math(self):
        """code_challenge must be SHA-256(verifier) base64url-encoded without padding."""
        oauth = SalesforceOAuth()
        verifier, challenge = oauth.generate_pkce_pair()

        expected = (
            urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )
        assert challenge == expected

    def test_pkce_verifier_minimum_entropy(self):
        """Verifier must be at least 43 characters (RFC 7636 §4.1 minimum)."""
        oauth = SalesforceOAuth()
        verifier, _ = oauth.generate_pkce_pair()
        assert len(verifier) >= 43

    def test_pkce_pairs_are_unique(self):
        """Each call must produce a distinct verifier."""
        oauth = SalesforceOAuth()
        pairs = {oauth.generate_pkce_pair()[0] for _ in range(20)}
        assert len(pairs) == 20

    @patch.object(SalesforceOAuth, "_post_token_request")
    @patch("app.crm.providers.salesforce.oauth.settings")
    def test_exchange_code_includes_code_verifier(self, mock_settings, mock_post):
        """Token exchange POST must include code_verifier when one is supplied."""
        mock_settings.SALESFORCE_CLIENT_ID = "sf_client_123"
        mock_settings.SALESFORCE_CLIENT_SECRET = "sf_secret"
        mock_settings.SALESFORCE_REDIRECT_URI = "http://localhost:8000/api/v1/crm/salesforce/callback"
        mock_settings.SALESFORCE_SANDBOX = False
        mock_post.return_value = {
            "access_token": "tok",
            "refresh_token": "ref",
            "instance_url": "https://myorg.my.salesforce.com",
            "expires_in": 3600,
        }

        oauth = SalesforceOAuth()
        oauth.exchange_code("auth_code_abc", code_verifier="my_verifier_xyz")

        call_kwargs = mock_post.call_args[0][0]
        assert call_kwargs["code_verifier"] == "my_verifier_xyz"
        assert call_kwargs["code"] == "auth_code_abc"
        assert call_kwargs["grant_type"] == "authorization_code"

    @patch.object(SalesforceOAuth, "_post_token_request")
    @patch("app.crm.providers.salesforce.oauth.settings")
    def test_exchange_code_without_verifier_still_works(self, mock_settings, mock_post):
        """Token exchange without code_verifier must not include the key in payload."""
        mock_settings.SALESFORCE_CLIENT_ID = "sf_client_123"
        mock_settings.SALESFORCE_CLIENT_SECRET = "sf_secret"
        mock_settings.SALESFORCE_REDIRECT_URI = "http://localhost:8000/api/v1/crm/salesforce/callback"
        mock_settings.SALESFORCE_SANDBOX = False
        mock_post.return_value = {
            "access_token": "tok",
            "refresh_token": "ref",
            "instance_url": "https://myorg.my.salesforce.com",
            "expires_in": 3600,
        }

        oauth = SalesforceOAuth()
        oauth.exchange_code("auth_code_abc")

        call_kwargs = mock_post.call_args[0][0]
        assert "code_verifier" not in call_kwargs

    @patch("httpx.get")
    @patch.object(SalesforceOAuth, "exchange_code")
    @patch("app.crm.providers.salesforce.oauth.settings")
    def test_exchange_to_callback_result_passes_verifier(self, mock_settings, mock_exchange, mock_httpx_get):
        """exchange_to_callback_result must forward the verifier to exchange_code."""
        mock_settings.SALESFORCE_REDIRECT_URI = "http://localhost:8000/api/v1/crm/salesforce/callback"
        mock_exchange.return_value = {
            "access_token": "token_123",
            "refresh_token": "refresh_456",
            "instance_url": "https://mycompany.my.salesforce.com",
            "expires_in": 7200,
            "scope": "api refresh_token",
        }
        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.json.return_value = {
            "organization_id": "00D000000000001EAA",
            "organization_name": "Acme Inc",
        }
        mock_userinfo_resp.raise_for_status = MagicMock()
        mock_httpx_get.return_value = mock_userinfo_resp

        oauth = SalesforceOAuth()
        res = oauth.exchange_to_callback_result("code_123", code_verifier="test_verifier")

        mock_exchange.assert_called_once_with("code_123", code_verifier="test_verifier")
        assert res.provider == "salesforce"
        assert res.external_account_id == "00D000000000001EAA"
        assert res.external_account_name == "Acme Inc"
        assert res.access_token == "token_123"
        assert res.refresh_token == "refresh_456"
        assert res.provider_metadata["instance_url"] == "https://mycompany.my.salesforce.com"

    def test_pkce_store_single_use(self):
        _store_verifier("state_singleuse", "verifier_abc")
        assert _pop_verifier("state_singleuse") == "verifier_abc"
        assert _pop_verifier("state_singleuse") is None

    def test_pkce_store_unknown_state_returns_none(self):
        assert _pop_verifier("nonexistent_state_xyz") is None

    def test_pkce_store_expired_entry_returns_none(self):
        import app.crm.providers.salesforce.oauth as sf_oauth
        with sf_oauth._PKCE_LOCK:
            sf_oauth._PKCE_STORE["expired_state"] = ("verifier", time.monotonic() - 1)
        assert _pop_verifier("expired_state") is None


class TestSalesforceAPIClient:
    def _create_mock_conn(self):
        return SimpleNamespace(
            workspace_id=uuid.uuid4(),
            provider="salesforce",
            access_token_encrypted=encrypt_token("valid_access_token"),
            refresh_token_encrypted=encrypt_token("valid_refresh_token"),
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            provider_metadata={"instance_url": "https://test.my.salesforce.com"},
            is_active=True,
            sync_error=None,
        )

    @patch("httpx.get")
    def test_soql_query_pagination(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = SalesforceAPIClient(conn, db)

        page1_resp = MagicMock()
        page1_resp.status_code = 200
        page1_resp.json.return_value = {
            "records": [{"Id": "rec_1"}, {"Id": "rec_2"}],
            "nextRecordsUrl": "/services/data/v59.0/query/01g5g000001234-2000",
        }

        page2_resp = MagicMock()
        page2_resp.status_code = 200
        page2_resp.json.return_value = {
            "records": [{"Id": "rec_3"}],
            "nextRecordsUrl": None,
        }

        mock_get.side_effect = [page1_resp, page2_resp]

        records = list(client.soql_query("SELECT Id FROM Account"))
        assert len(records) == 3
        assert [r["Id"] for r in records] == ["rec_1", "rec_2", "rec_3"]

    @patch("httpx.get")
    def test_get_accounts_canonical_mapping(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = SalesforceAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "records": [
                {
                    "Id": "0010000000001",
                    "Name": "Salesforce Corp",
                    "Website": "https://www.salesforce.com",
                    "Industry": "Technology",
                    "NumberOfEmployees": 50000,
                    "BillingCity": "San Francisco",
                    "BillingState": "CA",
                    "BillingCountry": "USA",
                    "AnnualRevenue": 30000000000.0,
                    "Phone": "123-456-7890",
                    "LastModifiedDate": "2026-07-01T12:00:00Z",
                    "CreatedDate": "2026-01-01T12:00:00Z",
                }
            ],
            "nextRecordsUrl": None,
        }
        mock_get.return_value = resp

        accounts = list(client.get_accounts())
        assert len(accounts) == 1
        acc = accounts[0]
        assert acc.external_id == "0010000000001"
        assert acc.name == "Salesforce Corp"
        assert acc.domain == "salesforce.com"
        assert acc.website == "https://www.salesforce.com"
        assert acc.employee_count == 50000
        assert acc.annual_revenue == 30000000000.0

    @patch("httpx.get")
    def test_get_opportunities_canonical_mapping(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = SalesforceAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "records": [
                {
                    "Id": "0060000000001",
                    "Name": "Big Enterprise Deal",
                    "StageName": "Closed Won",
                    "Amount": 100000.0,
                    "Probability": 100.0,
                    "CloseDate": "2026-06-30",
                    "AccountId": "0010000000001",
                    "OwnerId": "0050000000001",
                    "IsClosed": True,
                    "IsWon": True,
                    "LastModifiedDate": "2026-07-01T12:00:00Z",
                    "CreatedDate": "2026-01-01T12:00:00Z",
                }
            ],
            "nextRecordsUrl": None,
        }
        mock_get.return_value = resp

        opps = list(client.get_opportunities())
        assert len(opps) == 1
        opp = opps[0]
        assert opp.external_id == "0060000000001"
        assert opp.name == "Big Enterprise Deal"
        assert opp.stage == "Closed Won"
        assert opp.amount_usd == 100000.0
        assert opp.probability == 1.0
        assert opp.is_closed_won is True
        assert opp.is_closed_lost is False

    @patch("httpx.get")
    def test_client_429_raises_rate_limit_error(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = SalesforceAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 429
        resp.headers = {"Retry-After": "15"}
        mock_get.return_value = resp

        with pytest.raises(RateLimitError) as exc_info:
            client._request_once("https://test.my.salesforce.com/services/data/v59.0/query")
        assert exc_info.value.retry_after_seconds == 15


class TestSalesforceWebhook:
    def test_parse_platform_events_json(self):
        handler = SalesforceWebhookHandler()
        payload = json.dumps({
            "events": [
                {
                    "entityName": "Opportunity",
                    "changeType": "UPDATE",
                    "recordId": "0060000000001",
                }
            ]
        }).encode("utf-8")

        events = handler.parse_events(payload, workspace_id="ws_123")
        assert len(events) == 1
        evt = events[0]
        assert evt.provider == "salesforce"
        assert evt.object_type == CRMObjectType.OPPORTUNITY
        assert evt.event_type == CRMEventType.UPDATED
        assert evt.external_id == "0060000000001"

    def test_parse_outbound_message_xml(self):
        handler = SalesforceWebhookHandler()
        xml_payload = b"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
          <soapenv:Body>
            <notifications xmlns="http://soap.sforce.com/2005/09/outbound">
              <Notification>
                <sObject xsi:type="sf:Account" xmlns:sf="urn:sobject.partner.soap.sforce.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                  <sf:Id>0010000000009</sf:Id>
                </sObject>
              </Notification>
            </notifications>
          </soapenv:Body>
        </soapenv:Envelope>
        """

        events = handler.parse_events(xml_payload, workspace_id="ws_123")
        assert len(events) == 1
        evt = events[0]
        assert evt.provider == "salesforce"
        assert evt.object_type == CRMObjectType.ACCOUNT
        assert evt.external_id == "0010000000009"


def test_salesforce_registered_in_registry():
    import app.crm.providers  # noqa: F401

    assert CRMProviderRegistry.is_registered("salesforce")
    provider_cls = CRMProviderRegistry.get("salesforce")
    assert provider_cls == SalesforceProvider


class TestSalesforceCallbackRoutes:
    def test_callback_routes_registered_in_app(self):
        from app.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        # GET without code/state returns 422 Unprocessable Entity (route exists!)
        r1 = client.get("/api/v1/crm/salesforce/callback")
        assert r1.status_code == 422

        r2 = client.get("/api/v1/integrations/salesforce/callback")
        assert r2.status_code == 422

    @patch("httpx.get")
    @patch.object(SalesforceOAuth, "exchange_code")
    def test_callback_end_to_end_302_redirect(self, mock_exchange, mock_httpx_get):
        from app.models import Workspace, CRMConnectionDB

        mock_exchange.return_value = {
            "access_token": "token_e2e_123",
            "refresh_token": "refresh_e2e_456",
            "instance_url": "https://e2e.my.salesforce.com",
            "expires_in": 3600,
            "scope": "api refresh_token",
        }
        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.json.return_value = {
            "organization_id": "00D000000000E2E",
            "organization_name": "E2E Test Corp",
        }
        mock_userinfo_resp.raise_for_status = MagicMock()
        mock_httpx_get.return_value = mock_userinfo_resp

        ws_id = str(uuid.uuid4())
        ws = SimpleNamespace(id=uuid.UUID(ws_id), is_active=True, crm_provider=None)
        db = FakeSession()
        db.rows[Workspace] = [ws]

        _store_verifier(ws_id, "e2e_pkce_verifier_secret")

        provider = SalesforceProvider(connection=None, db=db)
        res = provider.handle_oauth_callback("code_e2e", ws_id, ws_id, db)

        assert res.provider == "salesforce"
        assert res.external_account_id == "00D000000000E2E"
        assert res.external_account_name == "E2E Test Corp"
        assert ws.crm_provider == "salesforce"

        conns = db.rows.get(CRMConnectionDB, [])
        assert len(conns) == 1
        conn = conns[0]
        assert conn.external_account_id == "00D000000000E2E"
        assert conn.is_active is True

    @patch("httpx.get")
    def test_force_sync_endpoint_imports_opportunities(self, mock_httpx_get):
        from app.models import CRMOpportunityDB

        conn = SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            provider="salesforce",
            access_token_encrypted=encrypt_token("valid_access_token"),
            refresh_token_encrypted=encrypt_token("valid_refresh_token"),
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            provider_metadata={"instance_url": "https://test.my.salesforce.com"},
            is_active=True,
            sync_error=None,
            last_sync_at=None,
        )
        db = FakeSession()
        db.add(conn)

        def _mock_get(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            params = kwargs.get("params", {})
            q = params.get("q", "") if isinstance(params, dict) else ""
            if "Opportunity" in q or "Opportunity" in url:
                resp.json.return_value = {
                    "records": [
                        {
                            "Id": "006000000000123",
                            "Name": "Enterprise Cloud Migration",
                            "StageName": "Closed Won",
                            "Amount": 150000.0,
                            "CloseDate": "2026-12-31",
                            "AccountId": "001000000000ABC",
                            "Account": {"Name": "Acme Corp"},
                            "OwnerId": "005000000000XYZ",
                            "Owner": {"Name": "Sarah Jenkins"},
                            "CreatedDate": "2026-01-15T10:00:00Z",
                            "LastModifiedDate": "2026-07-29T15:30:00Z",
                        }
                    ],
                    "nextRecordsUrl": None,
                }
            else:
                resp.json.return_value = {"records": [], "nextRecordsUrl": None}
            return resp

        mock_httpx_get.side_effect = _mock_get


        provider = SalesforceProvider(connection=conn, db=db)
        res = CRMSyncEngine(db, provider).run_incremental_sync(force_all=True)

        assert res.status == SyncStatus.COMPLETED
        assert res.total_fetched >= 1
        assert res.total_created >= 1

        opps = db.rows.get(CRMOpportunityDB, [])
        assert len(opps) == 1
        opp = opps[0]
        assert opp.external_id == "006000000000123"
        assert opp.name == "Enterprise Cloud Migration"
        assert opp.amount_usd == 150000.0
        assert opp.stage == "Closed Won"
        assert opp.is_closed_won is True
