"""app/crm/providers/zoho/client.py"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Generator

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, RateLimitError
from app.core.logging import get_logger
from app.crm.base.models import CRMAccount, CRMContact, CRMLead, CRMOpportunity, CRMUser
from app.utils.encryption import decrypt_token, encrypt_token

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = get_logger(__name__)
_TIMEOUT = 20.0
_PAGE_SIZE = 200

_DC_AUTH_DOMAINS = {
    "com": "accounts.zoho.com",
    "eu": "accounts.zoho.eu",
    "in": "accounts.zoho.in",
    "au": "accounts.zoho.com.au",
    "jp": "accounts.zoho.jp",
    "ca": "accounts.zohocloud.ca",
}


def _parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
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


class ZohoAPIClient:
    """Zoho CRM v7 REST API client."""

    def __init__(self, connection, db: "Session"):
        self.conn = connection
        self.db = db
        api_domain = (connection.provider_metadata or {}).get("api_domain", "www.zohoapis.com")
        self._base = f"https://{api_domain}/crm/v7"
        dc = settings.ZOHO_DATA_CENTER or "com"
        auth_domain = _DC_AUTH_DOMAINS.get(dc, _DC_AUTH_DOMAINS["com"])
        self._token_url = f"https://{auth_domain}/oauth/v2/token"
        self.request_count = 0

    def _get_token(self) -> str:
        expires = self.conn.token_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires - datetime.now(timezone.utc) < timedelta(minutes=5):
            self._refresh()
        return decrypt_token(self.conn.access_token_encrypted)

    def _refresh(self) -> None:
        try:
            resp = httpx.post(
                self._token_url,
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.ZOHO_CLIENT_ID,
                    "client_secret": settings.ZOHO_CLIENT_SECRET,
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
            if "error" in data:
                self.conn.is_active = False
                self.conn.sync_error = f"Token refresh error: {data['error']}"
                self.db.commit()
                raise ExternalServiceError("Zoho", f"Token refresh error: {data['error']}")
            self.conn.access_token_encrypted = encrypt_token(data["access_token"])
            if "refresh_token" in data:
                self.conn.refresh_token_encrypted = encrypt_token(data["refresh_token"])
            self.conn.token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=data.get("expires_in", 3600)
            )
            self.conn.sync_error = None
            self.db.commit()
        except Exception as exc:
            raise ExternalServiceError("Zoho", f"Token refresh failed: {exc}") from exc

    def _headers(self) -> dict:
        return {"Authorization": f"Zoho-oauthtoken {self._get_token()}"}

    @retry(
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
    )
    def _request_once(self, url: str, params: dict | None = None) -> dict:
        self.request_count += 1
        resp = httpx.get(url, params=params or {}, headers=self._headers(), timeout=_TIMEOUT)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 30))
            raise RateLimitError("Zoho", retry_after_seconds=retry_after)
        if resp.status_code == 401:
            raise ExternalServiceError("Zoho", "Unauthorized")
        resp.raise_for_status()
        return resp.json()

    def _request_with_refresh(self, url: str, params: dict | None = None) -> dict:
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
                    self.conn.sync_error = "Zoho authorization failed after token refresh"
                    self.db.commit()
                raise

    def _get(self, path: str, params: dict | None = None) -> dict:
        return self._request_with_refresh(f"{self._base}/{path}", params)

    def _paginate(self, module: str, params: dict | None = None) -> Generator[dict, None, None]:
        page = 1
        base_params = {**(params or {}), "per_page": str(_PAGE_SIZE)}
        while True:
            base_params["page"] = str(page)
            data = self._get(module, base_params)
            records = data.get("data", [])
            if not records:
                break
            for rec in records:
                yield rec
            info = data.get("info", {})
            if not info.get("more_records", False):
                break
            page += 1

    def _modified_filter(self, modified_after: datetime | None) -> dict:
        if not modified_after:
            return {}
        if modified_after.tzinfo is None:
            modified_after = modified_after.replace(tzinfo=timezone.utc)
        return {"modified_since": modified_after.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")}

    def get_accounts(self, modified_after: datetime | None = None) -> Generator[CRMAccount, None, None]:
        fields = "id,Account_Name,Website,Industry,No_of_Employees,Billing_City,Billing_State,Billing_Country,Annual_Revenue,Phone,Modified_Time,Created_Time"
        params = {"fields": fields, **self._modified_filter(modified_after)}
        for rec in self._paginate("Accounts", params):
            website = rec.get("Website")
            yield CRMAccount(
                external_id=str(rec["id"]),
                provider="zoho",
                name=rec.get("Account_Name") or "",
                domain=_extract_domain(website),
                website=website,
                industry=rec.get("Industry"),
                employee_count=rec.get("No_of_Employees"),
                location_city=rec.get("Billing_City"),
                location_state=rec.get("Billing_State"),
                location_country=rec.get("Billing_Country"),
                annual_revenue=rec.get("Annual_Revenue"),
                phone=rec.get("Phone"),
                modified_at=_parse_dt(rec.get("Modified_Time")),
                created_at=_parse_dt(rec.get("Created_Time")),
                raw_data=rec,
            )

    def get_contacts(self, modified_after: datetime | None = None) -> Generator[CRMContact, None, None]:
        fields = "id,First_Name,Last_Name,Email,Phone,Title,Department,Account_Name,Owner,Modified_Time,Created_Time"
        params = {"fields": fields, **self._modified_filter(modified_after)}
        for rec in self._paginate("Contacts", params):
            acct = rec.get("Account_Name") or {}
            owner = rec.get("Owner") or {}
            yield CRMContact(
                external_id=str(rec["id"]),
                provider="zoho",
                first_name=rec.get("First_Name"),
                last_name=rec.get("Last_Name"),
                full_name=f"{rec.get('First_Name','') or ''} {rec.get('Last_Name','') or ''}".strip() or None,
                email=rec.get("Email"),
                phone=rec.get("Phone"),
                title=rec.get("Title"),
                department=rec.get("Department"),
                account_external_id=str(acct["id"]) if acct.get("id") else None,
                owner_external_id=str(owner["id"]) if owner.get("id") else None,
                modified_at=_parse_dt(rec.get("Modified_Time")),
                created_at=_parse_dt(rec.get("Created_Time")),
                raw_data=rec,
            )

    def get_leads(self, modified_after: datetime | None = None) -> Generator[CRMLead, None, None]:
        fields = "id,First_Name,Last_Name,Email,Company,Title,Phone,Lead_Status,Lead_Source,Owner,Converted,Modified_Time,Created_Time"
        params = {"fields": fields, **self._modified_filter(modified_after)}
        for rec in self._paginate("Leads", params):
            owner = rec.get("Owner") or {}
            yield CRMLead(
                external_id=str(rec["id"]),
                provider="zoho",
                first_name=rec.get("First_Name"),
                last_name=rec.get("Last_Name"),
                full_name=f"{rec.get('First_Name','') or ''} {rec.get('Last_Name','') or ''}".strip() or None,
                email=rec.get("Email"),
                company_name=rec.get("Company"),
                title=rec.get("Title"),
                phone=rec.get("Phone"),
                status=rec.get("Lead_Status"),
                source=rec.get("Lead_Source"),
                owner_external_id=str(owner["id"]) if owner.get("id") else None,
                converted=bool(rec.get("Converted", False)),
                modified_at=_parse_dt(rec.get("Modified_Time")),
                created_at=_parse_dt(rec.get("Created_Time")),
                raw_data=rec,
            )

    def get_deals(self, modified_after: datetime | None = None) -> Generator[CRMOpportunity, None, None]:
        fields = "id,Deal_Name,Stage,Pipeline,Amount,Probability,Closing_Date,Account_Name,Owner,Modified_Time,Created_Time"
        params = {"fields": fields, **self._modified_filter(modified_after)}
        for rec in self._paginate("Deals", params):
            acct = rec.get("Account_Name") or {}
            owner = rec.get("Owner") or {}
            stage = rec.get("Stage", "")
            is_won = stage == "Closed Won"
            is_lost = stage == "Closed Lost"
            prob = rec.get("Probability")
            yield CRMOpportunity(
                external_id=str(rec["id"]),
                provider="zoho",
                name=rec.get("Deal_Name"),
                stage=stage,
                pipeline=rec.get("Pipeline"),
                amount_usd=rec.get("Amount"),
                probability=float(prob) / 100 if prob is not None else None,
                close_date=_parse_dt(rec.get("Closing_Date")),
                is_closed_won=is_won,
                is_closed_lost=is_lost,
                account_external_id=str(acct["id"]) if acct.get("id") else None,
                owner_external_id=str(owner["id"]) if owner.get("id") else None,
                modified_at=_parse_dt(rec.get("Modified_Time")),
                created_at=_parse_dt(rec.get("Created_Time")),
                raw_data=rec,
            )

    def get_users(self) -> Generator[CRMUser, None, None]:
        data = self._get("users", {"type": "AllUsers"})
        for rec in data.get("users", []):
            profile = rec.get("profile") or {}
            yield CRMUser(
                external_id=str(rec["id"]),
                provider="zoho",
                email=rec.get("email"),
                first_name=rec.get("first_name"),
                last_name=rec.get("last_name"),
                full_name=rec.get("full_name"),
                is_active=rec.get("status", "active") == "active",
                role=profile.get("name"),
                raw_data=rec,
            )
