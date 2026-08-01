"""
Mock LLM Provider Adapter
Production-ready deterministic mock adapter for offline testing and fallbacks.
"""
import asyncio
from typing import AsyncGenerator, List

from app.modules.copilot.domain.entities import CopilotMessageEntity
from app.modules.copilot.domain.interfaces import ILLMProviderAdapter


class MockLLMAdapter(ILLMProviderAdapter):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate_response(
        self, messages: List[CopilotMessageEntity], system_prompt: str, model_name: str, **kwargs
    ) -> str:
        user_query = messages[-1].content if messages else "help"
        return (
            f"[Avenor Revenue Strategist Mock Response]\n\n"
            f"Based on our predictive revenue intelligence platform analysis, "
            f"here is the recommendation for your query: '{user_query}'.\n\n"
            f"1. **High Intent Opportunity**: Prioritize outreach to accounts with active hiring and expansion buying signals.\n"
            f"2. **Strategic Angle**: Focus on economic ROI and time-to-value.\n"
            f"3. **Recommended Action**: Review your account intelligence feed and initiate personalized email sequences."
        )

    async def generate_stream(
        self, messages: List[CopilotMessageEntity], system_prompt: str, model_name: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        full_text = await self.generate_response(messages, system_prompt, model_name, **kwargs)
        # Stream word by word with slight delay
        words = full_text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == len(words) - 1 else word + " "
            yield chunk
            await asyncio.sleep(0.03)
