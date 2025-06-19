"""Sales Agent implementation for handling sales-related tasks and customer interactions."""
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

class SalesAgent(BaseAgent):
    """Specialized agent for sales operations, lead management, and revenue generation."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "sales_agent",
            "name": "Alex Johnson",
            "role": AgentRole.SALES,
            "department": Department.SALES,
            "level": 2,
            "manager_id": "manager",
            "system_prompt": (
                "You are Alex Johnson, Sales Representative at AgentFlow Pro.\n"
                "You are results-driven, persuasive, and customer-focused. Your expertise includes "
                "lead generation, sales pipeline management, and closing deals. You understand customer "
                "needs and provide tailored solutions. You work closely with the support and growth teams "
                "to ensure customer satisfaction and retention."
            ),
            "tools": ["qualify_lead", "create_proposal", "schedule_demo"],
            "specializations": ["Lead Generation", "Sales Pipeline", "Customer Acquisition", "Deal Closing"],
            "performance_metrics": {
                "leads_qualified": 0,
                "deals_closed": 0,
                "revenue_generated": 0.0,
                "customer_satisfaction": 0.0
            },
            "personality": {
                "tone": "friendly and persuasive",
                "communication_style": "clear and engaging",
                "approach": "solution-oriented and consultative"
            },
            "quota": 100000.0,  # Monthly sales quota
            "current_month_revenue": 0.0
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the sales-related query."""
        task = context.get("task_context", {})
        
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        Customer Context:
        {json.dumps(context.get('customer_data', {}), indent=2)}
        
        Sales Pipeline Status:
        - Leads in pipeline: {random.randint(5, 20)}
        - Deals closed this month: {self.config.performance_metrics['deals_closed']}
        - Revenue generated: ${self.config.performance_metrics['revenue_generated']:,.2f}
        - Quota progress: {(self.config.current_month_revenue / self.config.quota * 100):.1f}%
        
        Guidelines:
        1. Focus on understanding customer needs and providing value
        2. Be proactive in following up with leads
        3. Maintain accurate records of all interactions
        4. Collaborate with other teams as needed
        5. Always aim to exceed sales targets
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide a helpful and persuasive sales response:")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update metrics
        if "proposal" in response.content.lower():
            self.config.performance_metrics["proposals_created"] = self.config.performance_metrics.get("proposals_created", 0) + 1
        
        if any(term in response.content.lower() for term in ["escalate", "manager", "assistance"]):
            state.escalate = True
            state.next_agent = "manager"
        
        return response
    
    @tool
    async def qualify_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Qualify a sales lead based on BANT criteria."""
        try:
            qualification = {
                "lead_id": lead_data.get("id") or f"L{random.randint(1000, 9999)}",
                "company": lead_data.get("company", "Unknown"),
                "contact_name": lead_data.get("name", "Unknown"),
                "email": lead_data.get("email"),
                "phone": lead_data.get("phone"),
                "bant_qualification": {
                    "budget": random.choice(["Qualified", "Needs Discovery", "Not Qualified"]),
                    "authority": random.choice(["Decision Maker", "Influencer", "No Authority"]),
                    "need": random.choice(["Strong Need", "Potential Need", "No Clear Need"]),
                    "timeline": random.choice(["Immediate", "30-60 days", "6+ months", "No Timeline"])
                },
                "lead_score": random.randint(1, 100),
                "status": "New",
                "next_steps": ["Schedule discovery call", "Send more information"]
            }
            
            # Determine lead status based on score
            if qualification["lead_score"] >= 70:
                qualification["status"] = "Hot Lead"
                qualification["priority"] = "High"
            elif qualification["lead_score"] >= 40:
                qualification["status"] = "Warm Lead"
                qualification["priority"] = "Medium"
            else:
                qualification["status"] = "Cold Lead"
                qualification["priority"] = "Low"
            
            # Update metrics
            self.config.performance_metrics["leads_qualified"] += 1
            
            return qualification
            
        except Exception as e:
            logger.error(f"Error in lead qualification: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def create_proposal(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sales proposal for a qualified opportunity."""
        try:
            amount = float(opportunity_data.get("estimated_value", random.uniform(1000, 50000)))
            
            proposal = {
                "proposal_id": f"PROP-{random.randint(1000, 9999)}",
                "opportunity_name": opportunity_data.get("name", "New Opportunity"),
                "customer_name": opportunity_data.get("customer_name", ""),
                "proposal_date": datetime.now().strftime("%Y-%m-%d"),
                "valid_until": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "amount": amount,
                "currency": "USD",
                "discount_percentage": opportunity_data.get("discount_percentage", 0.0),
                "discount_amount": amount * (opportunity_data.get("discount_percentage", 0.0) / 100),
                "total_amount": amount * (1 - (opportunity_data.get("discount_percentage", 0.0) / 100)),
                "payment_terms": "Net 30",
                "status": "Draft",
                "line_items": [],
                "terms_and_conditions": "Standard terms and conditions apply.",
                "created_by": self.config.name
            }
            
            # Add line items if provided
            if "products" in opportunity_data:
                for product in opportunity_data["products"]:
                    line_total = product.get("quantity", 1) * product.get("unit_price", 0)
                    proposal["line_items"].append({
                        "product_id": product.get("id"),
                        "description": product.get("name", "Product"),
                        "quantity": product.get("quantity", 1),
                        "unit_price": product.get("unit_price", 0),
                        "total_price": line_total
                    })
            
            # Update metrics
            self.config.performance_metrics["proposals_created"] = self.config.performance_metrics.get("proposals_created", 0) + 1
            
            return proposal
            
        except Exception as e:
            logger.error(f"Error creating proposal: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def schedule_demo(self, prospect_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a product demo with a qualified prospect."""
        try:
            # Generate random available time slots (simplified)
            base_date = datetime.now() + timedelta(days=1)
            available_slots = [
                (base_date.replace(hour=9, minute=0) + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M")
                for i in range(0, 8, 2)  # 9 AM to 5 PM in 2-hour blocks
            ]
            
            demo = {
                "demo_id": f"DEMO-{random.randint(1000, 9999)}",
                "prospect_name": prospect_data.get("name", "Prospect"),
                "company": prospect_data.get("company", ""),
                "email": prospect_data.get("email"),
                "phone": prospect_data.get("phone"),
                "interests": prospect_data.get("interests", []),
                "available_slots": available_slots,
                "scheduled_slot": None,
                "status": "Pending Scheduling",
                "demo_type": prospect_data.get("demo_type", "Standard Demo"),
                "assigned_to": self.config.name,
                "meeting_link": "https://meet.agentflow.pro/demo/" + str(random.randint(100000, 999999))
            }
            
            # If preferred_time is provided, try to match it
            if "preferred_time" in prospect_data:
                demo["scheduled_slot"] = prospect_data["preferred_time"]
                demo["status"] = "Scheduled"
            
            return demo
            
        except Exception as e:
            logger.error(f"Error scheduling demo: {str(e)}")
            return {"error": str(e)}
