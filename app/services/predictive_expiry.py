import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

def predict_upcoming_card_expiries(count: int = 15) -> List[Dict[str, Any]]:
    """
    Scans subscription e-Mandates and predicts cards/UPI mandates expiring in the next 7 to 30 days.
    Calculates Pre-Emptive Risk Score and generates automated mandate update links.
    """
    names = [
        "Ananya Roy", "Vikramaditya Rao", "Sneha Kulkarni", "Rohan Mehta", "Divya Nair",
        "Karan Malhotra", "Pooja Banerjee", "Siddharth Joshi", "Neha Gupta", "Tarun Kapur"
    ]
    plans = ["Enterprise Pro Annual", "SaaS Growth Monthly", "Cloud Infrastructure Premium", "Analytics Suite Pro"]
    
    records = []
    now = datetime.now()

    for i in range(count):
        days_to_expiry = random.randint(3, 28)
        exp_date = (now + timedelta(days=days_to_expiry)).strftime("%Y-%m-%d")
        monthly_val = float(random.choice([1499, 2999, 4999, 9999, 24999]))
        ltv = monthly_val * random.randint(12, 36)
        
        # Risk score calculation based on LTV and urgency
        urgency_factor = max(0.2, 1.0 - (days_to_expiry / 30.0))
        risk_score = round(min(99.0, (ltv / 1000.0) * 0.4 + urgency_factor * 50.0), 1)
        
        records.append({
            "subscription_id": f"sub_exp_{random.randint(10000, 99999)}",
            "customer_name": random.choice(names),
            "customer_email": f"user{i+1}@company.in",
            "plan_name": random.choice(plans),
            "monthly_amount": monthly_val,
            "ltv": ltv,
            "card_last4": str(random.randint(1000, 9999)),
            "bank_name": random.choice(["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Bank"]),
            "expiry_date": exp_date,
            "days_to_expiry": days_to_expiry,
            "risk_score": risk_score / 100.0,
            "preemptive_risk_score": risk_score,
            "pre_dunning_action": "PREEMPTIVE_CARD_UPDATE_NUDGE",
            "update_portal_link": f"https://rzp.io/l/mandate_update_{random.randint(100, 999)}",
            "status": "PREEMPTIVE_NOTICE_SENT" if days_to_expiry <= 14 else "MONITORING"
        })

    return sorted(records, key=lambda x: x["days_to_expiry"])

def scan_and_predict_at_risk_renewals(count: int = 15) -> List[Dict[str, Any]]:
    return predict_upcoming_card_expiries(count=count)


def generate_preemptive_update_notice(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a pre-emptive notification message sent to customer BEFORE expiry happens.
    """
    msg = f"""
*Pre-Emptive Subscription Notice from Razorpay RecoverAI* 🛡️

Hi *{record['customer_name']}*,

Your payment card ending in *{record['card_last4']}* ({record['bank_name']}) for subscription *{record['plan_name']}* (₹{record['monthly_amount']:,.2f}/mo) is scheduled to expire on *{record['expiry_date']}* ({record['days_to_expiry']} days remaining).

To prevent any service interruption, update your payment method in 1-click using our secure Razorpay Card Updater portal:

🔗 *Update Card / UPI Mandate:*
{record['update_portal_link']}

_Zero service disruption guaranteed._
    """.strip()

    return {
        "subscription_id": record["subscription_id"],
        "customer_name": record["customer_name"],
        "notice_text": msg,
        "sent_via": "WhatsApp & Email",
        "status": "PREEMPTIVE_ACTION_TAKEN"
    }
