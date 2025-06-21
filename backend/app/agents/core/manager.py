from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json

from .base import BaseAgent, AgentConfig, AgentRole, Department, AgentState

class ManagerAgent(BaseAgent):
    """
    Manager agent responsible for coordinating specialized agents and
    executing high-level strategic decisions from the CoFounder.
    """
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        # Set default config values if not provided
        default_config = {
            "id": "manager",
            "name": "Alex Thompson",
            "role": AgentRole.MANAGER,
            "department": Department.OPERATIONS,
            "level": 2,
            "manager_id": "cofounder",
            "system_prompt": (
                "You are Alex Thompson, Manager Agent at AgentFlow Pro.\n"
                "Your role is to execute strategic decisions from the Co-Founder, "
                "coordinate specialized agents, break down complex goals into "
                "actionable tasks, manage workflow, and consolidate results.\n"
                "You report to the Co-Founder and oversee all specialized agents."
            ),
            "tools": ["team_coordination", "workflow_management", "reporting"],
            "specializations": ["Workflow Management", "Team Coordination", "Execution"],
            "performance_metrics": {
                "tasks_coordinated": 0,
                "team_efficiency": 0.0,
                "goal_achievement": 0.0
            },
            "direct_reports": [
                "crm_agent", "email_marketing_agent", "invoice_agent",
                "scheduling_agent", "social_agent", "hr_agent",
                "admin_agent", "review_agent"
            ]
        }
        
        # Merge provided config with defaults
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state: AgentState, context: Dict[str, Any]) -> AIMessage:
        """Generate a coordination response based on the current state and context"""
        # Build the system prompt with context
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {state.context.get('task_description', 'No task description')}
        
        Available Specialists:
        - CRM Agent: For lead management, customer relationships, sales pipeline
        - Email Marketing Agent: For email campaigns, drip sequences, automation
        - Invoice Agent: For billing, payments, financial transactions
        - Scheduling Agent: For appointments, calendar management, reminders
        - Social Agent: For social media management, content, engagement
        - HR Agent: For employee management, payroll, time tracking
        - Admin Agent: For forms, documents, reports, data processing
        - Review Agent: For customer feedback, reviews, sentiment analysis
        
        Analyze the request and determine which specialist(s) should be involved.
        Break down the work into specific tasks and coordinate the workflow.
        """
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response using the language model
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Determine next agent based on response content and CoFounder suggestions
        content_lower = response.content.lower()
        
        # Check for CoFounder's suggested vertical first
        if state.context.get("suggested_vertical"):
            state.next_agent = state.context["suggested_vertical"]
        # Otherwise, analyze content to determine appropriate vertical agent
        elif any(word in content_lower for word in ["crm", "lead", "customer", "pipeline", "prospect"]):
            state.next_agent = "crm_agent"
        elif any(word in content_lower for word in ["email", "campaign", "newsletter", "drip", "automation"]):
            state.next_agent = "email_marketing_agent"
        elif any(word in content_lower for word in ["invoice", "billing", "payment", "finance", "money"]):
            state.next_agent = "invoice_agent"
        elif any(word in content_lower for word in ["schedule", "calendar", "appointment", "meeting", "booking"]):
            state.next_agent = "scheduling_agent"
        elif any(word in content_lower for word in ["social", "post", "content", "engagement", "media"]):
            state.next_agent = "social_agent"
        elif any(word in content_lower for word in ["hr", "employee", "payroll", "leave", "time"]):
            state.next_agent = "hr_agent"
        elif any(word in content_lower for word in ["admin", "form", "document", "report", "data"]):
            state.next_agent = "admin_agent"
        elif any(word in content_lower for word in ["review", "feedback", "rating", "sentiment", "opinion"]):
            state.next_agent = "review_agent"
        else:
            # Default to CRM agent for general business tasks
            state.next_agent = "crm_agent"
        
        # Update performance metrics
        self.config.performance_metrics["tasks_coordinated"] += 1
        
        return response
    
    def _update_state(self, state: AgentState, response: AIMessage, context: Dict[str, Any]) -> AgentState:
        """Update the state with additional Manager-specific logic"""
        # Call parent implementation first
        state = super()._update_state(state, response, context)
        
        # Add Manager-specific state updates
        state.context["coordinated_by"] = self.config.name
        state.context["assigned_agent"] = state.next_agent
        
        # Add workflow tracking
        if "workflow_steps" not in state.context:
            state.context["workflow_steps"] = []
            
        state.context["workflow_steps"].append({
            "step": f"Managed by {self.config.name}",
            "action": f"Delegated to {state.next_agent}",
            "timestamp": state.reasoning_steps[-1]["timestamp"] if state.reasoning_steps else ""
        })
        
        return state
