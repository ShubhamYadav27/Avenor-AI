from app.modules.copilot.application.orchestrator.prompt_builder import prompt_builder
from app.modules.copilot.application.orchestrator.history_manager import history_manager
from app.modules.copilot.application.orchestrator.provider_router import provider_router
from app.modules.copilot.domain.entities import CopilotMessageEntity, CopilotRole
import uuid


def test_prompt_builder():
    prompt = prompt_builder.build_system_prompt(
        workspace_context={"name": "Acme Corp", "tier": "Scale", "crm_provider": "hubspot"}
    )
    assert "Avenor AI Revenue Copilot" in prompt
    assert "Acme Corp" in prompt
    assert "hubspot" in prompt


def test_history_manager_trimming():
    messages = [
        CopilotMessageEntity(
            id=uuid.uuid4(),
            thread_id=uuid.uuid4(),
            role=CopilotRole.USER,
            content=f"Message {i} content text",
        )
        for i in range(30)
    ]

    trimmed = history_manager.prepare_messages(messages, token_budget=500)
    assert len(trimmed) <= 20


def test_provider_router_chain():
    chain = provider_router.resolve_provider_chain("gemini", "gemini-1.5-pro")
    assert chain[0] == ("gemini", "gemini-1.5-pro")
    assert ("mock", "mock-model") in chain
