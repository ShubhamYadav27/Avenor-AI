"""app/crm/providers/salesforce/client.py"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Generator

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, RateLimitError
from app.core.logging import get_logger
from app.crm.base.models import CRMAccount, CRMContact, CRMLead, CRMOpportunity, CRMUser
from app.utils.encryption import decrypt_token, encrypt_token, is_fernet_token, migrate_legacy_token

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = get_logger(__name__)
_TIMEOUT = 20.0
_API_VERSION = "v59.0"
_RETRYABLE_HTTP_STATUSES = {500, 502, 503, 504}


def _parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _parse_date(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val).replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        return _parse_dt(val)


def _as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    url_str = url.strip().lower()
    if not url_str.startswith(("http://", "https://")):
        url_str = "http://" + url_str
    try:
        from urllib.parse import urlparse
        netloc = urlparse(url_str).netloc
        domain = netloc.split(":")[0]
        if domain.startswith("www."):
            domain = domain[4:]
        return domain or None
    except Exception:
        return None

def _validate_website(url: str | None) -> str | None:
    if not url:
        return None
    url_str = url.strip().lower()
    
    # Strip broken placeholder domains if any (user requested removing fake websites)
    if "example.com" in url_str or "placeholder" in url_str:
        return None
        
    if not url_str.startswith(("http://", "https://")):
        url_str = "https://" + url_str
        
    # Enforce https if it starts with http
    if url_str.startswith("http://"):
        url_str = "https://" + url_str[7:]
        
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url_str)
        if not parsed.netloc or "." not in parsed.netloc:
            return None
        return url_str
    except Exception:
        return None


class SalesforceAPIClient:
    def __init__(self, connection, db: "Session"):
        self.conn = connection
        self.db = db
        self.instance_url: str = (connection.provider_metadata or {}).get("instance_url", "")
        if not self.instance_url:
            raise ExternalServiceError("Salesforce", "Missing Salesforce instance URL")
        self._base = f"{self.instance_url.rstrip('/')}/services/data/{_API_VERSION}"
        self.request_count = 0

    def _get_token(self) -> str:
        if not is_fernet_token(self.conn.access_token_encrypted):
            self.conn.access_token_encrypted = migrate_legacy_token(
                self.conn.access_token_encrypted,
                settings.APP_SECRET_KEY,
            )
            self.conn.refresh_token_encrypted = migrate_legacy_token(
                self.conn.refresh_token_encrypted,
                settings.APP_SECRET_KEY,
            )
            self.db.commit()

        expires = self.conn.token_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires - datetime.now(timezone.utc) < timedelta(minutes=5):
            self._refresh()
        return decrypt_token(self.conn.access_token_encrypted)

    def _refresh(self) -> None:
        base = "test.salesforce.com" if settings.SALESFORCE_SANDBOX else "login.salesforce.com"
        logger.info("salesforce_refreshing_token", workspace_id=str(self.conn.workspace_id))
        try:
            resp = httpx.post(
                f"https://{base}/services/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.SALESFORCE_CLIENT_ID,
                    "client_secret": settings.SALESFORCE_CLIENT_SECRET,
                    "refresh_token": decrypt_token(self.conn.refresh_token_encrypted),
                },
                timeout=15,
            )
            if resp.status_code in (400, 401, 403):
                self.conn.is_active = False
                self.conn.sync_error = f"Token refresh failed: {resp.status_code}"
                self.db.commit()
            resp.raise_for_status()
            data = resp.json()
            self.conn.access_token_encrypted = encrypt_token(data["access_token"])
            if data.get("refresh_token"):
                self.conn.refresh_token_encrypted = encrypt_token(data["refresh_token"])
            self.conn.token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=data.get("expires_in", 3600),
            )
            if data.get("instance_url"):
                metadata = dict(self.conn.provider_metadata or {})
                metadata["instance_url"] = data["instance_url"]
                self.conn.provider_metadata = metadata
                self.instance_url = data["instance_url"]
                self._base = f"{self.instance_url.rstrip('/')}/services/data/{_API_VERSION}"
            self.conn.sync_error = None
            self.db.commit()
        except Exception as exc:
            raise ExternalServiceError("Salesforce", f"Token refresh failed: {exc}") from exc

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _retry_after_seconds(value: str | None) -> int:
        try:
            return max(int(value or 30), 1)
        except (TypeError, ValueError):
            return 30

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
    )
    def _request_once(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.request_count += 1
        resp = httpx.get(url, params=params or {}, headers=self._headers(), timeout=_TIMEOUT)
        if resp.status_code == 429:
            retry_after = self._retry_after_seconds(resp.headers.get("Retry-After"))
            raise RateLimitError("Salesforce", retry_after_seconds=retry_after)
        if resp.status_code in _RETRYABLE_HTTP_STATUSES:
            resp.raise_for_status()
        if resp.status_code == 401:
            raise ExternalServiceError("Salesforce", "Unauthorized")
        if resp.status_code >= 400:
            raise ExternalServiceError("Salesforce", f"API error {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    def _request_with_refresh(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            return self._request_once(url, params)
        except ExternalServiceError as exc:
            if "Unauthorized" not in exc.message:
                raise
            self._refresh()
            try:
                return self._request_once(url, params)
            except ExternalServiceError as second_exc:
                if "Unauthorized" in second_exc.message:
                    self.conn.is_active = False
                    self.conn.sync_error = "Salesforce authorization failed after token refresh"
                    self.db.commit()
                raise

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request_with_refresh(f"{self._base}{path}", params)

    def soql_query(self, query: str) -> Generator[dict, None, None]:
        data = self._get("/query", {"q": query})
        while True:
            for rec in data.get("records", []):
                yield rec
            next_url = data.get("nextRecordsUrl")
            if not next_url:
                break
            data = self._request_with_refresh(f"{self.instance_url.rstrip('/')}{next_url}")

    def _modified_filter(self, modified_after: datetime | None) -> str:
        if not modified_after:
            return ""
        if modified_after.tzinfo is None:
            modified_after = modified_after.replace(tzinfo=timezone.utc)
        ts = modified_after.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f" WHERE LastModifiedDate >= {ts}"

    def get_accounts(self, modified_after: datetime | None = None) -> Generator[CRMAccount, None, None]:
        query = (
            "SELECT Id, Name, Website, Industry, NumberOfEmployees, "
            "BillingCity, BillingState, BillingCountry, AnnualRevenue, Phone, "
            "LastModifiedDate, CreatedDate FROM Account"
            + self._modified_filter(modified_after)
        )
        for rec in self.soql_query(query):
            website = _validate_website(rec.get("Website"))
            yield CRMAccount(
                external_id=rec["Id"],
                provider="salesforce",
                name=rec.get("Name") or "",
                domain=_extract_domain(website),
                website=website,
                industry=rec.get("Industry"),
                employee_count=_as_int(rec.get("NumberOfEmployees")),
                location_city=rec.get("BillingCity"),
                location_state=rec.get("BillingState"),
                location_country=rec.get("BillingCountry"),
                annual_revenue=_as_float(rec.get("AnnualRevenue")),
                phone=rec.get("Phone"),
                modified_at=_parse_dt(rec.get("LastModifiedDate")),
                created_at=_parse_dt(rec.get("CreatedDate")),
                raw_data=rec,
            )

    def get_contacts(self, modified_after: datetime | None = None) -> Generator[CRMContact, None, None]:
        query = (
            "SELECT Id, FirstName, LastName, Email, Phone, Title, Department, "
            "AccountId, OwnerId, LastModifiedDate, CreatedDate FROM Contact"
            + self._modified_filter(modified_after)
        )
        for rec in self.soql_query(query):
            first_name = rec.get("FirstName") or ""
            last_name = rec.get("LastName") or ""
            yield CRMContact(
                external_id=rec["Id"],
                provider="salesforce",
                first_name=first_name or None,
                last_name=last_name or None,
                full_name=f"{first_name} {last_name}".strip() or None,
                email=rec.get("Email"),
                phone=rec.get("Phone"),
                title=rec.get("Title"),
                department=rec.get("Department"),
                account_external_id=rec.get("AccountId"),
                owner_external_id=rec.get("OwnerId"),
                modified_at=_parse_dt(rec.get("LastModifiedDate")),
                created_at=_parse_dt(rec.get("CreatedDate")),
                raw_data=rec,
            )

    def get_leads(self, modified_after: datetime | None = None) -> Generator[CRMLead, None, None]:
        query = (
            "SELECT Id, FirstName, LastName, Email, Company, Title, Phone, "
            "Status, LeadSource, OwnerId, IsConverted, ConvertedAccountId, "
            "ConvertedContactId, ConvertedOpportunityId, LastModifiedDate, CreatedDate FROM Lead"
            + self._modified_filter(modified_after)
        )
        for rec in self.soql_query(query):
            first_name = rec.get("FirstName") or ""
            last_name = rec.get("LastName") or ""
            yield CRMLead(
                external_id=rec["Id"],
                provider="salesforce",
                first_name=first_name or None,
                last_name=last_name or None,
                full_name=f"{first_name} {last_name}".strip() or None,
                email=rec.get("Email"),
                company_name=rec.get("Company"),
                title=rec.get("Title"),
                phone=rec.get("Phone"),
                status=rec.get("Status"),
                source=rec.get("LeadSource"),
                owner_external_id=rec.get("OwnerId"),
                converted=bool(rec.get("IsConverted")),
                converted_account_id=rec.get("ConvertedAccountId"),
                converted_contact_id=rec.get("ConvertedContactId"),
                converted_opportunity_id=rec.get("ConvertedOpportunityId"),
                modified_at=_parse_dt(rec.get("LastModifiedDate")),
                created_at=_parse_dt(rec.get("CreatedDate")),
                raw_data=rec,
            )

    def get_opportunities(self, modified_after: datetime | None = None) -> Generator[CRMOpportunity, None, None]:
        query = (
            "SELECT Id, Name, StageName, Amount, CloseDate, AccountId, Account.Name, "
            "OwnerId, Owner.Name, CreatedDate, LastModifiedDate FROM Opportunity"
            + self._modified_filter(modified_after)
        )
        for rec in self.soql_query(query):
            stage = rec.get("StageName") or ""
            stage_lower = stage.lower()
            is_won = bool(rec.get("IsWon")) or stage_lower in ("closed won", "closed-won")
            is_closed = bool(rec.get("IsClosed")) or stage_lower.startswith("closed")
            probability = _as_float(rec.get("Probability"))
            if probability is not None:
                prob_val = probability / 100.0 if probability > 1.0 else probability
            else:
                prob_val = 1.0 if is_won else (0.0 if (is_closed and not is_won) else 0.5)

            yield CRMOpportunity(
                external_id=rec["Id"],
                provider="salesforce",
                name=rec.get("Name"),
                stage=stage,
                amount_usd=_as_float(rec.get("Amount")),
                probability=prob_val,
                close_date=_parse_date(rec.get("CloseDate")),
                is_closed_won=is_won,
                is_closed_lost=is_closed and not is_won,
                account_external_id=rec.get("AccountId"),
                owner_external_id=rec.get("OwnerId"),
                modified_at=_parse_dt(rec.get("LastModifiedDate")),
                created_at=_parse_dt(rec.get("CreatedDate")),
                raw_data=rec,
            )

    def get_users(self) -> Generator[CRMUser, None, None]:
        query = "SELECT Id, Email, FirstName, LastName, Name, IsActive, UserType FROM User WHERE IsActive = true"
        for rec in self.soql_query(query):
            yield CRMUser(
                external_id=rec["Id"],
                provider="salesforce",
                email=rec.get("Email"),
                first_name=rec.get("FirstName"),
                last_name=rec.get("LastName"),
                full_name=rec.get("Name"),
                is_active=bool(rec.get("IsActive")),
                role=rec.get("UserType"),
                raw_data=rec,
            )

    def get_limits(self) -> dict[str, Any]:
        return self._get("/limits")
