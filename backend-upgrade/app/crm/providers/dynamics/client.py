"""app/crm/providers/dynamics/client.py"""
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
_API_VERSION = "v9.2"
_PAGE_SIZE = 200


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


class DynamicsAPIClient:
    def __init__(self, connection, db: "Session"):
        self.conn = connection
        self.db = db
        crm_url = (connection.provider_metadata or {}).get("crm_url", "").rstrip("/")
        self._base = f"{crm_url}/api/data/{_API_VERSION}" if crm_url else f"https://org.crm.dynamics.com/api/data/{_API_VERSION}"
        self.request_count = 0

    def _get_token(self) -> str:
        expires = self.conn.token_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires - datetime.now(timezone.utc) < timedelta(minutes=5):
            self._refresh()
        return decrypt_token(self.conn.access_token_encrypted)

    def _refresh(self) -> None:
        tenant = settings.DYNAMICS_TENANT_ID or "common"
        try:
            resp = httpx.post(
                f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.DYNAMICS_CLIENT_ID,
                    "client_secret": settings.DYNAMICS_CLIENT_SECRET,
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
            if "refresh_token" in data:
                self.conn.refresh_token_encrypted = encrypt_token(data["refresh_token"])
            self.conn.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=data.get("expires_in", 3600))
            self.conn.sync_error = None
            self.db.commit()
        except Exception as exc:
            raise ExternalServiceError("Dynamics", f"Token refresh failed: {exc}") from exc

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Prefer": f"odata.maxpagesize={_PAGE_SIZE}",
        }

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
            raise RateLimitError("Dynamics", retry_after_seconds=retry_after)
        if resp.status_code == 401:
            raise ExternalServiceError("Dynamics", "Unauthorized")
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
                    self.conn.sync_error = "Dynamics authorization failed after token refresh"
                    self.db.commit()
                raise

    def _get(self, path: str, params: dict | None = None) -> dict:
        return self._request_with_refresh(f"{self._base}/{path}", params)

    def odata_query(self, entity: str, select: str, filter_expr: str = "") -> Generator[dict, None, None]:
        params = {"$select": select, "$top": str(_PAGE_SIZE)}
        if filter_expr:
            params["$filter"] = filter_expr
        next_url = f"{self._base}/{entity}"
        while next_url:
            if next_url == f"{self._base}/{entity}":
                data = self._get(entity, params)
            else:
                data = self._request_with_refresh(next_url)
            for rec in data.get("value", []):
                yield rec
            next_url = data.get("@odata.nextLink")

    def _modified_filter(self, modified_after: datetime | None) -> str:
        if not modified_after:
            return ""
        if modified_after.tzinfo is None:
            modified_after = modified_after.replace(tzinfo=timezone.utc)
        ts = modified_after.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"modifiedon ge {ts}"

    def get_accounts(self, modified_after: datetime | None = None) -> Generator[CRMAccount, None, None]:
        select = "accountid,name,websiteurl,industrycode,numberofemployees,address1_city,address1_stateorprovince,address1_country,revenue,telephone1,modifiedon,createdon"
        for rec in self.odata_query("accounts", select, self._modified_filter(modified_after)):
            website = rec.get("websiteurl")
            yield CRMAccount(
                external_id=rec["accountid"],
                provider="dynamics",
                name=rec.get("name") or "",
                domain=_extract_domain(website),
                website=website,
                industry=str(rec["industrycode"]) if rec.get("industrycode") else None,
                employee_count=rec.get("numberofemployees"),
                location_city=rec.get("address1_city"),
                location_state=rec.get("address1_stateorprovince"),
                location_country=rec.get("address1_country"),
                annual_revenue=rec.get("revenue"),
                phone=rec.get("telephone1"),
                modified_at=_parse_dt(rec.get("modifiedon")),
                created_at=_parse_dt(rec.get("createdon")),
                raw_data=rec,
            )

    def get_contacts(self, modified_after: datetime | None = None) -> Generator[CRMContact, None, None]:
        select = "contactid,firstname,lastname,emailaddress1,telephone1,jobtitle,department,_accountid_value,_ownerid_value,modifiedon,createdon"
        for rec in self.odata_query("contacts", select, self._modified_filter(modified_after)):
            yield CRMContact(
                external_id=rec["contactid"],
                provider="dynamics",
                first_name=rec.get("firstname"),
                last_name=rec.get("lastname"),
                full_name=f"{rec.get('firstname','') or ''} {rec.get('lastname','') or ''}".strip() or None,
                email=rec.get("emailaddress1"),
                phone=rec.get("telephone1"),
                title=rec.get("jobtitle"),
                department=rec.get("department"),
                account_external_id=rec.get("_accountid_value"),
                owner_external_id=rec.get("_ownerid_value"),
                modified_at=_parse_dt(rec.get("modifiedon")),
                created_at=_parse_dt(rec.get("createdon")),
                raw_data=rec,
            )

    def get_leads(self, modified_after: datetime | None = None) -> Generator[CRMLead, None, None]:
        select = "leadid,firstname,lastname,emailaddress1,companyname,jobtitle,telephone1,statuscode,leadsourcecode,_ownerid_value,modifiedon,createdon"
        for rec in self.odata_query("leads", select, self._modified_filter(modified_after)):
            yield CRMLead(
                external_id=rec["leadid"],
                provider="dynamics",
                first_name=rec.get("firstname"),
                last_name=rec.get("lastname"),
                full_name=f"{rec.get('firstname','') or ''} {rec.get('lastname','') or ''}".strip() or None,
                email=rec.get("emailaddress1"),
                company_name=rec.get("companyname"),
                title=rec.get("jobtitle"),
                phone=rec.get("telephone1"),
                status=str(rec["statuscode"]) if rec.get("statuscode") is not None else None,
                source=str(rec["leadsourcecode"]) if rec.get("leadsourcecode") is not None else None,
                owner_external_id=rec.get("_ownerid_value"),
                modified_at=_parse_dt(rec.get("modifiedon")),
                created_at=_parse_dt(rec.get("createdon")),
                raw_data=rec,
            )

    def get_opportunities(self, modified_after: datetime | None = None) -> Generator[CRMOpportunity, None, None]:
        select = "opportunityid,name,stepname,estimatedvalue,closeprobability,estimatedclosedate,_accountid_value,_ownerid_value,statecode,statuscode,modifiedon,createdon"
        for rec in self.odata_query("opportunities", select, self._modified_filter(modified_after)):
            statecode = rec.get("statecode", 0)
            is_won = statecode == 1
            is_lost = statecode == 2
            prob = rec.get("closeprobability")
            yield CRMOpportunity(
                external_id=rec["opportunityid"],
                provider="dynamics",
                name=rec.get("name"),
                stage=rec.get("stepname"),
                amount_usd=rec.get("estimatedvalue"),
                probability=float(prob) / 100 if prob is not None else None,
                close_date=_parse_dt(rec.get("estimatedclosedate")),
                is_closed_won=is_won,
                is_closed_lost=is_lost,
                account_external_id=rec.get("_accountid_value"),
                owner_external_id=rec.get("_ownerid_value"),
                modified_at=_parse_dt(rec.get("modifiedon")),
                created_at=_parse_dt(rec.get("createdon")),
                raw_data=rec,
            )

    def get_users(self) -> Generator[CRMUser, None, None]:
        select = "systemuserid,internalemailaddress,firstname,lastname,fullname,isdisabled"
        for rec in self.odata_query("systemusers", select, "isdisabled eq false"):
            yield CRMUser(
                external_id=rec["systemuserid"],
                provider="dynamics",
                email=rec.get("internalemailaddress"),
                first_name=rec.get("firstname"),
                last_name=rec.get("lastname"),
                full_name=rec.get("fullname"),
                is_active=not bool(rec.get("isdisabled", False)),
                raw_data=rec,
            )
