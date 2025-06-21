"""CRM Agent implementation for lead and customer relationship management."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import json
import logging
import random
from datetime import datetime, timedelta

from ..base import BaseAgent, AgentConfig, Department, AgentRole, AgentState

logger = logging.getLogger(__name__)

class CRMAgent(BaseAgent):
    """Specialized agent for CRM operations, lead management, and customer relationships."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "crm_agent",
            "name": "Emma Rodriguez",
            "role": AgentRole.CRM_AGENT,
            "department": Department.SALES,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Emma Rodriguez, CRM Specialist at AgentFlow Pro.\n"
                "You are organized, detail-oriented, and customer-focused. Your expertise includes "
                "lead management, customer segmentation, sales pipeline optimization, and relationship building. "
                "You maintain comprehensive customer profiles and ensure no lead falls through the cracks. "
                "You work closely with sales and marketing teams to maximize customer lifetime value."
            ),
            "tools": ["enrich_lead", "segment_customers", "update_pipeline", "schedule_followup"],
            "specializations": ["Lead Management", "Customer Segmentation", "Pipeline Optimization", "Relationship Building"],
            "performance_metrics": {
                "leads_processed": 0,
                "customers_segmented": 0,
                "pipeline_updates": 0,
                "followups_scheduled": 0,
                "conversion_rate": 0.0
            },
            "personality": {
                "tone": "professional and organized",
                "communication_style": "clear and systematic",
                "approach": "data-driven and relationship-focused"
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state: AgentState, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the CRM-related query."""
        task = context.get("task_context", {})
        
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        CRM Context:
        {json.dumps(context.get('customer_data', {}), indent=2)}
        
        Pipeline Status:
        - Total leads in system: {random.randint(50, 200)}
        - Hot leads: {random.randint(5, 25)}
        - Warm leads: {random.randint(15, 50)}
        - Cold leads: {random.randint(20, 100)}
        - Conversion rate: {self.config.performance_metrics['conversion_rate']:.1f}%
        
        Guidelines:
        1. Focus on lead qualification and nurturing
        2. Maintain accurate customer profiles and interaction history
        3. Identify opportunities for upselling and cross-selling
        4. Ensure timely follow-ups and communication
        5. Segment customers based on behavior and preferences
        6. Collaborate with sales and marketing for optimal results
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide a comprehensive CRM analysis and recommendations:")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update metrics
        self.config.performance_metrics["leads_processed"] += 1
        
        # Determine if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "manager", "complex"]):
            state.escalate = True
            state.next_agent = "manager"
        
        return response
    
    @tool
    async def enrich_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich lead data with additional information and scoring."""
        try:
            lead_id = lead_data.get("id") or f"LEAD-{random.randint(10000, 99999)}"
            
            enriched_lead = {
                "id": lead_id,
                "basic_info": {
                    "name": lead_data.get("name", "Unknown"),
                    "email": lead_data.get("email"),
                    "phone": lead_data.get("phone"),
                    "company": lead_data.get("company"),
                    "title": lead_data.get("title"),
                    "industry": lead_data.get("industry")
                },
                "enriched_data": {
                    "company_size": random.choice(["1-10", "11-50", "51-200", "201-1000", "1000+"]),
                    "annual_revenue": random.choice(["<$1M", "$1M-$10M", "$10M-$50M", "$50M+"]),
                    "technology_stack": random.sample(["Salesforce", "HubSpot", "Pipedrive", "Zoho", "Custom"], k=2),
                    "social_profiles": {
                        "linkedin": f"https://linkedin.com/in/{lead_data.get('name', 'unknown').lower().replace(' ', '-')}",
                        "twitter": f"@{lead_data.get('company', 'company').lower()}"
                    }
                },
                "lead_score": random.randint(1, 100),
                "qualification_status": random.choice(["New", "Qualified", "Unqualified", "Nurturing"]),
                "source": lead_data.get("source", "Website"),
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "tags": lead_data.get("tags", []),
                "notes": []
            }
            
            # Determine lead temperature based on score
            if enriched_lead["lead_score"] >= 80:
                enriched_lead["temperature"] = "Hot"
                enriched_lead["priority"] = "High"
            elif enriched_lead["lead_score"] >= 60:
                enriched_lead["temperature"] = "Warm"
                enriched_lead["priority"] = "Medium"
            else:
                enriched_lead["temperature"] = "Cold"
                enriched_lead["priority"] = "Low"
            
            # Update metrics
            self.config.performance_metrics["leads_processed"] += 1
            
            return enriched_lead
            
        except Exception as e:
            logger.error(f"Error enriching lead: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def segment_customers(self, customer_list: List[Dict[str, Any]], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Segment customers based on specified criteria."""
        try:
            segments = {
                "high_value": [],
                "medium_value": [],
                "low_value": [],
                "at_risk": [],
                "new_customers": [],
                "loyal_customers": []
            }
            
            for customer in customer_list:
                # Simulate customer value calculation
                customer_value = random.uniform(100, 10000)
                days_since_last_purchase = random.randint(1, 365)
                total_purchases = random.randint(1, 50)
                
                # Value-based segmentation
                if customer_value >= 5000:
                    segments["high_value"].append(customer)
                elif customer_value >= 1000:
                    segments["medium_value"].append(customer)
                else:
                    segments["low_value"].append(customer)
                
                # Behavior-based segmentation
                if days_since_last_purchase > 180:
                    segments["at_risk"].append(customer)
                elif total_purchases <= 2:
                    segments["new_customers"].append(customer)
                elif total_purchases >= 10:
                    segments["loyal_customers"].append(customer)
            
            segmentation_result = {
                "total_customers": len(customer_list),
                "segments": {
                    segment: {
                        "count": len(customers),
                        "percentage": (len(customers) / len(customer_list) * 100) if customer_list else 0,
                        "customers": customers[:5]  # Return first 5 for preview
                    }
                    for segment, customers in segments.items()
                },
                "criteria_used": criteria,
                "created_at": datetime.now().isoformat()
            }
            
            # Update metrics
            self.config.performance_metrics["customers_segmented"] += len(customer_list)
            
            return segmentation_result
            
        except Exception as e:
            logger.error(f"Error segmenting customers: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def update_pipeline(self, opportunity_id: str, stage: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update sales pipeline with opportunity progress."""
        try:
            pipeline_stages = [
                "Lead", "Qualified", "Proposal", "Negotiation", "Closed Won", "Closed Lost"
            ]
            
            if stage not in pipeline_stages:
                return {"error": f"Invalid stage. Must be one of: {pipeline_stages}"}
            
            pipeline_update = {
                "opportunity_id": opportunity_id,
                "previous_stage": data.get("previous_stage", "Lead"),
                "current_stage": stage,
                "amount": data.get("amount", 0),
                "probability": data.get("probability", 50),
                "expected_close_date": data.get("expected_close_date"),
                "last_activity": datetime.now().isoformat(),
                "notes": data.get("notes", ""),
                "next_steps": data.get("next_steps", []),
                "stage_history": data.get("stage_history", [])
            }
            
            # Add current stage to history
            pipeline_update["stage_history"].append({
                "stage": stage,
                "date": datetime.now().isoformat(),
                "updated_by": self.config.name
            })
            
            # Calculate stage duration
            if data.get("previous_stage_date"):
                prev_date = datetime.fromisoformat(data["previous_stage_date"])
                current_date = datetime.now()
                duration_days = (current_date - prev_date).days
                pipeline_update["stage_duration_days"] = duration_days
            
            # Update metrics
            self.config.performance_metrics["pipeline_updates"] += 1
            
            return pipeline_update
            
        except Exception as e:
            logger.error(f"Error updating pipeline: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def schedule_followup(self, contact_info: Dict[str, Any], followup_type: str, days_from_now: int = 7) -> Dict[str, Any]:
        """Schedule a follow-up activity with a lead or customer."""
        try:
            followup_types = ["call", "email", "meeting", "demo", "proposal_review"]
            
            if followup_type not in followup_types:
                return {"error": f"Invalid followup type. Must be one of: {followup_types}"}
            
            followup_date = datetime.now() + timedelta(days=days_from_now)
            
            followup = {
                "id": f"FOLLOWUP-{random.randint(10000, 99999)}",
                "contact_id": contact_info.get("id"),
                "contact_name": contact_info.get("name"),
                "contact_email": contact_info.get("email"),
                "followup_type": followup_type,
                "scheduled_date": followup_date.isoformat(),
                "status": "Scheduled",
                "priority": contact_info.get("priority", "Medium"),
                "notes": contact_info.get("notes", ""),
                "created_by": self.config.name,
                "created_at": datetime.now().isoformat()
            }
            
            # Add type-specific details
            if followup_type == "call":
                followup["duration_minutes"] = 30
                followup["phone"] = contact_info.get("phone")
            elif followup_type == "email":
                followup["email_template"] = "standard_followup"
            elif followup_type == "meeting":
                followup["duration_minutes"] = 60
                followup["meeting_type"] = "discovery"
            elif followup_type == "demo":
                followup["duration_minutes"] = 45
                followup["demo_type"] = "product_overview"
            
            # Update metrics
            self.config.performance_metrics["followups_scheduled"] += 1
            
            return followup
            
        except Exception as e:
            logger.error(f"Error scheduling followup: {str(e)}")
            return {"error": str(e)}