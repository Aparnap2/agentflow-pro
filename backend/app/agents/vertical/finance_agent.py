"""Finance Agent implementation for handling financial analysis and planning."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import json
import logging
import random

from ...base import BaseAgent, AgentConfig, Department, AgentRole

logger = logging.getLogger(__name__)

class FinanceAgent(BaseAgent):
    """Specialized agent for financial analysis, planning, and reporting."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "finance_agent",
            "name": "Michael Chen",
            "role": AgentRole.FINANCE_AGENT,
            "department": Department.FINANCE,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Michael Chen, Financial Analyst at AgentFlow Pro.\n"
                "You are analytical, detail-oriented, and have a strong understanding of financial principles. "
                "Your expertise includes financial modeling, budgeting, forecasting, and investment analysis.\n"
                "You provide clear, data-driven insights and help guide business decisions through financial analysis.\n"
                "You work closely with other departments to ensure financial health and sustainability."
            ),
            "tools": ["analyze_financials", "create_forecast", "evaluate_investment"],
            "specializations": ["Financial Analysis", "Budgeting", "Forecasting", "Investment"],
            "performance_metrics": {
                "analyses_completed": 0,
                "forecasts_generated": 0,
                "investments_evaluated": 0
            },
            "personality": {
                "tone": "analytical and precise",
                "communication_style": "data-driven and clear",
                "approach": "methodical and risk-aware"
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the financial query."""
        # Get relevant context
        task = context.get("task_context", {})
        
        # Build system prompt with context
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        Available Data:
        {json.dumps(context.get('financial_data', {}), indent=2)}
        
        Guidelines:
        1. Analyze financial data thoroughly and accurately
        2. Provide clear, actionable insights and recommendations
        3. Consider both short-term and long-term financial implications
        4. Highlight potential risks and opportunities
        5. Use appropriate financial metrics and KPIs
        """
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide a detailed financial analysis and recommendations:")
        ])
        
        # Generate response
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update performance metrics
        self.config.performance_metrics["analyses_completed"] += 1
        
        # Determine if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "urgent", "critical"]):
            state.escalate = True
            state.next_agent = "cofounder"
        
        return response
    
    @tool
    async def analyze_financials(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial statements and metrics."""
        try:
            # In a real implementation, this would perform detailed financial analysis
            analysis = {
                "summary": "Financial analysis summary",
                "key_metrics": {
                    "revenue_growth": random.uniform(0.05, 0.15),  # 5-15% growth
                    "profit_margin": random.uniform(0.1, 0.25),     # 10-25% margin
                    "roi": random.uniform(0.08, 0.2),               # 8-20% ROI
                    "current_ratio": random.uniform(1.5, 3.0)       # 1.5-3.0 current ratio
                },
                "trends": [],
                "recommendations": []
            }
            
            # Simple analysis based on available data
            if "revenue" in financial_data:
                analysis["trends"].append("Revenue analysis complete")
                
            if "expenses" in financial_data:
                analysis["trends"].append("Expense analysis complete")
            
            # Update metrics
            self.config.performance_metrics["analyses_completed"] += 1
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in financial analysis: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def create_forecast(self, historical_data: Dict[str, Any], periods: int = 12) -> Dict[str, Any]:
        """Create financial forecasts based on historical data."""
        try:
            # In a real implementation, this would use time series forecasting
            forecast = {
                "periods": periods,
                "forecasted_values": {
                    "revenue": [random.uniform(10000, 50000) for _ in range(periods)],
                    "expenses": [random.uniform(8000, 40000) for _ in range(periods)],
                    "profit": [random.uniform(2000, 10000) for _ in range(periods)]
                },
                "confidence_interval": {
                    "lower": 0.8,
                    "upper": 0.95
                },
                "assumptions": [
                    "Market conditions remain stable",
                    "No major economic disruptions",
                    "Current growth trends continue"
                ]
            }
            
            # Update metrics
            self.config.performance_metrics["forecasts_generated"] += 1
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error in forecast creation: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def evaluate_investment(self, investment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a potential investment opportunity."""
        try:
            # In a real implementation, this would perform detailed investment analysis
            evaluation = {
                "opportunity_name": investment_data.get("name", "Unnamed Opportunity"),
                "npv": random.uniform(-100000, 500000),  # Net Present Value
                "irr": random.uniform(0.05, 0.3),        # Internal Rate of Return
                "payback_period": random.uniform(6, 36),  # Months
                "risk_assessment": {
                    "level": random.choice(["low", "medium", "high"]),
                    "factors": [
                        "Market competition",
                        "Regulatory environment",
                        "Technology risk"
                    ]
                },
                "recommendation": random.choice(["Proceed", "Proceed with Caution", "Reject"]),
                "key_considerations": [
                    "Market potential",
                    "Competitive advantage",
                    "Financial viability"
                ]
            }
            
            # Update metrics
            self.config.performance_metrics["investments_evaluated"] += 1
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in investment evaluation: {str(e)}")
            return {"error": str(e)}
