from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import uuid4

class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

class AgentRole(str, Enum):
    COFOUNDER = "cofounder"
    MANAGER = "manager"
    LEGAL_AGENT = "legal_agent"
    FINANCE_AGENT = "finance_agent"
    HEALTHCARE_AGENT = "healthcare_agent"
    MANUFACTURING_AGENT = "manufacturing_agent"
    ECOMMERCE_AGENT = "ecommerce_agent"
    COACHING_AGENT = "coaching_agent"
    SALES = "sales"
    SUPPORT = "support"
    GROWTH = "growth"

class Department(str, Enum):
    LEADERSHIP = "leadership"
    OPERATIONS = "operations"
    SALES = "sales"
    MARKETING = "marketing"
    SUPPORT = "support"
    FINANCE = "finance"
    HR = "hr"

class MessageType(str, Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    TOOL = "tool"
