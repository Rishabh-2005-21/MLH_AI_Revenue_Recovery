import random
from datetime import datetime, timezone
from typing import Dict, Any
from app.models import ActionType, ActionStatus
from app.services.guardrails import validate_action
from app.services.razorpay_client import RazorpayClient
from app.services.voice_agent import generate_hinglish_script
from app.services.retry_sequencer import calculate_optimal_retry_schedule
from app.services.promise_to_pay import create_promise_to_pay
from app.database import (
    save_recovery_action, log_audit, add_to_hitl_queue,
    update_event_status, save_risk_event
)

razorpay_client = RazorpayClient()

def execute_recovery_workflow(event: Dict[str, Any], decision: Dict[str, Any], simulate_success: bool = True) -> Dict[str, Any]:
    """
    Executes a bounded recovery workflow after guardrail verification.
    Updates event status, logs audit records, and measures money recovered.
    """
    event_id = event["event_id"]
    category = event.get("category", "payment_failure")
    amount = float(event.get("amount", 0.0))
    attempts = event.get("attempts_count", 0) + 1

    # Save event to database
    save_risk_event(event)

    # 1. Guardrail Validation Pass
    approved_by_guardrail, g_reason, applied_rules = validate_action(event, decision)

    if not approved_by_guardrail:
        # Action blocked by guardrails or routed to HITL
        if decision.get("requires_approval") or decision.get("action") == ActionType.ESCALATE_TO_HUMAN:
            add_to_hitl_queue(event_id, amount, decision["action"], decision["reason"])
            update_event_status(event_id, "escalated", attempts)
            log_audit(
                event_id=event_id,
                category=category,
                event_type="ESCALATED_TO_HITL_QUEUE",
                details={"reason": decision["reason"], "applied_guardrails": applied_rules},
                actor="AI_GUARDRAIL_ENGINE"
            )
            return {
                "event_id": event_id,
                "status": "escalated_hitl",
                "action": decision["action"],
                "message": "High-value/risk item queued for Human-In-The-Loop approval.",
                "applied_guardrails": applied_rules,
                "money_recovered": 0.0
            }
        else:
            update_event_status(event_id, "stopped", attempts)
            log_audit(
                event_id=event_id,
                category=category,
                event_type="ACTION_BLOCKED_BY_GUARDRAIL",
                details={"reason": g_reason, "applied_guardrails": applied_rules},
                actor="AI_GUARDRAIL_ENGINE"
            )
            return {
                "event_id": event_id,
                "status": "blocked",
                "action": decision["action"],
                "message": g_reason,
                "applied_guardrails": applied_rules,
                "money_recovered": 0.0
            }

    # 2. Action Execution & Multi-Channel Touchpoint Generation
    action_type = decision["action"]
    cust = event.get("customer") or {}
    cust_name = cust.get("name", "Valued Customer")
    cust_email = cust.get("email", "customer@example.com")
    cust_phone = cust.get("phone", "+919876543210")
    execution_result = {}
    money_recovered = 0.0

    if action_type in [ActionType.UPI_LINK_NUDGE, ActionType.CHECKOUT_DISCOUNT_OFFER, ActionType.DUNNING_REMINDER, ActionType.CARD_UPDATE_PORTAL]:
        discount = decision.get("payload", {}).get("discount_pct", 0.0)
        plink = razorpay_client.create_payment_link(
            amount=amount,
            description=f"RecoverAI Payment for {event_id}",
            customer_name=cust_name,
            customer_email=cust_email,
            customer_phone=cust_phone,
            discount_pct=discount
        )
        execution_result = {
            "channel": "WhatsApp / SMS / Email",
            "razorpay_link": plink["short_url"],
            "discount_applied": f"{discount}%",
            "final_payable_amount": plink["amount"]
        }

    elif action_type == ActionType.HINGLISH_VOICE_CALL:
        script_info = generate_hinglish_script(event)
        execution_result = {
            "channel": "Hinglish AI Voice Call",
            "voice_script": script_info["greeting"] + " " + script_info["full_script"],
            "dialog_turns": script_info["dialog_turns"],
            "audio_file": script_info["audio_file_path"],
            "call_duration": "38s"
        }
        # Also create P2P record for voice call agreement
        if category == "b2b_receivable":
            p2p = create_promise_to_pay(event_id, cust.get("customer_id", "CUST_001"), cust_name, amount)
            execution_result["p2p_commitment"] = p2p

    elif action_type == ActionType.SMART_RETRY:
        execution_result = {
            "channel": "Razorpay Auto-Retry Routing",
            "route_secondary": "HDFC_GATEWAY_NETBANKING_DIRECT",
            "retry_status": "success"
        }

    elif action_type == ActionType.MANDATE_RETRY_SCHEDULE:
        schedule = calculate_optimal_retry_schedule(event)
        execution_result = {
            "channel": "Mandate Retry Sequencer",
            "scheduled_time": schedule["display_slot"],
            "bank_uptime_probability": f"{schedule['expected_success_probability']*100}%",
            "reasoning": schedule["reasoning"]
        }

    # 3. Simulate Recovery Outcome based on realistic probabilities
    prob = event.get("recovery_probability", 0.80)
    # If simulate_success is True (for batch runs), evaluate probability
    recovered_success = random.random() < prob if simulate_success else True

    if recovered_success:
        money_recovered = amount
        update_event_status(event_id, "recovered", attempts)
        action_status = ActionStatus.RECOVERED
    else:
        update_event_status(event_id, "in_recovery", attempts)
        action_status = ActionStatus.EXECUTED

    # 4. Save Action & Audit Logs
    save_recovery_action({
        "event_id": event_id,
        "action": action_type,
        "reason": decision["reason"],
        "confidence": decision.get("confidence", 0.90),
        "status": action_status,
        "requires_approval": False,
        "payload": execution_result,
        "applied_guardrails": applied_rules,
        "money_recovered": money_recovered,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    log_audit(
        event_id=event_id,
        category=category,
        event_type="RECOVERY_ACTION_EXECUTED",
        details={
            "action": action_type,
            "status": action_status,
            "money_recovered": money_recovered,
            "execution_details": execution_result
        },
        actor="RECOVERAI_WORKFLOW_ENGINE",
        money_recovered=money_recovered
    )

    return {
        "event_id": event_id,
        "status": action_status,
        "action": action_type,
        "money_recovered": money_recovered,
        "execution_details": execution_result,
        "applied_guardrails": applied_rules
    }
