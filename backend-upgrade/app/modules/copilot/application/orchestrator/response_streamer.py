"""
Response Streamer
Orchestrates streaming token delivery across model adapters.
"""
from typing import AsyncGenerator, List
from app.modules.copilot.domain.entities import CopilotMessageEntity
from app.modules.copilot.domain.interfaces import ILLMProviderAdapter
from app.modules.copilot.infrastructure.streaming.streaming_service import streaming_service


class ResponseStreamer:
    async def stream_tokens(
        self,
        adapter: ILLMProviderAdapter,
        messages: List[CopilotMessageEntity],
        system_prompt: str,
        model_name: str,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        async for chunk in adapter.generate_stream(messages, system_prompt, model_name, **kwargs):
            yield chunk

    def format_sse(self, token_generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
        return streaming_service.format_stream(token_generator)


response_streamer = ResponseStreamer()
