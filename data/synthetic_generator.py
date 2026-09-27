import random
import json
import os
from datetime import datetime, timedelta, timezone
import pandas as pd

CUSTOMER_NAMES = [
    ("Rahul Sharma", "rahul.sharma@example.com", "+919810123456", "Hinglish"),
    ("Priya Patel", "priya.patel@techcorp.in", "+919820234567", "English"),
    ("Amit Verma", "amit.v@designstudio.io", "+919830345678", "Hinglish"),
    ("Neha Gupta", "neha.gupta@fintech.co", "+919840456789", "Hindi"),
    ("Vikram Singh", "vikram.singh@logistics.in", "+919850567890", "Hinglish"),
    ("Ananya Roy", "ananya.roy@retail.com", "+919860678901", "English"),
    ("Rajesh Kumar", "rajesh.k@agri.org", "+919870789012", "Hinglish"),
    ("Sanjay Mehta", "smehta@mehtatraders.com", "+919880890123", "Hindi"),
    ("Kavita Rao", "kavita.rao@healthcare.org", "+919890901234", "English"),
    ("Deepak Joshi", "deepak.j@cloudnet.in", "+919900012345", "Hinglish"),
]

CART_ITEM_COMBOS = [
    ["SaaS Pro Annual Subscription", "Dedicated IP Addon"],
    ["Noise-Cancelling Headphones", "Carrying Case"],
    ["Enterprise ERP User License x 10"],
    ["Cloud Hosting GPU Cluster - 1 Month"],
    ["Smart Fitness Watch v2", "Screen Protector"],
    ["B2B Consulting Hours Bundle"],
]

PAYMENT_FAILURE_REASONS = [
    ("BAD_REQUEST_PAYMENT_TIMED_OUT", 0.85, "payment_failure"),
    ("ISSUER_BANK_SERVER_DOWN", 0.90, "payment_failure"),
    ("INSUFFICIENT_FUNDS", 0.75, "payment_failure"),
    ("AUTHENTICATION_FAILED", 0.60, "payment_failure"),
    ("GATEWAY_ERROR", 0.88, "payment_failure"),
    ("MANDATE_EXPIRED", 0.70, "failed_subscription"),
    ("EXPIRED_CARD", 0.65, "failed_subscription"),
    ("CARD_DECLINED", 0.72, "failed_subscription"),
    ("CART_ABANDONED_STEP3", 0.80, "cart_abandonment"),
    ("CART_ABANDONED_HIGH_INTENT", 0.82, "cart_abandonment"),
    ("INVOICE_OVERDUE_15D", 0.80, "b2b_receivable"),
    ("INVOICE_OVERDUE_30D", 0.75, "b2b_receivable"),
    ("INVOICE_OVERDUE_60D", 0.50, "b2b_receivable"),
]

def generate_synthetic_batch(count: int = 150, seed: int = 42):
    random.seed(seed)
    events = []
    
    start_time = datetime.now(timezone.utc) - timedelta(days=7)

    for i in range(1, count + 1):
        name, email, phone, lang = random.choice(CUSTOMER_NAMES)
        reason_code, baseline_prob, category = random.choice(PAYMENT_FAILURE_REASONS)

        if category == "payment_failure":
            amount = round(random.uniform(500, 15000), 2)
            invoice_days = 0
            cart_items = None
        elif category == "cart_abandonment":
            amount = round(random.uniform(1200, 25000), 2)
            invoice_days = 0
            cart_items = random.choice(CART_ITEM_COMBOS)
        elif category == "failed_subscription":
            amount = round(random.uniform(999, 9999), 2)
            invoice_days = 0
            cart_items = None
        else: # b2b_receivable
            # Generate mix of standard and high-value (>50k for HITL testing)
            if random.random() < 0.25:
                amount = round(random.uniform(55000, 250000), 2)
            else:
                amount = round(random.uniform(15000, 48000), 2)
            invoice_days = int(reason_code.replace("INVOICE_OVERDUE_", "").replace("D", "")) if "INVOICE_OVERDUE" in reason_code else random.randint(15, 60)
            cart_items = None

        event_id = f"EVT_{category.upper()[:4]}_{1000 + i}"
        event_time = start_time + timedelta(hours=random.randint(0, 168))

        # Determine ground truth recoverable label for accuracy evaluation
        is_truly_recoverable = 1 if (baseline_prob > 0.65 and reason_code != "INSUFFICIENT_FUNDS_PERMANENT") else 0

        evt = {
            "event_id": event_id,
            "category": category,
            "amount": amount,
            "currency": "INR",
            "customer": {
                "customer_id": f"CUST_{i:03d}",
                "name": name,
                "email": email,
                "phone": phone,
                "preferred_language": lang,
                "ltv": round(amount * random.uniform(2, 10), 2),
                "trust_score": round(random.uniform(0.6, 0.98), 2)
            },
            "customer_id": f"CUST_{i:03d}",
            "payment_id": f"pay_{random.randint(10000000, 99999999)}" if category in ["payment_failure", "failed_subscription"] else None,
            "order_id": f"order_{random.randint(10000, 99999)}" if category in ["payment_failure", "cart_abandonment"] else None,
            "invoice_id": f"inv_{random.randint(1000, 9999)}" if category == "b2b_receivable" else None,
            "subscription_id": f"sub_{random.randint(100, 999)}" if category == "failed_subscription" else None,
            "failure_reason": reason_code,
            "cart_items": cart_items,
            "invoice_days_overdue": invoice_days,
            "attempts_count": random.choice([0, 0, 1]),
            "status": "detected",
            "created_at": event_time.isoformat(),
            "ground_truth_recoverable": is_truly_recoverable
        }
        events.append(evt)

    return events

def save_dataset_files(events, data_dir="data"):
    os.makedirs(os.path.join(data_dir, "raw"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "processed"), exist_ok=True)

    json_path = os.path.join(data_dir, "raw", "synthetic_batch.json")
    with open(json_path, "w") as f:
        json.dump(events, f, indent=2)

    df = pd.DataFrame(events)
    csv_path = os.path.join(data_dir, "raw", "synthetic_batch.csv")
    df.to_csv(csv_path, index=False)

    print(f"Dataset generated: {len(events)} events saved to {json_path} and {csv_path}")

if __name__ == "__main__":
    evts = generate_synthetic_batch(200)
    save_dataset_files(evts)
