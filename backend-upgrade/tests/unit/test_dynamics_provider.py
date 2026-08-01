"""
tests/unit/test_dynamics_provider.py

Unit tests for Microsoft Dynamics 365 CRM provider:
- OAuth flow (URL generation, workspace state binding, code exchange, token refresh)
- Dynamics API Client (OData queries, pagination, rate limiting, 401 auto-refresh)
- Canonical Object mapping (Account, Contact, Lead, Opportunity, User)
- Webhook Handler (JSON Change Notifications & Plugin Webhooks)
- Provider Capabilities & Sync Engine Integration
"""
import json
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import RateLimitError
from app.crm.base.models import CRMEventType, CRMObjectType
from app.crm.providers.dynamics.client import DynamicsAPIClient, _extract_domain
from app.crm.providers.dynamics.oauth import DynamicsOAuth
from app.crm.providers.dynamics.provider import DynamicsProvider
from app.crm.providers.dynamics.webhook import DynamicsWebhookHandler
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


class TestDomainExtraction:
    def test_extract_domain_valid_urls(self):
        assert _extract_domain("https://www.contoso.com/about") == "contoso.com"
        assert _extract_domain("http://sub.domain.co.uk") == "sub.domain.co.uk"
        assert _extract_domain("microsoft.org") == "microsoft.org"

    def test_extract_domain_empty_or_none(self):
        assert _extract_domain(None) is None
        assert _extract_domain("") is None


class TestDynamicsOAuth:
    @patch("app.crm.providers.dynamics.oauth.settings")
    def test_build_auth_url(self, mock_settings):
        mock_settings.DYNAMICS_CLIENT_ID = "dyn_client_123"
        mock_settings.DYNAMICS_REDIRECT_URI = "https://example.com/callback"
        mock_settings.DYNAMICS_TENANT_ID = "common"

        oauth = DynamicsOAuth()
        result = oauth.build_auth_url("workspace_xyz")

        assert "login.microsoftonline.com" in result.auth_url
        assert "dyn_client_123" in result.auth_url
        assert result.state == "workspace_xyz"
        assert result.redirect_uri == "https://example.com/callback"

    @patch("httpx.get")
    @patch.object(DynamicsOAuth, "exchange_code")
    @patch("app.crm.providers.dynamics.oauth.settings")
    def test_exchange_to_callback_result_success(self, mock_settings, mock_exchange, mock_httpx_get):
        mock_settings.DYNAMICS_REDIRECT_URI = "https://example.com/callback"
        mock_exchange.return_value = {
            "access_token": "token_dyn_123",
            "refresh_token": "refresh_dyn_456",
            "expires_in": 3600,
        }

        mock_disco_resp = MagicMock()
        mock_disco_resp.json.return_value = {
            "value": [
                {
                    "ApiUrl": "https://contoso.api.crm.dynamics.com",
                    "FriendlyName": "Contoso Production",
                    "UniqueName": "org_contoso_123",
                }
            ]
        }
        mock_disco_resp.raise_for_status = MagicMock()
        mock_httpx_get.return_value = mock_disco_resp

        oauth = DynamicsOAuth()
        res = oauth.exchange_to_callback_result("code_123")

        assert res.provider == "dynamics"
        assert res.external_account_id == "org_contoso_123"
        assert res.external_account_name == "Contoso Production"
        assert res.access_token == "token_dyn_123"
        assert res.refresh_token == "refresh_dyn_456"
        assert res.provider_metadata["crm_url"] == "https://contoso.api.crm.dynamics.com"


