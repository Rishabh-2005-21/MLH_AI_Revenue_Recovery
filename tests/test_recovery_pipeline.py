import pytest
from app.services.detector import detect_revenue_at_risk
from app.services.diagnoser import diagnose
from app.services.decision_agent import choose_action
from app.services.guardrails import validate_action
from app.services.recovery import execute_recovery_workflow
from app.services.voice_agent import generate_hinglish_script, simulate_interactive_objection
from app.services.promise_to_pay import create_promise_to_pay, verify_p2p_settlements
from app.evaluation.evaluate import run_batch_evaluation
from app.models import ActionType, RiskCategory

def test_detector_payment_failure():
    event = {
        "event_id": "EVT_TEST_001",
        "category": "payment_failure",
        "amount": 5000.0,
        "failure_reason": "BAD_REQUEST_PAYMENT_TIMED_OUT",
        "status": "detected"
    }
    res = detect_revenue_at_risk(event)
    assert res["is_at_risk"] is True
    assert res["risk_score"] > 0.8

def test_diagnoser_and_decision():
    event = {
        "event_id": "EVT_TEST_002",
        "category": "cart_abandonment",
        "amount": 15000.0,
        "failure_reason": "CART_ABANDONED_HIGH_INTENT",
        "customer": {"name": "Test User"}
    }
    diag = diagnose(event)
    assert diag["recovery_probability"] > 0.8
    decision = choose_action(event, diag)
    assert decision["action"] == ActionType.HINGLISH_VOICE_CALL

def test_hitl_high_value_guardrail():
    event = {
        "event_id": "EVT_TEST_003",
        "category": "b2b_receivable",
        "amount": 120000.0,
        "failure_reason": "INVOICE_OVERDUE_30D",
        "attempts_count": 0
    }
    diag = diagnose(event)
    decision = choose_action(event, diag)
    approved, reason, rules = validate_action(event, decision)
    assert approved is False
    assert decision["requires_approval"] is True
    assert decision["action"] == ActionType.ESCALATE_TO_HUMAN

def test_hinglish_voice_agent():
    event = {
        "event_id": "EVT_TEST_004",
        "category": "cart_abandonment",
        "amount": 8999.0,
        "customer": {"name": "Rahul Sharma", "phone": "+919810123456"}
    }
    script_info = generate_hinglish_script(event)
    assert "Rahul" in script_info["greeting"]
    assert "RecoverAI" in script_info["greeting"]
    assert len(script_info["dialog_turns"]) > 2

def test_promise_to_pay_workflow():
    event_id = "EVT_P2P_001"
    p2p = create_promise_to_pay(event_id, "CUST_99", "Rahul Sharma", 25000.0, 2)
    assert p2p["amount_promised"] == 25000.0
    assert p2p["status"] == "active"

    # Verify settlement matching
    settle_res = verify_p2p_settlements(event_id, 25000.0)
    assert settle_res["status"] == "fulfilled"

def test_batch_evaluation():
    metrics = run_batch_evaluation(batch_size=20, seed=123)
    assert metrics["batch_size"] == 20
    assert metrics["precision"] >= 0.0
    assert metrics["recall"] >= 0.0
    assert metrics["total_revenue_recovered"] >= 0.0

def test_payment_method_swap_link():
    from app.services.razorpay_client import RazorpayClient
    client = RazorpayClient()
    plink = client.create_payment_method_swap_link(
        event_id="EVT_SWAP_01",
        amount=5000.0,
        customer_name="Priya Patel",
        customer_email="priya@example.com",
        customer_phone="+919876543210",
        failed_method="card"
    )
    assert plink["swap_from"] == "card"
    assert "upi" in plink["recommended_methods"]
    assert "upi_intent_url" in plink

def test_installment_split_plan():
    from app.services.promise_to_pay import create_installment_split_plan
    plan = create_installment_split_plan("EVT_SPLIT_01", "CUST_100", "Aman Verma", 20000.0, installments_count=2)
    assert plan["total_amount"] == 20000.0
    assert plan["installments_count"] == 2
    assert plan["amount_per_installment"] == 10000.0
    assert len(plan["schedule"]) == 2

def test_retry_sequencer_bank_avoidance():
    from app.services.retry_sequencer import calculate_optimal_retry_schedule
    event = {"event_id": "EVT_RETRY_01", "bank_name": "SBI"}
    schedule = calculate_optimal_retry_schedule(event)
    assert schedule["bank_name"] == "SBI"
    assert "recommended_retry_time" in schedule
    assert schedule["expected_success_probability"] > 0.0

def test_digital_twin_simulation():
    from app.services.digital_twin import run_digital_twin_simulation
    from data.synthetic_generator import generate_synthetic_batch
    events = generate_synthetic_batch(count=15, seed=99)
    sim_result = run_digital_twin_simulation(events)
    assert sim_result["total_events_simulated"] == 15
    assert "baseline_retries" in sim_result["strategies_compared"]
    assert "ai_next_best_action" in sim_result["strategies_compared"]
    assert sim_result["strategies_compared"]["ai_next_best_action"]["net_recovered_revenue"] >= 0.0

def test_copilot_assistant_queries():
    from app.services.copilot import answer_merchant_copilot, calculate_merchant_health_score
    resp = answer_merchant_copilot("What is my current recovery rate?")
    assert "Recovery Rate" in resp or "recovered" in resp.lower()
    health = calculate_merchant_health_score()
    assert "health_score" in health
    assert 0 <= health["health_score"] <= 100

def test_predictive_expiry_engine():
    from app.services.predictive_expiry import scan_and_predict_at_risk_renewals
    renewals = scan_and_predict_at_risk_renewals(count=10)
    assert len(renewals) == 10
    for item in renewals:
        assert "risk_score" in item
        assert "pre_dunning_action" in item

def test_whatsapp_multitone_generation():
    from app.services.whatsapp_service import generate_whatsapp_recovery_message
    event = {"event_id": "EVT_WA_01", "amount": 3500.0, "customer": {"name": "Deepak", "preferred_language": "Hinglish"}}
    msg_hinglish = generate_whatsapp_recovery_message(event, tone="Hinglish")
    assert "Namaste" in msg_hinglish["whatsapp_message_text"]

    event_formal = {"event_id": "EVT_WA_02", "amount": 3500.0, "customer": {"name": "Deepak", "preferred_language": "Formal"}}
    msg_formal = generate_whatsapp_recovery_message(event_formal, tone="Formal")
    assert "Dear" in msg_formal["whatsapp_message_text"]

def test_voice_objection_handling():
    from app.services.voice_agent import simulate_interactive_objection
    obj = simulate_interactive_objection("EVT_V_01", "no_money_today")
    assert obj["status"] == "PROMISE_TO_PAY_RECORDED"
    assert "p2p_id" in obj

