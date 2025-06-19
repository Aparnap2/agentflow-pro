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
                "legal_agent", "finance_agent", "healthcare_agent",
                "manufacturing_agent", "ecommerce_agent", "coaching_agent",
                "sales", "support", "growth"
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
        - Legal Agent: For contracts, compliance, legal research
        - Finance Agent: For portfolio analysis, tax, financial modeling
        - Healthcare Agent: For patient data, HIPAA compliance, treatment planning
        - Manufacturing Agent: For predictive maintenance, quality control
        - E-commerce Agent: For cart recovery, product recommendations, Shopify
        - Coaching Agent: For lead follow-up, client management
        - Sales: For lead generation, revenue growth
        - Support: For customer service, issue resolution
        - Growth: For marketing campaigns, user acquisition
        
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
        
        # Determine next agent based on response content
        content_lower = response.content.lower()
        
        # Check for vertical industry agents first
        if any(word in content_lower for word in ["legal", "contract", "compliance"]):
            state.next_agent = "legal_agent"
        elif any(word in content_lower for word in ["finance", "portfolio", "tax"]):
            state.next_agent = "finance_agent"
        elif any(word in content_lower for word in ["healthcare", "medical", "patient"]):
            state.next_agent = "healthcare_agent"
        elif any(word in content_lower for word in ["manufacturing", "production", "quality"]):
            state.next_agent = "manufacturing_agent"
        elif any(word in content_lower for word in ["ecommerce", "shopify", "cart"]):
            state.next_agent = "ecommerce_agent"
        elif any(word in content_lower for word in ["coaching", "training", "mentoring"]):
            state.next_agent = "coaching_agent"
        # Fallback to generic agents
        elif any(word in content_lower for word in ["sales", "revenue", "leads"]):
            state.next_agent = "sales"
        elif any(word in content_lower for word in ["support", "customer", "tickets"]):
            state.next_agent = "support"
        elif any(word in content_lower for word in ["growth", "marketing", "campaigns"]):
            state.next_agent = "growth"
        else:
            # Default to sales for business-related tasks
            state.next_agent = "sales"
        
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
