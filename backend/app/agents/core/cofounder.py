from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json

from .base import BaseAgent, AgentConfig, AgentRole, Department, AgentState

class CoFounderAgent(BaseAgent):
    """
    CoFounder agent responsible for high-level strategic decisions and vision.
    Acts as the entry point for complex tasks requiring strategic thinking.
    """
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        # Set default config values if not provided
        default_config = {
            "id": "cofounder",
            "name": "Sarah Chen",
            "role": AgentRole.COFOUNDER,
            "department": Department.LEADERSHIP,
            "level": 1,
            "system_prompt": (
                "You are Sarah Chen, Co-Founder and Strategic Visionary of AgentFlow Pro.\n"
                "Your role is to make high-level strategic decisions, provide vision and direction "
                "for the company, evaluate opportunities and risks, and guide the leadership team.\n"
                "Focus on long-term implications and provide clear strategic direction."
            ),
            "tools": ["strategic_planning", "market_analysis", "investor_relations"],
            "specializations": ["Strategic Vision", "Market Analysis", "Leadership"],
            "performance_metrics": {
                "decisions_made": 45,
                "strategic_accuracy": 92.0,
                "team_satisfaction": 4.8
            }
        }
        
        # Merge provided config with defaults
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state: AgentState, context: Dict[str, Any]) -> AIMessage:
        """Generate a strategic response based on the current state and context"""
        # Build the system prompt with context
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Context:
        {json.dumps(context.get('task_context', {}), indent=2)}
        
        Relevant Memories:
        {json.dumps(context.get('memories', []), indent=2)}
        
        Consider the long-term strategic implications and provide clear direction.
        If this requires coordination with other team members, indicate who should be involved next.
        """
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response using the language model
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update next agent based on response content - Route to Manager for execution
        content_lower = response.content.lower()
        
        # For strategic decisions, always route to Manager for execution
        # Manager will then coordinate with appropriate vertical agents
        state.next_agent = "manager"
        
        # Add strategic context for the Manager
        if any(word in content_lower for word in ["crm", "leads", "customers", "pipeline"]):
            state.context["suggested_vertical"] = "crm_agent"
        elif any(word in content_lower for word in ["email", "campaign", "newsletter", "marketing"]):
            state.context["suggested_vertical"] = "email_marketing_agent"
        elif any(word in content_lower for word in ["invoice", "billing", "payment", "finance"]):
            state.context["suggested_vertical"] = "invoice_agent"
        elif any(word in content_lower for word in ["schedule", "calendar", "appointment", "meeting"]):
            state.context["suggested_vertical"] = "scheduling_agent"
        elif any(word in content_lower for word in ["social", "post", "content", "engagement"]):
            state.context["suggested_vertical"] = "social_agent"
        elif any(word in content_lower for word in ["hr", "employee", "payroll", "leave"]):
            state.context["suggested_vertical"] = "hr_agent"
        elif any(word in content_lower for word in ["admin", "form", "document", "report"]):
            state.context["suggested_vertical"] = "admin_agent"
        elif any(word in content_lower for word in ["review", "feedback", "rating", "sentiment"]):
            state.context["suggested_vertical"] = "review_agent"
        
        return response
    
    def _update_state(self, state: AgentState, response: AIMessage, context: Dict[str, Any]) -> AgentState:
        """Update the state with additional CoFounder-specific logic"""
        # Call parent implementation first
        state = super()._update_state(state, response, context)
        
        # Add CoFounder-specific state updates
        state.context["strategic_direction"] = response.content
        state.context["decision_maker"] = self.config.name
        
        return state
