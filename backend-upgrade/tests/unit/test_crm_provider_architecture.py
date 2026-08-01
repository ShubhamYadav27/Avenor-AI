import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.crm.base.models import CRMAccount, ProviderCapabilities, SyncStatus
from app.crm.engine import CRMSyncEngine
from app.crm.registry import CRMProviderRegistry
from app.models import CRMAccountDB, CRMSyncStateV2


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

    def commit(self):
        self.commits += 1

    def flush(self):
        """No-op flush for unit tests."""

    def execute(self, stmt, **kwargs):
        """Return a minimal result object that supports .scalars() iteration.

        The sync engine's deletion detection calls db.execute(select(Model)...)
        and iterates over .scalars(). In unit tests with an in-memory FakeSession
        the store is keyed by model class, not by SQLAlchemy statements, so we
        return the stored rows for the statement's entity class.
        """
        class _FakeResult:
            def __init__(self, rows):
                self._rows = rows

            def scalars(self):
                return iter(self._rows)

            def scalar(self):
                return len(self._rows)

            def scalar_one_or_none(self):
                return self._rows[0] if self._rows else None



        # Try to resolve the model from the statement's entity
        try:
            entity = stmt.column_descriptions[0]["entity"]
            rows = self.rows.get(entity, [])
        except Exception:
            rows = []
        return _FakeResult(rows)


class FakeProvider:
    provider_name = "hubspot"

    def __init__(self, connection):
        self.connection = connection

    def get_capabilities(self):
        return ProviderCapabilities(
            supports_accounts=True,
            supports_contacts=False,
            supports_leads=False,
            supports_opportunities=False,
            supports_users=False,
        )

    def sync_accounts(self, modified_after=None):
        yield CRMAccount(
            external_id="acct-1",
            provider="hubspot",
            name="Acme",
            domain="acme.test",
            modified_at=datetime.now(timezone.utc),
        )


def test_registered_crm_providers_are_available():
    import app.crm.providers  # noqa: F401

    assert set(CRMProviderRegistry.list_available()) >= {
        "hubspot",
        "salesforce",
        "dynamics",
        "zoho",
    }


def test_sync_engine_persists_canonical_accounts_and_state():
    workspace_id = uuid.uuid4()
    connection = SimpleNamespace(id=uuid.uuid4(), workspace_id=workspace_id, last_sync_at=None, sync_error=None)
    db = FakeSession()
    provider = FakeProvider(connection)

    result = CRMSyncEngine(db, provider).run_historical_sync()

    assert result.status == SyncStatus.COMPLETED
    assert result.provider == "hubspot"
    assert result.total_created == 1

    account = db.rows[CRMAccountDB][0]
    assert account.workspace_id == workspace_id
    assert account.provider == "hubspot"
    assert account.external_id == "acct-1"
    assert account.name == "Acme"

    state = db.rows[CRMSyncStateV2][0]
    assert state.provider == "hubspot"
    assert state.object_type == "account"
    assert state.historical_import_completed is True
