class PublicApiError(Exception):
    """Base exception for Public API domain."""
    pass

class UnauthorizedAccessError(PublicApiError):
    pass

class RateLimitExceededError(PublicApiError):
    pass

class InvalidScopeError(PublicApiError):
    pass
