"""Scheduling Agent implementation for calendar and appointment management."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import json
import logging
import random
from datetime import datetime, timedelta

from ..base import BaseAgent, AgentConfig, Department, AgentRole, AgentState

logger = logging.getLogger(__name__)

class SchedulingAgent(BaseAgent):
    """Specialized agent for scheduling, calendar management, and appointment coordination."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "scheduling_agent",
            "name": "Alex Rivera",
            "role": AgentRole.SCHEDULING_AGENT,
            "department": Department.OPERATIONS,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Alex Rivera, Scheduling Coordinator at AgentFlow Pro.\n"
                "You are organized, efficient, and detail-oriented. Your expertise includes "
                "appointment scheduling, calendar management, meeting coordination, and automated reminders. "
                "You ensure optimal time management and prevent scheduling conflicts. You understand "
                "different time zones, availability patterns, and meeting preferences."
            ),
            "tools": ["book_appointment", "sync_calendar", "send_reminder", "check_availability"],
            "specializations": ["Appointment Scheduling", "Calendar Management", "Meeting Coordination", "Automated Reminders"],
            "performance_metrics": {
                "appointments_booked": 0,
                "calendars_synced": 0,
                "reminders_sent": 0,
                "no_shows": 0,
                "booking_efficiency": 0.0,
                "average_booking_time": 0.0
            },
            "personality": {
                "tone": "friendly and efficient",
                "communication_style": "clear and organized",
                "approach": "proactive and systematic"
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state: AgentState, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the scheduling query."""
        task = context.get("task_context", {})
        
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        Scheduling Context:
        {json.dumps(context.get('calendar_data', {}), indent=2)}
        
        Scheduling Metrics:
        - Appointments booked: {self.config.performance_metrics['appointments_booked']}
        - Calendars synced: {self.config.performance_metrics['calendars_synced']}
        - Reminders sent: {self.config.performance_metrics['reminders_sent']}
        - No-show rate: {(self.config.performance_metrics['no_shows'] / max(1, self.config.performance_metrics['appointments_booked']) * 100):.1f}%
        - Booking efficiency: {self.config.performance_metrics['booking_efficiency']:.1f}%
        - Average booking time: {self.config.performance_metrics['average_booking_time']:.1f} minutes
        
        Guidelines:
        1. Optimize scheduling to minimize conflicts and maximize efficiency
        2. Consider time zones and participant preferences
        3. Send timely reminders and confirmations
        4. Handle rescheduling and cancellations professionally
        5. Maintain accurate calendar synchronization
        6. Provide clear meeting details and instructions
        7. Track and minimize no-shows
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide comprehensive scheduling analysis and recommendations:")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update metrics
        if "appointment" in response.content.lower() or "meeting" in response.content.lower():
            self.config.performance_metrics["appointments_booked"] += 1
        
        # Determine if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "manager", "conflict"]):
            state.escalate = True
            state.next_agent = "manager"
        
        return response
    
    @tool
    async def book_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Book a new appointment with availability checking."""
        try:
            appointment_id = f"APPT-{random.randint(10000, 99999)}"
            
            # Parse appointment details
            start_time = datetime.fromisoformat(appointment_data.get("start_time", datetime.now().isoformat()))
            duration_minutes = appointment_data.get("duration_minutes", 60)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            appointment = {
                "id": appointment_id,
                "title": appointment_data.get("title", "Meeting"),
                "description": appointment_data.get("description", ""),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": duration_minutes,
                "timezone": appointment_data.get("timezone", "UTC"),
                "location": {
                    "type": appointment_data.get("location_type", "virtual"),  # virtual, in_person, phone
                    "details": appointment_data.get("location_details", ""),
                    "meeting_url": f"https://meet.agentflow.pro/{appointment_id}" if appointment_data.get("location_type") == "virtual" else None
                },
                "organizer": {
                    "name": appointment_data.get("organizer_name", self.config.name),
                    "email": appointment_data.get("organizer_email", "scheduling@agentflow.pro")
                },
                "attendees": [],
                "status": "Confirmed",
                "booking_source": appointment_data.get("booking_source", "manual"),
                "reminders": [
                    {"type": "email", "minutes_before": 1440},  # 24 hours
                    {"type": "email", "minutes_before": 60},    # 1 hour
                    {"type": "sms", "minutes_before": 15}       # 15 minutes
                ],
                "created_by": self.config.name,
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat()
            }
            
            # Add attendees
            for attendee in appointment_data.get("attendees", []):
                appointment["attendees"].append({
                    "name": attendee.get("name", ""),
                    "email": attendee.get("email", ""),
                    "phone": attendee.get("phone", ""),
                    "status": "Pending",
                    "required": attendee.get("required", True)
                })
            
            # Add recurring pattern if specified
            if appointment_data.get("recurring"):
                appointment["recurring"] = {
                    "pattern": appointment_data["recurring"].get("pattern", "weekly"),  # daily, weekly, monthly
                    "interval": appointment_data["recurring"].get("interval", 1),
                    "end_date": appointment_data["recurring"].get("end_date"),
                    "occurrences": appointment_data["recurring"].get("occurrences")
                }
            
            # Check for conflicts (simulated)
            conflict_probability = random.random()
            if conflict_probability < 0.1:  # 10% chance of conflict
                appointment["status"] = "Conflict Detected"
                appointment["conflicts"] = [
                    {
                        "conflicting_appointment_id": f"APPT-{random.randint(10000, 99999)}",
                        "conflict_type": "time_overlap",
                        "suggested_alternatives": [
                            (start_time + timedelta(hours=1)).isoformat(),
                            (start_time + timedelta(hours=2)).isoformat(),
                            (start_time + timedelta(days=1)).isoformat()
                        ]
                    }
                ]
            
            # Update metrics
            self.config.performance_metrics["appointments_booked"] += 1
            
            return appointment
            
        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def sync_calendar(self, calendar_config: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize with external calendar systems."""
        try:
            sync_id = f"SYNC-{random.randint(10000, 99999)}"
            
            calendar_sync = {
                "sync_id": sync_id,
                "calendar_provider": calendar_config.get("provider", "google"),  # google, outlook, apple
                "account_email": calendar_config.get("account_email", ""),
                "sync_direction": calendar_config.get("sync_direction", "bidirectional"),  # import, export, bidirectional
                "sync_settings": {
                    "sync_frequency": calendar_config.get("sync_frequency", "real_time"),  # real_time, hourly, daily
                    "sync_past_days": calendar_config.get("sync_past_days", 30),
                    "sync_future_days": calendar_config.get("sync_future_days", 365),
                    "include_private_events": calendar_config.get("include_private", False)
                },
                "last_sync": datetime.now().isoformat(),
                "sync_status": "Success",
                "events_synced": random.randint(10, 100),
                "conflicts_resolved": random.randint(0, 5),
                "errors": []
            }
            
            # Simulate sync results
            sync_success_rate = random.uniform(0.85, 1.0)
            if sync_success_rate < 0.9:
                calendar_sync["sync_status"] = "Partial Success"
                calendar_sync["errors"] = [
                    {
                        "error_type": "permission_denied",
                        "event_id": f"EXT-{random.randint(1000, 9999)}",
                        "message": "Insufficient permissions to sync private event"
                    }
                ]
            
            # Add sync statistics
            calendar_sync["statistics"] = {
                "total_events": random.randint(50, 500),
                "events_imported": random.randint(20, 200),
                "events_exported": random.randint(10, 100),
                "duplicates_found": random.randint(0, 10),
                "conflicts_detected": random.randint(0, 5)
            }
            
            # Update metrics
            self.config.performance_metrics["calendars_synced"] += 1
            
            return calendar_sync
            
        except Exception as e:
            logger.error(f"Error syncing calendar: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def send_reminder(self, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send appointment reminders to attendees."""
        try:
            reminder_id = f"REM-{random.randint(10000, 99999)}"
            
            reminder = {
                "id": reminder_id,
                "appointment_id": reminder_data.get("appointment_id"),
                "reminder_type": reminder_data.get("type", "email"),  # email, sms, push
                "minutes_before": reminder_data.get("minutes_before", 60),
                "recipients": reminder_data.get("recipients", []),
                "template": {
                    "subject": reminder_data.get("subject", "Appointment Reminder"),
                    "message": reminder_data.get("message", "You have an upcoming appointment."),
                    "include_calendar_invite": reminder_data.get("include_calendar_invite", True),
                    "include_join_link": reminder_data.get("include_join_link", True)
                },
                "delivery_status": {},
                "scheduled_time": (datetime.now() + timedelta(minutes=reminder_data.get("minutes_before", 60))).isoformat(),
                "sent_time": None,
                "created_by": self.config.name,
                "created_at": datetime.now().isoformat()
            }
            
            # Simulate delivery status for each recipient
            for recipient in reminder["recipients"]:
                delivery_success = random.random() > 0.05  # 95% success rate
                reminder["delivery_status"][recipient] = {
                    "status": "Delivered" if delivery_success else "Failed",
                    "delivered_at": datetime.now().isoformat() if delivery_success else None,
                    "error_message": None if delivery_success else "Invalid email address"
                }
            
            # If sending immediately
            if reminder_data.get("send_immediately", False):
                reminder["sent_time"] = datetime.now().isoformat()
                reminder["status"] = "Sent"
            else:
                reminder["status"] = "Scheduled"
            
            # Update metrics
            self.config.performance_metrics["reminders_sent"] += 1
            
            return reminder
            
        except Exception as e:
            logger.error(f"Error sending reminder: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def check_availability(self, availability_request: Dict[str, Any]) -> Dict[str, Any]:
        """Check availability for scheduling appointments."""
        try:
            # Parse request parameters
            start_date = datetime.fromisoformat(availability_request.get("start_date", datetime.now().strftime("%Y-%m-%d")))
            end_date = datetime.fromisoformat(availability_request.get("end_date", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")))
            duration_minutes = availability_request.get("duration_minutes", 60)
            timezone = availability_request.get("timezone", "UTC")
            
            # Working hours configuration
            working_hours = availability_request.get("working_hours", {
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "09:00", "end": "17:00"},
                "saturday": None,  # Not available
                "sunday": None    # Not available
            })
            
            availability = {
                "request_id": f"AVAIL-{random.randint(10000, 99999)}",
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "timezone": timezone
                },
                "requirements": {
                    "duration_minutes": duration_minutes,
                    "working_hours": working_hours
                },
                "available_slots": [],
                "busy_periods": [],
                "summary": {
                    "total_slots_found": 0,
                    "earliest_available": None,
                    "latest_available": None
                },
                "generated_at": datetime.now().isoformat()
            }
            
            # Generate available slots (simulated)
            current_date = start_date
            while current_date <= end_date:
                day_name = current_date.strftime("%A").lower()
                
                if working_hours.get(day_name):
                    day_hours = working_hours[day_name]
                    start_hour, start_minute = map(int, day_hours["start"].split(":"))
                    end_hour, end_minute = map(int, day_hours["end"].split(":"))
                    
                    # Generate slots for the day
                    slot_start = current_date.replace(hour=start_hour, minute=start_minute)
                    day_end = current_date.replace(hour=end_hour, minute=end_minute)
                    
                    while slot_start + timedelta(minutes=duration_minutes) <= day_end:
                        # Simulate some slots being busy (30% chance)
                        if random.random() > 0.3:
                            slot = {
                                "start_time": slot_start.isoformat(),
                                "end_time": (slot_start + timedelta(minutes=duration_minutes)).isoformat(),
                                "duration_minutes": duration_minutes,
                                "availability_score": random.uniform(0.7, 1.0)  # Quality score
                            }
                            availability["available_slots"].append(slot)
                        else:
                            # Add busy period
                            busy_period = {
                                "start_time": slot_start.isoformat(),
                                "end_time": (slot_start + timedelta(minutes=duration_minutes)).isoformat(),
                                "reason": random.choice(["Meeting", "Blocked Time", "Personal"])
                            }
                            availability["busy_periods"].append(busy_period)
                        
                        slot_start += timedelta(minutes=30)  # 30-minute intervals
                
                current_date += timedelta(days=1)
            
            # Update summary
            availability["summary"]["total_slots_found"] = len(availability["available_slots"])
            if availability["available_slots"]:
                availability["summary"]["earliest_available"] = availability["available_slots"][0]["start_time"]
                availability["summary"]["latest_available"] = availability["available_slots"][-1]["start_time"]
            
            return availability
            
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return {"error": str(e)}