from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any

class RiskCategory(str, Enum):
    PAYMENT_FAILURE = "payment_failure"
    CART_ABANDONMENT = "cart_abandonment"
    FAILED_SUBSCRIPTION = "failed_subscription"
    B2B_RECEIVABLE = "b2b_receivable"

class ActionType(str, Enum):
    SMART_RETRY = "smart_retry"
    UPI_LINK_NUDGE = "upi_link_nudge"
    CHECKOUT_DISCOUNT_OFFER = "checkout_discount_offer"
    DUNNING_REMINDER = "dunning_reminder"
    HINGLISH_VOICE_CALL = "hinglish_voice_call"
    PROMISE_TO_PAY_SETUP = "promise_to_pay_setup"
    CARD_UPDATE_PORTAL = "card_update_portal"
    MANDATE_RETRY_SCHEDULE = "mandate_retry_schedule"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    STOP_HARASSMENT_RULE = "stop_harassment_rule"

class ActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    RECOVERED = "recovered"
    FAILED = "failed"
    STOPPED = "stopped"

@dataclass
class CustomerProfile:
    customer_id: str
    name: str
    phone: str
    email: str
    preferred_language: str = "Hinglish" # English, Hinglish, Hindi
    ltv: float = 0.0
    trust_score: float = 0.8
    past_recovered_count: int = 0

@dataclass
class RevenueRiskEvent:
    event_id: str
    category: RiskCategory
    amount: float
    currency: str = "INR"
    customer: Optional[CustomerProfile] = None
    customer_id: str = "CUST_DEFAULT"
    payment_id: Optional[str] = None
    order_id: Optional[str] = None
    invoice_id: Optional[str] = None
    subscription_id: Optional[str] = None
    failure_reason: Optional[str] = None # e.g., BAD_REQUEST_PAYMENT_TIMED_OUT, ISSUER_BANK_SERVER_DOWN, INSUFFICIENT_FUNDS
    cart_items: Optional[List[str]] = None
    invoice_days_overdue: int = 0
    attempts_count: int = 0
    status: str = "detected" # detected, in_recovery, recovered, escalated, abandoned
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class DiagnosisResult:
    event_id: str
    root_cause: str
    category: RiskCategory
    recovery_probability: float # 0.0 to 1.0
    recommended_action: ActionType
    urgency_level: str # HIGH, MEDIUM, LOW
    explanation: str

@dataclass
class RecoveryDecision:
    event_id: str
    action: ActionType
    reason: str
    confidence: float
    max_attempts: int
    requires_approval: bool
    payload: Dict[str, Any] = field(default_factory=dict)
    applied_guardrails: List[str] = field(default_factory=list)

@dataclass
class PromiseToPayRecord:
    p2p_id: str
    event_id: str
    customer_id: str
    customer_name: str
    amount_promised: float
    promised_date: str # YYYY-MM-DD
    status: str = "active" # active, fulfilled, defaulted
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class AuditRecord:
    id: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: str = ""
    category: str = ""
    event_type: str = ""
    actor: str = "AI_AGENT"
    details: Dict[str, Any] = field(default_factory=dict)
    money_recovered: float = 0.0

