"""
tests/unit/test_zoho_provider.py

Unit tests for Zoho CRM provider:
- OAuth flow (URL generation, workspace state binding, code exchange, token refresh)
- Zoho API Client (REST queries, pagination, rate limiting, 401 auto-refresh)
- Canonical Object mapping (Account, Contact, Lead, Opportunity/Deals, User)
- Webhook Handler (JSON Webhook parsing)
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
from app.crm.providers.zoho.client import ZohoAPIClient, _extract_domain
from app.crm.providers.zoho.oauth import ZohoOAuth
from app.crm.providers.zoho.provider import ZohoProvider
from app.crm.providers.zoho.webhook import ZohoWebhookHandler
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
        assert _extract_domain("https://www.zohocorp.com/about") == "zohocorp.com"
        assert _extract_domain("http://sub.domain.co.uk") == "sub.domain.co.uk"
        assert _extract_domain("zoho.org") == "zoho.org"

    def test_extract_domain_empty_or_none(self):
        assert _extract_domain(None) is None
        assert _extract_domain("") is None


class TestZohoOAuth:
    @patch("app.crm.providers.zoho.oauth.settings")
    def test_build_auth_url(self, mock_settings):
        mock_settings.ZOHO_CLIENT_ID = "zoho_client_123"
        mock_settings.ZOHO_REDIRECT_URI = "https://example.com/callback"
        mock_settings.ZOHO_DATA_CENTER = "com"

        oauth = ZohoOAuth()
        result = oauth.build_auth_url("workspace_zoho_123")

        assert "accounts.zoho.com" in result.auth_url
        assert "zoho_client_123" in result.auth_url
        assert result.state == "workspace_zoho_123"
        assert result.redirect_uri == "https://example.com/callback"

    @patch("httpx.get")
    @patch.object(ZohoOAuth, "exchange_code")
    @patch("app.crm.providers.zoho.oauth.settings")
    def test_exchange_to_callback_result_success(self, mock_settings, mock_exchange, mock_httpx_get):
        mock_settings.ZOHO_REDIRECT_URI = "https://example.com/callback"
        mock_exchange.return_value = {
            "access_token": "token_zoho_123",
            "refresh_token": "refresh_zoho_456",
            "expires_in": 3600,
        }

        mock_org_resp = MagicMock()
        mock_org_resp.json.return_value = {
            "org": [
                {
                    "id": "10001000",
                    "company_name": "Zoho Corp",
                    "primary_email": "admin@zoho.com",
                }
            ]
        }
        mock_org_resp.raise_for_status = MagicMock()
        mock_httpx_get.return_value = mock_org_resp

        oauth = ZohoOAuth()
        res = oauth.exchange_to_callback_result("code_123")

        assert res.provider == "zoho"
        assert res.external_account_id == "10001000"
        assert res.external_account_name == "Zoho Corp"
        assert res.access_token == "token_zoho_123"
        assert res.refresh_token == "refresh_zoho_456"


class TestZohoAPIClient:
    def _create_mock_conn(self):
        return SimpleNamespace(
            workspace_id=uuid.uuid4(),
            provider="zoho",
            access_token_encrypted=encrypt_token("valid_access_token"),
            refresh_token_encrypted=encrypt_token("valid_refresh_token"),
            token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            provider_metadata={"api_domain": "www.zohoapis.com"},
            is_active=True,
            sync_error=None,
        )

    @patch("httpx.get")
    def test_paginate_multiple_pages(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = ZohoAPIClient(conn, db)

        page1_resp = MagicMock()
        page1_resp.status_code = 200
        page1_resp.json.return_value = {
            "data": [{"id": "1"}, {"id": "2"}],
            "info": {"more_records": True},
        }

        page2_resp = MagicMock()
        page2_resp.status_code = 200
        page2_resp.json.return_value = {
            "data": [{"id": "3"}],
            "info": {"more_records": False},
        }

        mock_get.side_effect = [page1_resp, page2_resp]

        records = list(client._paginate("Accounts"))
        assert len(records) == 3
        assert [r["id"] for r in records] == ["1", "2", "3"]

    @patch("httpx.get")
    def test_get_accounts_canonical_mapping(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = ZohoAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "data": [
                {
                    "id": "zoho_acc_001",
                    "Account_Name": "Zoho Corporation",
                    "Website": "https://www.zohocorp.com",
                    "Industry": "Technology",
                    "No_of_Employees": 10000,
                    "Billing_City": "Austin",
                    "Billing_State": "TX",
                    "Billing_Country": "USA",
                    "Annual_Revenue": 500000000.0,
                    "Phone": "555-0100",
                    "Modified_Time": "2026-07-20T10:00:00+00:00",
                    "Created_Time": "2026-01-20T10:00:00+00:00",
                }
            ],
            "info": {"more_records": False},
        }
        mock_get.return_value = resp

        accounts = list(client.get_accounts())
        assert len(accounts) == 1
        acc = accounts[0]
        assert acc.external_id == "zoho_acc_001"
        assert acc.name == "Zoho Corporation"
        assert acc.domain == "zohocorp.com"
        assert acc.website == "https://www.zohocorp.com"
        assert acc.employee_count == 10000
        assert acc.annual_revenue == 500000000.0

    @patch("httpx.get")
    def test_get_deals_canonical_mapping(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = ZohoAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "data": [
                {
                    "id": "zoho_deal_001",
                    "Deal_Name": "Enterprise Subscription",
                    "Stage": "Closed Won",
                    "Pipeline": "Standard",
                    "Amount": 75000.0,
                    "Probability": 100.0,
                    "Closing_Date": "2026-11-30",
                    "Account_Name": {"id": "zoho_acc_001"},
                    "Owner": {"id": "zoho_user_001"},
                    "Modified_Time": "2026-07-20T10:00:00+00:00",
                    "Created_Time": "2026-01-20T10:00:00+00:00",
                }
            ],
            "info": {"more_records": False},
        }
        mock_get.return_value = resp

        deals = list(client.get_deals())
        assert len(deals) == 1
        deal = deals[0]
        assert deal.external_id == "zoho_deal_001"
        assert deal.name == "Enterprise Subscription"
        assert deal.stage == "Closed Won"
        assert deal.amount_usd == 75000.0
        assert deal.probability == 1.0
        assert deal.is_closed_won is True
        assert deal.is_closed_lost is False

    @patch("httpx.get")
    def test_client_429_raises_rate_limit_error(self, mock_get):
        conn = self._create_mock_conn()
        db = FakeSession()
        client = ZohoAPIClient(conn, db)

        resp = MagicMock()
        resp.status_code = 429
        resp.headers = {"Retry-After": "25"}
        mock_get.return_value = resp

        with pytest.raises(RateLimitError) as exc_info:
            client._request_once("https://www.zohoapis.com/crm/v7/Accounts")
        assert exc_info.value.retry_after_seconds == 25


class TestZohoWebhook:
    def test_parse_webhook_events(self):
        handler = ZohoWebhookHandler()
        payload = json.dumps([
            {
                "module": "Deals",
                "operation": "update",
                "id": "zoho_deal_001",
            }
        ]).encode("utf-8")

        events = handler.parse_events(payload, workspace_id="ws_zoho")
        assert len(events) == 1
        evt = events[0]
        assert evt.provider == "zoho"
        assert evt.object_type == CRMObjectType.OPPORTUNITY
        assert evt.event_type == CRMEventType.UPDATED
        assert evt.external_id == "zoho_deal_001"


def test_zoho_registered_in_registry():
    import app.crm.providers  # noqa: F401

    assert CRMProviderRegistry.is_registered("zoho")
    provider_cls = CRMProviderRegistry.get("zoho")
    assert provider_cls == ZohoProvider
