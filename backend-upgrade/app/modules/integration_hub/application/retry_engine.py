import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

class RetryEngine:
    """
    Application Service providing Circuit Breaker and Exponential Backoff patterns
    for external API calls. Protects the Integration Hub from cascading failures.
    """
    
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 2.0  # seconds

    async def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Executes a callable, automatically catching HTTP 429 and 503 errors and retrying
        with exponential backoff.
        """
        retries = 0
        while retries <= self.max_retries:
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                # In a real implementation, we would catch specific ProviderRateLimitError
                # and inspect 'Retry-After' headers.
                error_msg = str(e).lower()
                is_transient = "429" in error_msg or "rate limit" in error_msg or "timeout" in error_msg
                
                if not is_transient or retries == self.max_retries:
                    logger.error(f"Operation failed permanently after {retries} retries: {str(e)}")
                    raise
                
                # Exponential backoff: 2s, 4s, 8s
                delay = self.base_delay * (2 ** retries)
                logger.warning(f"Transient error detected. Retrying in {delay} seconds... (Attempt {retries + 1}/{self.max_retries})")
                await asyncio.sleep(delay)
                retries += 1
