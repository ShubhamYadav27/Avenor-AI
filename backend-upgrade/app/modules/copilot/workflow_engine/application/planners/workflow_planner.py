"""
Workflow Planner (Phase 5.5.7)
Generates structured enterprise workflow definitions for Meeting Prep, Hot Account Intent Surge, Deal Review, and Renewals.
"""
from typing import Dict, Optional

from app.modules.copilot.domain.workflow_entities import WorkflowDefinition, WorkflowStep
from app.modules.copilot.domain.workflow_value_objects import StepType, TriggerType


class WorkflowPlanner:
    def get_preset_definitions(self) -> Dict[str, WorkflowDefinition]:
        meeting_prep = WorkflowDefinition(

            name="Meeting Preparation Workflow",
            description="Retrieve CRM history, gather buying signals, research account, and generate executive briefing.",
            trigger_type=TriggerType.MANUAL,
            steps=[
                WorkflowStep(name="Fetch CRM History", type=StepType.TOOL_ACTION, action_name="CrmTool"),
                WorkflowStep(name="Gather Buying Signals", type=StepType.TOOL_ACTION, action_name="SignalTool"),
                WorkflowStep(name="Research Company", type=StepType.TOOL_ACTION, action_name="ResearchTool"),
                WorkflowStep(name="Generate Briefing", type=StepType.TOOL_ACTION, action_name="BriefingTool"),
                WorkflowStep(name="Notify Sales Rep", type=StepType.NOTIFICATION, action_name="SlackNotification"),
            ],
        )

        hot_account = WorkflowDefinition(
            name="Hot Account Intent Surge",
            description="Detect intent surge, update ICP score, create CRM task, draft outreach, and notify team.",
            trigger_type=TriggerType.BUYING_SIGNAL_SURGE,
            steps=[
                WorkflowStep(name="Detect Intent Surge", type=StepType.TOOL_ACTION, action_name="SignalTool"),
                WorkflowStep(name="Qualify Lead & ICP", type=StepType.AI_DECISION, action_name="LeadQualificationAgent"),
                WorkflowStep(name="Create CRM Followup Task", type=StepType.CRM_MUTATION, action_name="CrmTool"),
                WorkflowStep(name="Draft Personalized Email", type=StepType.TOOL_ACTION, action_name="EmailTool"),
                WorkflowStep(name="Notify Revenue Team", type=StepType.NOTIFICATION, action_name="SlackNotification"),
            ],
        )

        deal_review = WorkflowDefinition(
            name="Deal Health Review",
            description="Evaluate opportunity health, identify stagnation risks, and generate executive summary.",
            trigger_type=TriggerType.CRM_EVENT,
            steps=[
                WorkflowStep(name="Analyze CRM Opportunity", type=StepType.TOOL_ACTION, action_name="CrmTool"),
                WorkflowStep(name="Evaluate Deal Risk", type=StepType.AI_DECISION, action_name="DealRiskAgent"),
                WorkflowStep(name="Sales Coaching Brief", type=StepType.TOOL_ACTION, action_name="SalesCoachTool"),
                WorkflowStep(name="Approval Gate for Executive Escalate", type=StepType.APPROVAL_GATE, action_name="ApprovalGate"),
            ],
        )

        return {
            "meeting_prep": meeting_prep,
            "hot_account": hot_account,
            "deal_review": deal_review,
        }

    def get_definition(self, workflow_name: str) -> Optional[WorkflowDefinition]:
        presets = self.get_preset_definitions()
        key = workflow_name.lower().replace(" ", "_")
        return presets.get(key) or presets.get("meeting_prep")


workflow_planner = WorkflowPlanner()
