"""Invoice Agent implementation for billing, payments, and financial transactions."""
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

class InvoiceAgent(BaseAgent):
    """Specialized agent for invoice management, billing, and payment processing."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "invoice_agent",
            "name": "Michael Chen",
            "role": AgentRole.INVOICE_AGENT,
            "department": Department.FINANCE,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Michael Chen, Invoice and Billing Specialist at AgentFlow Pro.\n"
                "You are precise, detail-oriented, and financially savvy. Your expertise includes "
                "invoice generation, payment processing, financial reconciliation, and billing automation. "
                "You ensure accurate financial records and timely payments. You understand tax regulations, "
                "payment terms, and financial compliance requirements."
            ),
            "tools": ["generate_invoice", "send_payment_reminder", "reconcile_payment", "generate_report"],
            "specializations": ["Invoice Generation", "Payment Processing", "Financial Reconciliation", "Billing Automation"],
            "performance_metrics": {
                "invoices_generated": 0,
                "payments_processed": 0,
                "total_revenue": 0.0,
                "outstanding_amount": 0.0,
                "collection_rate": 0.0,
                "average_payment_time": 0.0
            },
            "personality": {
                "tone": "professional and precise",
                "communication_style": "clear and systematic",
                "approach": "detail-oriented and compliant"
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state: AgentState, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the invoice/billing query."""
        task = context.get("task_context", {})
        
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        Financial Context:
        {json.dumps(context.get('financial_data', {}), indent=2)}
        
        Billing Status:
        - Invoices generated: {self.config.performance_metrics['invoices_generated']}
        - Payments processed: {self.config.performance_metrics['payments_processed']}
        - Total revenue: ${self.config.performance_metrics['total_revenue']:,.2f}
        - Outstanding amount: ${self.config.performance_metrics['outstanding_amount']:,.2f}
        - Collection rate: {self.config.performance_metrics['collection_rate']:.1f}%
        - Average payment time: {self.config.performance_metrics['average_payment_time']:.1f} days
        
        Guidelines:
        1. Ensure accuracy in all financial calculations and records
        2. Follow proper invoicing standards and legal requirements
        3. Maintain clear payment terms and conditions
        4. Track payment status and follow up on overdue accounts
        5. Generate comprehensive financial reports
        6. Ensure compliance with tax regulations
        7. Automate recurring billing processes
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide comprehensive billing and financial analysis:")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update metrics
        if "invoice" in response.content.lower():
            self.config.performance_metrics["invoices_generated"] += 1
        
        # Determine if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "manager", "complex", "legal"]):
            state.escalate = True
            state.next_agent = "manager"
        
        return response
    
    @tool
    async def generate_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new invoice with line items and calculations."""
        try:
            invoice_number = f"INV-{datetime.now().strftime('%Y%m')}-{random.randint(1000, 9999)}"
            
            # Calculate line items
            line_items = []
            subtotal = Decimal('0.00')
            
            for item in invoice_data.get("items", []):
                quantity = Decimal(str(item.get("quantity", 1)))
                unit_price = Decimal(str(item.get("unit_price", 0)))
                line_total = quantity * unit_price
                
                line_item = {
                    "description": item.get("description", "Service"),
                    "quantity": float(quantity),
                    "unit_price": float(unit_price),
                    "total": float(line_total)
                }
                line_items.append(line_item)
                subtotal += line_total
            
            # Calculate taxes and totals
            tax_rate = Decimal(str(invoice_data.get("tax_rate", 0.0))) / 100
            tax_amount = subtotal * tax_rate
            discount_amount = Decimal(str(invoice_data.get("discount_amount", 0.0)))
            total_amount = subtotal + tax_amount - discount_amount
            
            invoice = {
                "invoice_number": invoice_number,
                "status": "Draft",
                "issue_date": datetime.now().strftime("%Y-%m-%d"),
                "due_date": (datetime.now() + timedelta(days=invoice_data.get("payment_terms_days", 30))).strftime("%Y-%m-%d"),
                "customer": {
                    "id": invoice_data.get("customer_id"),
                    "name": invoice_data.get("customer_name", ""),
                    "email": invoice_data.get("customer_email", ""),
                    "address": invoice_data.get("customer_address", {}),
                    "tax_id": invoice_data.get("customer_tax_id", "")
                },
                "vendor": {
                    "name": "AgentFlow Pro",
                    "address": {
                        "street": "123 Business Ave",
                        "city": "San Francisco",
                        "state": "CA",
                        "zip": "94105",
                        "country": "USA"
                    },
                    "tax_id": "12-3456789",
                    "email": "billing@agentflow.pro",
                    "phone": "+1 (555) 123-4567"
                },
                "line_items": line_items,
                "financial_summary": {
                    "subtotal": float(subtotal),
                    "tax_rate": float(tax_rate * 100),
                    "tax_amount": float(tax_amount),
                    "discount_amount": float(discount_amount),
                    "total_amount": float(total_amount),
                    "currency": invoice_data.get("currency", "USD")
                },
                "payment_terms": {
                    "terms": f"Net {invoice_data.get('payment_terms_days', 30)}",
                    "late_fee": invoice_data.get("late_fee_percentage", 1.5),
                    "accepted_methods": ["Credit Card", "Bank Transfer", "Check"]
                },
                "notes": invoice_data.get("notes", ""),
                "created_by": self.config.name,
                "created_at": datetime.now().isoformat()
            }
            
            # Update metrics
            self.config.performance_metrics["invoices_generated"] += 1
            self.config.performance_metrics["outstanding_amount"] += float(total_amount)
            
            return invoice
            
        except Exception as e:
            logger.error(f"Error generating invoice: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def send_payment_reminder(self, invoice_id: str, reminder_type: str = "friendly") -> Dict[str, Any]:
        """Send a payment reminder for an overdue invoice."""
        try:
            reminder_types = ["friendly", "firm", "final", "legal"]
            
            if reminder_type not in reminder_types:
                return {"error": f"Invalid reminder type. Must be one of: {reminder_types}"}
            
            # Simulate invoice lookup
            days_overdue = random.randint(1, 90)
            amount_due = random.uniform(100, 5000)
            
            reminder_templates = {
                "friendly": {
                    "subject": "Friendly Payment Reminder - Invoice {invoice_id}",
                    "tone": "polite and understanding",
                    "urgency": "low"
                },
                "firm": {
                    "subject": "Payment Required - Invoice {invoice_id}",
                    "tone": "professional and direct",
                    "urgency": "medium"
                },
                "final": {
                    "subject": "Final Notice - Invoice {invoice_id}",
                    "tone": "serious and urgent",
                    "urgency": "high"
                },
                "legal": {
                    "subject": "Legal Action Notice - Invoice {invoice_id}",
                    "tone": "formal and legal",
                    "urgency": "critical"
                }
            }
            
            template = reminder_templates[reminder_type]
            
            reminder = {
                "id": f"REM-{random.randint(10000, 99999)}",
                "invoice_id": invoice_id,
                "reminder_type": reminder_type,
                "days_overdue": days_overdue,
                "amount_due": amount_due,
                "subject": template["subject"].format(invoice_id=invoice_id),
                "template": {
                    "tone": template["tone"],
                    "urgency": template["urgency"],
                    "include_late_fees": reminder_type in ["firm", "final", "legal"],
                    "payment_deadline": (datetime.now() + timedelta(days=7 if reminder_type != "legal" else 3)).strftime("%Y-%m-%d")
                },
                "delivery_method": "email",
                "sent_at": datetime.now().isoformat(),
                "sent_by": self.config.name,
                "status": "Sent"
            }
            
            # Add escalation recommendations
            if reminder_type == "legal":
                reminder["next_steps"] = [
                    "Prepare for legal action",
                    "Contact legal department",
                    "Consider debt collection agency"
                ]
            elif days_overdue > 60:
                reminder["next_steps"] = [
                    "Consider final notice",
                    "Review payment plan options",
                    "Escalate to management"
                ]
            
            return reminder
            
        except Exception as e:
            logger.error(f"Error sending payment reminder: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def reconcile_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reconcile a payment against outstanding invoices."""
        try:
            payment_id = f"PAY-{random.randint(10000, 99999)}"
            payment_amount = Decimal(str(payment_data.get("amount", 0)))
            
            reconciliation = {
                "payment_id": payment_id,
                "amount_received": float(payment_amount),
                "payment_date": payment_data.get("payment_date", datetime.now().strftime("%Y-%m-%d")),
                "payment_method": payment_data.get("payment_method", "Bank Transfer"),
                "reference_number": payment_data.get("reference_number", ""),
                "customer_id": payment_data.get("customer_id"),
                "invoices_applied": [],
                "remaining_credit": 0.0,
                "status": "Processed",
                "processed_by": self.config.name,
                "processed_at": datetime.now().isoformat()
            }
            
            # Apply payment to invoices
            invoice_ids = payment_data.get("invoice_ids", [])
            remaining_amount = payment_amount
            
            for invoice_id in invoice_ids:
                if remaining_amount <= 0:
                    break
                
                # Simulate invoice amount lookup
                invoice_amount = Decimal(str(random.uniform(50, 1000)))
                applied_amount = min(remaining_amount, invoice_amount)
                
                invoice_application = {
                    "invoice_id": invoice_id,
                    "invoice_amount": float(invoice_amount),
                    "amount_applied": float(applied_amount),
                    "remaining_balance": float(invoice_amount - applied_amount),
                    "status": "Paid" if applied_amount >= invoice_amount else "Partially Paid"
                }
                
                reconciliation["invoices_applied"].append(invoice_application)
                remaining_amount -= applied_amount
            
            # Handle remaining credit
            if remaining_amount > 0:
                reconciliation["remaining_credit"] = float(remaining_amount)
                reconciliation["credit_memo_id"] = f"CM-{random.randint(1000, 9999)}"
            
            # Update metrics
            self.config.performance_metrics["payments_processed"] += 1
            self.config.performance_metrics["total_revenue"] += float(payment_amount)
            self.config.performance_metrics["outstanding_amount"] -= float(payment_amount - remaining_amount)
            
            return reconciliation
            
        except Exception as e:
            logger.error(f"Error reconciling payment: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def generate_report(self, report_type: str, period: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial reports for billing and payments."""
        try:
            report_types = ["aging", "revenue", "outstanding", "payment_summary"]
            
            if report_type not in report_types:
                return {"error": f"Invalid report type. Must be one of: {report_types}"}
            
            start_date = period.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
            end_date = period.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            
            report = {
                "report_id": f"RPT-{random.randint(10000, 99999)}",
                "report_type": report_type,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "generated_by": self.config.name,
                "generated_at": datetime.now().isoformat()
            }
            
            if report_type == "aging":
                report["aging_buckets"] = {
                    "current": {"count": random.randint(10, 50), "amount": random.uniform(5000, 25000)},
                    "1_30_days": {"count": random.randint(5, 25), "amount": random.uniform(2000, 15000)},
                    "31_60_days": {"count": random.randint(2, 15), "amount": random.uniform(1000, 8000)},
                    "61_90_days": {"count": random.randint(1, 10), "amount": random.uniform(500, 5000)},
                    "over_90_days": {"count": random.randint(0, 5), "amount": random.uniform(0, 3000)}
                }
                
            elif report_type == "revenue":
                report["revenue_summary"] = {
                    "total_invoiced": random.uniform(50000, 200000),
                    "total_collected": random.uniform(45000, 180000),
                    "outstanding": random.uniform(5000, 20000),
                    "collection_rate": random.uniform(85, 95)
                }
                
            elif report_type == "outstanding":
                report["outstanding_summary"] = {
                    "total_outstanding": random.uniform(10000, 50000),
                    "number_of_invoices": random.randint(20, 100),
                    "average_days_outstanding": random.uniform(25, 45),
                    "largest_outstanding": random.uniform(2000, 10000)
                }
                
            elif report_type == "payment_summary":
                report["payment_summary"] = {
                    "total_payments": random.uniform(40000, 150000),
                    "number_of_payments": random.randint(50, 200),
                    "average_payment_amount": random.uniform(500, 2000),
                    "payment_methods": {
                        "credit_card": random.uniform(40, 60),
                        "bank_transfer": random.uniform(30, 50),
                        "check": random.uniform(5, 15)
                    }
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {"error": str(e)}