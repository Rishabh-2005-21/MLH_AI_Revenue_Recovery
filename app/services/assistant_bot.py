from typing import Dict, Any, List
from app.services.gemini_service import call_gemini_api, is_gemini_available

APP_TOUR_STEPS = [
    {
        "step": 1,
        "title": "📊 Executive Overview",
        "description": "Shows real-time high-level business metrics: Total At-Risk Revenue (₹), Total Recovered Money (₹), Success Rate %, and Revenue Breakdown across 4 tracks."
    },
    {
        "step": 2,
        "title": "🤖 Interactive Recovery Sandbox",
        "description": "Test single scenarios live! Select failure type (e.g. HDFC server down, cart abandonment), view 4-step AI execution (Detect → Diagnose → Decide → Act), generate Razorpay links, and test webhooks."
    },
    {
        "step": 3,
        "title": "⚡ 150-Event Batch Benchmark",
        "description": "Run the AI agent across a 150-event batch. Delineates precision, recall, net ROI %, false positive rates, and guardrail prevention counts."
    },
    {
        "step": 4,
        "title": "🎙️ Hinglish AI Voice Agent Studio",
        "description": "Trigger multi-lingual Hinglish/English voice calls, listen to synthetic audio, inspect dialog transcripts, and test interactive objection handling."
    },
    {
        "step": 5,
        "title": "⚖️ Guardrails & HITL Approval Queue",
        "description": "Enforces strict financial rules (max 2 retries, 9 PM-9 AM quiet hours). High-value enterprise receivables (>₹50,000) pause here for 1-click supervisor approval."
    },
    {
        "step": 6,
        "title": "📜 Immutable Audit Log Explorer",
        "description": "Complete searchable history log of every AI decision, timestamp, guardrail match, and Razorpay webhook payload."
    }
]

FAQ_KNOWLEDGE_BASE = {
    "uses": """
💡 **Main Uses & Benefits of RecoverAI**:
1. **Stop Revenue Leakage**: Automatically detects money slipping away due to payment timeouts, bank downtime, cart drop-offs, and overdue invoices.
2. **Smart AI Interventions**: Chooses the right recovery action (Smart Retry, Dynamic Discount UPI link, Hinglish Voice call, Card updater portal).
3. **100% Compliant & Safe**: Strict guardrails prevent harassment (max 2 retries, 9 PM - 9 AM quiet hours, auto-stop on payment).
4. **Human Control for High Value**: Enterprise receivables >₹50,000 automatically route to a supervisor for 1-click approval.
5. **Measurable ROI**: Shows exact money recovered (₹) with full audit trails.
""",
    "tour": """
🚀 **Full App Tour**:
1. **Executive Overview**: High-level KPIs and conversion funnel charts.
2. **Interactive Sandbox**: 1-Click testing of payment errors, cart drop-offs, and Razorpay webhooks.
3. **Batch Benchmark**: Test AI precision, recall, and revenue recovered across 150+ synthetic transactions.
4. **Hinglish Voice Studio**: Interactive voice call simulator with objection handling (e.g. 'Pay tomorrow', 'Discount request').
5. **HITL Queue**: Supervisor 1-click approval for high-value cases.
6. **Audit Explorer**: Complete searchable timeline of all AI actions.
""",
    "voice": """
🎙️ **Hinglish AI Voice Recovery Agent**:
The AI calls customers in natural Hinglish (*"Namaste Rahulji, aapka ₹4,999 ka payment decline ho gaya hai..."*) to answer questions, handle objections (e.g. offering instant 5% cashback or recording Promise-To-Pay dates), and send direct 1-click Razorpay payment links to WhatsApp!
""",
    "guardrails": """
🛡️ **Guardrails & Compliance Rules**:
- **Max Retries**: Max 2 automatic retries per payment failure (prevents bank bounce charges).
- **Quiet Hours**: Automated voice calls blocked between 9:00 PM and 9:00 AM.
- **HITL Threshold**: Any B2B invoice or payment > ₹50,000 requires human supervisor approval.
- **Auto-Stop**: Immediately halts all dunning when payment is captured or customer opts out ('STOP').
""",
    "razorpay": """
💳 **Razorpay Integration**:
RecoverAI generates functional Razorpay Payment Links (`https://rzp.io/i/...`) and handles Webhooks (`payment.captured`, `invoice.paid`). It operates 100% out-of-the-box in standalone Test Mode Sandbox, or with live API keys if configured in `.env`.
"""
}

def query_assistant(user_prompt: str) -> str:
    """
    Answers user queries about RecoverAI app, giving full tour & guidance in Hinglish/English.
    Uses Google Gemini API when GEMINI_API_KEY is configured.
    """
    if is_gemini_available():
        system_instruction = """
You are the AI Assistant for RecoverAI (Razorpay AI Buildathon 2026 - Track 03: AI Agent for Business Revenue Recovery).
Your role is to guide merchants and users about how RecoverAI works, its features, guardrails, Hinglish voice agent, Razorpay integration, HITL queue (>₹50,000 threshold), and measurable ROI.
Respond in a friendly, expert, professional tone using clean Markdown formatting. Keep answers concise, actionable, and rich in detail.
"""
        gemini_response = call_gemini_api(user_prompt, system_instruction=system_instruction)
        if gemini_response:
            return f"✨ **RecoverAI Assistant (Powered by Gemini AI)**:\n\n{gemini_response}"

    # Fallback Rule Matcher
    prompt = user_prompt.lower()
    if any(w in prompt for w in ["tour", "guide", "overview", "kaise use", "how to use", "start"]):
        return FAQ_KNOWLEDGE_BASE["tour"]
    elif any(w in prompt for w in ["use", "benefit", "kya kam", "purpose", "why"]):
        return FAQ_KNOWLEDGE_BASE["uses"]
    elif any(w in prompt for w in ["voice", "call", "hinglish", "audio", "phone"]):
        return FAQ_KNOWLEDGE_BASE["voice"]
    elif any(w in prompt for w in ["guardrail", "rule", "safety", "quiet", "hitl", "50000", "50k"]):
        return FAQ_KNOWLEDGE_BASE["guardrails"]
    elif any(w in prompt for w in ["razorpay", "link", "webhook", "sandbox", "payment"]):
        return FAQ_KNOWLEDGE_BASE["razorpay"]
    else:
        return f"""
🤖 **RecoverAI AI Assistant**:
I am here to guide you through the **RecoverAI Platform**!

You asked: *"{user_prompt}"*

**Quick Summary**: RecoverAI is an autonomous AI agent for Razorpay AI Buildathon 2026 (Track 03) that detects slipping revenue (failed payments, cart abandonment, expired subscriptions, overdue invoices), diagnoses root causes, and executes compliant recovery (Hinglish Voice calls, Razorpay links, smart retries).

💡 Try asking me:
- *"Take me on a full app tour"*
- *"What are the main uses and benefits?"*
- *"How does the Hinglish voice agent work?"*
- *"Explain guardrails & HITL rule"*
"""

