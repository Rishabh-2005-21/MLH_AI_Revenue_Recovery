import os
import random
from datetime import datetime
from typing import Dict, Any, List
from app.services.gemini_service import call_gemini_api, is_gemini_available


# Try importing gTTS for optional voice audio generation
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "audio")

def generate_hinglish_script(
    event: Dict[str, Any],
    action_type: str = "payment_reminder",
    sentiment: str = "empathic"
) -> Dict[str, Any]:
    """
    Generates a personalized Hinglish voice script and dialog flow for AI Voice Call recovery
    with dynamic tone adaptation based on customer sentiment (Empathetic / Professional / Assertive).
    """
    cust = event.get("customer") or {}
    cust_name = cust.get("name", "Valued Customer").split()[0]
    ltv = float(cust.get("ltv", 0.0))
    amount = float(event.get("amount", 0.0))
    formatted_amount = f"₹{amount:,.0f}"
    category = event.get("category", "payment_failure")
    items = event.get("cart_items") or ["your items"]
    item_str = ", ".join(items)

    # Tone adaptation logic
    if sentiment == "empathic" or ltv > 10000.0:
        tone_prefix = f"Namaste VIP {cust_name} ji! Aap humare bohot prized customer hain. "
        tone_style = "Empathetic & Soft-Touch"
    elif sentiment == "assertive":
        tone_prefix = f"Attention {cust_name} ji! Urgent notification regarding overdue status. "
        tone_style = "Firm & Time-Sensitive"
    else:
        tone_prefix = f"Hello {cust_name} ji, hope you are having a good day! "
        tone_style = "Professional & Helpful"

    if category == "cart_abandonment":
        greeting = tone_prefix + "Main RecoverAI Assistant bol raha hoon."
        opening = f"Aapne aapke cart mein {item_str} add kiya tha par checkout complete nahi ho paya ({formatted_amount})."
        pitch = "Kya aapko checkout karne mein koi payment issue aa rahi hai? Aaj hum standard 5% instant UPI cashback code offer kar rahe hain!"
        cta = "Main abhi aapke WhatsApp par direct 1-click Razorpay UPI Payment Link bhej deta hoon."
    elif category == "failed_subscription":
        greeting = tone_prefix
        opening = f"Aapka {formatted_amount} ka auto-subscription payment decline ho gaya hai."
        pitch = "Bank security rules ki wajah se mandate update ki zaroorat pad sakti hai."
        cta = "Kya main aapke mobile pe 1-click Card/UPI Update portal link WhatsApp kar doon?"
    elif category == "b2b_receivable":
        greeting = tone_prefix + "Accounts & Finance Team ki taraf se."
        opening = f"Aapke account par Invoice #{event.get('invoice_id', 'INV-102')} for {formatted_amount} overdue chal raha hai."
        pitch = "Kya hum is payment ke liye koi specific Promise-to-Pay (P2P) date fix kar sakte hain, so overall account credit clear rahe?"
        cta = "Aap kab tak payment process kar payenge — kal 12 Baje tak ya Monday tak?"
    else:
        greeting = tone_prefix
        opening = f"Aapka recent payment request of {formatted_amount} attempt approve nahi ho paya."
        pitch = "Network issue ki wajah se transaction timeout ho gaya tha. Pareshan hone ki koi baat nahi hai."
        cta = "Aap abhi humare direct Razorpay UPI link se securely pay kar sakte hain."

    dialog_turns = [
        {"speaker": "AI Voice Agent", "text": greeting + " " + opening},
        {"speaker": "Customer (Simulated)", "text": "Haan, main payment karna chahta hoon par kal bank server down tha."},
        {"speaker": "AI Voice Agent", "text": pitch + " " + cta},
        {"speaker": "Customer (Simulated)", "text": "Ji bilkul, mere WhatsApp pe payment link bhej dijiye, main abhi UPI se pay kar deta hoon."},
        {"speaker": "AI Voice Agent", "text": f"Bahut badiya {cust_name} ji! Link generate ho gaya hai aur aapke WhatsApp no pe bhej diya gaya hai. Thank you!"}
    ]

    full_transcript = " ".join([t["text"] for t in dialog_turns if t["speaker"] == "AI Voice Agent"])

    # Generate real MP3 file if gTTS is available
    audio_path = None
    if GTTS_AVAILABLE:
        try:
            os.makedirs(AUDIO_DIR, exist_ok=True)
            filename = f"call_{event.get('event_id', 'demo')}.mp3"
            filepath = os.path.join(AUDIO_DIR, filename)
            if not os.path.exists(filepath):
                tts = gTTS(text=greeting + " " + opening + " " + pitch + " " + cta, lang="hi")
                tts.save(filepath)
            audio_path = filepath
        except Exception:
            audio_path = None

    return {
        "event_id": event.get("event_id"),
        "customer_name": cust_name,
        "language": "Hinglish",
        "greeting": greeting,
        "full_script": full_transcript,
        "dialog_turns": dialog_turns,
        "audio_file_path": audio_path,
        "call_status": "completed",
        "duration_seconds": 38,
        "sentiment": sentiment,
        "adapted_tone_style": tone_style,
        "outcome": "P2P_AGREED_UPI_SENT"
    }

