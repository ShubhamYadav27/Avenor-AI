"""
AI module — provider-agnostic LLM access for the Avenor Revenue Copilot.

Layering (business logic must never import a concrete provider):

    research_service.py   orchestration, caching, persistence
        ├── context.py    gathers Avenor intelligence into a typed context
        ├── prompts.py    versioned prompt templates
        ├── schemas.py    Pydantic contracts for LLM output and the API
        └── provider.py   LLMProvider ABC + concrete implementations
"""
