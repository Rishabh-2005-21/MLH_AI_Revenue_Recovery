from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.database import (
    get_summary_stats, get_hitl_queue, resolve_hitl_item, get_audit_logs, log_audit
)
from app.services.detector import detect_revenue_at_risk
from app.services.diagnoser import diagnose
from app.services.decision_agent import choose_action
from app.services.recovery import execute_recovery_workflow
from app.services.voice_agent import generate_hinglish_script, simulate_interactive_objection
from app.services.promise_to_pay import verify_p2p_settlements, create_installment_split_plan
from app.services.razorpay_client import RazorpayClient
from app.services.digital_twin import run_digital_twin_simulation
from app.services.copilot import answer_merchant_copilot, calculate_merchant_health_score
from app.evaluation.evaluate import run_batch_evaluation
from data.synthetic_generator import generate_synthetic_batch

razorpay_client = RazorpayClient()

app = FastAPI(
    title="RecoverAI – AI Revenue Recovery API",
    version="1.0.0",
    description="Autonomous, bounded AI revenue recovery decision engine for Track 03."
)

@app.get("/")
def root():
    return {
        "title": "RecoverAI – AI Revenue Recovery Platform API",
        "status": "online",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "summary": "/api/recovery/summary",
            "health_score": "/api/recovery/health-score",
            "audit_trail": "/api/recovery/audit",
            "hitl_queue": "/api/recovery/hitl"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "system": "RecoverAI Agent Engine", "version": "1.0.0"}

@app.get("/api/recovery/summary")
def recovery_summary():
    return get_summary_stats()

@app.get("/api/recovery/health-score")
def get_health_score():
    return calculate_merchant_health_score()

@app.post("/api/recovery/copilot")
def ask_copilot(query: str = Body(..., embed=True)):
    return {"query": query, "response": answer_merchant_copilot(query)}

@app.post("/api/recovery/digital-twin")
def simulate_digital_twin(batch_size: int = 100):
    events = generate_synthetic_batch(count=batch_size, seed=42)
    return run_digital_twin_simulation(events)

@app.post("/api/recovery/detect")
def detect_event(event: Dict[str, Any] = Body(...)):
    return detect_revenue_at_risk(event)

@app.post("/api/recovery/diagnose")
def diagnose_event(event: Dict[str, Any] = Body(...)):
    return diagnose(event)

@app.post("/api/recovery/execute")
def execute_event(event: Dict[str, Any] = Body(...)):
    detection = detect_revenue_at_risk(event)
    diag = diagnose(event)
    decision = choose_action(event, diag)
    result = execute_recovery_workflow(event, decision)
    return {
        "detection": detection,
        "diagnosis": diag,
        "decision": decision,
        "execution": result
    }

@app.post("/api/recovery/payment-swap")
def create_payment_swap(event_id: str = Body(...), amount: float = Body(...), name: str = Body(...), email: str = Body(...), phone: str = Body(...)):
    return razorpay_client.create_payment_method_swap_link(
        event_id=event_id,
        amount=amount,
        customer_name=name,
        customer_email=email,
        customer_phone=phone
    )

@app.post("/api/recovery/micro-split")
def create_micro_split(event_id: str = Body(...), customer_id: str = Body(...), name: str = Body(...), amount: float = Body(...), installments: int = Body(2)):
    return create_installment_split_plan(
        event_id=event_id,
        customer_id=customer_id,
        customer_name=name,
        total_amount=amount,
        installments_count=installments
    )

@app.post("/api/recovery/batch")
def execute_batch(batch_size: int = 100):
    return run_batch_evaluation(batch_size=batch_size)

@app.get("/api/recovery/hitl")
def get_hitl_pending():
    return {"pending_items": get_hitl_queue()}

@app.post("/api/recovery/hitl/{event_id}/resolve")
def resolve_hitl(event_id: str, approved: bool = True):
    resolve_hitl_item(event_id, approved)
    log_audit(
        event_id=event_id,
        category="b2b_receivable",
        event_type="HITL_SUPERVISOR_ACTION",
        details={"status": "approved" if approved else "rejected"},
        actor="HUMAN_SUPERVISOR"
    )
    return {"event_id": event_id, "status": "approved" if approved else "rejected"}

@app.post("/api/recovery/voice/script")
def get_voice_script(event: Dict[str, Any] = Body(...)):
    return generate_hinglish_script(event)

@app.post("/api/webhooks/razorpay")
def handle_razorpay_webhook(payload: Dict[str, Any] = Body(...)):
    event_type = payload.get("event", "payment.captured")
    pay_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    amount = float(pay_entity.get("amount", 0)) / 100.0
    payment_id = pay_entity.get("id", "pay_unknown")
    event_id = payload.get("event_id", f"EVT_{payment_id}")

    p2p_res = verify_p2p_settlements(event_id, amount)

    log_audit(
        event_id=event_id,
        category="payment_webhook",
        event_type=f"RAZORPAY_{event_type.upper()}",
        details={"payment_id": payment_id, "amount": amount, "p2p_matched": p2p_res},
        actor="RAZORPAY_WEBHOOK",
        money_recovered=amount
    )

    return {"status": "webhook_processed", "payment_id": payment_id, "amount_recovered": amount, "p2p_result": p2p_res}

@app.get("/api/recovery/audit")
def get_audit_trail_logs(limit: int = 100):
    return {"logs": get_audit_logs(limit)}
