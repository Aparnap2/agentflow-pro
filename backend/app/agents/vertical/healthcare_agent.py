"""Healthcare Agent implementation for handling healthcare-related tasks and compliance."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import json
import logging
import random
from datetime import datetime, timedelta

from ...base import BaseAgent, AgentConfig, Department, AgentRole

logger = logging.getLogger(__name__)

class HealthcareAgent(BaseAgent):
    """Specialized agent for healthcare operations, compliance, and patient data handling."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "healthcare_agent",
            "name": "Dr. Emily Watson",
            "role": AgentRole.HEALTHCARE_AGENT,
            "department": Department.HEALTHCARE,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Dr. Emily Watson, Healthcare Specialist at AgentFlow Pro.\n"
                "You are compassionate, detail-oriented, and deeply knowledgeable about healthcare operations. "
                "Your expertise includes patient care coordination, HIPAA compliance, medical terminology, "
                "and healthcare regulations. You ensure all operations prioritize patient privacy and care quality.\n"
                "You work closely with medical professionals and other departments to deliver optimal healthcare solutions."
            ),
            "tools": ["analyze_patient_data", "check_hipaa_compliance", "schedule_appointment"],
            "specializations": ["Patient Care", "HIPAA Compliance", "Medical Records", "Healthcare Operations"],
            "performance_metrics": {
                "patients_served": 0,
                "compliance_checks": 0,
                "appointments_scheduled": 0
            },
            "personality": {
                "tone": "empathetic and professional",
                "communication_style": "clear and compassionate",
                "approach": "patient-centered and thorough"
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the healthcare-related query."""
        # Get relevant context
        task = context.get("task_context", {})
        
        # Build system prompt with context
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        Patient Context:
        {json.dumps(context.get('patient_data', {}), indent=2)}
        
        Guidelines:
        1. Always prioritize patient privacy and HIPAA compliance
        2. Provide clear, accurate healthcare information
        3. Consider both medical and operational aspects
        4. Be empathetic and professional in all communications
        5. Escalate complex medical decisions to appropriate professionals
        """
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide a detailed healthcare response and recommendations:")
        ])
        
        # Generate response
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update performance metrics
        self.config.performance_metrics["patients_served"] += 1
        
        # Determine if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "emergency", "urgent"]):
            state.escalate = True
            state.next_agent = "cofounder"
        
        return response
    
    @tool
    async def analyze_patient_data(self, patient_id: str, data_categories: List[str]) -> Dict[str, Any]:
        """Analyze patient health data while maintaining privacy."""
        try:
            # In a real implementation, this would query a secure healthcare database
            analysis = {
                "patient_id": patient_id,
                "data_categories_analyzed": data_categories,
                "health_summary": "Patient health summary with key indicators",
                "risk_factors": [],
                "recommendations": []
            }
            
            # Generate sample health metrics
            if "vitals" in data_categories:
                analysis["vitals"] = {
                    "heart_rate": random.randint(60, 100),
                    "blood_pressure": f"{random.randint(100, 140)}/{random.randint(60, 90)}",
                    "temperature": round(random.uniform(97.0, 99.5), 1),
                    "oxygen_saturation": random.randint(95, 100)
                }
                
            if "labs" in data_categories:
                analysis["lab_results"] = {
                    "glucose": random.randint(70, 140),
                    "cholesterol": random.randint(150, 240),
                    "a1c": round(random.uniform(4.5, 7.5), 1)
                }
            
            # Update metrics
            self.config.performance_metrics["patients_served"] += 1
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in patient data analysis: {str(e)}")
            return {"error": str(e), "message": "Failed to analyze patient data"}
    
    @tool
    async def check_hipaa_compliance(self, document_text: str) -> Dict[str, Any]:
        """Check if a document or process is HIPAA compliant."""
        try:
            # In a real implementation, this would perform detailed HIPAA compliance checks
            compliance_check = {
                "is_compliant": True,  # Would be determined by analysis
                "issues_found": [],
                "required_actions": [],
                "risk_level": "low"
            }
            
            # Check for common HIPAA requirements
            hipaa_keywords = ["phi", "protected health information", "hipaa", "privacy rule"]
            has_hipaa_terms = any(term in document_text.lower() for term in hipaa_keywords)
            
            if not has_hipaa_terms:
                compliance_check["issues_found"].append(
                    "Document does not reference HIPAA requirements or PHI handling"
                )
                compliance_check["is_compliant"] = False
            
            # Check for sensitive information patterns (simplified)
            sensitive_patterns = ["ssn", "social security", "medical record", "patient name"]
            for pattern in sensitive_patterns:
                if pattern in document_text.lower() and "confidential" not in document_text.lower():
                    compliance_check["issues_found"].append(
                        f"Potential unprotected PHI detected: {pattern}"
                    )
                    compliance_check["is_compliant"] = False
            
            # Update metrics
            self.config.performance_metrics["compliance_checks"] += 1
            
            # Set risk level based on findings
            if not compliance_check["is_compliant"]:
                compliance_check["risk_level"] = "high"
                compliance_check["required_actions"].append(
                    "Review document with compliance officer"
                )
            
            return compliance_check
            
        except Exception as e:
            logger.error(f"Error in HIPAA compliance check: {str(e)}")
            return {"error": str(e), "message": "Failed to complete HIPAA compliance check"}
    
    @tool
    async def schedule_appointment(self, patient_id: str, provider_id: str, 
                                 appointment_type: str, preferred_times: List[str]) -> Dict[str, Any]:
        """Schedule a healthcare appointment."""
        try:
            # In a real implementation, this would interface with a scheduling system
            appointment = {
                "appointment_id": f"APP-{random.randint(10000, 99999)}",
                "patient_id": patient_id,
                "provider_id": provider_id,
                "type": appointment_type,
                "status": "scheduled",
                "scheduled_time": preferred_times[0] if preferred_times else "",
                "duration_minutes": 30,
                "location": "Main Hospital, Room 205",
                "notes": "Please arrive 15 minutes early for check-in"
            }
            
            # Update metrics
            self.config.performance_metrics["appointments_scheduled"] += 1
            
            return appointment
            
        except Exception as e:
            logger.error(f"Error scheduling appointment: {str(e)}")
            return {"error": str(e), "message": "Failed to schedule appointment"}
