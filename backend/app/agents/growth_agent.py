"""Growth Agent implementation for handling growth strategies and customer retention."""
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

class GrowthAgent(BaseAgent):
    """Specialized agent for growth strategies, customer retention, and expansion."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "growth_agent",
            "name": "Jordan Lee",
            "role": AgentRole.GROWTH,
            "department": Department.MARKETING,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Jordan Lee, Growth Strategist at AgentFlow Pro.\n"
                "You are data-driven, creative, and focused on sustainable growth. Your expertise includes "
                "customer acquisition, retention strategies, and revenue optimization. You analyze market trends, "
                "identify growth opportunities, and implement data-backed strategies. You collaborate with sales, "
                "marketing, and product teams to drive business growth."
            ),
            "tools": ["analyze_growth_metrics", "create_growth_campaign", "segment_customers"],
            "specializations": ["Customer Acquisition", "Retention", "Upselling", "Market Expansion"],
            "performance_metrics": {
                "campaigns_launched": 0,
                "customer_acquisition_cost": 0.0,
                "customer_lifetime_value": 0.0,
                "retention_rate": 0.0,
                "revenue_increase": 0.0
            },
            "personality": {
                "tone": "insightful and persuasive",
                "communication_style": "data-driven and strategic",
                "approach": "analytical and innovative"
            },
            "growth_targets": {
                "monthly_growth_rate": 0.1,  # 10% MoM growth target
                "churn_rate_target": 0.05,   # Max 5% monthly churn
                "expansion_mrr_rate": 0.15    # 15% MRR from expansion
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the growth-related query."""
        task = context.get("task_context", {})
        
        system_prompt = f"""
        {self.config.system_prompt}
        
        Growth Task:
        {task.get('description', 'No task description')}
        
        Current Growth Metrics:
        - Monthly Growth Rate: {random.uniform(5, 15):.1f}% (Target: {self.config.growth_targets['monthly_growth_rate']*100:.1f}%)
        - Customer Churn Rate: {random.uniform(3, 8):.1f}% (Target: <{self.config.growth_targets['churn_rate_target']*100:.1f}%)
        - Expansion MRR: {random.uniform(10, 20):.1f}% (Target: {self.config.growth_targets['expansion_mrr_rate']*100:.1f}%)
        - Customer Acquisition Cost: ${random.uniform(100, 500):.2f}
        - Customer Lifetime Value: ${random.uniform(1000, 5000):.2f}
        
        Guidelines:
        1. Focus on data-driven growth strategies
        2. Balance acquisition and retention efforts
        3. Identify expansion opportunities with existing customers
        4. Monitor and optimize key growth metrics
        5. Collaborate with other teams for cross-functional growth
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide strategic growth insights and recommendations:")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Track campaign mentions
        if any(term in response.content.lower() for term in ["campaign", "initiative", "strategy"]):
            self.config.performance_metrics["campaigns_launched"] += 1
        
        # Check if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "executive", "approval"]):
            state.escalate = True
            state.next_agent = "cofounder"
        
        return response
    
    @tool
    async def analyze_growth_metrics(self, time_period: str = "last_30_days") -> Dict[str, Any]:
        """Analyze key growth metrics and identify trends."""
        try:
            # In a real implementation, this would query analytics databases
            metrics = {
                "time_period": time_period,
                "mrr": {
                    "current": random.uniform(50000, 200000),
                    "growth_rate": random.uniform(0.05, 0.15)
                },
                "customers": {
                    "total": random.randint(100, 1000),
                    "new": random.randint(10, 100),
                    "churned": random.randint(1, 20),
                    "net_growth": random.randint(5, 50)
                },
                "revenue": {
                    "total": random.uniform(100000, 500000),
                    "recurring": random.uniform(80000, 400000),
                    "one_time": random.uniform(20000, 100000)
                },
                "conversion": {
                    "trial_to_paid": random.uniform(0.1, 0.3),
                    "visitor_to_signup": random.uniform(0.02, 0.1),
                    "signup_to_paying": random.uniform(0.1, 0.25)
                },
                "key_insights": [
                    "Strong growth in enterprise segment",
                    "High churn in SMB segment",
                    "Expansion revenue increasing"
                ],
                "recommendations": [
                    "Focus on reducing SMB churn",
                    "Scale successful enterprise acquisition channels",
                    "Implement customer success initiatives"
                ]
            }
            
            # Calculate derived metrics
            metrics["customers"]["churn_rate"] = (
                metrics["customers"]["churned"] / metrics["customers"]["total"]
                if metrics["customers"]["total"] > 0 else 0
            )
            
            # Update performance metrics
            self.config.performance_metrics["retention_rate"] = 1 - metrics["customers"]["churn_rate"]
            self.config.performance_metrics["customer_acquisition_cost"] = random.uniform(100, 500)
            self.config.performance_metrics["customer_lifetime_value"] = random.uniform(1000, 5000)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing growth metrics: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def create_growth_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and launch a new growth campaign."""
        try:
            campaign = {
                "campaign_id": f"CMP-{random.randint(1000, 9999)}",
                "name": campaign_data.get("name", f"Growth Campaign {datetime.now().strftime('%Y%m%d')}"),
                "type": campaign_data.get("type", "Acquisition"),  # or "Retention", "Upsell", "Referral"
                "target_audience": campaign_data.get("target_audience", "All Customers"),
                "goal": campaign_data.get("goal", "Increase product adoption"),
                "channels": campaign_data.get("channels", ["Email", "In-app"]),
                "budget": campaign_data.get("budget", 5000.0),
                "start_date": campaign_data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                "end_date": campaign_data.get("end_date", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")),
                "status": "Draft",
                "kpis": campaign_data.get("kpis", ["Conversion Rate", "ROI", "New MRR"]),
                "success_metrics": {
                    "target_conversion": campaign_data.get("target_conversion", 0.05),  # 5%
                    "target_roi": campaign_data.get("target_roi", 3.0),  # 3x ROI
                    "target_mrr": campaign_data.get("target_mrr", 10000.0)  # $10,000
                },
                "created_by": self.config.name,
                "created_at": datetime.now().isoformat(),
                "performance": {
                    "reached": 0,
                    "converted": 0,
                    "revenue_generated": 0.0,
                    "roi": 0.0
                }
            }
            
            # Update metrics
            self.config.performance_metrics["campaigns_launched"] += 1
            
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating growth campaign: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def segment_customers(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Segment customers based on specified criteria for targeted growth initiatives."""
        try:
            # In a real implementation, this would query customer data
            segments = {
                "segmentation_criteria": criteria,
                "total_customers": random.randint(100, 1000),
                "segments": [],
                "insights": []
            }
            
            # Generate sample segments based on criteria
            if "product_usage" in criteria.get("types", []):
                segments["segments"].append({
                    "segment_id": "high_usage",
                    "name": "High Usage Customers",
                    "size": random.randint(50, 200),
                    "criteria": "Top 20% by usage",
                    "characteristics": {
                        "avg_sessions_per_week": random.uniform(10, 20),
                        "avg_session_duration_minutes": random.uniform(15, 60),
                        "features_used": random.randint(5, 15)
                    },
                    "growth_opportunity": "Upsell to higher tier, request referrals"
                })
            
            if "revenue" in criteria.get("types", []):
                segments["segments"].append({
                    "segment_id": "high_value",
                    "name": "High Revenue Customers",
                    "size": random.randint(20, 100),
                    "criteria": "Top 10% by revenue",
                    "characteristics": {
                        "avg_mrr": random.uniform(500, 5000),
                        "lifetime_value": random.uniform(5000, 50000),
                        "churn_risk": random.uniform(0.01, 0.1)
                    },
                    "growth_opportunity": "Account expansion, white-glove service"
                })
            
            if "engagement" in criteria.get("types", []):
                segments["segments"].append({
                    "segment_id": "disengaged",
                    "name": "At-Risk Customers",
                    "size": random.randint(30, 150),
                    "criteria": "Declining usage or engagement",
                    "characteristics": {
                        "days_since_last_login": random.randint(15, 90),
                        "usage_trend": random.uniform(-0.4, -0.1),  # Negative trend
                        "support_tickets": random.randint(1, 5)
                    },
                    "growth_opportunity": "Re-engagement campaign, success review"
                })
            
            # Generate insights
            if segments["segments"]:
                segments["insights"] = [
                    f"{seg['size']} customers in {seg['name']} segment - {seg['growth_opportunity']}"
                    for seg in segments["segments"]
                ]
            
            return segments
            
        except Exception as e:
            logger.error(f"Error segmenting customers: {str(e)}")
            return {"error": str(e)}
