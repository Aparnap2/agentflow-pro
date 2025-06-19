"""Legal Agent implementation for handling legal matters and compliance."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import json
import logging

from ...base import BaseAgent, AgentConfig, Department, AgentRole

logger = logging.getLogger(__name__)

class LegalAgent(BaseAgent):
    """Specialized agent for legal matters, contracts, and compliance."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "legal_agent",
            "name": "Sarah Chen",
            "role": AgentRole.LEGAL_AGENT,
            "department": Department.LEGAL,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Sarah Chen, Legal Counsel at AgentFlow Pro.\n"
                "You are detail-oriented, precise, and always ensure compliance with laws and regulations. "
                "Your expertise includes contract law, intellectual property, data privacy, and corporate compliance.\n"
                "You carefully analyze legal documents, identify risks, and provide clear, actionable advice.\n"
                "You work closely with other departments to ensure all operations are legally sound."
            ),
            "tools": ["review_contract", "check_compliance", "research_laws"],
            "specializations": ["Contract Law", "Compliance", "Intellectual Property", "Data Privacy"],
            "performance_metrics": {
                "contracts_reviewed": 0,
                "compliance_issues_found": 0,
                "legal_risks_mitigated": 0
            },
            "personality": {
                "tone": "professional and precise",
                "communication_style": "clear and concise",
                "approach": "thorough and risk-averse"
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the legal query."""
        # Get relevant context
        task = context.get("task_context", {})
        
        # Build system prompt with context
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        Relevant Context:
        {json.dumps(context.get('documents', []), indent=2)}
        
        Guidelines:
        1. Carefully analyze all legal documents and requirements
        2. Identify potential risks and compliance issues
        3. Provide clear, actionable recommendations
        4. Reference specific laws and regulations when applicable
        5. Consider both short-term and long-term implications
        """
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide a detailed legal analysis and recommendations:")
        ])
        
        # Generate response
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update performance metrics
        self.config.performance_metrics["contracts_reviewed"] += 1
        
        # Determine if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "high risk", "legal action"]):
            state.escalate = True
            state.next_agent = "cofounder"
        
        return response
    
    @tool
    async def review_contract(self, contract_text: str) -> Dict[str, Any]:
        """Review a contract and identify key terms, risks, and recommendations."""
        try:
            # In a real implementation, this would use more sophisticated analysis
            analysis = {
                "summary": "Contract review summary",
                "key_terms": [],
                "risks": [],
                "recommendations": []
            }
            
            # Simple keyword analysis (would be enhanced in production)
            if "indemnification" in contract_text.lower():
                analysis["key_terms"].append("Indemnification Clause")
                
            if "confidentiality" in contract_text.lower():
                analysis["key_terms"].append("Confidentiality Agreement")
                
            # Update metrics
            self.config.performance_metrics["contracts_reviewed"] += 1
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in contract review: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def check_compliance(self, policy_text: str, regulation: str) -> Dict[str, Any]:
        """Check if a policy complies with specific regulations."""
        try:
            # In a real implementation, this would use regulatory databases
            compliance_check = {
                "regulation": regulation,
                "is_compliant": True,  # Would be determined by analysis
                "issues_found": [],
                "recommendations": []
            }
            
            # Simple check for common compliance terms
            required_terms = ["compliance", "regulation", "policy"]
            for term in required_terms:
                if term not in policy_text.lower():
                    compliance_check["issues_found"].append(f"Missing required term: {term}")
                    compliance_check["is_compliant"] = False
            
            # Update metrics
            if not compliance_check["is_compliant"]:
                self.config.performance_metrics["compliance_issues_found"] += 1
            
            return compliance_check
            
        except Exception as e:
            logger.error(f"Error in compliance check: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def research_laws(self, query: str, jurisdiction: str = "US") -> Dict[str, Any]:
        """Research relevant laws and regulations."""
        try:
            # In a real implementation, this would query legal databases
            research_results = {
                "query": query,
                "jurisdiction": jurisdiction,
                "relevant_laws": [],
                "summary": "Summary of legal research findings"
            }
            
            # Simple placeholder implementation
            if "privacy" in query.lower():
                research_results["relevant_laws"].append({
                    "name": "General Data Protection Regulation (GDPR)",
                    "relevance": "high",
                    "summary": "Regulates data protection and privacy in the EU"
                })
                
            if "intellectual property" in query.lower():
                research_results["relevant_laws"].append({
                    "name": "Digital Millennium Copyright Act (DMCA)",
                    "relevance": "medium",
                    "summary": "Addresses digital copyright issues"
                })
            
            return research_results
            
        except Exception as e:
            logger.error(f"Error in legal research: {str(e)}")
            return {"error": str(e)}
