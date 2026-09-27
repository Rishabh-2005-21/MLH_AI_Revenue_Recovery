import json
from datetime import datetime, timezone
from typing import Dict, Any

def generate_whatsapp_recovery_message(event_dict: Dict[str, Any], tone: str = "Hinglish") -> Dict[str, Any]:
    """
    Generates a personalized WhatsApp recovery message with Razorpay UPI Intent Link
    and dynamic discount token in Formal, Conversational, or Hinglish tones.
    """
    cust = event_dict.get("customer") or {}
    cust_name = cust.get("name", "Valued Customer")
    amount = float(event_dict.get("amount", 4999.0))
    event_id = event_dict.get("event_id", f"EVT_{datetime.now().strftime('%H%M%S')}")
    pref_lang = cust.get("preferred_language", tone)
    
    # Calculate 5% instant recovery discount
    discount_amount = round(amount * 0.05, 2)
    final_amount = round(amount - discount_amount, 2)
    
    upi_link = f"upi://pay?pa=razorpay.recoverai@icici&pn=Razorpay+RecoverAI&am={final_amount}&cu=INR&tr={event_id}"
    rzp_pay_link = f"https://rzp.io/l/rec_{event_id.lower()}"

    if pref_lang == "Hinglish":
        message_text = f"""
*Razorpay RecoverAI Revenue Recovery Assistant* 🛡️

Namaste *{cust_name}* ji! 🙏

Aapka order `#{event_id}` for *₹{amount:,.2f}* complete nahi ho paya due to a temporary bank server timeout.

🎁 *Instant Special Discount:*
Abhi 1-Click Razorpay UPI link se pay kariye & instant *₹{discount_amount:,.2f} (5% OFF)* paiye!

👉 *Net Amount:* *₹{final_amount:,.2f}*

🔗 *Payment Link:* {rzp_pay_link}
📲 *Direct UPI Pay:* {upi_link}

_Valid for 24 hours. Secured by Razorpay._
        """.strip()
    elif pref_lang == "Formal":
        message_text = f"""
*Razorpay Payment Notice* 🛡️

Dear *{cust_name}*,

Your payment of *₹{amount:,.2f}* for Order `#{event_id}` was unsuccessful due to a gateway timeout.

We have authorized an instant concession of *₹{discount_amount:,.2f}*.

👉 *Revised Amount:* *₹{final_amount:,.2f}*

🔗 *Pay Online:* {rzp_pay_link}

_Secured by Razorpay Payment Gateway._
        """.strip()
    else:
        message_text = f"""
*Razorpay RecoverAI Assistant* 🛡️

Hi *{cust_name}*,

We noticed your recent payment of *₹{amount:,.2f}* for Order `#{event_id}` was incomplete due to a temporary bank server timeout.

🎁 *Instant Recovery Special Offer:*
Pay now using our 1-Click Razorpay UPI link and get an instant *₹{discount_amount:,.2f} (5% OFF)* discount!

👉 *Net Payable:* *₹{final_amount:,.2f}*

🔗 *1-Click Payment Link:* {rzp_pay_link}
📲 *Direct UPI Pay:* {upi_link}

_This link is valid for 24 hours. Secured by Razorpay Payment Gateway._
        """.strip()

    return {
        "event_id": event_id,
        "customer_name": cust_name,
        "customer_phone": cust.get("phone", "+919810123456"),
        "original_amount": amount,
        "discount_applied": discount_amount,
        "final_payable_amount": final_amount,
        "upi_intent_link": upi_link,
        "razorpay_pay_link": rzp_pay_link,
        "whatsapp_message_text": message_text,
        "status": "QUEUED_FOR_DISPATCH",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def simulate_whatsapp_dispatch(event_dict: Dict[str, Any]) -> Dict[str, Any]:
    msg_data = generate_whatsapp_recovery_message(event_dict)
    msg_data["status"] = "DELIVERED_AND_READ"
    return msg_data
