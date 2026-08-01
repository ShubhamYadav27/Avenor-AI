"""
StreamingService
Manages SSE lifecycle, event encoding, and streaming delivery across protocols.
"""
import json
from typing import AsyncGenerator, Dict, Any


class StreamingService:
    def __init__(self, ping_interval: int = 15):
        self.ping_interval = ping_interval

    def encode_sse_event(self, event: str, data: Dict[str, Any]) -> str:
        """Formats a JSON dictionary as a Server-Sent Event (SSE) message."""
        payload = json.dumps(data)
        return f"event: {event}\ndata: {payload}\n\n"

    async def format_stream(
        self, token_generator: AsyncGenerator[str, None]
    ) -> AsyncGenerator[str, None]:
        """Wraps token generator into SSE event stream."""
        yield self.encode_sse_event("start", {"status": "streaming_started"})
        
        full_content = []
        try:
            async for token in token_generator:
                full_content.append(token)
                yield self.encode_sse_event("token", {"delta": token})
            
            yield self.encode_sse_event(
                "done",
                {
                    "status": "completed",
                    "full_content": "".join(full_content),
                },
            )
        except Exception as e:
            yield self.encode_sse_event("error", {"message": str(e), "code": "STREAMING_ERROR"})


streaming_service = StreamingService()
