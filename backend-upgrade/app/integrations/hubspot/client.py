"""
app/integrations/hubspot/client.py

Authenticated HubSpot CRM API client.
Handles token refresh, rate limiting, and pagination automatically.
Used by all sync operations — never call httpx directly from sync code.

All methods raise ExternalServiceError on unrecoverable failures.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Generator

import httpx
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, RateLimitError
from app.core.logging import get_logger
from app.models import HubSpotConnection
from app.utils.encryption import decrypt_token, encrypt_token, is_fernet_token, migrate_legacy_token

logger = get_logger(__name__)

HUBSPOT_API_BASE = "https://api.hubapi.com"
HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

# HubSpot rate limit: 100 requests/10 seconds (burst), 150/second (sustained)
# We stay conservative
_DEFAULT_TIMEOUT = 20.0
_PAGE_SIZE = 100  # max per HubSpot page


class HubSpotClient:
    """
    Authenticated HubSpot API client for one workspace connection.
    Automatically refreshes tokens when needed.
    Thread-safe: creates a new httpx client per call batch.
    """

    def __init__(self, conn: HubSpotConnection, db: Session):
        self.conn = conn
        self.db = db
        self._access_token: str | None = None

    # ── Token management ─────────────────────────────────────

    def _get_token(self) -> str:
        """
        Return valid access token.
        Refreshes automatically if within 5 minutes of expiry.
        Migrates legacy XOR tokens to Fernet on first use.
        """
        # Migrate legacy tokens transparently
        if not is_fernet_token(self.conn.access_token_encrypted):
            logger.info(
                "migrating_legacy_token",
                workspace_id=str(self.conn.workspace_id),
            )
            self.conn.access_token_encrypted = migrate_legacy_token(
                self.conn.access_token_encrypted, settings.APP_SECRET_KEY
            )
            self.conn.refresh_token_encrypted = migrate_legacy_token(
                self.conn.refresh_token_encrypted, settings.APP_SECRET_KEY
            )
            self.db.commit()

        now = datetime.now(timezone.utc)
        expires = self.conn.token_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        if expires - now < timedelta(minutes=5):
            self._refresh_token()

        return decrypt_token(self.conn.access_token_encrypted)

    def _refresh_token(self) -> None:
        """Exchange refresh token for new access + refresh tokens."""
        logger.info(
            "refreshing_hubspot_token",
            workspace_id=str(self.conn.workspace_id),
        )

        try:
            resp = httpx.post(
                HUBSPOT_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.HUBSPOT_APP_CLIENT_ID,
                    "client_secret": settings.HUBSPOT_APP_CLIENT_SECRET,
                    "refresh_token": decrypt_token(
                        self.conn.refresh_token_encrypted
                    ),
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            self.conn.access_token_encrypted = encrypt_token(data["access_token"])
            self.conn.refresh_token_encrypted = encrypt_token(data["refresh_token"])
            self.conn.token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=data.get("expires_in", 1800)
            )
            self.db.commit()

            logger.info(
                "token_refreshed",
                workspace_id=str(self.conn.workspace_id),
            )

        except httpx.HTTPStatusError as e:
            print("========== HUBSPOT REFRESH ERROR ==========")
            print(e.response.status_code)
            print(e.response.text)
            print("===========================================")

            logger.error(
                "hubspot_refresh_failed",
                status=e.response.status_code,
                body=e.response.text,
            )

            if e.response.status_code in (401, 403):
                self.conn.is_active = False
                self.conn.sync_error = e.response.text
                self.db.commit()

            raise

        except Exception as e:
            raise ExternalServiceError(
                "HubSpot",
                f"Token refresh error: {e}",
            ) from e

    # ── HTTP helpers ─────────────────────────────────────────

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
    )
    def _get(self, path: str, params: dict | None = None) -> dict:
        """GET with automatic retry on transient errors."""
        try:
            resp = httpx.get(
                f"{HUBSPOT_API_BASE}{path}",
                params=params or {},
                headers=self._headers(),
                timeout=_DEFAULT_TIMEOUT,
            )
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 10))
                raise RateLimitError("HubSpot", retry_after_seconds=retry_after)
            resp.raise_for_status()
            return resp.json()
        except RateLimitError:
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500:
                raise ExternalServiceError("HubSpot", f"HTTP {e.response.status_code}: {e.response.text[:200]}")
            raise  # 5xx — let tenacity retry

    @retry(
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
    )
    def _post(self, path: str, json_body: dict) -> dict:
        try:
            resp = httpx.post(
                f"{HUBSPOT_API_BASE}{path}",
                json=json_body,
                headers=self._headers(),
                timeout=_DEFAULT_TIMEOUT,
            )
            if resp.status_code == 429:
                raise RateLimitError("HubSpot", retry_after_seconds=10)
            resp.raise_for_status()
            return resp.json()
        except RateLimitError:
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500:
                raise ExternalServiceError("HubSpot", f"HTTP {e.response.status_code}: {e.response.text[:200]}")
            raise

    # ── Pagination helper ─────────────────────────────────────

    def _paginate(
        self,
        path: str,
        params: dict | None = None,
        results_key: str = "results",
    ) -> Generator[dict, None, None]:
        """
        Yield individual records across all pages.
        Handles HubSpot cursor-based pagination automatically.
        """
        base_params = {**(params or {}), "limit": _PAGE_SIZE}
        after = None

        while True:
            if after:
                base_params["after"] = after

            data = self._get(path, params=base_params)
            results = data.get(results_key, [])

            for record in results:
                yield record

            # Check for next page
            paging = data.get("paging", {})
            next_page = paging.get("next", {})
            after = next_page.get("after")

            if not after or not results:
                break

    # ── Portal info ───────────────────────────────────────────

    def get_portal_info(self) -> dict:
        """Get portal ID and domain for the connected account."""
        token = self._get_token()
        resp = httpx.get(
            f"{HUBSPOT_API_BASE}/oauth/v1/access-tokens/{token}",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # ── Companies ─────────────────────────────────────────────

    def get_companies(
        self,
        modified_after: datetime | None = None,
        properties: list[str] | None = None,
    ) -> Generator[dict, None, None]:
        """Yield all (or recently modified) company records."""
        props = properties or [
            "name", "domain", "website", "industry", "numberofemployees",
            "city", "state", "country", "founded_year", "description",
            "annualrevenue", "hs_lastmodifieddate", "createdate",
        ]
        params: dict[str, Any] = {"properties": ",".join(props)}

        if modified_after:
            # Use search API for filtered queries
            yield from self._search_companies_modified_after(modified_after, props)
        else:
            yield from self._paginate("/crm/v3/objects/companies", params)

    def _search_companies_modified_after(
        self, modified_after: datetime, properties: list[str]
    ) -> Generator[dict, None, None]:
        ts_ms = int(modified_after.timestamp() * 1000)
        body = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "hs_lastmodifieddate",
                    "operator": "GTE",
                    "value": str(ts_ms),
                }]
            }],
            "properties": properties,
            "limit": _PAGE_SIZE,
        }
        after = None
        while True:
            if after:
                body["after"] = after
            data = self._post("/crm/v3/objects/companies/search", body)
            for r in data.get("results", []):
                yield r
            paging = data.get("paging", {}).get("next", {})
            after = paging.get("after")
            if not after:
                break

    # ── Contacts ─────────────────────────────────────────────

    def get_contacts(
        self,
        modified_after: datetime | None = None,
        properties: list[str] | None = None,
    ) -> Generator[dict, None, None]:
        """Yield all (or recently modified) contact records."""
        props = properties or [
            "firstname", "lastname", "email", "jobtitle", "company",
            "phone", "linkedinbio", "hs_lastmodifieddate", "createdate",
            "associatedcompanyid",
        ]
        if modified_after:
            yield from self._search_contacts_modified_after(modified_after, props)
        else:
            yield from self._paginate(
                "/crm/v3/objects/contacts",
                params={"properties": ",".join(props)},
            )

    def _search_contacts_modified_after(
        self, modified_after: datetime, properties: list[str]
    ) -> Generator[dict, None, None]:
        ts_ms = int(modified_after.timestamp() * 1000)
        body = {
            "filterGroups": [{"filters": [{
                "propertyName": "lastmodifieddate",
                "operator": "GTE",
                "value": str(ts_ms),
            }]}],
            "properties": properties,
            "limit": _PAGE_SIZE,
        }
        after = None
        while True:
            if after:
                body["after"] = after
            data = self._post("/crm/v3/objects/contacts/search", body)
            for r in data.get("results", []):
                yield r
            after = data.get("paging", {}).get("next", {}).get("after")
            if not after:
                break

    # ── Deals ─────────────────────────────────────────────────

    def get_deals(
        self,
        modified_after: datetime | None = None,
        properties: list[str] | None = None,
        include_associations: bool = True,
    ) -> Generator[dict, None, None]:
        """Yield deal records with company associations."""
        props = properties or [
            "dealname", "amount", "dealstage", "pipeline",
            "closedate", "createdate", "hs_lastmodifieddate",
            "hubspot_owner_id", "hs_deal_stage_probability",
        ]
        if modified_after:
            yield from self._search_deals_modified_after(modified_after, props)
        else:
            params: dict[str, Any] = {
                "properties": ",".join(props),
            }
            if include_associations:
                params["associations"] = "companies,contacts"
            yield from self._paginate("/crm/v3/objects/deals", params)

    def _search_deals_modified_after(
        self, modified_after: datetime, properties: list[str]
    ) -> Generator[dict, None, None]:
        ts_ms = int(modified_after.timestamp() * 1000)
        body = {
            "filterGroups": [{"filters": [{
                "propertyName": "hs_lastmodifieddate",
                "operator": "GTE",
                "value": str(ts_ms),
            }]}],
            "properties": properties,
            "associations": ["companies", "contacts"],
            "limit": _PAGE_SIZE,
        }
        after = None
        while True:
            if after:
                body["after"] = after
            data = self._post("/crm/v3/objects/deals/search", body)
            for r in data.get("results", []):
                yield r
            after = data.get("paging", {}).get("next", {}).get("after")
            if not after:
                break

    def get_deal_by_id(self, deal_id: str) -> dict:
        """Fetch single deal with all associations."""
        return self._get(
            f"/crm/v3/objects/deals/{deal_id}",
            params={
                "properties": "dealname,amount,dealstage,pipeline,closedate,createdate,hubspot_owner_id",
                "associations": "companies,contacts",
            },
        )

    # ── Owners ────────────────────────────────────────────────

    def get_owners(self) -> list[dict]:
        """Fetch all deal owners."""
        data = self._get("/crm/v3/owners", params={"limit": 100})
        return data.get("results", [])

    # ── Pipelines ─────────────────────────────────────────────

    def get_pipelines(self) -> list[dict]:
        """Fetch all deal pipelines with their stages."""
        data = self._get("/crm/v3/pipelines/deals")
        return data.get("results", [])

    # ── Company associations ───────────────────────────────────

    def get_company_domain(self, hubspot_company_id: str) -> str | None:
        """Get domain for a specific company ID."""
        try:
            data = self._get(
                f"/crm/v3/objects/companies/{hubspot_company_id}",
                params={"properties": "domain,website"},
            )
            props = data.get("properties", {})
            return props.get("domain") or props.get("website")
        except Exception:
            return None

    def get_deal_associated_company_ids(self, deal_id: str) -> list[str]:
        """Get company IDs associated with a deal."""
        try:
            data = self._get(f"/crm/v3/associations/deals/companies/batch/read", params={})
            # Simpler: fetch from deal object associations
            deal = self._get(
                f"/crm/v3/objects/deals/{deal_id}",
                params={"associations": "companies"},
            )
            associations = (
                deal.get("associations", {})
                .get("companies", {})
                .get("results", [])
            )
            return [str(a["id"]) for a in associations]
        except Exception:
            return []

    # ── Webhook registration ──────────────────────────────────

    def register_webhook(self, target_url: str) -> str | None:
        """
        Register webhook subscriptions for deal and contact changes.
        Returns webhook subscription ID or None on failure.
        """
        if not settings.HUBSPOT_APP_CLIENT_ID:
            return None

        subscriptions = [
            {"eventType": "deal.propertyChange", "propertyName": "dealstage", "active": True},
            {"eventType": "deal.creation", "active": True},
            {"eventType": "contact.creation", "active": True},
        ]

        created_ids = []
        for sub in subscriptions:
            try:
                resp = httpx.post(
                    f"{HUBSPOT_API_BASE}/webhooks/v3/{settings.HUBSPOT_APP_CLIENT_ID}/subscriptions",
                    json=sub,
                    headers=self._headers(),
                    timeout=15,
                )
                if resp.status_code in (200, 201):
                    sub_id = resp.json().get("id")
                    if sub_id:
                        created_ids.append(str(sub_id))
                    logger.info("webhook_subscription_registered", event_type=sub["eventType"])
                else:
                    logger.warning(
                        "webhook_subscription_failed",
                        event_type=sub["eventType"],
                        status=resp.status_code,
                    )
            except Exception as e:
                logger.warning(
                    "webhook_subscription_error",
                    event_type=sub["eventType"],
                    error=str(e),
                )

        return ",".join(created_ids) if created_ids else None
