from typing import Optional

class SdkException(Exception):
    """Base exception for all SDKs, mapped from HTTP errors."""
    def __init__(self, message: str, status_code: int, request_id: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id

class AuthenticationError(SdkException):
    """HTTP 401"""
    pass

class AuthorizationError(SdkException):
    """HTTP 403"""
    pass

class RateLimitError(SdkException):
    """HTTP 429"""
    pass

class ValidationError(SdkException):
    """HTTP 400"""
    pass

class NotFoundError(SdkException):
    """HTTP 404"""
    pass

class ServerError(SdkException):
    """HTTP 5xx"""
    pass
