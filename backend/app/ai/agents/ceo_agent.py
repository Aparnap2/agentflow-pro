"""
CEO Agent for strategic decision making and company oversight.
"""

from typing import Dict, Any, List, Optional, Union, Type, TypeVar, Callable
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
    get_crm_integration,
    get_finance_integration,
    get_communication_integration
)

logger = logging.getLogger(__name__)

class CompanyStage(str, Enum):
    """Stages of company growth."""
    IDEA = "idea"
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C_PLUS = "series_c_plus"
    GROWTH = "growth"
    MATURE = "mature"

class StrategicInitiative(BaseModel):
    """A strategic initiative or company objective."""
    id: str
    name: str
    description: str
    owner: str
    start_date: datetime
    target_date: datetime
    priority: int  # 1-5, 1 being highest
    status: str = "planned"  # planned, in_progress, completed, blocked
    kpis: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    resources_required: Dict[str, Any] = Field(default_factory=dict)
    budget_allocation: Optional[float] = None
    actual_spend: float = 0.0
    progress: float = 0.0  # 0-100
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class OKR(BaseModel):
    """Objectives and Key Results for company goals."""
    objective: str
    key_results: List[Dict[str, Union[str, float, bool]]]
    owner: str
    timeline: Dict[str, datetime]  # start_date and end_date
    progress: float = 0.0
    status: str = "on_track"  # on_track, at_risk, off_track, completed
    last_reviewed: datetime = Field(default_factory=datetime.utcnow)

