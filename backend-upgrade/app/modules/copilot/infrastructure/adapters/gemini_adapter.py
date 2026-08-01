"""
Gemini Provider Adapter
"""
import os
from typing import AsyncGenerator, List
from app.modules.copilot.domain.entities import CopilotMessageEntity
from app.modules.copilot.domain.exceptions import ProviderUnavailableError
from app.modules.copilot.domain.interfaces import ILLMProviderAdapter


class GeminiAdapter(ILLMProviderAdapter):
    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate_response(
        self, messages: List[CopilotMessageEntity], system_prompt: str, model_name: str, **kwargs
    ) -> str:
        if not self._api_key:
            raise ProviderUnavailableError("gemini", "GEMINI_API_KEY environment variable is not configured.")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel(
                model_name=model_name or "gemini-1.5-pro",
                system_instruction=system_prompt,
            )
            chat_history = []
            for m in messages[:-1]:
                role = "user" if m.role.value == "user" else "model"
                chat_history.append({"role": role, "parts": [m.content]})

            latest = messages[-1].content if messages else ""
            chat = model.start_chat(history=chat_history)
            response = await chat.send_message_async(latest)
            return response.text or ""
        except Exception as e:
            raise ProviderUnavailableError("gemini", str(e))

    async def generate_stream(
        self, messages: List[CopilotMessageEntity], system_prompt: str, model_name: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        if not self._api_key:
            raise ProviderUnavailableError("gemini", "GEMINI_API_KEY environment variable is not configured.")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel(
                model_name=model_name or "gemini-1.5-pro",
                system_instruction=system_prompt,
            )
            chat_history = []
            for m in messages[:-1]:
                role = "user" if m.role.value == "user" else "model"
                chat_history.append({"role": role, "parts": [m.content]})

            latest = messages[-1].content if messages else ""
            chat = model.start_chat(history=chat_history)
            response = await chat.send_message_async(latest, stream=True)
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise ProviderUnavailableError("gemini", str(e))
