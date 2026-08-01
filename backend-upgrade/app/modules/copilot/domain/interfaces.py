"""
Copilot Domain Interfaces (Ports)
Abstract interfaces defining repository, provider, context engine, and tool orchestration contracts.
"""
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional
import uuid

from app.modules.copilot.domain.context import ContextCategory, ContextIntent, ContextItem, UnifiedContext
from app.modules.copilot.domain.entities import (
    CopilotMessageEntity,
    CopilotStateEntity,
    CopilotThreadEntity,
)
from app.modules.copilot.domain.memory_entities import (
    MemoryConsolidationResult,
    MemoryItem,
    MemoryPackage,
    MemoryRetrievalPlan,
)
from app.modules.copilot.domain.tools import (
    ExecutionNode,
    ToolExecutionPlan,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolSpecification,
    UnifiedIntelligencePackage,
)




class IThreadRepository(ABC):
    @abstractmethod
    async def create(self, thread: CopilotThreadEntity) -> CopilotThreadEntity:
        pass

    @abstractmethod
    async def get_by_id(self, thread_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[CopilotThreadEntity]:
        pass

    @abstractmethod
    async def list_by_workspace(
        self, workspace_id: uuid.UUID, user_id: Optional[uuid.UUID] = None, limit: int = 50, offset: int = 0
    ) -> List[CopilotThreadEntity]:
        pass

    @abstractmethod
    async def update(self, thread: CopilotThreadEntity) -> CopilotThreadEntity:
        pass

    @abstractmethod
    async def delete(self, thread_id: uuid.UUID, workspace_id: uuid.UUID) -> bool:
        pass


class IMessageRepository(ABC):
    @abstractmethod
    async def add_message(self, message: CopilotMessageEntity) -> CopilotMessageEntity:
        pass

    @abstractmethod
    async def get_messages(self, thread_id: uuid.UUID, limit: int = 100) -> List[CopilotMessageEntity]:
        pass


class IStateRepository(ABC):
    @abstractmethod
    async def get_state(self, thread_id: uuid.UUID, workspace_id: uuid.UUID) -> Optional[CopilotStateEntity]:
        pass

    @abstractmethod
    async def upsert_state(self, state: CopilotStateEntity) -> CopilotStateEntity:
        pass


class ILLMProviderAdapter(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def generate_response(
        self, messages: List[CopilotMessageEntity], system_prompt: str, model_name: str, **kwargs
    ) -> str:
        pass

    @abstractmethod
    async def generate_stream(
        self, messages: List[CopilotMessageEntity], system_prompt: str, model_name: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        pass


class IContextProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def category(self) -> ContextCategory:
        pass

    @abstractmethod
    def supports_intent(self, intent: ContextIntent) -> bool:
        pass

    @abstractmethod
    async def fetch_context(
        self, workspace_id: uuid.UUID, query: str, state: Optional[CopilotStateEntity] = None
    ) -> List[ContextItem]:
        pass


class IContextEngine(ABC):
    @abstractmethod
    async def assemble_context(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        state: Optional[CopilotStateEntity] = None,
        max_token_budget: int = 4000,
    ) -> UnifiedContext:
        pass


# Phase 5.5.3 Tool Orchestration Interfaces (Ports)
class ITool(ABC):
    @property
    @abstractmethod
    def spec(self) -> ToolSpecification:
        pass

    @abstractmethod
    async def can_execute(self, request: ToolExecutionRequest) -> bool:
        pass

    @abstractmethod
    async def execute(self, request: ToolExecutionRequest, db: Optional[Any] = None) -> ToolExecutionResult:
        pass


class IToolRegistry(ABC):
    @abstractmethod
    def register_tool(self, tool: ITool) -> None:
        pass

    @abstractmethod
    def get_tool(self, name: str) -> Optional[ITool]:
        pass

    @abstractmethod
    def get_tools_for_intent(self, intent: ContextIntent) -> List[ITool]:
        pass

    @abstractmethod
    def list_all_tools(self) -> List[ITool]:
        pass


class IToolPlanner(ABC):
    @abstractmethod
    def create_plan(
        self,
        intent: ContextIntent,
        context: UnifiedContext,
        available_tools: List[ITool],
    ) -> ToolExecutionPlan:
        pass


class IToolRouter(ABC):
    @abstractmethod
    def build_execution_stages(
        self,
        plan: ToolExecutionPlan,
        registry: IToolRegistry,
    ) -> List[List[ExecutionNode]]:
        pass


class IToolExecutionEngine(ABC):
    @abstractmethod
    async def execute_plan(
        self,
        plan: ToolExecutionPlan,
        request: ToolExecutionRequest,
        db: Optional[Any] = None,
    ) -> UnifiedIntelligencePackage:
        pass


# Phase 5.5.4 Enterprise Memory Engine Interfaces (Ports)
class IMemoryAdapter(ABC):
    @abstractmethod
    async def save_memory(self, item: MemoryItem) -> MemoryItem:
        pass

    @abstractmethod
    async def get_memory_by_id(self, memory_id: str, workspace_id: uuid.UUID) -> Optional[MemoryItem]:
        pass

    @abstractmethod
    async def query_memories(
        self,
        workspace_id: uuid.UUID,
        categories: Optional[List[str]] = None,
        entity_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[MemoryItem]:
        pass

    @abstractmethod
    async def update_memory(self, item: MemoryItem) -> MemoryItem:
        pass


class IMemoryPlanner(ABC):
    @abstractmethod
    def create_retrieval_plan(
        self,
        workspace_id: uuid.UUID,
        query: str,
        intent: ContextIntent,
    ) -> MemoryRetrievalPlan:
        pass


class IMemoryEngine(ABC):
    @abstractmethod
    async def retrieve_memories(
        self,
        workspace_id: uuid.UUID,
        query: str,
        intent: ContextIntent,
        thread_id: Optional[uuid.UUID] = None,
    ) -> MemoryPackage:
        pass

    @abstractmethod
    async def consolidate_and_persist(
        self,
        workspace_id: uuid.UUID,
        raw_items: List[MemoryItem],
    ) -> MemoryConsolidationResult:
        pass


class ICitationCollector(ABC):
    @abstractmethod
    def collect_evidence(
        self,
        context: Optional[UnifiedContext] = None,
        intelligence_pkg: Optional[UnifiedIntelligencePackage] = None,
        memory_pkg: Optional[MemoryPackage] = None,
    ) -> List[Any]:
        pass


class ICitationEngine(ABC):
    @abstractmethod
    async def generate_citation_package(
        self,
        workspace_id: uuid.UUID,
        query: str,
        intent: ContextIntent,
        context: Optional[UnifiedContext] = None,
        intelligence_pkg: Optional[UnifiedIntelligencePackage] = None,
        memory_pkg: Optional[MemoryPackage] = None,
        thread_id: Optional[uuid.UUID] = None,
    ) -> Any:
        pass


class IFeedbackCollector(ABC):
    @abstractmethod
    async def submit_feedback(
        self,
        workspace_id: uuid.UUID,
        feedback_type: str,
        rating: float,
        thread_id: Optional[uuid.UUID] = None,
        message_id: Optional[uuid.UUID] = None,
        correction_text: Optional[str] = None,
    ) -> Any:
        pass


class ILearningEngine(ABC):
    @abstractmethod
    async def process_learning_cycle(
        self,
        workspace_id: uuid.UUID,
    ) -> Any:
        pass


class IWorkflowPlanner(ABC):
    @abstractmethod
    def create_workflow_plan(
        self,
        workspace_id: uuid.UUID,
        workflow_type: str,
        target_entity_id: Optional[str] = None,
    ) -> Any:
        pass


class IWorkflowEngine(ABC):
    @abstractmethod
    async def execute_workflow(
        self,
        workspace_id: uuid.UUID,
        workflow_name: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        pass


class IAgentRegistry(ABC):
    @abstractmethod
    def list_agents(self) -> List[Any]:
        pass


class IMultiAgentEngine(ABC):
    @abstractmethod
    async def execute_collaboration(
        self,
        workspace_id: uuid.UUID,
        user_query: str,
        target_entity_id: Optional[str] = None,
    ) -> Any:
        pass


class IPredictiveEngine(ABC):
    @abstractmethod
    async def predict_account_intelligence(
        self,
        workspace_id: uuid.UUID,
        company_id: str,
    ) -> Any:
        pass


class IRevenueDecisionEngine(ABC):
    @abstractmethod
    async def decide_next_best_action(
        self,
        workspace_id: uuid.UUID,
        company_id: str,
    ) -> Any:
        pass


class IAutonomousRevOpsEngine(ABC):
    @abstractmethod
    async def plan_and_execute_mission(
        self,
        workspace_id: uuid.UUID,
        mission_type: str,
        target_company_ids: List[str],
    ) -> Any:
        pass


class IRevenueOSEngine(ABC):
    @abstractmethod
    async def get_operating_system_status(
        self,
        workspace_id: uuid.UUID,
    ) -> Any:
        pass










