"""
HR Agent Leave Management Module.
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, date
import logging
from pydantic import BaseModel, Field

from .base_agent import AgentResponse

logger = logging.getLogger(__name__)

class LeaveType(str, Enum):
    """Types of leave."""
    VACATION = "vacation"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    UNPAID = "unpaid"

class LeaveRequest(BaseModel):
    """Leave request model."""
    id: str
    employee_id: str
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str
    status: str = "pending"  # pending, approved, rejected, cancelled
    approver_id: Optional[str] = None
    approver_comments: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HRAgentLeaveMixin:
    """Mixin class for leave management functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.leave_requests: Dict[str, LeaveRequest] = {}
    
    async def request_leave(self, leave_data: Dict[str, Any]) -> AgentResponse:
        """
        Submit a leave request.
        
        Args:
            leave_data: Dictionary containing leave request details
                - employee_id: ID of the employee requesting leave
                - leave_type: Type of leave (from LeaveType enum)
                - start_date: Start date of leave
                - end_date: End date of leave
                - reason: Reason for leave
                
        Returns:
            AgentResponse with leave request status
        """
        try:
            if leave_data.get("employee_id") not in self.employees:
                raise ValueError(f"Employee {leave_data.get('employee_id')} not found")
                
            # Check for leave balance
            leave_balance = await self._check_leave_balance(
                leave_data["employee_id"], 
                leave_data["leave_type"]
            )
            
            if not leave_balance.get("has_sufficient_balance", False):
                return AgentResponse(
                    success=False,
                    error="Insufficient leave balance",
                    output={"leave_balance": leave_balance}
                )
            
            # Create leave request
            leave_request = LeaveRequest(**leave_data)
            self.leave_requests[leave_request.id] = leave_request
            
            # Notify manager for approval
            await self._notify_leave_request(leave_request)
            
            logger.info(f"Leave request {leave_request.id} submitted by employee {leave_request.employee_id}")
            
            return AgentResponse(
                success=True,
                output={
                    "leave_request": leave_request.dict(),
                    "leave_balance": leave_balance
                },
                message="Leave request submitted successfully"
            )
            
        except Exception as e:
            error_msg = f"Failed to submit leave request: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _check_leave_balance(self, employee_id: str, leave_type: str) -> Dict[str, Any]:
        """Check employee's leave balance for the specified leave type."""
        # In a real implementation, this would check against HRMS/leave management system
        # This is a simplified version
        return {
            "employee_id": employee_id,
            "leave_type": leave_type,
            "total_entitlement": 20,  # days per year
            "used": 5,  # days used so far
            "remaining": 15,  # days remaining
            "has_sufficient_balance": True
        }
    
    async def _notify_leave_request(self, leave_request: LeaveRequest) -> None:
        """Notify manager about a new leave request."""
        employee = self.employees.get(leave_request.employee_id)
        if not employee or not employee.manager_id:
            return
            
        manager = self.employees.get(employee.manager_id)
        if not manager:
            return
            
        subject = f"Leave Request from {employee.first_name} {employee.last_name}"
        body = f"""
        Dear {manager.first_name},
        
        {employee.first_name} {employee.last_name} has submitted a leave request:
        
        Type: {leave_request.leave_type.value}
        Dates: {leave_request.start_date} to {leave_request.end_date}
        Reason: {leave_request.reason}
        
        Please review and approve/deny this request.
        
        Best regards,
        HR System
        """
        
        await self.communication.send_email(
            to=manager.email,
            subject=subject,
            body=body.strip()
        )
    
    async def update_leave_request(self, request_id: str, updates: Dict[str, Any]) -> AgentResponse:
        """
        Update a leave request (e.g., approve, reject, cancel).
        
        Args:
            request_id: ID of the leave request to update
            updates: Dictionary of fields to update
                - status: New status (approved, rejected, cancelled)
                - approver_id: ID of the person approving/rejecting
                - approver_comments: Optional comments
                
        Returns:
            AgentResponse with update status
        """
        try:
            if request_id not in self.leave_requests:
                raise ValueError(f"Leave request {request_id} not found")
                
            leave_request = self.leave_requests[request_id]
            
            # Update fields
            for field, value in updates.items():
                if hasattr(leave_request, field):
                    setattr(leave_request, field, value)
            
            leave_request.updated_at = datetime.utcnow()
            
            # Notify employee of status change
            await self._notify_leave_status_change(leave_request)
            
            logger.info(f"Updated leave request {request_id} to status: {leave_request.status}")
            
            return AgentResponse(
                success=True,
                output={"leave_request": leave_request.dict()},
                message=f"Leave request {request_id} updated to {leave_request.status}"
            )
            
        except Exception as e:
            error_msg = f"Failed to update leave request: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_leave_status_change(self, leave_request: LeaveRequest) -> None:
        """Notify employee about leave request status change."""
        employee = self.employees.get(leave_request.employee_id)
        if not employee:
            return
            
        approver = self.employees.get(leave_request.approver_id) if leave_request.approver_id else None
        
        status_display = leave_request.status.capitalize()
        subject = f"Leave Request {status_display} - {leave_request.start_date} to {leave_request.end_date}"
        
        body = f"""
        Dear {employee.first_name},
        
        Your leave request has been {leave_request.status}.
        
        Details:
        Type: {leave_request.leave_type.value}
        Dates: {leave_request.start_date} to {leave_request.end_date}
        Status: {status_display}
        """
        
        if leave_request.approver_comments:
            body += f"\nComments: {leave_request.approver_comments}"
            
        if approver:
            body += f"\n\nApproved by: {approver.first_name} {approver.last_name}"
            
        body += "\n\nBest regards,\n        HR System"
        
        await self.communication.send_email(
            to=employee.email,
            subject=subject,
            body=body.strip()
        )
    
    async def get_leave_balance(self, employee_id: str, leave_type: Optional[str] = None) -> AgentResponse:
        """
        Get leave balance for an employee.
        
        Args:
            employee_id: ID of the employee
            leave_type: Optional filter for specific leave type
            
        Returns:
            AgentResponse with leave balance information
        """
        try:
            if employee_id not in self.employees:
                raise ValueError(f"Employee {employee_id} not found")
                
            # In a real implementation, this would fetch from HRMS
            # This is a simplified version
            balances = {
                "vacation": {"entitlement": 20, "used": 5, "remaining": 15},
                "sick": {"entitlement": 10, "used": 2, "remaining": 8},
                "personal": {"entitlement": 5, "used": 1, "remaining": 4}
            }
            
            if leave_type:
                if leave_type not in balances:
                    return AgentResponse(
                        success=False,
                        error=f"Invalid leave type: {leave_type}"
                    )
                return AgentResponse(
                    success=True,
                    output={"balance": balances[leave_type]},
                    message=f"Leave balance for {leave_type}"
                )
            
            return AgentResponse(
                success=True,
                output={"balances": balances},
                message="Retrieved all leave balances"
            )
            
        except Exception as e:
            error_msg = f"Failed to get leave balance: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
