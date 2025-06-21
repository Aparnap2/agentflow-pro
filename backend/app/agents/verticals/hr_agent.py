"""HR Agent implementation for human resources management and employee operations."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import json
import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal

from ..base import BaseAgent, AgentConfig, Department, AgentRole, AgentState

logger = logging.getLogger(__name__)

class HRAgent(BaseAgent):
    """Specialized agent for human resources management and employee operations."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "hr_agent",
            "name": "Patricia Williams",
            "role": AgentRole.HR_AGENT,
            "department": Department.HR,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Patricia Williams, HR Manager at AgentFlow Pro.\n"
                "You are empathetic, organized, and policy-focused. Your expertise includes "
                "employee management, payroll processing, leave administration, and HR compliance. "
                "You ensure fair treatment of all employees and maintain confidentiality. "
                "You understand employment law, benefits administration, and performance management."
            ),
            "tools": ["track_time", "manage_leave", "onboard_employee", "generate_payroll_report"],
            "specializations": ["Employee Management", "Payroll Processing", "Leave Administration", "HR Compliance"],
            "performance_metrics": {
                "employees_managed": 0,
                "leave_requests_processed": 0,
                "onboarding_completed": 0,
                "payroll_cycles_processed": 0,
                "compliance_score": 0.0,
                "employee_satisfaction": 0.0
            },
            "personality": {
                "tone": "professional and empathetic",
                "communication_style": "clear and supportive",
                "approach": "policy-compliant and people-focused"
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state: AgentState, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the HR query."""
        task = context.get("task_context", {})
        
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        HR Context:
        {json.dumps(context.get('hr_data', {}), indent=2)}
        
        HR Metrics:
        - Employees managed: {self.config.performance_metrics['employees_managed']}
        - Leave requests processed: {self.config.performance_metrics['leave_requests_processed']}
        - Onboarding completed: {self.config.performance_metrics['onboarding_completed']}
        - Payroll cycles processed: {self.config.performance_metrics['payroll_cycles_processed']}
        - Compliance score: {self.config.performance_metrics['compliance_score']:.1f}%
        - Employee satisfaction: {self.config.performance_metrics['employee_satisfaction']:.1f}/5.0
        
        Guidelines:
        1. Maintain strict confidentiality of employee information
        2. Ensure compliance with employment laws and regulations
        3. Treat all employees fairly and consistently
        4. Provide clear communication about policies and procedures
        5. Support employee development and well-being
        6. Maintain accurate records and documentation
        7. Handle sensitive situations with empathy and professionalism
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide comprehensive HR analysis and recommendations:")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update metrics
        if "employee" in response.content.lower():
            self.config.performance_metrics["employees_managed"] += 1
        
        # Determine if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "manager", "legal", "violation"]):
            state.escalate = True
            state.next_agent = "manager"
        
        return response
    
    @tool
    async def track_time(self, time_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Track employee time and attendance."""
        try:
            entry_id = f"TIME-{random.randint(10000, 99999)}"
            
            time_tracking = {
                "entry_id": entry_id,
                "employee_id": time_entry.get("employee_id"),
                "employee_name": time_entry.get("employee_name", ""),
                "date": time_entry.get("date", datetime.now().strftime("%Y-%m-%d")),
                "time_in": time_entry.get("time_in"),
                "time_out": time_entry.get("time_out"),
                "break_duration": time_entry.get("break_duration", 60),  # minutes
                "total_hours": 0.0,
                "overtime_hours": 0.0,
                "project_allocations": time_entry.get("project_allocations", []),
                "location": time_entry.get("location", "office"),  # office, remote, client_site
                "status": "Pending Approval",
                "notes": time_entry.get("notes", ""),
                "created_at": datetime.now().isoformat()
            }
            
            # Calculate total hours if time_in and time_out are provided
            if time_entry.get("time_in") and time_entry.get("time_out"):
                time_in = datetime.strptime(time_entry["time_in"], "%H:%M")
                time_out = datetime.strptime(time_entry["time_out"], "%H:%M")
                
                # Handle overnight shifts
                if time_out < time_in:
                    time_out += timedelta(days=1)
                
                total_minutes = (time_out - time_in).total_seconds() / 60
                total_minutes -= time_tracking["break_duration"]  # Subtract break time
                time_tracking["total_hours"] = round(total_minutes / 60, 2)
                
                # Calculate overtime (assuming 8-hour standard day)
                standard_hours = 8.0
                if time_tracking["total_hours"] > standard_hours:
                    time_tracking["overtime_hours"] = time_tracking["total_hours"] - standard_hours
            
            # Add project time allocations
            if time_tracking["project_allocations"]:
                total_allocated = sum(alloc.get("hours", 0) for alloc in time_tracking["project_allocations"])
                if total_allocated != time_tracking["total_hours"]:
                    time_tracking["allocation_discrepancy"] = time_tracking["total_hours"] - total_allocated
            
            # Validate against employee schedule
            time_tracking["schedule_compliance"] = {
                "expected_start": "09:00",
                "expected_end": "17:00",
                "early_arrival": False,
                "late_departure": False,
                "schedule_variance": 0
            }
            
            if time_entry.get("time_in"):
                expected_start = datetime.strptime("09:00", "%H:%M")
                actual_start = datetime.strptime(time_entry["time_in"], "%H:%M")
                variance_minutes = (actual_start - expected_start).total_seconds() / 60
                time_tracking["schedule_compliance"]["schedule_variance"] = variance_minutes
                time_tracking["schedule_compliance"]["early_arrival"] = variance_minutes < -15
                
            return time_tracking
            
        except Exception as e:
            logger.error(f"Error tracking time: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def manage_leave(self, leave_request: Dict[str, Any]) -> Dict[str, Any]:
        """Manage employee leave requests and balances."""
        try:
            request_id = f"LEAVE-{random.randint(10000, 99999)}"
            
            leave_types = ["vacation", "sick", "personal", "maternity", "paternity", "bereavement", "jury_duty"]
            leave_type = leave_request.get("type", "vacation")
            
            if leave_type not in leave_types:
                return {"error": f"Invalid leave type. Must be one of: {leave_types}"}
            
            # Parse dates
            start_date = datetime.fromisoformat(leave_request.get("start_date", datetime.now().strftime("%Y-%m-%d")))
            end_date = datetime.fromisoformat(leave_request.get("end_date", start_date.strftime("%Y-%m-%d")))
            
            # Calculate business days
            business_days = 0
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                    business_days += 1
                current_date += timedelta(days=1)
            
            leave_management = {
                "request_id": request_id,
                "employee_id": leave_request.get("employee_id"),
                "employee_name": leave_request.get("employee_name", ""),
                "leave_type": leave_type,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days_requested": business_days,
                "reason": leave_request.get("reason", ""),
                "status": "Pending",
                "submitted_date": datetime.now().strftime("%Y-%m-%d"),
                "manager_approval": None,
                "hr_approval": None,
                "balance_check": {},
                "coverage_plan": leave_request.get("coverage_plan", ""),
                "emergency_contact": leave_request.get("emergency_contact", {}),
                "processed_by": self.config.name
            }
            
            # Check leave balance (simulated)
            leave_balances = {
                "vacation": random.randint(10, 25),
                "sick": random.randint(5, 15),
                "personal": random.randint(2, 8)
            }
            
            current_balance = leave_balances.get(leave_type, 0)
            leave_management["balance_check"] = {
                "current_balance": current_balance,
                "requested_days": business_days,
                "remaining_balance": max(0, current_balance - business_days),
                "sufficient_balance": current_balance >= business_days
            }
            
            # Auto-approve certain types of leave
            if leave_type in ["sick", "bereavement"] and business_days <= 3:
                leave_management["status"] = "Auto-Approved"
                leave_management["hr_approval"] = {
                    "approved_by": self.config.name,
                    "approved_date": datetime.now().strftime("%Y-%m-%d"),
                    "notes": f"Auto-approved {leave_type} leave"
                }
            elif not leave_management["balance_check"]["sufficient_balance"]:
                leave_management["status"] = "Rejected"
                leave_management["rejection_reason"] = "Insufficient leave balance"
            
            # Add compliance checks
            leave_management["compliance"] = {
                "fmla_eligible": leave_type in ["maternity", "paternity"] and business_days > 10,
                "advance_notice_met": True,  # Assume proper notice given
                "documentation_required": leave_type in ["sick", "maternity", "paternity"] and business_days > 3,
                "return_to_work_required": leave_type == "sick" and business_days > 5
            }
            
            # Update metrics
            self.config.performance_metrics["leave_requests_processed"] += 1
            
            return leave_management
            
        except Exception as e:
            logger.error(f"Error managing leave: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def onboard_employee(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage employee onboarding process."""
        try:
            onboarding_id = f"ONBOARD-{random.randint(10000, 99999)}"
            
            onboarding = {
                "onboarding_id": onboarding_id,
                "employee_info": {
                    "employee_id": employee_data.get("employee_id", f"EMP-{random.randint(1000, 9999)}"),
                    "first_name": employee_data.get("first_name", ""),
                    "last_name": employee_data.get("last_name", ""),
                    "email": employee_data.get("email", ""),
                    "phone": employee_data.get("phone", ""),
                    "start_date": employee_data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                    "position": employee_data.get("position", ""),
                    "department": employee_data.get("department", ""),
                    "manager": employee_data.get("manager", ""),
                    "employment_type": employee_data.get("employment_type", "full_time")  # full_time, part_time, contract
                },
                "onboarding_checklist": {
                    "pre_boarding": {
                        "offer_letter_signed": employee_data.get("offer_signed", False),
                        "background_check_completed": employee_data.get("background_check", False),
                        "i9_form_completed": False,
                        "tax_forms_completed": False,
                        "benefits_enrollment": False,
                        "equipment_ordered": False
                    },
                    "first_day": {
                        "workspace_setup": False,
                        "id_badge_issued": False,
                        "system_access_granted": False,
                        "welcome_meeting": False,
                        "hr_orientation": False,
                        "safety_training": False
                    },
                    "first_week": {
                        "department_introduction": False,
                        "role_specific_training": False,
                        "mentor_assigned": False,
                        "initial_goals_set": False,
                        "company_culture_session": False
                    },
                    "first_month": {
                        "30_day_check_in": False,
                        "performance_expectations_review": False,
                        "feedback_session": False,
                        "training_plan_finalized": False
                    }
                },
                "required_documents": [
                    {"name": "I-9 Form", "status": "pending", "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")},
                    {"name": "W-4 Tax Form", "status": "pending", "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                    {"name": "Direct Deposit Form", "status": "pending", "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")},
                    {"name": "Emergency Contact Form", "status": "pending", "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")},
                    {"name": "Employee Handbook Acknowledgment", "status": "pending", "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")}
                ],
                "equipment_assignment": {
                    "laptop": {"assigned": False, "model": "MacBook Pro", "serial": ""},
                    "monitor": {"assigned": False, "model": "Dell 27\"", "serial": ""},
                    "phone": {"assigned": False, "model": "iPhone 13", "number": ""},
                    "accessories": {"assigned": False, "items": ["keyboard", "mouse", "headset"]}
                },
                "system_access": {
                    "email_account": {"created": False, "username": "", "temporary_password": ""},
                    "slack": {"invited": False, "channels": ["#general", "#hr", "#department"]},
                    "project_management": {"access_granted": False, "role": "member"},
                    "hr_system": {"access_granted": False, "permissions": ["view_profile", "submit_requests"]},
                    "vpn": {"configured": False, "credentials_provided": False}
                },
                "training_schedule": [
                    {
                        "training": "Company Overview",
                        "scheduled_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                        "duration": "2 hours",
                        "completed": False
                    },
                    {
                        "training": "HR Policies and Procedures",
                        "scheduled_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                        "duration": "1 hour",
                        "completed": False
                    },
                    {
                        "training": "Department-Specific Training",
                        "scheduled_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                        "duration": "4 hours",
                        "completed": False
                    }
                ],
                "progress": {
                    "overall_completion": 0.0,
                    "pre_boarding_completion": 0.0,
                    "first_day_completion": 0.0,
                    "first_week_completion": 0.0,
                    "first_month_completion": 0.0
                },
                "assigned_buddy": {
                    "name": random.choice(["Sarah Johnson", "Mike Chen", "Lisa Rodriguez"]),
                    "email": "buddy@agentflow.pro",
                    "department": employee_data.get("department", "")
                },
                "created_by": self.config.name,
                "created_at": datetime.now().isoformat(),
                "status": "In Progress"
            }
            
            # Calculate initial progress
            total_items = sum(len(section) for section in onboarding["onboarding_checklist"].values())
            completed_items = sum(
                sum(1 for item in section.values() if item) 
                for section in onboarding["onboarding_checklist"].values()
            )
            onboarding["progress"]["overall_completion"] = (completed_items / total_items * 100) if total_items > 0 else 0
            
            # Update metrics
            self.config.performance_metrics["onboarding_completed"] += 1
            
            return onboarding
            
        except Exception as e:
            logger.error(f"Error onboarding employee: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def generate_payroll_report(self, report_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate payroll reports and summaries."""
        try:
            report_id = f"PAYROLL-{random.randint(10000, 99999)}"
            
            # Parse report parameters
            pay_period_start = datetime.fromisoformat(report_params.get("pay_period_start", (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")))
            pay_period_end = datetime.fromisoformat(report_params.get("pay_period_end", datetime.now().strftime("%Y-%m-%d")))
            report_type = report_params.get("report_type", "summary")  # summary, detailed, tax_report
            
            payroll_report = {
                "report_id": report_id,
                "report_type": report_type,
                "pay_period": {
                    "start_date": pay_period_start.strftime("%Y-%m-%d"),
                    "end_date": pay_period_end.strftime("%Y-%m-%d"),
                    "pay_date": (pay_period_end + timedelta(days=3)).strftime("%Y-%m-%d")
                },
                "summary": {
                    "total_employees": random.randint(20, 100),
                    "total_gross_pay": 0.0,
                    "total_deductions": 0.0,
                    "total_net_pay": 0.0,
                    "total_employer_taxes": 0.0,
                    "total_hours_worked": 0.0,
                    "overtime_hours": 0.0
                },
                "employee_details": [],
                "deduction_summary": {
                    "federal_tax": 0.0,
                    "state_tax": 0.0,
                    "social_security": 0.0,
                    "medicare": 0.0,
                    "health_insurance": 0.0,
                    "dental_insurance": 0.0,
                    "retirement_401k": 0.0,
                    "other_deductions": 0.0
                },
                "compliance_checks": {
                    "minimum_wage_compliance": True,
                    "overtime_calculations_correct": True,
                    "tax_withholding_accurate": True,
                    "benefit_deductions_valid": True
                },
                "generated_by": self.config.name,
                "generated_at": datetime.now().isoformat()
            }
            
            # Generate employee payroll data
            for i in range(payroll_report["summary"]["total_employees"]):
                employee_id = f"EMP-{1000 + i}"
                
                # Simulate employee payroll data
                regular_hours = random.uniform(70, 80)  # Bi-weekly hours
                overtime_hours = random.uniform(0, 10)
                hourly_rate = random.uniform(20, 50)
                
                gross_pay = (regular_hours * hourly_rate) + (overtime_hours * hourly_rate * 1.5)
                
                # Calculate deductions
                federal_tax = gross_pay * 0.12
                state_tax = gross_pay * 0.05
                social_security = gross_pay * 0.062
                medicare = gross_pay * 0.0145
                health_insurance = random.uniform(50, 150)
                retirement_401k = gross_pay * random.uniform(0.03, 0.06)
                
                total_deductions = federal_tax + state_tax + social_security + medicare + health_insurance + retirement_401k
                net_pay = gross_pay - total_deductions
                
                employee_payroll = {
                    "employee_id": employee_id,
                    "name": f"Employee {i+1}",
                    "regular_hours": round(regular_hours, 2),
                    "overtime_hours": round(overtime_hours, 2),
                    "hourly_rate": round(hourly_rate, 2),
                    "gross_pay": round(gross_pay, 2),
                    "deductions": {
                        "federal_tax": round(federal_tax, 2),
                        "state_tax": round(state_tax, 2),
                        "social_security": round(social_security, 2),
                        "medicare": round(medicare, 2),
                        "health_insurance": round(health_insurance, 2),
                        "retirement_401k": round(retirement_401k, 2)
                    },
                    "total_deductions": round(total_deductions, 2),
                    "net_pay": round(net_pay, 2)
                }
                
                payroll_report["employee_details"].append(employee_payroll)
                
                # Update summary totals
                payroll_report["summary"]["total_gross_pay"] += gross_pay
                payroll_report["summary"]["total_deductions"] += total_deductions
                payroll_report["summary"]["total_net_pay"] += net_pay
                payroll_report["summary"]["total_hours_worked"] += regular_hours
                payroll_report["summary"]["overtime_hours"] += overtime_hours
                
                # Update deduction summary
                for deduction_type, amount in employee_payroll["deductions"].items():
                    payroll_report["deduction_summary"][deduction_type] += amount
            
            # Round summary totals
            for key in payroll_report["summary"]:
                if isinstance(payroll_report["summary"][key], float):
                    payroll_report["summary"][key] = round(payroll_report["summary"][key], 2)
            
            for key in payroll_report["deduction_summary"]:
                payroll_report["deduction_summary"][key] = round(payroll_report["deduction_summary"][key], 2)
            
            # Update metrics
            self.config.performance_metrics["payroll_cycles_processed"] += 1
            
            return payroll_report
            
        except Exception as e:
            logger.error(f"Error generating payroll report: {str(e)}")
            return {"error": str(e)}