class CompanyPerformanceMetrics(BaseModel):
    """Comprehensive company performance metrics."""
    revenue: Dict[str, float]  # MRR, ARR, etc.
    expenses: Dict[str, float]
    customer_metrics: Dict[str, Any]  # CAC, LTV, churn, etc.
    product_metrics: Dict[str, Any]  # MAU, DAU, retention, etc.
    team_metrics: Dict[str, Any]  # Headcount, hiring, retention
    financial_health: Dict[str, float]  # Runway, burn rate, etc.
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class CEOAgent(BaseAgent):
    """
    CEO Agent responsible for high-level strategic decisions and company oversight.
    
    This agent provides capabilities for:
    - Setting and tracking company vision and strategy
    - Managing OKRs and strategic initiatives
    - Overseeing company performance and financial health
    - Making high-stakes decisions
    - Managing investor and board relations
    - Crisis management and risk assessment
    - Resource allocation and budgeting
    - Team structure and leadership
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.company_stage: CompanyStage = CompanyStage.IDEA
        self.strategic_initiatives: Dict[str, StrategicInitiative] = {}
        self.okrs: List[OKR] = []
        self.metrics: Optional[CompanyPerformanceMetrics] = None
        self._init_integrations()
    
    def _init_integrations(self) -> None:
        """Initialize necessary integrations."""
        try:
            self.analytics = get_analytics_integration()
            self.crm = get_crm_integration()
            self.finance = get_finance_integration()
            self.comms = get_communication_integration()
            logger.info("CEO Agent integrations initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CEO Agent integrations: {str(e)}")
            raise
    
    async def set_company_stage(self, stage: Union[CompanyStage, str]) -> AgentResponse:
        """
        Set or update the company's current growth stage.
        
        Args:
            stage: The company stage to set
            
        Returns:
            AgentResponse with success/error status
        """
        try:
            if isinstance(stage, str):
                stage = CompanyStage(stage.lower())
            
            self.company_stage = stage
            logger.info(f"Company stage updated to: {stage.value}")
            
            # Trigger stage-appropriate actions
            await self._on_stage_change(stage)
            
            return AgentResponse(
                success=True,
                output={"company_stage": stage.value},
                message=f"Company stage updated to {stage.value}"
            )
            
        except ValueError as e:
            error_msg = f"Invalid company stage: {stage}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Failed to update company stage: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _on_stage_change(self, new_stage: CompanyStage) -> None:
        """Handle actions when company stage changes."""
        # This method can be expanded to trigger stage-specific actions
        logger.info(f"Processing stage change to {new_stage.value}")
        
        # Example: Automatically create strategic initiatives for new stages
        if new_stage == CompanyStage.SEED:
            await self._create_seed_stage_initiatives()
        elif new_stage == CompanyStage.SERIES_A:
            await self._create_series_a_initiatives()
    
    async def _create_seed_stage_initiatives(self) -> None:
        """Create strategic initiatives for seed stage companies."""
        initiatives = [
            {
                "id": "product_mvp",
                "name": "Launch MVP",
                "description": "Develop and launch minimum viable product",
                "owner": "Product Team",
                "start_date": datetime.utcnow(),
                "target_date": datetime.utcnow() + timedelta(days=90),
                "priority": 1,
                "kpis": {"mrr_target": 10000, "users_target": 1000}
            },
            # Add more seed stage initiatives
        ]
        
        for init_data in initiatives:
            await self.create_strategic_initiative(init_data)
    
    async def create_strategic_initiative(self, initiative_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new strategic initiative.
        
        Args:
            initiative_data: Dictionary containing initiative details
            
        Returns:
            AgentResponse with created initiative or error
        """
        try:
            initiative = StrategicInitiative(**initiative_data)
            self.strategic_initiatives[initiative.id] = initiative
            
            logger.info(f"Created strategic initiative: {initiative.name}")
            
            return AgentResponse(
                success=True,
                output={"initiative": initiative.dict()},
                message=f"Created strategic initiative: {initiative.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create strategic initiative: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def update_initiative_progress(
        self, 
        initiative_id: str, 
        progress: float,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> AgentResponse:
        """
        Update progress on a strategic initiative.
        
        Args:
            initiative_id: ID of the initiative to update
            progress: New progress percentage (0-100)
            status: Optional new status
            notes: Optional progress notes
            
        Returns:
            AgentResponse with updated initiative or error
        """
        try:
            if initiative_id not in self.strategic_initiatives:
                raise ValueError(f"Initiative {initiative_id} not found")
            
            initiative = self.strategic_initiatives[initiative_id]
            initiative.progress = max(0, min(100, progress))  # Clamp between 0-100
            
            if status:
                initiative.status = status
            
            initiative.last_updated = datetime.utcnow()
            
            # Log the update
            logger.info(f"Updated initiative {initiative_id} progress to {progress}%")
            
            # Check if initiative is complete
            if progress >= 100 and initiative.status != "completed":
                initiative.status = "completed"
                await self._on_initiative_complete(initiative)
            
            return AgentResponse(
                success=True,
                output={"initiative": initiative.dict()},
                message=f"Updated initiative progress to {progress}%"
            )
            
        except Exception as e:
            error_msg = f"Failed to update initiative progress: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _on_initiative_complete(self, initiative: StrategicInitiative) -> None:
        """Handle actions when a strategic initiative is completed."""
        logger.info(f"Initiative completed: {initiative.name}")
        
        # Example: Send notification to leadership team
        await self.comms.send_message(
            channel="#leadership",
            message=f"🚀 Strategic Initiative Completed: {initiative.name}\n"
                   f"✅ Progress: 100%\n"
                   f"📅 Completed on: {datetime.utcnow().strftime('%Y-%m-%d')}"
        )
    
    async def create_okr(self, okr_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new OKR (Objectives and Key Results).
        
        Args:
            okr_data: Dictionary containing OKR details
            
        Returns:
            AgentResponse with created OKR or error
        """
        try:
            okr = OKR(**okr_data)
            self.okrs.append(okr)
            
            logger.info(f"Created OKR: {okr.objective}")
            
            return AgentResponse(
                success=True,
                output={"okr": okr.dict()},
                message=f"Created OKR: {okr.objective}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create OKR: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def update_company_metrics(self) -> AgentResponse:
        """
        Update company performance metrics from various data sources.
        
        Returns:
            AgentResponse with updated metrics or error
        """
        try:
            # Example: Get metrics from various integrations
            revenue_data = await self.finance.get_revenue_metrics()
            customer_metrics = await self.crm.get_customer_metrics()
            product_metrics = await self.analytics.get_product_metrics()
            
            # Create or update metrics
            self.metrics = CompanyPerformanceMetrics(
                revenue=revenue_data,
                expenses={},  # Would come from finance system
                customer_metrics=customer_metrics,
                product_metrics=product_metrics,
                team_metrics={},  # Would come from HR system
                financial_health={
                    "runway_months": 18,  # Example
                    "burn_rate": 50000,  # Monthly burn in USD
                    "gross_margin": 0.75  # 75%
                }
            )
            
            logger.info("Updated company performance metrics")
            
            return AgentResponse(
                success=True,
                output={"metrics": self.metrics.dict()},
                message="Updated company performance metrics"
            )
            
        except Exception as e:
            error_msg = f"Failed to update company metrics: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def make_strategic_decision(
        self,
        decision_context: Dict[str, Any],
        options: List[Dict[str, Any]],
        criteria: List[Dict[str, Any]]
    ) -> AgentResponse:
        """
        Make a strategic decision by evaluating options against criteria.
        
        Args:
            decision_context: Context about the decision to be made
            options: List of possible options with their attributes
            criteria: List of criteria to evaluate options against
            
        Returns:
            AgentResponse with decision and analysis
        """
        try:
            # This is a simplified example - in practice, this would use more sophisticated analysis
            # and potentially consult with other agents or data sources
            
            # Score each option based on criteria
            scored_options = []
            for option in options:
                score = 0
                analysis = {}
                
                for criterion in criteria:
                    criterion_name = criterion["name"]
                    weight = criterion.get("weight", 1.0)
                    
                    # Simple scoring logic - would be more sophisticated in practice
                    if criterion_name in option:
                        score += option[criterion_name] * weight
                    
                    analysis[criterion_name] = {
                        "weight": weight,
                        "score": option.get(criterion_name, 0)
                    }
                
                scored_options.append({
                    **option,
                    "total_score": score,
                    "analysis": analysis
                })
            
            # Sort by score (descending)
            scored_options.sort(key=lambda x: x["total_score"], reverse=True)
            
            # Get top recommendation
            recommendation = scored_options[0] if scored_options else None
            
            return AgentResponse(
                success=True,
                output={
                    "recommendation": recommendation,
                    "all_options": scored_options,
                    "context": decision_context
                },
                message="Strategic decision analysis complete"
            )
            
        except Exception as e:
            error_msg = f"Failed to make strategic decision: {str(e)}"
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
        # Initialize CEO Agent
        config = {
            "name": "CEO Agent",
            "description": "Manages company strategy and high-level decisions",
            "llm": {
                "model": "gpt-4"
            }
        }
        
        ceo = CEOAgent(config=config)
        
        # Set company stage
        await ceo.set_company_stage("seed")
        
        # Create a strategic initiative
        initiative = {
            "id": "market_expansion",
            "name": "Expand to New Market",
            "description": "Launch product in European market",
            "owner": "Growth Team",
            "start_date": "2023-07-01",
            "target_date": "2023-12-31",
            "priority": 1,
            "kpis": {"new_customers": 1000, "revenue_target": 50000}
        }
        await ceo.create_strategic_initiative(initiative)
        
        # Update progress
        await ceo.update_initiative_progress("market_expansion", 25, "in_progress")
        
        # Create an OKR
        okr_data = {
            "objective": "Achieve product-market fit in Europe",
            "key_results": [
                {"description": "Acquire 1000 paying customers", "target": 1000, "current": 250},
                {"description": "Achieve 40% week-over-week growth", "target": 40, "current": 15},
                {"description": "Maintain NPS > 50", "target": 50, "current": 45}
            ],
            "owner": "Growth Team",
            "timeline": {
                "start_date": "2023-07-01",
                "end_date": "2023-12-31"
            }
        }
        await ceo.create_okr(okr_data)
        
        # Make a strategic decision
        decision = await ceo.make_strategic_decision(
            decision_context={"question": "Which market should we expand to next?"},
            options=[
                {"market": "Germany", "market_size": 8, "competition": 7, "ease_of_entry": 6},
                {"market": "France", "market_size": 7, "competition": 6, "ease_of_entry": 8},
                {"market": "Spain", "market_size": 6, "competition": 5, "ease_of_entry": 9}
            ],
            criteria=[
                {"name": "market_size", "weight": 0.4},
                {"name": "competition", "weight": -0.3},  # Negative because lower is better
                {"name": "ease_of_entry", "weight": 0.3}
            ]
        )
        
        print("Decision:", decision.output["recommendation"])
    
    asyncio.run(main())
