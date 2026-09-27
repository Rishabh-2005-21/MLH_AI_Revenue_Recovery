from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RecoverAI – AI Revenue Recovery Platform</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', sans-serif;
                background: #090d16;
                color: #f3f4f6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 2rem 1rem;
                background-image: 
                    radial-gradient(circle at 15% 20%, rgba(0, 242, 254, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 85% 80%, rgba(79, 172, 254, 0.08) 0%, transparent 40%);
            }
            .container {
                max-width: 900px;
                width: 100%;
                background: rgba(17, 24, 39, 0.75);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 3rem 2.5rem;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }
            .header-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background: rgba(16, 185, 129, 0.15);
                border: 1px solid rgba(16, 185, 129, 0.3);
                color: #10b981;
                padding: 0.4rem 1rem;
                border-radius: 9999px;
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 1.5rem;
            }
            .pulse {
                width: 8px;
                height: 8px;
                background-color: #10b981;
                border-radius: 50%;
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
                70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
                100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
            }
            h1 {
                font-family: 'Outfit', sans-serif;
                font-size: 2.75rem;
                font-weight: 800;
                letter-spacing: -0.025em;
                background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.75rem;
            }
            p.subtitle {
                font-size: 1.125rem;
                color: #94a3b8;
                line-height: 1.6;
                margin-bottom: 2.5rem;
            }
            .cards-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2.5rem;
            }
            .card {
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
                padding: 1.75rem;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                transition: transform 0.2s ease, border-color 0.2s ease;
            }
            .card:hover {
                transform: translateY(-4px);
                border-color: rgba(79, 172, 254, 0.4);
            }
            .card-icon {
                font-size: 2rem;
                margin-bottom: 1rem;
            }
            .card-title {
                font-family: 'Outfit', sans-serif;
                font-size: 1.35rem;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 0.5rem;
            }
            .card-desc {
                font-size: 0.925rem;
                color: #94a3b8;
                line-height: 1.5;
                margin-bottom: 1.5rem;
                flex-grow: 1;
            }
            .btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                padding: 0.85rem 1.25rem;
                border-radius: 12px;
                font-weight: 600;
                text-decoration: none;
                transition: all 0.2s ease;
                font-size: 0.95rem;
            }
            .btn-primary {
                background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
                color: #090d16;
                box-shadow: 0 4px 14px rgba(0, 242, 254, 0.3);
            }
            .btn-primary:hover {
                box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5);
                transform: scale(1.02);
            }
            .btn-secondary {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #ffffff;
            }
            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.12);
                border-color: rgba(255, 255, 255, 0.3);
            }
            .endpoints-box {
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 16px;
                padding: 1.5rem;
            }
            .endpoints-title {
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #64748b;
                margin-bottom: 1rem;
            }
            .endpoint-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 0.75rem;
            }
            .endpoint-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-family: monospace;
                font-size: 0.85rem;
                color: #cbd5e1;
                text-decoration: none;
                padding: 0.5rem 0.75rem;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                transition: background 0.2s ease;
            }
            .endpoint-item:hover {
                background: rgba(255, 255, 255, 0.08);
                color: #38bdf8;
            }
            .method {
                font-weight: 700;
                font-size: 0.75rem;
                padding: 0.15rem 0.4rem;
                border-radius: 4px;
            }
            .method-get { background: rgba(16, 185, 129, 0.2); color: #34d399; }
            .method-post { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
            .footer {
                margin-top: 2rem;
                text-align: center;
                font-size: 0.85rem;
                color: #64748b;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-badge">
                <span class="pulse"></span> System Status: Online & Operational
            </div>
            <h1>🛡️ RecoverAI Engine</h1>
            <p class="subtitle">Autonomous, bounded AI revenue recovery decision engine built for MLH Hackathon 2026.</p>
            
            <div class="cards-grid">
                <div class="card">
                    <div>
                        <div class="card-icon">🖥️</div>
                        <div class="card-title">Streamlit UI Dashboard</div>
                        <div class="card-desc">Interactive visual analytics dashboard, scenario simulator, merchant health score, and copilot. Hosted live on Render.</div>
                    </div>
                    <a href="https://recoverai-dashboard-xega.onrender.com" target="_blank" class="btn btn-primary">
                        Launch Streamlit UI ↗
                    </a>
                </div>
                
                <div class="card">
                    <div>
                        <div class="card-icon">⚡</div>
                        <div class="card-title">Interactive API Docs</div>
                        <div class="card-desc">Explore OpenAPI / Swagger documentation to inspect and test all FastAPI recovery decision endpoints & webhooks.</div>
                    </div>
                    <a href="/docs" class="btn btn-secondary">
                        Open Swagger UI ↗
                    </a>
                </div>
            </div>

            <div class="endpoints-box">
                <div class="endpoints-title">Active API Endpoints</div>
                <div class="endpoint-list">
                    <a href="/health" class="endpoint-item"><span class="method method-get">GET</span> /health</a>
                    <a href="/api/recovery/summary" class="endpoint-item"><span class="method method-get">GET</span> /summary</a>
                    <a href="/api/recovery/health-score" class="endpoint-item"><span class="method method-get">GET</span> /health-score</a>
                    <a href="/api/recovery/audit" class="endpoint-item"><span class="method method-get">GET</span> /audit</a>
                    <a href="/api/recovery/hitl" class="endpoint-item"><span class="method method-get">GET</span> /hitl</a>
                    <a href="/docs" class="endpoint-item"><span class="method method-post">POST</span> /execute</a>
                </div>
            </div>

            <div class="footer">
                RecoverAI • Major League Hacking (MLH) AI Revenue Recovery Track
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

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
