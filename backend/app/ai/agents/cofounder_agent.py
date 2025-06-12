"""
Co-founder Agent for strategic leadership and company vision.
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum, auto
import json
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator, HttpUrl
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base_agent import BaseAgent, AgentConfig, AgentResponse, AgentState
from ..integrations import (
    get_analytics_integration,
    get_communication_integration,
    get_finance_integration,
    get_project_management_integration
)

logger = logging.getLogger(__name__)

class CoFounderRole(str, Enum):
    """Different roles a co-founder can have."""
    TECHNICAL = "technical"
    BUSINESS = "business"
    PRODUCT = "product"
    DESIGN = "design"
    MARKETING = "marketing"
    OPERATIONS = "operations"

class InvestmentRound(BaseModel):
    """Details about a funding round."""
    round_name: str  # e.g., "Seed", "Series A"
    amount_raised: float
    valuation: Optional[float] = None
    lead_investor: str
    investors: List[str] = Field(default_factory=list)
    date_closed: datetime
    use_of_funds: List[Dict[str, Union[str, float]]] = Field(default_factory=list)
    terms: Dict[str, Any] = Field(default_factory=dict)

class Advisor(BaseModel):
    """Information about a company advisor."""
    name: str
    title: str
    company: str
    expertise: List[str] = Field(default_factory=list)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    equity_percentage: Optional[float] = None
    notes: str = ""

class CoFounderAgent(BaseAgent):
    """
    Co-founder Agent responsible for strategic leadership and company vision.
    
    This agent provides capabilities for:
    - Defining and communicating company vision and mission
    - Fundraising and investor relations
    - Strategic partnerships and business development
    - High-level hiring and team building
    - Company culture and values
    - Long-term strategic planning
    - Crisis management
    - Board and advisor management
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.role: CoFounderRole = CoFounderRole(config.get("role", "technical"))
        self.equity_percentage: float = config.get("equity_percentage", 0.0)
        self.investment_rounds: List[InvestmentRound] = []
        self.advisors: List[Advisor] = []
        self._init_integrations()
    
    def _init_integrations(self) -> None:
        """Initialize necessary integrations."""
        try:
            self.analytics = get_analytics_integration()
            self.communication = get_communication_integration()
            self.finance = get_finance_integration()
            self.project_management = get_project_management_integration()
            logger.info("Co-founder Agent integrations initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Co-founder Agent integrations: {str(e)}")
            raise
    
    async def define_vision_mission(
        self, 
        vision: str, 
        mission: str, 
        core_values: List[str]
    ) -> AgentResponse:
        """
        Define or update the company vision, mission, and core values.
        
        Args:
            vision: The company's vision statement
            mission: The company's mission statement
            core_values: List of core values
            
        Returns:
            AgentResponse with the defined vision, mission, and values
        """
        try:
            self.vision = vision
            self.mission = mission
            self.core_values = core_values
            
            logger.info(f"Defined company vision: {vision[:50]}...")
            
            # Document this in the company wiki or knowledge base
            await self._document_company_foundation()
            
            return AgentResponse(
                success=True,
                output={
                    "vision": vision,
                    "mission": mission,
                    "core_values": core_values
                },
                message="Company vision, mission, and values defined successfully"
            )
            
        except Exception as e:
            error_msg = f"Failed to define company vision: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _document_company_foundation(self) -> None:
        """Document company foundation details in the knowledge base."""
        doc_content = {
            "vision": self.vision,
            "mission": self.mission,
            "core_values": self.core_values,
            "founding_date": datetime.utcnow().isoformat(),
            "co_founders": [{
                "name": self.config.get("name", ""),
                "role": self.role.value,
                "equity_percentage": self.equity_percentage
            }]
        }
        
        # This would save to a document management system in a real implementation
        logger.info(f"Documenting company foundation: {doc_content}")
    
    async def add_investment_round(self, round_data: Dict[str, Any]) -> AgentResponse:
        """
        Add details about a funding round.
        
        Args:
            round_data: Dictionary containing round details
            
        Returns:
            AgentResponse with the added investment round
        """
        try:
            investment_round = InvestmentRound(**round_data)
            self.investment_rounds.append(investment_round)
            
            # Sort rounds by date
            self.investment_rounds.sort(key=lambda x: x.date_closed)
            
            logger.info(f"Added {investment_round.round_name} round: ${investment_round.amount_raised:,.0f}")
            
            # Update financial projections and runway
            await self._update_financials_after_funding(investment_round)
            
            return AgentResponse(
                success=True,
                output={"investment_round": investment_round.dict()},
                message=f"Added {investment_round.round_name} round"
            )
            
        except Exception as e:
            error_msg = f"Failed to add investment round: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _update_financials_after_funding(self, investment_round: InvestmentRound) -> None:
        """Update financial projections after a funding round."""
        # This would update financial models and projections
        logger.info(f"Updating financials after {investment_round.round_name} round")
    
    async def add_advisor(self, advisor_data: Dict[str, Any]) -> AgentResponse:
        """
        Add an advisor to the company.
        
        Args:
            advisor_data: Dictionary containing advisor details
            
        Returns:
            AgentResponse with the added advisor
        """
        try:
            advisor = Advisor(**advisor_data)
            self.advisors.append(advisor)
            
            logger.info(f"Added advisor: {advisor.name} ({advisor.title} at {advisor.company})")
            
            # Send welcome email
            await self.communication.send_email(
                to=advisor.email if hasattr(advisor, 'email') else "",
                subject=f"Welcome as an Advisor to {self.config.get('company_name', 'Our Company')}",
                body=f"""
                Dear {advisor.name},
                
                We're thrilled to welcome you as an advisor to {self.config.get('company_name', 'Our Company')}!
                
                Your expertise in {', '.join(advisor.expertise)} will be invaluable as we work towards {self.vision}.
                
                We'll be in touch soon to schedule our first advisory session.
                
                Best regards,
                {self.config.get('name', 'The Founders')}
                """
            )
            
            return AgentResponse(
                success=True,
                output={"advisor": advisor.dict()},
                message=f"Added advisor: {advisor.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to add advisor: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def evaluate_strategic_opportunity(
        self,
        opportunity: Dict[str, Any],
        criteria: List[Dict[str, Any]]
    ) -> AgentResponse:
        """
        Evaluate a strategic opportunity against defined criteria.
        
        Args:
            opportunity: Details about the opportunity
            criteria: List of criteria to evaluate against
            
        Returns:
            AgentResponse with evaluation results
        """
        try:
            # This would involve more sophisticated analysis in a real implementation
            evaluation = {
                "opportunity": opportunity.get("name", ""),
                "alignment_score": 0,
                "risks": [],
                "rewards": [],
                "recommendation": "further_analysis_needed",
                "next_steps": []
            }
            
            # Simple scoring based on criteria
            total_score = 0
            max_score = 0
            
            for criterion in criteria:
                weight = criterion.get("weight", 1)
                max_score += 10 * weight  # Assuming 10 is max score per criterion
                
                # This is a simplified evaluation - in practice, this would be more sophisticated
                score = min(10, criterion.get("score", 5)) * weight
                total_score += score
                
                if score < 5:
                    evaluation["risks"].append(f"Low score on '{criterion['name']}'")
                elif score > 8:
                    evaluation["rewards"].append(f"High score on '{criterion['name']}'")
            
            # Calculate alignment score (0-100%)
            alignment_score = (total_score / max_score) * 100 if max_score > 0 else 0
            evaluation["alignment_score"] = alignment_score
            
            # Make recommendation
            if alignment_score >= 80:
                evaluation["recommendation"] = "pursue"
                evaluation["next_steps"].append("Schedule meeting with key stakeholders")
            elif alignment_score >= 50:
                evaluation["recommendation"] = "consider_with_conditions"
                evaluation["next_steps"].append("Identify conditions for moving forward")
            else:
                evaluation["recommendation"] = "do_not_pursue"
                evaluation["next_steps"].append("Document learnings and close opportunity")
            
            return AgentResponse(
                success=True,
                output={"evaluation": evaluation},
                message=f"Evaluated opportunity: {opportunity.get('name', '')}"
            )
            
        except Exception as e:
            error_msg = f"Failed to evaluate opportunity: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )

