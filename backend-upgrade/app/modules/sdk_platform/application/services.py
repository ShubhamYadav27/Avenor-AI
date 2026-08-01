from typing import List, Dict, Any, Optional
import time

from app.modules.sdk_platform.domain.models import SdkLanguage, SdkRelease, SdkConfig
from app.modules.sdk_platform.domain.exceptions import (
    SdkException, AuthenticationError, AuthorizationError, RateLimitError,
    ValidationError, NotFoundError, ServerError
)

class SdkRegistry:
    """Manages active SDK releases across all supported languages."""
    def __init__(self):
        self._releases: List[SdkRelease] = []

    def register_release(self, release: SdkRelease):
        self._releases.append(release)

    def get_latest(self, language: SdkLanguage) -> Optional[SdkRelease]:
        for r in sorted(self._releases, key=lambda x: x.published_at, reverse=True):
            if r.language == language and r.is_latest:
                return r
        return None

class ErrorMapper:
    """Maps HTTP Status Codes to strictly typed SDK Exceptions."""
    @staticmethod
    def map_http_response(status_code: int, payload: Dict[str, Any]) -> None:
        if 200 <= status_code < 300:
            return
            
        req_id = payload.get("request_id")
        msg = payload.get("message", f"API Error: {status_code}")
        
        if status_code == 401:
            raise AuthenticationError(msg, status_code, req_id)
        if status_code == 403:
            raise AuthorizationError(msg, status_code, req_id)
        if status_code == 429:
            raise RateLimitError(msg, status_code, req_id)
        if status_code == 400:
            raise ValidationError(msg, status_code, req_id)
        if status_code == 404:
            raise NotFoundError(msg, status_code, req_id)
        
        raise ServerError(msg, status_code, req_id)

class RequestPipelineBuilder:
    """
    Simulates the core Request/Response pipeline logic embedded in all SDKs.
    Handles Exponential Backoff and Error Mapping.
    """
    def __init__(self, config: SdkConfig):
        self.config = config

    def execute_with_retries(self, api_call_func) -> Dict[str, Any]:
        """
        Executes a mock API call function, handling rate limits with exponential backoff.
        """
        retries = 0
        while retries <= self.config.max_retries:
            status_code, payload = api_call_func()
            
            try:
                ErrorMapper.map_http_response(status_code, payload)
                return payload
            except RateLimitError as e:
                if retries == self.config.max_retries:
                    raise e
                
                # Exponential backoff simulation
                backoff_time = (2 ** retries) * 0.1 # 0.1s, 0.2s, 0.4s
                time.sleep(backoff_time)
                retries += 1
            except SdkException as e:
                # Other exceptions do not retry
                raise e
        
        raise ServerError("Max retries exceeded", 500)
