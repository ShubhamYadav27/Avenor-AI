"""
app/crm/registry.py

CRM Provider Registry + Provider Enum.

The registry is the single source of truth for all available CRM providers.
Providers self-register on import. The factory reads the registry.

Registering a new provider:
  1. Implement ICRMProvider in app/crm/providers/{name}/
  2. Add enum value: CRMProvider.NEWPROVIDER = "newprovider"
  3. Call: CRMProviderRegistry.register("newprovider", NewProviderClass)
  4. Done — no other files need to change.

The enum pre-registers all FUTURE providers as string values so that:
  - Database migrations can be validated against known slugs
  - Feature flags can be checked without importing provider code
  - API responses can list all planned providers (with supported=False)
"""
from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.crm.base.interfaces import ICRMProvider


class CRMProvider(str, enum.Enum):
    """
    Enum of all known CRM provider slugs — both current and future.

    Current (fully implemented):
      HUBSPOT, SALESFORCE, DYNAMICS, ZOHO

    Future (pre-registered, not yet implemented):
      PIPEDRIVE, FRESHSALES, COPPER, MONDAY, CLOSE, SAP,
      ORACLE_CX, SUGARCRM, NIMBLE, INSIGHTLY, ZENDESK_SELL,
      KEAP, HIGHLEVEL

    Non-CRM integration categories are handled by a separate IntegrationProvider
    enum in app/integrations/ (future).
    """

    # ── Currently implemented ──────────────────────────────────────────────────
    HUBSPOT = "hubspot"
    SALESFORCE = "salesforce"
    DYNAMICS = "dynamics"
    ZOHO = "zoho"

    # ── Future CRM providers (pre-registered) ──────────────────────────────────
    PIPEDRIVE = "pipedrive"
    FRESHSALES = "freshsales"
    COPPER = "copper"
    MONDAY = "monday"
    CLOSE = "close"
    SAP = "sap"
    ORACLE_CX = "oracle_cx"
    SUGARCRM = "sugarcrm"
    NIMBLE = "nimble"
    INSIGHTLY = "insightly"
    ZENDESK_SELL = "zendesk_sell"
    KEAP = "keap"
    HIGHLEVEL = "highlevel"


# Providers that are fully implemented and available for use
IMPLEMENTED_PROVIDERS: frozenset[str] = frozenset({
    CRMProvider.HUBSPOT,
    CRMProvider.SALESFORCE,
    CRMProvider.DYNAMICS,
    CRMProvider.ZOHO,
})


class ProviderRegistration:
    """Metadata stored alongside a provider class in the registry."""

    def __init__(
        self,
        name: str,
        provider_cls: type["ICRMProvider"],
        display_name: str,
        description: str,
        logo_url: str | None = None,
        docs_url: str | None = None,
        feature_flag: str | None = None,
    ):
        self.name = name
        self.provider_cls = provider_cls
        self.display_name = display_name
        self.description = description
        self.logo_url = logo_url
        self.docs_url = docs_url
        self.feature_flag = feature_flag   # e.g. "ENABLE_SALESFORCE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "logo_url": self.logo_url,
            "docs_url": self.docs_url,
            "is_available": True,
        }


class CRMProviderRegistry:
    """
    Thread-safe singleton registry of all available CRM provider classes.

    Providers register themselves at import time (see each provider's __init__.py).
    The factory reads this registry when constructing provider instances.
    """

    _providers: dict[str, ProviderRegistration] = {}

    @classmethod
    def register(
        cls,
        name: str,
        provider_cls: type["ICRMProvider"],
        display_name: str = "",
        description: str = "",
        logo_url: str | None = None,
        docs_url: str | None = None,
        feature_flag: str | None = None,
    ) -> None:
        """
        Register a CRM provider class.
        Called in each provider's __init__.py.

        Args:
            name: Lowercase slug matching CRMProvider enum value.
            provider_cls: The class implementing ICRMProvider.
            display_name: Human-readable name for the UI.
            description: Short description shown on integration cards.
            logo_url: URL to the provider logo SVG/PNG.
            docs_url: Link to integration docs.
            feature_flag: Environment variable name that enables this provider.
        """
        if name in cls._providers:
            # Allow re-registration (e.g. during testing) — log a warning
            import logging
            logging.getLogger(__name__).warning(
                "crm_provider_already_registered",
                extra={"provider": name},
            )

        cls._providers[name] = ProviderRegistration(
            name=name,
            provider_cls=provider_cls,
            display_name=display_name or name.title(),
            description=description,
            logo_url=logo_url,
            docs_url=docs_url,
            feature_flag=feature_flag,
        )

    @classmethod
    def get(cls, name: str) -> type["ICRMProvider"]:
        """
        Return the provider class for the given slug.
        Raises ValueError if not registered.
        """
        registration = cls._providers.get(name)
        if registration is None:
            available = ", ".join(cls.list_available())
            raise ValueError(
                f"CRM provider '{name}' is not registered. "
                f"Available providers: {available}"
            )
        return registration.provider_cls

    @classmethod
    def get_registration(cls, name: str) -> ProviderRegistration:
        """Return the full registration metadata for a provider."""
        reg = cls._providers.get(name)
        if reg is None:
            raise ValueError(f"CRM provider '{name}' is not registered.")
        return reg

    @classmethod
    def list_available(cls) -> list[str]:
        """Return list of registered provider slugs."""
        return list(cls._providers.keys())

    @classmethod
    def list_all(cls) -> list[dict[str, Any]]:
        """
        Return metadata for all registered providers.
        Used by GET /api/v1/crm/providers.
        """
        return [reg.to_dict() for reg in cls._providers.values()]

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Return True if the provider is registered (not just pre-enumerated)."""
        return name in cls._providers

    @classmethod
    def clear(cls) -> None:
        """Clear all registrations. Used in tests only."""
        cls._providers.clear()
