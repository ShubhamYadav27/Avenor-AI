class MarketplaceError(Exception):
    """Base exception for Marketplace domain."""
    pass

class AppNotFoundError(MarketplaceError):
    pass

class InstallationNotFoundError(MarketplaceError):
    pass

class PermissionDeniedError(MarketplaceError):
    pass

class InvalidAppConfigurationError(MarketplaceError):
    pass

class CircularDependencyError(MarketplaceError):
    pass

class IncompatibleVersionError(MarketplaceError):
    pass

class PublisherVerificationError(MarketplaceError):
    pass

