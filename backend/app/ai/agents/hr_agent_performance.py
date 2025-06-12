"""
HR Agent Performance Management Module.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
import logging
from pydantic import BaseModel, Field

from .base_agent import AgentResponse

logger = logging.getLogger(__name__)

class PerformanceReview(BaseModel):
    """Employee performance review model."""
    id: str
    employee_id: str
    review_period: str  # e.g., "2023-Q2"
    review_date: date = Field(default_factory=date.today)
    reviewer_id: str
    scores: Dict[str, float]  # category: score (1-5)
    strengths: List[str]
    areas_for_improvement: List[str]
    goals: List[Dict[str, Any]]
    overall_rating: float  # 1-5
    comments: str = ""
    is_approved: bool = False
    approved_by: Optional[str] = None
    approval_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HRAgentPerformanceMixin:
    """Mixin class for performance management functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.performance_reviews: Dict[str, List[PerformanceReview]] = {}
    
    async def create_performance_review(self, review_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a performance review for an employee.
        
        Args:
            review_data: Dictionary containing review details
                - employee_id: ID of the employee being reviewed
                - reviewer_id: ID of the person conducting the review
                - review_period: e.g., "2023-Q2"
                - scores: Dict of category: score (1-5)
                - strengths: List of strengths
                - areas_for_improvement: List of areas for improvement
                - goals: List of goals for next period
                - comments: Overall comments
                
        Returns:
            AgentResponse with created review or error
        """
        try:
            review = PerformanceReview(**review_data)
            
            if review.employee_id not in self.performance_reviews:
                self.performance_reviews[review.employee_id] = []
                
            self.performance_reviews[review.employee_id].append(review)
            
            # Notify employee and manager
            await self._notify_review_submission(review)
            
            logger.info(f"Created performance review {review.id} for employee {review.employee_id}")
            
            return AgentResponse(
                success=True,
                output={"review": review.dict()},
                message=f"Created performance review for employee {review.employee_id}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create performance review: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_review_submission(self, review: PerformanceReview) -> None:
        """Notify relevant parties about a submitted review."""
        employee = self.employees.get(review.employee_id)
        reviewer = self.employees.get(review.reviewer_id)
        
        if not employee or not reviewer:
            return
            
        # Notify employee
        subject = f"New Performance Review Submitted - {review.review_period}"
        body = f"""
        Dear {employee.first_name},
        
        A performance review has been submitted for you by {reviewer.first_name} {reviewer.last_name} 
        for the period: {review.review_period}.
        
        Overall Rating: {review.overall_rating}/5
        
        You can view the full review in the HR portal.
        
        Best regards,
        {self.config.get('hr_team_name', 'HR Team')}
        """
        
        await self.communication.send_email(
            to=employee.email,
            subject=subject,
            body=body.strip()
        )
    
    async def get_employee_reviews(self, employee_id: str) -> AgentResponse:
        """
        Get all performance reviews for an employee.
        
        Args:
            employee_id: ID of the employee
            
        Returns:
            AgentResponse with list of reviews or error
        """
        try:
            if employee_id not in self.employees:
                raise ValueError(f"Employee {employee_id} not found")
                
            reviews = self.performance_reviews.get(employee_id, [])
            
            return AgentResponse(
                success=True,
                output={"reviews": [r.dict() for r in reviews]},
                message=f"Found {len(reviews)} performance reviews for employee {employee_id}"
            )
            
        except Exception as e:
            error_msg = f"Failed to get performance reviews: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def approve_performance_review(self, review_id: str, approver_id: str, comments: str = "") -> AgentResponse:
        """
        Approve a performance review.
        
        Args:
            review_id: ID of the review to approve
            approver_id: ID of the person approving the review
            comments: Optional approval comments
            
        Returns:
            AgentResponse with approval status
        """
        try:
            # Find the review
            review = None
            for employee_id, reviews in self.performance_reviews.items():
                for r in reviews:
                    if r.id == review_id:
                        review = r
                        break
                if review:
                    break
                    
            if not review:
                raise ValueError(f"Performance review {review_id} not found")
                
            # Update review status
            review.is_approved = True
            review.approved_by = approver_id
            review.approval_date = datetime.utcnow().date()
            review.updated_at = datetime.utcnow()
            
            # Notify employee and reviewer
            await self._notify_review_approval(review, comments)
            
            logger.info(f"Approved performance review {review_id} by {approver_id}")
            
            return AgentResponse(
                success=True,
                output={"review": review.dict()},
                message=f"Approved performance review {review_id}"
            )
            
        except Exception as e:
            error_msg = f"Failed to approve performance review: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_review_approval(self, review: PerformanceReview, comments: str = "") -> None:
        """Notify relevant parties about review approval."""
        employee = self.employees.get(review.employee_id)
        reviewer = self.employees.get(review.reviewer_id)
        approver = self.employees.get(review.approved_by) if review.approved_by else None
        
        if not employee or not reviewer:
            return
            
        # Notify employee
        subject = f"Performance Review Approved - {review.review_period}"
        body = f"""
        Dear {employee.first_name},
        
        Your performance review for {review.review_period} has been approved.
        
        Overall Rating: {review.overall_rating}/5
        """
        
        if comments:
            body += f"\nApprover Comments: {comments}"
            
        if approver and approver.id != reviewer.id:
            body += f"\n\nApproved by: {approver.first_name} {approver.last_name}"
            
        body += "\n\nYou can view the full review in the HR portal.\n\nBest regards,\n        {self.config.get('hr_team_name', 'HR Team')}"
        
        await self.communication.send_email(
            to=employee.email,
            subject=subject,
            body=body.strip()
        )
        
        # Notify reviewer if different from approver
        if approver and approver.id != reviewer.id:
            subject = f"Performance Review Approved - {employee.first_name} {employee.last_name} - {review.review_period}"
            body = f"""
            Dear {reviewer.first_name},
            
            Your performance review for {employee.first_name} {employee.last_name} 
            for {review.review_period} has been approved by {approver.first_name} {approver.last_name}.
            
            Overall Rating: {review.overall_rating}/5
            """
            
            if comments:
                body += f"\nApprover Comments: {comments}"
                
            body += "\n\nYou can view the review in the HR portal.\n\nBest regards,\n            {self.config.get('hr_team_name', 'HR Team')}"
            
            await self.communication.send_email(
                to=reviewer.email,
                subject=subject,
                body=body.strip()
            )