def simulate_interactive_objection(arg1: str = "will_pay_tomorrow", arg2: str = "Rahul", amount: float = 4999.0) -> Dict[str, Any]:
    """
    Handles live dynamic objections during UI voice call simulation & unit tests.
    Uses Google Gemini API for real-time natural Hinglish response when GEMINI_API_KEY is configured.
    """
    if arg2 in ["no_money_today", "will_pay_tomorrow", "discount_request", "wrong_invoice", "upi_request"]:
        event_id = arg1
        objection_type = arg2
        cust_name = "Customer"
    else:
        event_id = f"EVT_{arg1}"
        objection_type = arg1
        cust_name = arg2

    formatted_amount = f"₹{amount:,.0f}"

    objection_prompts = {
        "no_money_today": ("Main abhi payment nahi kar sakta, mere paas paise nahi hain.", "Record Promise-To-Pay for payday/next week and offer a payment link."),
        "will_pay_tomorrow": ("Main abhi thoda busy hoon, main kal shaam tak pay kar doonga.", "Accept P2P gracefully for tomorrow evening, record it, and mention sending a WhatsApp reminder link."),
        "discount_request": (f"Kya isme thoda discount mil sakta hai for amount {formatted_amount}?", f"Offer an instant 5% cashback auto-applied to their Razorpay payment link. New total is ₹{amount*0.95:,.0f}."),
        "wrong_invoice": ("Yeh invoice amount galat lag raha hai.", "Politely acknowledge, offer to put the invoice on 24-hour review hold, and escalate to finance audit tag."),
        "upi_request": ("Kya main PhonePe / Google Pay UPI se kar sakta hoon?", "Confirm enthusiastically that Razorpay 1-click link supports all UPI apps (GPay, PhonePe, Paytm, BHIM).")
    }

    cust_input, agent_goal = objection_prompts.get(
        objection_type,
        (objection_type, "Handle the customer query helpfully and guide them to pay securely via Razorpay payment link.")
    )

    agent_reply = None
    if is_gemini_available():
        system_prompt = f"""
You are an empathetic, polite Hinglish AI Voice Agent for RecoverAI contacting customer '{cust_name}' regarding an unpaid transaction of {formatted_amount}.
Your goal: {agent_goal}
Rules:
- Respond in 1-2 natural sentences of spoken Hinglish (Hindi + English blend).
- Include polite Indian honorifics ('ji').
- Be helpful and non-pushy.
"""
        agent_reply = call_gemini_api(f"Customer said: '{cust_input}'", system_instruction=system_prompt)

    if not agent_reply:
        if objection_type in ["no_money_today", "will_pay_tomorrow"]:
            agent_reply = f"Koyi baat nahi {cust_name} ji! Main aapka Promise-to-Pay record kar leta hoon. Reminder link WhatsApp pe rahega."
        elif objection_type == "discount_request":
            agent_reply = f"Ji {cust_name} ji, humne abhi instant 5% cashback auto-apply kar diya hai! Naya total ₹{amount*0.95:,.0f} hai."
        elif objection_type == "wrong_invoice":
            agent_reply = f"Samajh gaya {cust_name} ji. Main is invoice ko review ke liye hold pe dal ke humari finance team ko audit tag bhej deta hoon."
        else:
            agent_reply = f"Ji bilkul! 1-click Razorpay link saare UPI Apps (GPay, PhonePe, Paytm, BHIM) support karta hai."

    return {
        "event_id": event_id,
        "objection_type": objection_type,
        "customer": cust_input,
        "agent": agent_reply,
        "status": "PROMISE_TO_PAY_RECORDED",
        "p2p_id": f"p2p_{event_id}_001"
    }