# Example usage
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def main():
        # Initialize Co-founder Agent
        config = {
            "name": "Alex Johnson",
            "role": "technical",
            "company_name": "TechStart Inc.",
            "email": "alex@techstart.example",
            "equity_percentage": 60.0,
            "llm": {"model": "gpt-4"}
        }
        
        cofounder = CoFounderAgent(config=config)
        
        # Define company vision and mission
        await cofounder.define_vision_mission(
            vision="To revolutionize how businesses leverage AI",
            mission="Empower businesses with accessible AI solutions",
            core_values=["Innovation", "Integrity", "Customer Focus", "Excellence"]
        )
        
        # Add seed funding round
        await cofounder.add_investment_round({
            "round_name": "Seed",
            "amount_raised": 2_000_000,
            "valuation": 10_000_000,
            "lead_investor": "Sequoia Capital",
            "investors": ["Sequoia Capital", "Y Combinator"],
            "date_closed": "2023-01-15",
            "use_of_funds": [
                {"category": "Product Development", "amount": 1_000_000, "percentage": 50},
                {"category": "Team", "amount": 600_000, "percentage": 30},
                {"category": "Marketing", "amount": 300_000, "percentage": 15},
                {"category": "Legal & Admin", "amount": 100_000, "percentage": 5}
            ]
        })
        
        # Add an advisor
        await cofounder.add_advisor({
            "name": "Dr. Sarah Chen",
            "title": "AI Research Director",
            "company": "Stanford AI Lab",
            "expertise": ["Machine Learning", "Computer Vision", "Startup Mentoring"],
            "equity_percentage": 0.5,
            "email": "sarah@stanford.edu"
        })
        
        # Evaluate a strategic opportunity
        opportunity = {
            "name": "Partnership with Enterprise Corp",
            "description": "Potential enterprise partnership to integrate our AI into their platform",
            "potential_revenue": 5_000_000,
            "time_horizon": 12,  # months
            "resources_required": ["2 engineers", "1 PM", "$200k"],
            "strategic_importance": "high"
        }
        
        criteria = [
            {"name": "Strategic Fit", "weight": 3, "score": 8},
            {"name": "Revenue Potential", "weight": 2, "score": 9},
            {"name": "Resource Requirements", "weight": 2, "score": 6},
            {"name": "Competitive Advantage", "weight": 2, "score": 7},
            {"name": "Alignment with Vision", "weight": 3, "score": 9}
        ]
        
        evaluation = await cofounder.evaluate_strategic_opportunity(opportunity, criteria)
        print("\nOpportunity Evaluation:", evaluation.output["evaluation"])
    
    asyncio.run(main())
