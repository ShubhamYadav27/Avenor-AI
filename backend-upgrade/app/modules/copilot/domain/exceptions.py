"""
Copilot Domain Exceptions
"""


class CopilotDomainError(Exception):
    """Base domain exception for Copilot."""

    def __init__(self, message: str, code: str = "COPILOT_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class ThreadNotFoundError(CopilotDomainError):
    def __init__(self, thread_id: str):
        super().__init__(f"Conversation thread '{thread_id}' not found.", code="THREAD_NOT_FOUND")


class MessageNotFoundError(CopilotDomainError):
    def __init__(self, message_id: str):
        super().__init__(f"Conversation message '{message_id}' not found.", code="MESSAGE_NOT_FOUND")


class ProviderUnavailableError(CopilotDomainError):
    def __init__(self, provider_name: str, detail: str = ""):
        msg = f"LLM Provider '{provider_name}' is currently unavailable."
        if detail:
            msg += f" Details: {detail}"
        super().__init__(msg, code="PROVIDER_UNAVAILABLE")


class ContextWindowExceededError(CopilotDomainError):
    def __init__(self, token_count: int, max_budget: int):
        super().__init__(
            f"Context window exceeded: {token_count} tokens requested, maximum budget is {max_budget}.",
            code="CONTEXT_EXCEEDED",
        )
