import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from app.database import save_p2p, get_all_p2p, log_audit, update_event_status

def create_promise_to_pay(event_id: str, customer_id: str, customer_name: str, amount: float, promised_days_ahead: int = 1, notes: str = "") -> Dict[str, Any]:
    """
    Creates a new Promise-To-Pay (P2P) commitment record.
    """
    p2p_id = f"P2P_{uuid.uuid4().hex[:8]}"
    promised_date = (datetime.now() + timedelta(days=promised_days_ahead)).strftime("%Y-%m-%d")

    p2p_data = {
        "p2p_id": p2p_id,
        "event_id": event_id,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "amount_promised": amount,
        "promised_date": promised_date,
        "status": "active",
        "notes": notes or f"Customer committed to pay ₹{amount:,.2f} on {promised_date} via AI Voice Call.",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    save_p2p(p2p_data)
    log_audit(
        event_id=event_id,
        category="b2b_receivable",
        event_type="PROMISE_TO_PAY_CREATED",
        details={"p2p_id": p2p_id, "amount": amount, "promised_date": promised_date},
        actor="AI_VOICE_AGENT"
    )

    return p2p_data

def verify_p2p_settlements(incoming_payment_event_id: str, paid_amount: float) -> Dict[str, Any]:
    """
    Checks if an incoming payment satisfies any active P2P commitments.
    """
    all_p2p = get_all_p2p()
    matched = None
    for item in all_p2p:
        if item["event_id"] == incoming_payment_event_id and item["status"] == "active":
            matched = item
            break

    if matched:
        # Fulfill P2P commitment
        save_p2p({
            **matched,
            "status": "fulfilled",
            "notes": matched["notes"] + f" [FULFILLED on {datetime.now().strftime('%Y-%m-%d %H:%M')}]"
        })
        update_event_status(incoming_payment_event_id, "recovered")
        log_audit(
            event_id=incoming_payment_event_id,
            category="b2b_receivable",
            event_type="PROMISE_TO_PAY_FULFILLED",
            details={"p2p_id": matched["p2p_id"], "amount": paid_amount},
            actor="RAZORPAY_WEBHOOK",
            money_recovered=paid_amount
        )
        return {"status": "fulfilled", "p2p_id": matched["p2p_id"], "amount": paid_amount}

    return {"status": "no_active_p2p_matched"}


def create_installment_split_plan(
    event_id: str,
    customer_id: str,
    customer_name: str,
    total_amount: float,
    installments_count: int = 2
) -> Dict[str, Any]:
    """
    Creates a Micro-Split Installment Plan ("Recover-as-a-Split") for high-value failed payments.
    Splits total_amount into weekly installments.
    """
    per_installment = round(total_amount / installments_count, 2)
    schedule = []

    for i in range(1, installments_count + 1):
        promised_days = i * 7
        p2p = create_promise_to_pay(
            event_id=f"{event_id}_PART{i}",
            customer_id=customer_id,
            customer_name=customer_name,
            amount=per_installment,
            promised_days_ahead=promised_days,
            notes=f"Micro-Split Installment {i}/{installments_count} for original payment {event_id}"
        )
        schedule.append(p2p)

    return {
        "original_event_id": event_id,
        "total_amount": total_amount,
        "installments_count": installments_count,
        "amount_per_installment": per_installment,
        "schedule": schedule,
        "status": "micro_split_active"
    }
