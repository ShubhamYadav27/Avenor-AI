"""
OpenAI Provider Adapter
"""
import os
from typing import AsyncGenerator, List
from app.modules.copilot.domain.entities import CopilotMessageEntity
from app.modules.copilot.domain.exceptions import ProviderUnavailableError
from app.modules.copilot.domain.interfaces import ILLMProviderAdapter


class OpenAIAdapter(ILLMProviderAdapter):
    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_response(
        self, messages: List[CopilotMessageEntity], system_prompt: str, model_name: str, **kwargs
    ) -> str:
        if not self._api_key:
            raise ProviderUnavailableError("openai", "OPENAI_API_KEY environment variable is not configured.")

        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self._api_key)
            formatted_messages = [{"role": "system", "content": system_prompt}]
            for m in messages:
                formatted_messages.append({"role": m.role.value, "content": m.content})

            response = await client.chat.completions.create(
                model=model_name or "gpt-4o",
                messages=formatted_messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise ProviderUnavailableError("openai", str(e))

    async def generate_stream(
        self, messages: List[CopilotMessageEntity], system_prompt: str, model_name: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        if not self._api_key:
            raise ProviderUnavailableError("openai", "OPENAI_API_KEY environment variable is not configured.")

        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self._api_key)
            formatted_messages = [{"role": "system", "content": system_prompt}]
            for m in messages:
                formatted_messages.append({"role": m.role.value, "content": m.content})

            stream = await client.chat.completions.create(
                model=model_name or "gpt-4o",
                messages=formatted_messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise ProviderUnavailableError("openai", str(e))
