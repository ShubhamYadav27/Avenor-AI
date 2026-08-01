"""Generic CRM sync engine.

Provider adapters only yield canonical CRM models. This engine owns the
provider-agnostic persistence, sync state updates, audit logs, and metrics.

Production-grade features:
- Streaming sync: never loads all records into memory (scalable to 100k+ records)
- Per-object incremental cursors: each object type (Account, Contact, etc.) tracks
  its own LastModifiedDate cursor independently
- Deletion detection: full syncs soft-delete records no longer present in the CRM
- Periodic DB flush every 200 records to prevent SQLAlchemy identity map from growing
  unboundedly for very large orgs
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Callable, Iterable, Set

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.crm.base.interfaces import ICRMProvider
from app.crm.base.models import (
    CRMAccount,
    CRMContact,
    CRMLead,
    CRMOpportunity,
    CRMUser,
    SyncResult,
    SyncStats,
    SyncStatus,
)
from app.models import (
    CRMAccountDB,
    CRMAuditLog,
    CRMConnectionDB,
    CRMContactDB,
    CRMLeadDB,
    CRMOpportunityDB,
    CRMSyncStateV2,
    CRMUserDB,
    Company,
    Contact,
    Opportunity,
    Lead,
    CRMUser as CanonicalCRMUser,
)

logger = get_logger(__name__)

# Flush the SQLAlchemy session every N records to cap identity-map memory use.
# At 200 records the overhead is negligible; at 100k records this prevents OOM.
_FLUSH_EVERY = 200

# DB model type map used for deletion detection
_OBJECT_MODEL_MAP: dict[str, type] = {
    "account": CRMAccountDB,
    "contact": CRMContactDB,
    "lead": CRMLeadDB,
    "opportunity": CRMOpportunityDB,
    "user": CRMUserDB,
}


class CRMSyncEngine:
    """Persists canonical CRM objects from any registered provider.

    Scalability guarantees:
    - Streams records one-by-one from the provider generator: O(1) memory
    - Flushes the DB session every _FLUSH_EVERY records
    - Uses per-object LastModifiedDate cursors for incremental sync
    - Tombstone-scans for deletions on full (force_all) syncs
    """

    def __init__(self, db: Session, provider: ICRMProvider):
        self.db = db
        self.provider = provider
        self.connection: CRMConnectionDB = provider.connection
        self.workspace_id = self.connection.workspace_id
        self.provider_name = provider.provider_name

    # ── Public sync entry points ─────────────────────────────────────────────

    def run_historical_sync(self, days_back: int = 180) -> SyncResult:
        """Full sync: fetch all records from the provider. Used on first connect."""
        return self._run_sync(sync_type="historical", modified_after=None, detect_deletions=True)

    def run_incremental_sync(self, force_all: bool = False) -> SyncResult:
        """Incremental sync: fetch only records modified since the last cursor.

        When force_all=True (user-triggered Force Sync), fetches all records and
        runs deletion detection to tombstone records removed from the CRM.
        """
        if force_all:
            return self._run_sync(sync_type="full", modified_after=None, detect_deletions=True)
        return self._run_sync(sync_type="incremental", modified_after=None, detect_deletions=False)

    def process_events(self, events: list) -> dict:
        """Record webhook events and let scheduled sync handle reconciliation."""
        for event in events:
            self._audit(
                operation="webhook.event",
                object_type=event.object_type.value,
                external_id=event.external_id,
                status="received",
                detail=event.event_type.value,
            )
        self.db.commit()
        return {"received": len(events)}

    # ── Core orchestration ───────────────────────────────────────────────────

    def _run_sync(
        self,
        sync_type: str,
        modified_after: datetime | None,
        detect_deletions: bool,
    ) -> SyncResult:
        started = datetime.now(timezone.utc)
        stats: list[SyncStats] = []
        status = SyncStatus.COMPLETED
        error = None

        logger.info(
            "crm_sync_started",
            provider=self.provider_name,
            workspace_id=str(self.workspace_id),
            sync_type=sync_type,
        )

        try:
            capabilities = self.provider.get_capabilities()

            # Build the execution plan: (object_type, enabled, iterator_factory, upsert_fn)
            plan: list[tuple[str, bool, Callable[[], Iterable], Callable[[object], bool]]] = [
                (
                    "account",
                    capabilities.supports_accounts,
                    lambda: self.provider.sync_accounts(self._cursor_for("account") if sync_type == "incremental" else None),
                    self._upsert_account,
                ),
                (
                    "contact",
                    capabilities.supports_contacts,
                    lambda: self.provider.sync_contacts(self._cursor_for("contact") if sync_type == "incremental" else None),
                    self._upsert_contact,
                ),
                (
                    "lead",
                    capabilities.supports_leads,
                    lambda: self.provider.sync_leads(self._cursor_for("lead") if sync_type == "incremental" else None),
                    self._upsert_lead,
                ),
                (
                    "opportunity",
                    capabilities.supports_opportunities,
                    lambda: self.provider.sync_opportunities(self._cursor_for("opportunity") if sync_type == "incremental" else None),
                    self._upsert_opportunity,
                ),
                (
                    "user",
                    capabilities.supports_users,
                    # Users never have a modified_after — always fetch all active users
                    lambda: self.provider.sync_users(),
                    self._upsert_user,
                ),
            ]

            for object_type, enabled, iterator_factory, upsert_fn in plan:
                if not enabled:
                    stats.append(SyncStats(object_type=object_type, skipped=1))
                    continue
                obj_stats = self._sync_object_type(
                    object_type=object_type,
                    iterator_factory=iterator_factory,
                    upsert=upsert_fn,
                    sync_type=sync_type,
                    detect_deletions=detect_deletions,
                )
                stats.append(obj_stats)

            self.connection.last_sync_at = datetime.now(timezone.utc)
            self.connection.sync_error = None
            logger.info(
                "crm_sync_completed",
                provider=self.provider_name,
                workspace_id=str(self.workspace_id),
                total_fetched=sum(s.fetched for s in stats),
                total_created=sum(s.created for s in stats),
                total_updated=sum(s.updated for s in stats),
                total_deleted=sum(getattr(s, "deleted", 0) for s in stats),
            )
        except Exception as exc:
            status = SyncStatus.FAILED
            error = str(exc)
            self.connection.sync_error = error
            self._audit("sync", None, None, "failed", error=error)
            logger.exception(
                "crm_sync_failed_with_exception",
                provider=self.provider_name,
                workspace_id=str(self.workspace_id),
                error=error,
                exc_info=True,
            )

        self.db.commit()
        return SyncResult(
            provider=self.provider_name,
            workspace_id=str(self.workspace_id),
            sync_type=sync_type,
            status=status,
            started_at=started,
            completed_at=datetime.now(timezone.utc),
            stats=stats,
            error=error,
        )

    def _sync_object_type(
        self,
        object_type: str,
        iterator_factory: Callable[[], Iterable],
        upsert: Callable[[object], bool],
        sync_type: str,
        detect_deletions: bool,
    ) -> SyncStats:
        """Stream records one-by-one from the provider, upsert each into the DB.

        Key scalability properties:
        - Never materialises the full record list (no list())
        - Flushes the SQLAlchemy session every _FLUSH_EVERY records
        - Accumulates seen external_ids for deletion detection on full syncs
        """
        started = time.monotonic()
        fetched = 0
        created = 0
        updated = 0
        failed = 0
        deleted = 0

        # Collect seen external_ids during full syncs for deletion detection.
        # A Python set of 100k Salesforce IDs uses ~10MB — acceptable.
        seen_external_ids: Set[str] | None = set() if detect_deletions else None

        logger.info(
            f"crm_sync_starting_{object_type}s",
            provider=self.provider_name,
            workspace_id=str(self.workspace_id),
            sync_type=sync_type,
        )

        for item in iterator_factory():
            fetched += 1
            item_ext_id = getattr(item, "external_id", "unknown")

            if seen_external_ids is not None:
                seen_external_ids.add(item_ext_id)

            try:
                was_created = upsert(item)
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as exc:
                failed += 1
                logger.exception(
                    f"crm_sync_upsert_failed_{object_type}",
                    provider=self.provider_name,
                    external_id=item_ext_id,
                    error=str(exc),
                    exc_info=True,
                )
                self._audit("upsert", object_type, item_ext_id, "failed", error=str(exc))

            # Periodic flush to prevent unbounded SQLAlchemy identity-map growth
            if fetched % _FLUSH_EVERY == 0:
                self.db.flush()
                logger.debug(
                    f"crm_sync_{object_type}_flush",
                    provider=self.provider_name,
                    processed=fetched,
                )

        logger.info(
            f"crm_sync_fetched_{object_type}s",
            provider=self.provider_name,
            count=fetched,
            workspace_id=str(self.workspace_id),
        )

        # Flush any remaining records before updating sync state metrics
        self.db.flush()

        # ── Deletion detection ───────────────────────────────────────────────
        # On full syncs: any record in our DB that the provider did NOT return
        # is soft-deleted (synced_at set to epoch, raw_data["_deleted"] = True).
        if detect_deletions and seen_external_ids is not None and fetched > 0:
            deleted = self._tombstone_deleted(object_type, seen_external_ids)

        self._update_sync_state(object_type, sync_type, created, updated, failed)
        return SyncStats(
            object_type=object_type,
            fetched=fetched,
            created=created,
            updated=updated,
            failed=failed,
            duration_seconds=time.monotonic() - started,
        )

    # ── Deletion detection ───────────────────────────────────────────────────

    def _tombstone_deleted(self, object_type: str, seen_ids: Set[str]) -> int:
        """Soft-delete records that are absent from the provider's full sync response.

        We do NOT hard-delete records to preserve referential integrity with
        downstream tables (company_scores, intelligence_feed_items, etc.).
        Instead we mark raw_data["_deleted"] = True and update synced_at so
        the next incremental sync won't re-process them.

        Returns the count of records soft-deleted.
        """
        model = _OBJECT_MODEL_MAP.get(object_type)
        if model is None:
            return 0

        # Fetch all external_ids for this workspace/provider in batches
        deleted_count = 0
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

        # Use a streaming query to avoid loading all rows at once
        stmt = (
            select(model)
            .where(
                model.workspace_id == self.workspace_id,
                model.provider == self.provider_name,
            )
            .execution_options(yield_per=500)
        )

        for row in self.db.execute(stmt).scalars():
            if row.external_id not in seen_ids:
                # Mark as deleted in raw_data
                raw = dict(row.raw_data or {})
                if raw.get("_deleted"):
                    continue  # already tombstoned
                raw["_deleted"] = True
                raw["_deleted_at"] = datetime.now(timezone.utc).isoformat()
                row.raw_data = raw
                row.synced_at = epoch
                deleted_count += 1

        if deleted_count > 0:
            self.db.flush()
            logger.info(
                "crm_sync_deletions_detected",
                provider=self.provider_name,
                object_type=object_type,
                workspace_id=str(self.workspace_id),
                deleted_count=deleted_count,
            )
            self._audit(
                "deletion_scan",
                object_type,
                None,
                "completed",
                detail=f"{deleted_count} records soft-deleted",
            )

        return deleted_count

    # ── Upsert methods ───────────────────────────────────────────────────────

    def _upsert_account(self, account: CRMAccount) -> bool:
        row, created = self._get_or_create(CRMAccountDB, account.external_id)
        row.name = account.name
        row.domain = account.domain
        row.website = account.website
        row.industry = account.industry
        row.employee_count = account.employee_count
        row.location_city = account.location_city
        row.location_state = account.location_state
        row.location_country = account.location_country
        row.annual_revenue = account.annual_revenue
        row.phone = account.phone
        row.company_id = self._match_company_id(account.domain)
        
        # Safely fetch or create Company to avoid auto-flush constraint violations
        company_row = self.db.execute(
            select(Company).where(
                Company.workspace_id == self.workspace_id,
                Company.external_id == account.external_id
            )
        ).scalar_one_or_none()
        
        company_created = False
        
        if not company_row and account.domain:
            # Fallback to domain lookup if not found by external_id
            company_row = self.db.execute(
                select(Company).where(
                    Company.workspace_id == self.workspace_id,
                    Company.domain == account.domain
                )
            ).scalar_one_or_none()
            
        if not company_row:
            # Still not found, create new
            company_row = Company(
                workspace_id=self.workspace_id,
                provider=self.provider_name,
                external_id=account.external_id
            )
            self.db.add(company_row)
            company_created = True
        else:
            # Update external_id in case it was found by domain
            company_row.external_id = account.external_id

        company_row.provider = self.provider_name
        company_row.name = account.name
        company_row.domain = account.domain
        company_row.website = account.website
        company_row.industry = account.industry
        company_row.employee_count = account.employee_count
        company_row.location_city = account.location_city
        company_row.location_state = account.location_state
        company_row.location_country = account.location_country
        company_row.annual_revenue = account.annual_revenue
        company_row.phone = account.phone

        # Clear deletion tombstone if account reappears after being deleted
        raw = dict(account.raw_data or {})
        raw.pop("_deleted", None)
        raw.pop("_deleted_at", None)
        row.raw_data = raw
        row.synced_at = datetime.now(timezone.utc)
        
        company_row.raw_data = raw
        company_row.synced_at = datetime.now(timezone.utc)
        
        return created or company_created

    def _upsert_contact(self, contact: CRMContact) -> bool:
        row, created = self._get_or_create(CRMContactDB, contact.external_id)
        row.external_account_id = contact.account_external_id
        row.first_name = contact.first_name
        row.last_name = contact.last_name
        row.full_name = contact.full_name
        row.email = contact.email
        row.phone = contact.phone
        row.title = contact.title
        row.department = contact.department
        row.seniority = contact.seniority
        row.linkedin_url = contact.linkedin_url
        
        # Fetch company_id before creating the Contact to avoid auto-flush constraint violations
        company_id = None
        if contact.account_external_id:
            company_row = self.db.execute(
                select(Company).where(
                    Company.workspace_id == self.workspace_id,
                    Company.external_id == contact.account_external_id
                )
            ).scalar_one_or_none()
            if company_row:
                company_id = company_row.id
        
        # Dual-write Canonical Contact only if we can link it to a Company (company_id is NOT NULL)
        contact_created = False
        if company_id:
            contact_row, contact_created = self._get_or_create(Contact, contact.external_id)
            contact_row.provider = self.provider_name
            contact_row.external_account_id = contact.account_external_id
            contact_row.company_id = company_id
            
            contact_row.first_name = contact.first_name
            contact_row.last_name = contact.last_name
            contact_row.full_name = contact.full_name
            contact_row.email = contact.email
            contact_row.phone = contact.phone
            contact_row.title = contact.title
            contact_row.department = contact.department
            contact_row.seniority = contact.seniority
            contact_row.linkedin_url = contact.linkedin_url
            
            raw = dict(contact.raw_data or {})
            raw.pop("_deleted", None)
            raw.pop("_deleted_at", None)
            contact_row.raw_data = raw
            contact_row.synced_at = datetime.now(timezone.utc)
        
        raw = dict(contact.raw_data or {})
        raw.pop("_deleted", None)
        raw.pop("_deleted_at", None)
        row.raw_data = raw
        row.synced_at = datetime.now(timezone.utc)
        
        return created or contact_created

    def _upsert_opportunity(self, opportunity: CRMOpportunity) -> bool:
        row, created = self._get_or_create(CRMOpportunityDB, opportunity.external_id)
        row.external_account_id = opportunity.account_external_id
        row.external_contact_ids = opportunity.contact_external_ids
        row.external_owner_id = opportunity.owner_external_id
        row.name = opportunity.name
        row.stage = opportunity.stage
        row.pipeline = opportunity.pipeline
        row.amount_usd = opportunity.amount_usd
        row.probability = opportunity.probability
        row.close_date = opportunity.close_date
        row.created_date = opportunity.created_at
        row.is_closed_won = opportunity.is_closed_won
        row.is_closed_lost = opportunity.is_closed_lost
        row.closed_at = opportunity.closed_at
        
        # Fetch company_id before creating the Opportunity to avoid auto-flush constraint violations
        company_id = None
        if opportunity.account_external_id:
            company_row = self.db.execute(
                select(Company).where(
                    Company.workspace_id == self.workspace_id, 
                    Company.external_id == opportunity.account_external_id
                )
            ).scalar_one_or_none()
            if company_row:
                company_id = company_row.id
                
        # Dual-write Canonical Opportunity
        opp_row, opp_created = self._get_or_create(Opportunity, opportunity.external_id)
        opp_row.provider = self.provider_name
        opp_row.external_account_id = opportunity.account_external_id
        opp_row.external_contact_ids = opportunity.contact_external_ids
        opp_row.external_owner_id = opportunity.owner_external_id
        opp_row.company_id = company_id
        
        opp_row.name = opportunity.name
        opp_row.stage = opportunity.stage
        opp_row.pipeline = opportunity.pipeline
        opp_row.amount_usd = opportunity.amount_usd
        opp_row.probability = opportunity.probability
        opp_row.close_date = opportunity.close_date
        opp_row.created_date = opportunity.created_at
        opp_row.is_closed_won = opportunity.is_closed_won
        opp_row.is_closed_lost = opportunity.is_closed_lost
        opp_row.closed_at = opportunity.closed_at
        
        raw = dict(opportunity.raw_data or {})
        raw.pop("_deleted", None)
        raw.pop("_deleted_at", None)
        row.raw_data = raw
        row.synced_at = datetime.now(timezone.utc)
        
        opp_row.raw_data = raw
        opp_row.synced_at = datetime.now(timezone.utc)
        
        return created or opp_created

    def _upsert_user(self, user: CRMUser) -> bool:
        row, created = self._get_or_create(CRMUserDB, user.external_id)
        row.email = user.email
        row.first_name = user.first_name
        row.last_name = user.last_name
        row.full_name = user.full_name
        row.is_active = user.is_active
        row.role = user.role
        
        # Dual-write Canonical CRMUser
        user_row, user_created = self._get_or_create(CanonicalCRMUser, user.external_id)
        user_row.provider = self.provider_name
        user_row.email = user.email
        user_row.name = user.full_name
        user_row.is_active = user.is_active
        
        raw = dict(user.raw_data or {})
        raw.pop("_deleted", None)
        raw.pop("_deleted_at", None)
        row.raw_data = raw
        row.synced_at = datetime.now(timezone.utc)
        
        user_row.raw_data = raw
        user_row.synced_at = datetime.now(timezone.utc)
        
        return created or user_created

    def _upsert_lead(self, lead: CRMLead) -> bool:
        row, created = self._get_or_create(CRMLeadDB, lead.external_id)
        row.first_name = lead.first_name
        row.last_name = lead.last_name
        row.full_name = lead.full_name
        row.email = lead.email
        row.company_name = lead.company_name
        row.title = lead.title
        row.phone = lead.phone
        row.status = lead.status
        row.source = lead.source
        row.external_owner_id = lead.owner_external_id
        row.converted = lead.converted
        row.converted_account_id = lead.converted_account_id
        row.converted_contact_id = lead.converted_contact_id
        row.converted_opportunity_id = lead.converted_opportunity_id
        
        # Dual-write Canonical Lead
        lead_row, lead_created = self._get_or_create(Lead, lead.external_id)
        lead_row.provider = self.provider_name
        lead_row.first_name = lead.first_name
        lead_row.last_name = lead.last_name
        lead_row.full_name = lead.full_name
        lead_row.email = lead.email
        lead_row.company_name = lead.company_name
        lead_row.title = lead.title
        lead_row.phone = lead.phone
        lead_row.status = lead.status
        
        raw = dict(lead.raw_data or {})
        raw.pop("_deleted", None)
        raw.pop("_deleted_at", None)
        row.raw_data = raw
        row.synced_at = datetime.now(timezone.utc)
        
        lead_row.raw_data = raw
        lead_row.synced_at = datetime.now(timezone.utc)
        
        return created or lead_created

    # ── DB helpers ───────────────────────────────────────────────────────────

    def _get_or_create(self, model, external_id: str):
        row = (
            self.db.query(model)
            .filter_by(
                workspace_id=self.workspace_id,
                provider=self.provider_name,
                external_id=external_id,
            )
            .first()
        )
        if row:
            return row, False
        row = model(
            workspace_id=self.workspace_id,
            provider=self.provider_name,
            external_id=external_id,
        )
        self.db.add(row)
        return row, True

    def _cursor_for(self, object_type: str) -> datetime | None:
        """Return the last_synced_at cursor for a specific object type.

        Using per-object cursors means Accounts and Opportunities advance
        independently — a slow Lead sync does not cause Accounts to re-sync
        from the beginning on the next incremental run.
        """
        state = (
            self.db.query(CRMSyncStateV2)
            .filter_by(
                workspace_id=self.workspace_id,
                provider=self.provider_name,
                object_type=object_type,
            )
            .first()
        )
        return state.last_synced_at if state else None

    def _update_sync_state(
        self,
        object_type: str,
        sync_type: str,
        created: int,
        updated: int,
        failed: int,
    ) -> None:
        state = (
            self.db.query(CRMSyncStateV2)
            .filter_by(
                workspace_id=self.workspace_id,
                provider=self.provider_name,
                object_type=object_type,
            )
            .first()
        )
        if state is None:
            state = CRMSyncStateV2(
                workspace_id=self.workspace_id,
                connection_id=self.connection.id,
                provider=self.provider_name,
                object_type=object_type,
            )
            self.db.add(state)

        now = datetime.now(timezone.utc)
        state.connection_id = self.connection.id
        # Advance the cursor to now — next incremental sync uses this
        state.last_synced_at = now
        state.last_run_at = now
        state.last_run_created = created
        state.last_run_updated = updated
        state.last_run_status = "failed" if failed else "completed"
        state.last_run_error = f"{failed} records failed" if failed else None
        
        # Calculate true current records in canonical DB
        current_count = 0
        if object_type in ("account", "accounts"):
            current_count = self.db.execute(select(func.count()).select_from(Company).where(Company.workspace_id == self.workspace_id, Company.provider == self.provider_name)).scalar() or 0
        elif object_type in ("contact", "contacts"):
            current_count = self.db.execute(select(func.count()).select_from(Contact).where(Contact.workspace_id == self.workspace_id, Contact.provider == self.provider_name)).scalar() or 0
        elif object_type in ("opportunity", "opportunities"):
            current_count = self.db.execute(select(func.count()).select_from(Opportunity).where(Opportunity.workspace_id == self.workspace_id, Opportunity.provider == self.provider_name)).scalar() or 0
        elif object_type in ("lead", "leads"):
            current_count = self.db.execute(select(func.count()).select_from(Lead).where(Lead.workspace_id == self.workspace_id, Lead.provider == self.provider_name)).scalar() or 0
        elif object_type in ("user", "users"):
            current_count = self.db.execute(select(func.count()).select_from(CRMUserDB).where(CRMUserDB.workspace_id == self.workspace_id, CRMUserDB.provider == self.provider_name)).scalar() or 0
            
        state.current_sync_records = current_count
        state.total_synced = current_count  # Keep for backwards compatibility
        state.lifetime_records_processed = (state.lifetime_records_processed or 0) + created + updated
        
        if sync_type in ("historical", "full"):
            state.historical_import_completed = True
            state.historical_import_completed_at = now
            state.historical_records_imported = (state.historical_records_imported or 0) + created + updated

    def _match_company_id(self, domain: str | None):
        if not domain:
            return None
        company = (
            self.db.query(Company)
            .filter_by(workspace_id=self.workspace_id, domain=domain.lower())
            .first()
        )
        return company.id if company else None

    def _audit(
        self,
        operation: str,
        object_type: str | None,
        external_id: str | None,
        status: str,
        detail: str | None = None,
        error: str | None = None,
    ) -> None:
        self.db.add(
            CRMAuditLog(
                workspace_id=self.workspace_id,
                provider=self.provider_name,
                operation=operation,
                object_type=object_type,
                external_id=external_id,
                status=status,
                detail=detail,
                error=error,
            )
        )