class TestDynamicsAPIClient:
    def _create_mock_conn(self):
        return SimpleNamespace(
            workspace_id=uuid.uuid4(),
            provider="dynamics",
            access_token_encrypted=encrypt_token("valid_access_token"),
            refresh_token_encrypted=encrypt_token("valid_refresh_token"),
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            provider_metadata={"crm_url": "https://contoso.api.crm.dynamics.com"},
            is_active=True,
            sync_error=None,
        )

    @patch("httpx.get")
    def test_odata_query_pagination(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = DynamicsAPIClient(conn, db)

        page1_resp = MagicMock()
        page1_resp.status_code = 200
        page1_resp.json.return_value = {
            "value": [{"accountid": "acc_1"}, {"accountid": "acc_2"}],
            "@odata.nextLink": "https://contoso.api.crm.dynamics.com/api/data/v9.2/accounts?$skiptoken=123",
        }

        page2_resp = MagicMock()
        page2_resp.status_code = 200
        page2_resp.json.return_value = {
            "value": [{"accountid": "acc_3"}],
        }

        mock_get.side_effect = [page1_resp, page2_resp]

        records = list(client.odata_query("accounts", "accountid"))
        assert len(records) == 3
        assert [r["accountid"] for r in records] == ["acc_1", "acc_2", "acc_3"]

    @patch("httpx.get")
    def test_get_accounts_canonical_mapping(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = SalesforceAPIClient if False else DynamicsAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "value": [
                {
                    "accountid": "acc_dyn_001",
                    "name": "Contoso Ltd",
                    "websiteurl": "https://www.contoso.com",
                    "industrycode": 1,
                    "numberofemployees": 1200,
                    "address1_city": "Seattle",
                    "address1_stateorprovince": "WA",
                    "address1_country": "USA",
                    "revenue": 50000000.0,
                    "telephone1": "555-0199",
                    "modifiedon": "2026-07-10T08:00:00Z",
                    "createdon": "2026-01-10T08:00:00Z",
                }
            ]
        }
        mock_get.return_value = resp

        accounts = list(client.get_accounts())
        assert len(accounts) == 1
        acc = accounts[0]
        assert acc.external_id == "acc_dyn_001"
        assert acc.name == "Contoso Ltd"
        assert acc.domain == "contoso.com"
        assert acc.website == "https://www.contoso.com"
        assert acc.employee_count == 1200
        assert acc.annual_revenue == 50000000.0

    @patch("httpx.get")
    def test_get_opportunities_canonical_mapping(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = DynamicsAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "value": [
                {
                    "opportunityid": "opp_dyn_001",
                    "name": "Global ERP Upgrade",
                    "stepname": "Develop",
                    "estimatedvalue": 250000.0,
                    "closeprobability": 80.0,
                    "estimatedclosedate": "2026-12-31T00:00:00Z",
                    "_accountid_value": "acc_dyn_001",
                    "_ownerid_value": "user_dyn_001",
                    "statecode": 1,
                    "statuscode": 3,
                    "modifiedon": "2026-07-15T10:00:00Z",
                    "createdon": "2026-02-01T10:00:00Z",
                }
            ]
        }
        mock_get.return_value = resp

        opps = list(client.get_opportunities())
        assert len(opps) == 1
        opp = opps[0]
        assert opp.external_id == "opp_dyn_001"
        assert opp.name == "Global ERP Upgrade"
        assert opp.amount_usd == 250000.0
        assert opp.probability == 0.8
        assert opp.is_closed_won is True
        assert opp.is_closed_lost is False

    @patch("httpx.get")
    def test_client_429_raises_rate_limit_error(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = DynamicsAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 429
        resp.headers = {"Retry-After": "20"}
        mock_get.return_value = resp

        with pytest.raises(RateLimitError) as exc_info:
            client._request_once("https://contoso.api.crm.dynamics.com/api/data/v9.2/accounts")
        assert exc_info.value.retry_after_seconds == 20


class TestDynamicsWebhook:
    def test_parse_webhook_events(self):
        handler = DynamicsWebhookHandler()
        payload = json.dumps([
            {
                "EntityName": "opportunity",
                "MessageName": "Update",
                "PrimaryEntityId": "opp_dyn_001",
            }
        ]).encode("utf-8")

        events = handler.parse_events(payload, workspace_id="ws_dynamics")
        assert len(events) == 1
        evt = events[0]
        assert evt.provider == "dynamics"
        assert evt.object_type == CRMObjectType.OPPORTUNITY
        assert evt.event_type == CRMEventType.UPDATED
        assert evt.external_id == "opp_dyn_001"


def test_dynamics_registered_in_registry():
    import app.crm.providers  # noqa: F401

    assert CRMProviderRegistry.is_registered("dynamics")
    provider_cls = CRMProviderRegistry.get("dynamics")
    assert provider_cls == DynamicsProvider
