from typing import Dict, Any, List, Optional
from decimal import Decimal
from .base_agent import BaseAgent, AgentConfig, AgentResponse

class FinanceAgent(BaseAgent):
    """Base class for finance and accounting agents."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.financial_categories = ['income', 'expense', 'asset', 'liability', 'equity']
    
    async def process_invoice(self, invoice_data: Dict) -> AgentResponse:
        """Process an invoice and extract key information."""
        try:
            analysis = await self.llm.generate(
                f"Process this invoice data and extract key information:\n{invoice_data}"
            )
            return AgentResponse(
                success=True,
                output={"invoice_processing": analysis},
                metadata={"document_type": "invoice"}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Invoice processing failed: {str(e)}"
            )
    
    async def analyze_financials(self, financial_data: Dict) -> AgentResponse:
        """Analyze financial statements and provide insights."""
        try:
            analysis = await self.llm.generate(
                f"Analyze these financial statements and provide key insights and recommendations:\n{financial_data}"
            )
            return AgentResponse(
                success=True,
                output={"financial_analysis": analysis},
                metadata={"analysis_type": "financial_statements"}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Financial analysis failed: {str(e)}"
            )
