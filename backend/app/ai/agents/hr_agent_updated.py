"""
Updated HRAgent with comprehensive HR management capabilities.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum
import logging

from .base_agent import BaseAgent, AgentConfig, AgentResponse
from .hr_agent_leave import HRAgentLeaveMixin, LeaveType, LeaveRequest
from .hr_agent_performance import HRAgentPerformanceMixin, PerformanceReview
from .hr_agent_training import HRAgentTrainingMixin, TrainingProgram

logger = logging.getLogger(__name__)

class EmploymentType(str, Enum):
    """Types of employment."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"
    FREELANCE = "freelance"

class EmployeeStatus(str, Enum):
    """Employee statuses."""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"
    OFFBOARDED = "offboarded"
    RETIRED = "retired"

class Employee(BaseModel):
    """Employee information model."""
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department: str
    position: str
    manager_id: Optional[str] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    hire_date: date
    termination_date: Optional[date] = None
    salary: Optional[float] = None
    skills: List[str] = []
    certifications: List[Dict[str, str]] = []
    emergency_contact: Optional[Dict[str, str]] = None
    work_location: Optional[str] = None
    work_schedule: Optional[Dict[str, Any]] = None
    documents: List[Dict[str, str]] = []
    custom_fields: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class HRAgent(HRAgentLeaveMixin, HRAgentPerformanceMixin, HRAgentTrainingMixin, BaseAgent):
    """
    Comprehensive HR Agent with employee lifecycle management, performance tracking,
    leave management, and training administration capabilities.
    
    This agent provides a complete suite of HR functions including:
    - Employee lifecycle management (hiring to offboarding)
    - Performance management and reviews
    - Leave and attendance tracking
    - Learning and development
    - HR analytics and reporting
    - Policy compliance
    - Employee engagement
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.employees: Dict[str, Employee] = {}
        self._init_integrations()
    
    def _init_integrations(self) -> None:
        """Initialize necessary integrations."""
        try:
            self.hrms = get_hrms_integration()
            self.communication = get_communication_integration()
            self.lms = get_learning_management_integration()
            self.analytics = get_analytics_integration()
            logger.info("HR Agent integrations initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HR Agent integrations: {str(e)}")
            raise
    
    # Employee Management
    async def onboard_employee(self, employee_data: Dict[str, Any]) -> AgentResponse:
        """
        Onboard a new employee.
        
        Args:
            employee_data: Dictionary containing employee details
            
        Returns:
            AgentResponse with onboarding status
        """
        try:
            # Create employee record
            employee = Employee(**employee_data)
            self.employees[employee.id] = employee
            
            # Generate onboarding tasks
            onboarding_plan = self._generate_onboarding_plan(employee)
            
            # Send welcome email
            await self._send_welcome_email(employee)
            
            # Create employee in HRMS
            await self.hrms.create_employee(employee.dict())
            
            logger.info(f"Onboarded new employee: {employee.first_name} {employee.last_name} ({employee.id})")
            
            return AgentResponse(
                success=True,
                output={
                    "employee_id": employee.id,
                    "onboarding_plan": onboarding_plan,
                    "status": "onboarding_started"
                },
                message=f"Started onboarding for {employee.first_name} {employee.last_name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to onboard employee: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    def _generate_onboarding_plan(self, employee: Employee) -> Dict[str, Any]:
        """Generate a personalized onboarding plan for a new employee."""
        return {
            "first_day": [
                "Complete HR paperwork",
                "Set up workstation and accounts",
                "Meet with HR for orientation",
                "Lunch with team"
            ],
            "first_week": [
                "Department overview meetings",
                "Product training sessions",
                "Meet with key stakeholders",
                "Set up 1:1 with manager"
            ],
            "first_30_days": [
                "Complete required training",
                "Meet with cross-functional teams",
                "Set 30/60/90 day goals",
                "Initial performance check-in"
            ],
            "resources": [
                "Employee handbook",
                "Company directory",
                "Team org chart",
                "Training materials"
            ]
        }
    
    async def _send_welcome_email(self, employee: Employee) -> None:
        """Send welcome email to new employee."""
        subject = f"Welcome to {self.config.get('company_name', 'Our Company')}, {employee.first_name}!"
        
        body = f"""
        Dear {employee.first_name},
        
        Welcome to {self.config.get('company_name', 'Our Company')}! We're thrilled to have you join our team as {employee.position}.
        
        Your first day is scheduled for {employee.hire_date.strftime('%A, %B %d, %Y')}.
        
        Next steps:
        1. Complete your new hire paperwork (check your email for links)
        2. Review the attached onboarding materials
        3. Join us for orientation at 9:00 AM on your first day
        
        If you have any questions before your start date, feel free to reach out to {self.config.get('hr_contact', 'HR')}.
        
        We look forward to seeing you soon!
        
        Best regards,
        {self.config.get('hr_team_name', 'The HR Team')}
        """
        
        await self.communication.send_email(
            to=employee.email,
            subject=subject,
            body=body.strip()
        )
    
    async def offboard_employee(self, employee_id: str, exit_details: Dict[str, Any]) -> AgentResponse:
        """
        Offboard an employee.
        
        Args:
            employee_id: ID of the employee to offboard
            exit_details: Dictionary containing exit details
                - last_working_date: Last working date
                - exit_reason: Reason for leaving
                - exit_interview_notes: Notes from exit interview
                - equipment_returned: Whether company equipment was returned
                - knowledge_transfer: Details of knowledge transfer
                
        Returns:
            AgentResponse with offboarding status
        """
        try:
            if employee_id not in self.employees:
                raise ValueError(f"Employee {employee_id} not found")
            
            employee = self.employees[employee_id]
            employee.status = EmployeeStatus.OFFBOARDED
            employee.termination_date = exit_details.get("last_working_date")
            employee.updated_at = datetime.utcnow()
            
            # Update HRMS
            await self.hrms.update_employee(employee_id, {
                "status": "offboarded",
                "termination_date": employee.termination_date.isoformat() if employee.termination_date else None,
                "exit_details": exit_details
            })
            
            # Send exit survey
            await self._send_exit_survey(employee, exit_details)
            
            # Disable system access
            await self._disable_system_access(employee_id)
            
            logger.info(f"Offboarded employee: {employee.first_name} {employee.last_name} ({employee_id})")
            
            return AgentResponse(
                success=True,
                output={
                    "employee_id": employee_id,
                    "status": "offboarded",
                    "last_working_date": exit_details.get("last_working_date")
                },
                message=f"Successfully offboarded {employee.first_name} {employee.last_name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to offboard employee: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _send_exit_survey(self, employee: Employee, exit_details: Dict[str, Any]) -> None:
        """Send exit survey to offboarding employee."""
        survey_link = f"{self.config.get('hr_portal_url', '')}/exit-survey/{employee.id}"
        
        subject = f"{self.config.get('company_name', 'Our Company')} - Exit Survey"
        body = f"""
        Dear {employee.first_name},
        
        As you prepare to leave {self.config.get('company_name', 'Our Company')}, we would appreciate your feedback 
        through our exit survey. Your input is valuable in helping us improve the employee experience.
        
        Please take a few minutes to complete the survey:
        {survey_link}
        
        Thank you for your time and contributions to our company. We wish you all the best in your future endeavors.
        
        Best regards,
        {self.config.get('hr_team_name', 'The HR Team')}
        """
        
        await self.communication.send_email(
            to=employee.email,
            subject=subject,
            body=body.strip()
        )
    
    async def _disable_system_access(self, employee_id: str) -> None:
        """Disable system access for an employee."""
        # In a real implementation, this would integrate with IAM systems
        logger.info(f"Disabling system access for employee {employee_id}")
        # Placeholder for actual implementation
        await asyncio.sleep(0.1)  # Simulate API call
    
    async def update_employee(self, employee_id: str, updates: Dict[str, Any]) -> AgentResponse:
        """
        Update employee information.
        
        Args:
            employee_id: ID of the employee to update
            updates: Dictionary of fields to update
            
        Returns:
            AgentResponse with update status
        """
        try:
            if employee_id not in self.employees:
                raise ValueError(f"Employee {employee_id} not found")
            
            employee = self.employees[employee_id]
            
            # Update employee fields
            for field, value in updates.items():
                if hasattr(employee, field):
                    setattr(employee, field, value)
            
            employee.updated_at = datetime.utcnow()
            
            # Update in HRMS
            await self.hrms.update_employee(employee_id, updates)
            
            logger.info(f"Updated employee {employee_id}")
            
            return AgentResponse(
                success=True,
                output={"employee": employee.dict()},
                message=f"Successfully updated employee {employee_id}"
            )
            
        except Exception as e:
            error_msg = f"Failed to update employee: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def get_employee(self, employee_id: str) -> AgentResponse:
        """
        Get employee details.
        
        Args:
            employee_id: ID of the employee
            
        Returns:
            AgentResponse with employee details or error
        """
        try:
            if employee_id not in self.employees:
                raise ValueError(f"Employee {employee_id} not found")
                
            employee = self.employees[employee_id]
            
            return AgentResponse(
                success=True,
                output={"employee": employee.dict()},
                message=f"Retrieved details for employee {employee_id}"
            )
            
        except Exception as e:
            error_msg = f"Failed to get employee: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def list_employees(self, filters: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        List employees with optional filtering.
        
        Args:
            filters: Dictionary of filters to apply
                - department: Filter by department
                - status: Filter by employee status
                - employment_type: Filter by employment type
                - etc.
                
        Returns:
            AgentResponse with list of employees matching filters
        """
        try:
            employees = list(self.employees.values())
            
            # Apply filters if provided
            if filters:
                filtered_employees = []
                for emp in employees:
                    match = True
                    for key, value in filters.items():
                        if hasattr(emp, key) and getattr(emp, key) != value:
                            match = False
                            break
                    if match:
                        filtered_employees.append(emp)
                employees = filtered_employees
            
            return AgentResponse(
                success=True,
                output={"employees": [e.dict() for e in employees]},
                message=f"Found {len(employees)} employees matching criteria"
            )
            
        except Exception as e:
            error_msg = f"Failed to list employees: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )

# Update the __init__.py to expose the new HRAgent
__all__ = [
    'HRAgent',
    'Employee',
    'EmployeeStatus',
    'EmploymentType',
    'LeaveType',
    'LeaveRequest',
    'PerformanceReview',
    'TrainingProgram'
]
