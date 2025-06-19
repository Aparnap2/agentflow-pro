"""Support Agent implementation for handling customer support and technical assistance."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import json
import logging
import random
from datetime import datetime, timedelta

from .base import BaseAgent, AgentConfig, Department, AgentRole

logger = logging.getLogger(__name__)

class SupportAgent(BaseAgent):
    """Specialized agent for customer support, technical assistance, and issue resolution."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "support_agent",
            "name": "Taylor Smith",
            "role": AgentRole.SUPPORT,
            "department": Department.SUPPORT,
            "level": 2,
            "manager_id": "manager",
            "system_prompt": (
                "You are Taylor Smith, Customer Support Specialist at AgentFlow Pro.\n"
                "You are patient, empathetic, and technically proficient. Your expertise includes "
                "troubleshooting, product knowledge, and customer service. You excel at understanding "
                "customer issues and providing clear, helpful solutions. You work closely with the "
                "development and sales teams to ensure customer satisfaction and product improvement."
            ),
            "tools": ["create_support_ticket", "escalate_issue", "provide_solution"],
            "specializations": ["Technical Support", "Customer Service", "Troubleshooting", "Product Knowledge"],
            "performance_metrics": {
                "tickets_resolved": 0,
                "first_response_time": 0.0,
                "customer_satisfaction": 0.0,
                "escalations": 0
            },
            "personality": {
                "tone": "friendly and helpful",
                "communication_style": "clear and patient",
                "approach": "solution-focused and empathetic"
            },
            "support_level": "Tier 1"
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the support request."""
        task = context.get("task_context", {})
        
        system_prompt = f"""
        {self.config.system_prompt}
        
        Support Request:
        {task.get('description', 'No description provided')}
        
        Customer Information:
        {json.dumps(context.get('customer_data', {}), indent=2)}
        
        Support Metrics:
        - Tickets resolved today: {random.randint(5, 20)}
        - Average response time: {random.randint(5, 30)} minutes
        - Customer satisfaction: {random.randint(80, 100)}%
        
        Guidelines:
        1. Be empathetic and patient with customers
        2. Gather all necessary information to understand the issue
        3. Provide clear, step-by-step solutions
        4. Escalate complex issues when necessary
        5. Document all interactions and solutions
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide helpful and effective support:")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update metrics
        self.config.performance_metrics["tickets_resolved"] += 1
        
        # Check if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "tier 2", "senior"]):
            state.escalate = True
            state.next_agent = "manager"
            self.config.performance_metrics["escalations"] += 1
        
        return response
    
    @tool
    async def create_support_ticket(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new support ticket for a customer issue."""
        try:
            ticket = {
                "ticket_id": f"TKT-{random.randint(1000, 9999)}",
                "customer_id": issue_data.get("customer_id") or f"CUST-{random.randint(10000, 99999)}",
                "customer_name": issue_data.get("customer_name", "Anonymous"),
                "email": issue_data.get("email"),
                "subject": issue_data.get("subject", "No subject"),
                "description": issue_data.get("description", "No description provided"),
                "category": issue_data.get("category", "General"),
                "priority": issue_data.get("priority", "Medium"),
                "status": "Open",
                "assigned_to": self.config.name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "tags": issue_data.get("tags", []),
                "attachments": issue_data.get("attachments", []),
                "internal_notes": []
            }
            
            # Set priority based on keywords if not provided
            if "priority" not in issue_data:
                urgent_terms = ["urgent", "critical", "down", "not working"]
                if any(term in ticket["description"].lower() for term in urgent_terms):
                    ticket["priority"] = "High"
            
            # Add initial internal note
            ticket["internal_notes"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": self.config.name,
                "note": f"Ticket created and assigned to {self.config.name}"
            })
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def escalate_issue(self, ticket_data: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Escalate a support issue to a higher tier or specialized team."""
        try:
            escalation = {
                "escalation_id": f"ESC-{random.randint(1000, 9999)}",
                "ticket_id": ticket_data.get("ticket_id"),
                "from_agent": self.config.name,
                "to_team": "Tier 2 Support",  # Would be determined by issue type
                "reason": reason,
                "escalation_notes": "",
                "status": "Pending",
                "created_at": datetime.now().isoformat(),
                "assigned_to": None
            }
            
            # Determine appropriate escalation path
            if "billing" in reason.lower() or "payment" in reason.lower():
                escalation["to_team"] = "Billing Department"
            elif "technical" in reason.lower() or "bug" in reason.lower():
                escalation["to_team"] = "Technical Support"
            
            # Update ticket status
            ticket_data["status"] = f"Escalated to {escalation['to_team']}"
            ticket_data["escalation"] = escalation
            
            # Add escalation note
            if "internal_notes" not in ticket_data:
                ticket_data["internal_notes"] = []
                
            ticket_data["internal_notes"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": self.config.name,
                "note": f"Issue escalated to {escalation['to_team']}. Reason: {reason}"
            })
            
            # Update metrics
            self.config.performance_metrics["escalations"] += 1
            
            return {
                "success": True,
                "message": f"Issue escalated to {escalation['to_team']}",
                "escalation": escalation,
                "ticket": ticket_data
            }
            
        except Exception as e:
            logger.error(f"Error escalating issue: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def provide_solution(self, ticket_data: Dict[str, Any], solution: str) -> Dict[str, Any]:
        """Provide a solution to a support ticket and update its status."""
        try:
            # Update ticket with solution
            ticket_data["solution"] = solution
            ticket_data["status"] = "Resolved"
            ticket_data["resolved_at"] = datetime.now().isoformat()
            ticket_data["resolved_by"] = self.config.name
            
            # Add resolution note
            if "internal_notes" not in ticket_data:
                ticket_data["internal_notes"] = []
                
            ticket_data["internal_notes"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": self.config.name,
                "note": f"Provided solution: {solution[:100]}..."
            })
            
            # Calculate resolution time
            created_at = datetime.fromisoformat(ticket_data.get("created_at", datetime.now().isoformat()))
            resolved_at = datetime.now()
            resolution_time = (resolved_at - created_at).total_seconds() / 60  # in minutes
            
            # Update metrics
            self.config.performance_metrics["tickets_resolved"] += 1
            
            # Update average response time (simplified)
            current_avg = self.config.performance_metrics.get("first_response_time", 0)
            total_tickets = self.config.performance_metrics.get("tickets_resolved", 1)
            self.config.performance_metrics["first_response_time"] = (
                (current_avg * (total_tickets - 1) + resolution_time) / total_tickets
            )
            
            return {
                "success": True,
                "message": "Ticket resolved successfully",
                "ticket": ticket_data,
                "resolution_time_minutes": round(resolution_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error providing solution: {str(e)}")
            return {"error": str(e)}
