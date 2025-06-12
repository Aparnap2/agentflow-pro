"""
HR Agent Training Management Module.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
import logging
from pydantic import BaseModel, Field

from .base_agent import AgentResponse

logger = logging.getLogger(__name__)

class TrainingProgram(BaseModel):
    """Employee training program model."""
    id: str
    name: str
    description: str
    provider: str
    start_date: date
    end_date: Optional[date] = None
    cost: Optional[float] = None
    max_participants: Optional[int] = None
    enrolled_employees: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "upcoming"  # upcoming, in_progress, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HRAgentTrainingMixin:
    """Mixin class for training management functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.training_programs: Dict[str, TrainingProgram] = {}
    
    async def create_training_program(self, program_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new training program.
        
        Args:
            program_data: Dictionary containing program details
                - name: Name of the training program
                - description: Description of the program
                - provider: Training provider
                - start_date: Start date of the program
                - end_date: End date of the program (optional)
                - cost: Cost per participant (optional)
                - max_participants: Maximum number of participants (optional)
                
        Returns:
            AgentResponse with created program or error
        """
        try:
            program = TrainingProgram(**program_data)
            self.training_programs[program.id] = program
            
            logger.info(f"Created training program: {program.name} ({program.id})")
            
            return AgentResponse(
                success=True,
                output={"program": program.dict()},
                message=f"Created training program: {program.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create training program: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def enroll_employee_in_training(self, program_id: str, employee_id: str) -> AgentResponse:
        """
        Enroll an employee in a training program.
        
        Args:
            program_id: ID of the training program
            employee_id: ID of the employee to enroll
            
        Returns:
            AgentResponse with enrollment status
        """
        try:
            if program_id not in self.training_programs:
                raise ValueError(f"Training program {program_id} not found")
                
            if employee_id not in self.employees:
                raise ValueError(f"Employee {employee_id} not found")
                
            program = self.training_programs[program_id]
            employee = self.employees[employee_id]
            
            # Check if program is full
            if program.max_participants and len(program.enrolled_employees) >= program.max_participants:
                return AgentResponse(
                    success=False,
                    error="Training program is full",
                    output={
                        "program_id": program_id,
                        "max_participants": program.max_participants,
                        "current_enrollment": len(program.enrolled_employees)
                    }
                )
            
            # Check if employee is already enrolled
            if any(e.get("id") == employee_id for e in program.enrolled_employees):
                return AgentResponse(
                    success=False,
                    error="Employee is already enrolled in this program",
                    output={
                        "program_id": program_id,
                        "employee_id": employee_id
                    }
                )
            
            # Enroll employee
            enrollment = {
                "id": employee_id,
                "name": f"{employee.first_name} {employee.last_name}",
                "email": employee.email,
                "department": employee.department,
                "enrollment_date": datetime.utcnow().isoformat(),
                "status": "enrolled",
                "completion_status": "in_progress"
            }
            
            program.enrolled_employees.append(enrollment)
            program.updated_at = datetime.utcnow()
            
            # Notify employee
            await self._notify_training_enrollment(program, employee)
            
            logger.info(f"Enrolled employee {employee_id} in training program {program_id}")
            
            return AgentResponse(
                success=True,
                output={
                    "program_id": program_id,
                    "employee_id": employee_id,
                    "enrollment": enrollment
                },
                message=f"Enrolled {employee.first_name} {employee.last_name} in {program.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to enroll employee in training: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_training_enrollment(self, program: TrainingProgram, employee: 'Employee') -> None:
        """Notify employee about training enrollment."""
        subject = f"Enrollment Confirmation: {program.name}"
        
        body = f"""
        Dear {employee.first_name},
        
        You have been successfully enrolled in the following training program:
        
        Program: {program.name}
        Provider: {program.provider}
        Start Date: {program.start_date.strftime('%B %d, %Y')}
        """
        
        if program.end_date:
            body += f"End Date: {program.end_date.strftime('%B %d, %Y')}\n"
            
        body += "\n"
        
        if program.description:
            body += f"Program Description:\n{program.description}\n\n"
            
        body += """
        Please mark your calendar and prepare for the training. Additional details will be sent closer to the start date.
        
        If you have any questions, please contact your manager or the HR department.
        
        Best regards,
        {self.config.get('hr_team_name', 'HR Team')}
        """
        
        await self.communication.send_email(
            to=employee.email,
            subject=subject,
            body=body.strip()
        )
    
    async def update_training_program(self, program_id: str, updates: Dict[str, Any]) -> AgentResponse:
        """
        Update a training program.
        
        Args:
            program_id: ID of the program to update
            updates: Dictionary of fields to update
                - name: New name
                - description: New description
                - start_date: New start date
                - end_date: New end date
                - status: New status
                - etc.
                
        Returns:
            AgentResponse with update status
        """
        try:
            if program_id not in self.training_programs:
                raise ValueError(f"Training program {program_id} not found")
                
            program = self.training_programs[program_id]
            
            # Update fields
            for field, value in updates.items():
                if hasattr(program, field):
                    setattr(program, field, value)
            
            program.updated_at = datetime.utcnow()
            
            # Notify enrolled employees if there are important changes
            important_fields = {'start_date', 'end_date', 'status'}
            if any(field in updates for field in important_fields) and program.enrolled_employees:
                await self._notify_training_update(program, updates)
            
            logger.info(f"Updated training program {program_id}")
            
            return AgentResponse(
                success=True,
                output={"program": program.dict()},
                message=f"Updated training program: {program.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to update training program: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _notify_training_update(self, program: TrainingProgram, updates: Dict[str, Any]) -> None:
        """Notify enrolled employees about important training updates."""
        if not program.enrolled_employees:
            return
            
        # Get list of changed fields for the notification
        changed_fields = []
        for field, new_value in updates.items():
            if field in {'start_date', 'end_date', 'status'}:
                old_value = getattr(program, field, None)
                changed_fields.append(f"- {field.replace('_', ' ').title()}: {old_value} → {new_value}")
        
        if not changed_fields:
            return
            
        subject = f"Update: Changes to {program.name}"
        
        body = f"""
        Dear Participant,
        
        There have been important updates to the training program you are enrolled in:
        
        Program: {program.name}
        
        The following changes have been made:
        {changes}
        
        If you have any questions or concerns, please contact your manager or the HR department.
        
        Best regards,
        {self.config.get('hr_team_name', 'HR Team')}
        """.format(
            changes="\n".join(changed_fields)
        )
        
        # Send to all enrolled employees
        for enrollment in program.enrolled_employees:
            await self.communication.send_email(
                to=enrollment["email"],
                subject=subject,
                body=body.strip()
            )
    
    async def get_employee_trainings(self, employee_id: str) -> AgentResponse:
        """
        Get all training programs an employee is enrolled in.
        
        Args:
            employee_id: ID of the employee
            
        Returns:
            AgentResponse with list of training programs
        """
        try:
            if employee_id not in self.employees:
                raise ValueError(f"Employee {employee_id} not found")
                
            employee_trainings = []
            
            for program in self.training_programs.values():
                for enrollment in program.enrolled_employees:
                    if enrollment.get("id") == employee_id:
                        program_data = program.dict()
                        # Only include relevant enrollment info
                        program_data["enrollment"] = {
                            "status": enrollment.get("status"),
                            "completion_status": enrollment.get("completion_status"),
                            "enrollment_date": enrollment.get("enrollment_date")
                        }
                        employee_trainings.append(program_data)
                        break
            
            return AgentResponse(
                success=True,
                output={"trainings": employee_trainings},
                message=f"Found {len(employee_trainings)} training programs for employee {employee_id}"
            )
            
        except Exception as e:
            error_msg = f"Failed to get employee trainings: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
