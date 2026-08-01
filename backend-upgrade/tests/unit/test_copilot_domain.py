import uuid
from app.modules.copilot.domain.entities import (
    CopilotThreadEntity,
    CopilotStateEntity,
    ModelCapability,
    ModelDescriptor,
)
from app.modules.copilot.domain.exceptions import (
    ThreadNotFoundError,
    ProviderUnavailableError,
)
from app.modules.copilot.domain.events import (
    ThreadCreatedEvent,
)


def test_copilot_domain_entities():
    thread_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    user_id = uuid.uuid4()

    thread = CopilotThreadEntity(
        id=thread_id,
        workspace_id=workspace_id,
        user_id=user_id,
        title="Test Session",
    )

    assert thread.id == thread_id
    assert thread.workspace_id == workspace_id
    assert thread.title == "Test Session"
    assert thread.messages == []


def test_copilot_state_entity():
    thread_id = uuid.uuid4()
    workspace_id = uuid.uuid4()

    state = CopilotStateEntity(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        thread_id=thread_id,
        token_budget=16000,
    )

    assert state.thread_id == thread_id
    assert state.token_budget == 16000
    assert state.current_company_id is None


def test_model_capability_descriptor():
    cap = ModelCapability(supports_streaming=True, supports_tools=True)
    desc = ModelDescriptor(provider="gemini", name="gemini-1.5-pro", capabilities=cap)

    assert desc.provider == "gemini"
    assert desc.capabilities.supports_streaming is True


def test_copilot_domain_exceptions():
    err = ThreadNotFoundError("12345")
    assert err.code == "THREAD_NOT_FOUND"
    assert "12345" in err.message

    provider_err = ProviderUnavailableError("openai", "Key missing")
    assert provider_err.code == "PROVIDER_UNAVAILABLE"


def test_copilot_events():
    event = ThreadCreatedEvent(workspace_id=uuid.uuid4(), thread_id=uuid.uuid4())
    assert event.event_type == "copilot.thread.created"
    assert event.event_id is not None
