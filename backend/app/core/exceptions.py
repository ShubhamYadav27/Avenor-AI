"""
Domain exceptions. Raise these from modules; catch them in API routes
and translate to HTTP responses.
"""


class AvenorError(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, code: str = "internal_error"):
        self.message = message
        self.code = code
        super().__init__(message)


# ── Resource errors ──────────────────────────────────────────

class NotFoundError(AvenorError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            code="not_found",
        )
        self.resource = resource
        self.identifier = identifier


class ConflictError(AvenorError):
    def __init__(self, message: str):
        super().__init__(message=message, code="conflict")


# ── Auth errors ───────────────────────────────────────────────

class AuthenticationError(AvenorError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, code="unauthenticated")


class AuthorizationError(AvenorError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, code="unauthorized")


# ── External service errors ────────────────────────────────────

class ExternalServiceError(AvenorError):
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} error: {message}",
            code="external_service_error",
        )
        self.service = service


class RateLimitError(AvenorError):
    def __init__(self, service: str, retry_after_seconds: int = 60):
        super().__init__(
            message=f"{service} rate limit hit. Retry after {retry_after_seconds}s",
            code="rate_limited",
        )
        self.retry_after_seconds = retry_after_seconds


# ── Validation errors ─────────────────────────────────────────

class ValidationError(AvenorError):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message=message, code="validation_error")
        self.field = field


# ── Intelligence errors ───────────────────────────────────────

class InsufficientDataError(AvenorError):
    """Raised when there is not enough data to generate a prediction."""
    def __init__(self, message: str = "Insufficient data for prediction"):
        super().__init__(message=message, code="insufficient_data")


class LLMError(AvenorError):
    """Raised when LLM generation fails or produces unusable output."""
    def __init__(self, message: str):
        super().__init__(message=message, code="llm_error")
