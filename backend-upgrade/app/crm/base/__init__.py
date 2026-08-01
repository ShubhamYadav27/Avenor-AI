"""app/crm/base/__init__.py"""
from app.crm.base.interfaces import ICRMProvider
from app.crm.base.models import (
    CRMAccount,
    CRMContact,
    CRMLead,
    CRMOpportunity,
    CRMUser,
    CRMEvent,
    CRMConnectionState,
    CRMEventType,
    CRMObjectType,
    OAuthCallbackResult,
    OAuthURLResult,
    ProviderCapabilities,
    SyncResult,
    SyncStats,
    SyncStatus,
)
from app.crm.base.auth import BaseOAuthHandler

__all__ = [
    "ICRMProvider",
    "CRMAccount",
    "CRMContact",
    "CRMLead",
    "CRMOpportunity",
    "CRMUser",
    "CRMEvent",
    "CRMConnectionState",
    "CRMEventType",
    "CRMObjectType",
    "OAuthCallbackResult",
    "OAuthURLResult",
    "ProviderCapabilities",
    "SyncResult",
    "SyncStats",
    "SyncStatus",
    "BaseOAuthHandler",
]
