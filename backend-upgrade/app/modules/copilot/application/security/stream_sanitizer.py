"""
Stream Sanitizer (Phase 5.5.6)
Real-time SSE token stream sanitizer scrubbing PII, API keys, and sensitive tokens.
"""
import re
from typing import AsyncGenerator

SECRET_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9]{24,}", re.IGNORECASE), "[REDACTED_API_KEY]"),
    (re.compile(r"bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
]


class StreamSanitizer:
    def sanitize_text(self, text: str) -> str:
        sanitized = text
        for pattern, replacement in SECRET_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    async def sanitize_stream(self, generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
        async for chunk in generator:
            yield self.sanitize_text(chunk)


stream_sanitizer = StreamSanitizer()
