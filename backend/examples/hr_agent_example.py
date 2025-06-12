"""
Example usage of the HRAgent with comprehensive HR management capabilities.
"""

import asyncio
from datetime import date, datetime, timedelta
import logging
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ai.agents.hr_agent_updated import HRAgent, Employee, EmploymentType, EmployeeStatus, LeaveType
from app.ai.agents.base_agent import AgentConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock integration functions
def get_hrms_integration():
    class MockHRMS:
        async def create_employee(self, employee_data):
            logger.info(f"[MockHRMS] Creating employee: {employee_data['first_name']} {employee_data['last_name']}")
            return {"status": "success", "employee_id": employee_data['id']}
            
        async def update_employee(self, employee_id, updates):
            logger.info(f"[MockHRMS] Updating employee {employee_id}: {updates}")
            return {"status": "success"}
            
    return MockHRMS()

def get_communication_integration():
    class MockCommunication:
        async def send_email(self, to, subject, body):
            logger.info(f"[MockCommunication] Sending email to {to}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body[:200]}..." if len(body) > 200 else f"Body: {body}")
            return {"status": "sent"}
            
    return MockCommunication()

def get_learning_management_integration():
    class MockLMS:
        async def enroll_employee(self, employee_id, course_id):
            logger.info(f"[MockLMS] Enrolling employee {employee_id} in course {course_id}")
            return {"status": "enrolled"}
            
    return MockLMS()

def get_analytics_integration():
    class MockAnalytics:
        async def track_event(self, event_name, properties):
            logger.info(f"[MockAnalytics] Tracking event: {event_name} - {properties}")
            return {"status": "tracked"}
            
    return MockAnalytics()

# Override the integration functions in the module
import app.ai.agents.hr_agent_updated as hr_module
hr_module.get_hrms_integration = get_hrms_integration
hr_module.get_communication_integration = get_communication_integration
hr_module.get_learning_management_integration = get_learning_management_integration
hr_module.get_analytics_integration = get_analytics_integration

async def main():
    # Initialize the HR Agent
    config = AgentConfig(
        company_name="Acme Corp",
        hr_team_name="Acme HR Team",
        hr_contact="hr@acme.com",
        hr_portal_url="https://hr.acme.com"
    )
    hr_agent = HRAgent(config)
    
    # Example 1: Onboard a new employee
    print("\n=== EXAMPLE 1: ONBOARDING A NEW EMPLOYEE ===")
    onboarding_result = await hr_agent.onboard_employee({
        "id": "emp_001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@acme.com",
        "department": "Engineering",
        "position": "Software Engineer",
        "employment_type": EmploymentType.FULL_TIME,
        "hire_date": date.today(),
        "salary": 120000.00
    })
    print(f"Onboarding result: {onboarding_result}")
    
    # Example 2: Request leave
    print("\n=== EXAMPLE 2: REQUESTING LEAVE ===")
    leave_result = await hr_agent.request_leave({
        "id": "leave_001",
        "employee_id": "emp_001",
        "leave_type": LeaveType.VACATION,
        "start_date": date.today() + timedelta(days=30),
        "end_date": date.today() + timedelta(days=37),  # 1 week vacation
        "reason": "Annual vacation with family"
    })
    print(f"Leave request result: {leave_result}")
    
    # Example 3: Create a performance review
    print("\n=== EXAMPLE 3: CREATING A PERFORMANCE REVIEW ===")
    review_result = await hr_agent.create_performance_review({
        "id": "review_001",
        "employee_id": "emp_001",
        "reviewer_id": "mgr_001",  # Assuming manager ID
        "review_period": "2023-Q4",
        "scores": {
            "quality_of_work": 4.5,
            "productivity": 4.0,
            "teamwork": 4.5,
            "communication": 4.0
        },
        "strengths": [
            "Strong problem-solving skills",
            "Excellent team player",
            "Quick learner"
        ],
        "areas_for_improvement": [
            "Time management could be improved",
            "Could take more initiative in meetings"
        ],
        "goals": [
            {"goal": "Complete advanced Python certification", "timeline": "6 months"},
            {"goal": "Lead a small project", "timeline": "3 months"}
        ],
        "overall_rating": 4.25,
        "comments": "John has made significant contributions to the team and shows great potential."
    })
    print(f"Performance review result: {review_result}")
    
    # Example 4: Create a training program
    print("\n=== EXAMPLE 4: CREATING A TRAINING PROGRAM ===")
    training_result = await hr_agent.create_training_program({
        "id": "train_001",
        "name": "Advanced Python Development",
        "description": "In-depth training on advanced Python concepts and best practices.",
        "provider": "Acme Learning Solutions",
        "start_date": date.today() + timedelta(days=14),
        "end_date": date.today() + timedelta(days=21),
        "cost": 1500.00,
        "max_participants": 15
    })
    print(f"Training program result: {training_result}")
    
    # Example 5: Enroll employee in training
    print("\n=== EXAMPLE 5: ENROLLING EMPLOYEE IN TRAINING ===")
    enroll_result = await hr_agent.enroll_employee_in_training(
        program_id="train_001",
        employee_id="emp_001"
    )
    print(f"Enrollment result: {enroll_result}")
    
    # Example 6: Get employee details
    print("\n=== EXAMPLE 6: GETTING EMPLOYEE DETAILS ===")
    employee_result = await hr_agent.get_employee("emp_001")
    print(f"Employee details: {employee_result}")
    
    # Example 7: List all employees
    print("\n=== EXAMPLE 7: LISTING ALL EMPLOYEES ===")
    list_result = await hr_agent.list_employees()
    print(f"List employees result: {list_result}")
    
    # Example 8: Update employee information
    print("\n=== EXAMPLE 8: UPDATING EMPLOYEE INFORMATION ===")
    update_result = await hr_agent.update_employee("emp_001", {
        "position": "Senior Software Engineer",
        "salary": 135000.00,
        "skills": ["Python", "Django", "React", "AWS"]
    })
    print(f"Update result: {update_result}")
    
    # Example 9: Approve performance review
    print("\n=== EXAMPLE 9: APPROVING PERFORMANCE REVIEW ===")
    approve_result = await hr_agent.approve_performance_review(
        review_id="review_001",
        approver_id="hr_001",
        comments="Well-deserved promotion!"
    )
    print(f"Approve review result: {approve_result}")
    
    # Example 10: Offboard employee
    print("\n=== EXAMPLE 10: OFFBOARDING AN EMPLOYEE ===")
    offboard_result = await hr_agent.offboard_employee(
        employee_id="emp_001",
        exit_details={
            "last_working_date": date.today() + timedelta(days=30),
            "exit_reason": "Resignation",
            "exit_interview_notes": "Pursuing another opportunity",
            "equipment_returned": True,
            "knowledge_transfer": {
                "completed": True,
                "notes": "Knowledge transfer completed with team."
            }
        }
    )
    print(f"Offboarding result: {offboard_result}")

if __name__ == "__main__":
    asyncio.run(main())
