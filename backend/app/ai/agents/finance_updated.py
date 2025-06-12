"""
Updated FinanceAgent with comprehensive financial management capabilities.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from enum import Enum
import logging
from decimal import Decimal
from pydantic import BaseModel, Field, validator

from .base_agent import BaseAgent, AgentConfig, AgentResponse

logger = logging.getLogger(__name__)

class TransactionType(str, Enum):
    """Types of financial transactions."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    INVOICE = "invoice"
    PAYMENT = "payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"

class TransactionStatus(str, Enum):
    """Status of a transaction."""
    DRAFT = "draft"
    PENDING = "pending"
    POSTED = "posted"
    RECONCILED = "reconciled"
    VOID = "void"

class AccountType(str, Enum):
    """Types of financial accounts."""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class Currency(str, Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CNY = "CNY"

class Transaction(BaseModel):
    """Financial transaction model."""
    id: str
    type: TransactionType
    amount: Decimal
    currency: Currency = Currency.USD
    description: str
    category: str
    date: date = Field(default_factory=date.today)
    status: TransactionStatus = TransactionStatus.PENDING
    account_id: str
    reference: Optional[str] = None
    notes: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

class Account(BaseModel):
    """Financial account model."""
    id: str
    name: str
    type: AccountType
    currency: Currency = Currency.USD
    balance: Decimal = Decimal('0.00')
    parent_account_id: Optional[str] = None
    is_active: bool = True
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Budget(BaseModel):
    """Budget model for financial planning."""
    id: str
    name: str
    description: str
    category: str
    amount: Decimal
    currency: Currency = Currency.USD
    start_date: date
    end_date: date
    actual_spent: Decimal = Decimal('0.00')
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Invoice(BaseModel):
    """Invoice model for billing."""
    id: str
    invoice_number: str
    customer_id: str
    issue_date: date = Field(default_factory=date.today)
    due_date: date
    status: str = "draft"  # draft, sent, paid, overdue, cancelled
    items: List[Dict[str, Any]]
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    currency: Currency = Currency.USD
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FinanceAgent(BaseAgent):
    """
    Comprehensive Finance Agent with financial management capabilities.
    
    This agent provides a complete suite of financial functions including:
    - Transaction management
    - Account reconciliation
    - Budgeting and forecasting
    - Invoicing and payments
    - Financial reporting
    - Expense tracking
    - Financial analysis
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.accounts: Dict[str, Account] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.budgets: Dict[str, Budget] = {}
        self.invoices: Dict[str, Invoice] = {}
        self._init_integrations()
    
    def _init_integrations(self) -> None:
        """Initialize necessary integrations."""
        try:
            self.accounting_system = get_accounting_integration()
            self.payment_processor = get_payment_processor()
            self.communication = get_communication_integration()
            self.analytics = get_analytics_integration()
            logger.info("Finance Agent integrations initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Finance Agent integrations: {str(e)}")
            raise
    
    # Account Management
    async def create_account(self, account_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new financial account.
        
        Args:
            account_data: Dictionary containing account details
                - name: Name of the account
                - type: Type of account (from AccountType enum)
                - currency: Currency code (from Currency enum)
                - parent_account_id: Optional parent account ID
                - description: Optional description
                
        Returns:
            AgentResponse with created account or error
        """
        try:
            account = Account(**account_data)
            self.accounts[account.id] = account
            
            # Create in accounting system
            await self.accounting_system.create_account(account.dict())
            
            logger.info(f"Created account: {account.name} ({account.id})")
            
            return AgentResponse(
                success=True,
                output={"account": account.dict()},
                message=f"Created account: {account.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create account: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def record_transaction(self, transaction_data: Dict[str, Any]) -> AgentResponse:
        """
        Record a financial transaction.
        
        Args:
            transaction_data: Dictionary containing transaction details
                - type: Type of transaction (from TransactionType enum)
                - amount: Transaction amount
                - currency: Currency code (from Currency enum)
                - description: Description of the transaction
                - category: Transaction category
                - account_id: ID of the account
                - reference: Optional reference number
                - notes: Optional notes
                - metadata: Optional metadata
                
        Returns:
            AgentResponse with recorded transaction or error
        """
        try:
            # Validate account exists
            account_id = transaction_data.get('account_id')
            if account_id not in self.accounts:
                raise ValueError(f"Account {account_id} not found")
            
            # Create and record transaction
            transaction = Transaction(**transaction_data)
            self.transactions[transaction.id] = transaction
            
            # Update account balance
            account = self.accounts[account_id]
            if transaction.type in [TransactionType.INCOME, TransactionType.REFUND]:
                account.balance += transaction.amount
            else:
                account.balance -= transaction.amount
            
            # Record in accounting system
            await self.accounting_system.record_transaction(transaction.dict())
            
            logger.info(f"Recorded {transaction.type} transaction: {transaction.id}")
            
            return AgentResponse(
                success=True,
                output={"transaction": transaction.dict()},
                message=f"Recorded {transaction.type} transaction"
            )
            
        except Exception as e:
            error_msg = f"Failed to record transaction: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def create_budget(self, budget_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new budget.
        
        Args:
            budget_data: Dictionary containing budget details
                - name: Name of the budget
                - description: Budget description
                - category: Budget category
                - amount: Budget amount
                - currency: Currency code (from Currency enum)
                - start_date: Start date of the budget
                - end_date: End date of the budget
                - created_by: ID of the user creating the budget
                
        Returns:
            AgentResponse with created budget or error
        """
        try:
            budget = Budget(**budget_data)
            self.budgets[budget.id] = budget
            
            logger.info(f"Created budget: {budget.name} ({budget.id})")
            
            return AgentResponse(
                success=True,
                output={"budget": budget.dict()},
                message=f"Created budget: {budget.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create budget: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> AgentResponse:
        """
        Create a new invoice.
        
        Args:
            invoice_data: Dictionary containing invoice details
                - invoice_number: Unique invoice number
                - customer_id: ID of the customer
                - issue_date: Date the invoice is issued
                - due_date: Payment due date
                - items: List of line items
                - subtotal: Subtotal amount
                - tax_amount: Tax amount
                - total: Total amount
                - currency: Currency code (from Currency enum)
                - notes: Optional notes
                
        Returns:
            AgentResponse with created invoice or error
        """
        try:
            invoice = Invoice(**invoice_data)
            self.invoices[invoice.id] = invoice
            
            # Create in accounting system
            await self.accounting_system.create_invoice(invoice.dict())
            
            # Send invoice to customer
            await self._send_invoice_to_customer(invoice)
            
            logger.info(f"Created invoice: {invoice.invoice_number} ({invoice.id})")
            
            return AgentResponse(
                success=True,
                output={"invoice": invoice.dict()},
                message=f"Created invoice: {invoice.invoice_number}"
            )
            
        except Exception as e:
            error_msg = f"Failed to create invoice: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def _send_invoice_to_customer(self, invoice: Invoice) -> None:
        """Send invoice to customer via email."""
        # In a real implementation, this would fetch customer details and send the invoice
        logger.info(f"Sending invoice {invoice.invoice_number} to customer {invoice.customer_id}")
        
        subject = f"Invoice {invoice.invoice_number} from {self.config.get('company_name', 'Our Company')}"
        
        body = f"""
        Dear Valued Customer,
        
        Please find attached your invoice #{invoice.invoice_number} for {invoice.total} {invoice.currency}.
        
        Due Date: {invoice.due_date.strftime('%B %d, %Y')}
        
        You can view and pay your invoice online at:
        {self.config.get('payment_portal_url', '')}/invoices/{invoice.id}
        
        If you have any questions about this invoice, please contact our billing department.
        
        Thank you for your business!
        
        Best regards,
        {self.config.get('billing_team_name', 'Billing Department')}
        {self.config.get('company_name', 'Our Company')}
        """
        
        await self.communication.send_email(
            to=f"customer-{invoice.customer_id}@example.com",  # In real app, get from customer data
            subject=subject,
            body=body.strip()
        )
    
    async def get_account_balance(self, account_id: str) -> AgentResponse:
        """
        Get the current balance of an account.
        
        Args:
            account_id: ID of the account
            
        Returns:
            AgentResponse with account balance or error
        """
        try:
            if account_id not in self.accounts:
                raise ValueError(f"Account {account_id} not found")
                
            account = self.accounts[account_id]
            
            return AgentResponse(
                success=True,
                output={
                    "account_id": account_id,
                    "account_name": account.name,
                    "balance": float(account.balance),
                    "currency": account.currency
                },
                message=f"Current balance for {account.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to get account balance: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )
    
    async def get_budget_status(self, budget_id: str) -> AgentResponse:
        """
        Get the current status of a budget.
        
        Args:
            budget_id: ID of the budget
            
        Returns:
            AgentResponse with budget status or error
        """
        try:
            if budget_id not in self.budgets:
                raise ValueError(f"Budget {budget_id} not found")
                
            budget = self.budgets[budget_id]
            
            # Calculate budget utilization
            utilization = (budget.actual_spent / budget.amount) * 100 if budget.amount > 0 else 0
            remaining = budget.amount - budget.actual_spent
            
            return AgentResponse(
                success=True,
                output={
                    "budget_id": budget_id,
                    "budget_name": budget.name,
                    "allocated": float(budget.amount),
                    "spent": float(budget.actual_spent),
                    "remaining": float(remaining),
                    "utilization_percentage": float(utilization),
                    "currency": budget.currency,
                    "start_date": budget.start_date.isoformat(),
                    "end_date": budget.end_date.isoformat()
                },
                message=f"Status for budget: {budget.name}"
            )
            
        except Exception as e:
            error_msg = f"Failed to get budget status: {str(e)}"
            logger.error(error_msg)
            return AgentResponse(
                success=False,
                error=error_msg
            )

# Mock integration functions
def get_accounting_integration():
    class MockAccountingIntegration:
        async def create_account(self, account_data):
            logger.info(f"[MockAccounting] Creating account: {account_data['name']}")
            return {"status": "success"}
            
        async def record_transaction(self, transaction_data):
            logger.info(f"[MockAccounting] Recording transaction: {transaction_data['id']}")
            return {"status": "success"}
            
        async def create_invoice(self, invoice_data):
            logger.info(f"[MockAccounting] Creating invoice: {invoice_data['invoice_number']}")
            return {"status": "success"}
            
    return MockAccountingIntegration()

def get_payment_processor():
    class MockPaymentProcessor:
        async def process_payment(self, amount, currency, payment_method, **kwargs):
            logger.info(f"[MockPayment] Processing payment of {amount} {currency}")
            return {"status": "completed", "transaction_id": f"txn_{datetime.now().timestamp()}"}
            
    return MockPaymentProcessor()

# Update the __init__.py to expose the new FinanceAgent
__all__ = [
    'FinanceAgent',
    'Transaction',
    'Account',
    'Budget',
    'Invoice',
    'TransactionType',
    'TransactionStatus',
    'AccountType',
    'Currency'
]
