import sqlite3
import json
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    DB_PATH = "/tmp/recoverai.db"
else:
    DB_PATH = os.getenv("DATABASE_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "recoverai.db"))

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Revenue risk events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_events (
        event_id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'INR',
        customer_id TEXT,
        customer_name TEXT,
        customer_phone TEXT,
        customer_email TEXT,
        customer_language TEXT,
        payment_id TEXT,
        order_id TEXT,
        invoice_id TEXT,
        subscription_id TEXT,
        failure_reason TEXT,
        invoice_days_overdue INTEGER DEFAULT 0,
        attempts_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'detected',
        created_at TEXT
    )
    """)

    # Recovery decisions / actions executed table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recovery_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT NOT NULL,
        action TEXT NOT NULL,
        reason TEXT,
        confidence REAL,
        status TEXT DEFAULT 'executed',
        requires_approval INTEGER DEFAULT 0,
        payload TEXT,
        applied_guardrails TEXT,
        money_recovered REAL DEFAULT 0.0,
        timestamp TEXT
    )
    """)

    # Promise to Pay table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS promise_to_pay (
        p2p_id TEXT PRIMARY KEY,
        event_id TEXT NOT NULL,
        customer_id TEXT,
        customer_name TEXT,
        amount_promised REAL NOT NULL,
        promised_date TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        notes TEXT,
        created_at TEXT
    )
    """)

    # Audit Trail table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT,
        category TEXT,
        event_type TEXT NOT NULL,
        actor TEXT DEFAULT 'AI_AGENT',
        details TEXT,
        money_recovered REAL DEFAULT 0.0,
        timestamp TEXT
    )
    """)

    # Human-In-The-Loop Approval Queue
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hitl_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        amount REAL NOT NULL,
        proposed_action TEXT NOT NULL,
        reason TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_risk_event(event_dict: Dict[str, Any]):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cust = event_dict.get("customer") or {}
    cust_id = event_dict.get("customer_id") or cust.get("customer_id", "CUST_UNKNOWN")
    cust_name = cust.get("name", "Valued Customer")
    cust_phone = cust.get("phone", "+919876543210")
    cust_email = cust.get("email", "customer@example.com")
    cust_lang = cust.get("preferred_language", "Hinglish")

    cursor.execute("""
    INSERT OR REPLACE INTO risk_events (
        event_id, category, amount, currency, customer_id, customer_name, customer_phone,
        customer_email, customer_language, payment_id, order_id, invoice_id, subscription_id,
        failure_reason, invoice_days_overdue, attempts_count, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_dict["event_id"],
        event_dict["category"],
        event_dict["amount"],
        event_dict.get("currency", "INR"),
        cust_id,
        cust_name,
        cust_phone,
        cust_email,
        cust_lang,
        event_dict.get("payment_id"),
        event_dict.get("order_id"),
        event_dict.get("invoice_id"),
        event_dict.get("subscription_id"),
        event_dict.get("failure_reason"),
        event_dict.get("invoice_days_overdue", 0),
        event_dict.get("attempts_count", 0),
        event_dict.get("status", "detected"),
        event_dict.get("created_at", datetime.now(timezone.utc).isoformat())
    ))
    conn.commit()
    conn.close()

def update_event_status(event_id: str, status: str, attempts_count: Optional[int] = None):
    conn = get_connection()
    cursor = conn.cursor()
    if attempts_count is not None:
        cursor.execute("UPDATE risk_events SET status=?, attempts_count=? WHERE event_id=?", (status, attempts_count, event_id))
    else:
        cursor.execute("UPDATE risk_events SET status=? WHERE event_id=?", (status, event_id))
    conn.commit()
    conn.close()

def save_recovery_action(action_dict: Dict[str, Any]):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO recovery_actions (
        event_id, action, reason, confidence, status, requires_approval, payload, applied_guardrails, money_recovered, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        action_dict["event_id"],
        action_dict["action"],
        action_dict.get("reason", ""),
        action_dict.get("confidence", 1.0),
        action_dict.get("status", "executed"),
        1 if action_dict.get("requires_approval") else 0,
        json.dumps(action_dict.get("payload", {})),
        json.dumps(action_dict.get("applied_guardrails", [])),
        action_dict.get("money_recovered", 0.0),
        action_dict.get("timestamp", datetime.now(timezone.utc).isoformat())
    ))
    conn.commit()
    conn.close()

def log_audit(event_id: str, category: str, event_type: str, details: Dict[str, Any], actor: str = "AI_AGENT", money_recovered: float = 0.0):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO audit_logs (event_id, category, event_type, actor, details, money_recovered, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        category,
        event_type,
        actor,
        json.dumps(details),
        money_recovered,
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()

def add_to_hitl_queue(event_id: str, amount: float, proposed_action: str, reason: str):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO hitl_queue (event_id, amount, proposed_action, reason, status, created_at)
    VALUES (?, ?, ?, ?, 'pending', ?)
    """, (
        event_id, amount, proposed_action, reason, datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()

def get_hitl_queue():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hitl_queue WHERE status='pending' ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def resolve_hitl_item(event_id: str, approved: bool):
    conn = get_connection()
    cursor = conn.cursor()
    new_status = "approved" if approved else "rejected"
    cursor.execute("UPDATE hitl_queue SET status=? WHERE event_id=?", (new_status, event_id))
    conn.commit()
    conn.close()

def save_p2p(p2p_dict: Dict[str, Any]):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO promise_to_pay (p2p_id, event_id, customer_id, customer_name, amount_promised, promised_date, status, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p2p_dict["p2p_id"],
        p2p_dict["event_id"],
        p2p_dict.get("customer_id", ""),
        p2p_dict.get("customer_name", ""),
        p2p_dict["amount_promised"],
        p2p_dict["promised_date"],
        p2p_dict.get("status", "active"),
        p2p_dict.get("notes", ""),
        p2p_dict.get("created_at", datetime.now(timezone.utc).isoformat())
    ))
    conn.commit()
    conn.close()

def get_all_p2p():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM promise_to_pay ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_audit_logs(limit: int = 100):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    res = []
    for r in rows:
        item = dict(r)
        try:
            item["details"] = json.loads(item["details"])
        except Exception:
            pass
        res.append(item)
    return res

def get_summary_stats():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM risk_events")
    total_events, total_at_risk = cursor.fetchone()
    total_events = total_events or 0
    total_at_risk = total_at_risk or 0.0

    cursor.execute("SELECT COUNT(*), SUM(amount) FROM risk_events WHERE status='recovered'")
    recovered_events, total_recovered = cursor.fetchone()
    recovered_events = recovered_events or 0
    total_recovered = total_recovered or 0.0

    cursor.execute("SELECT COUNT(*) FROM hitl_queue WHERE status='pending'")
    hitl_pending = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM promise_to_pay WHERE status='active'")
    active_p2p = cursor.fetchone()[0] or 0

    conn.close()
    return {
        "total_events": total_events,
        "total_at_risk": total_at_risk,
        "recovered_events": recovered_events,
        "total_recovered": total_recovered,
        "recovery_rate": (recovered_events / total_events * 100) if total_events > 0 else 0.0,
        "hitl_pending": hitl_pending,
        "active_p2p": active_p2p
    }

def get_category_breakdown_db():
    """
    Returns actual category breakdown counts & recovered sums directly from SQLite database.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT category, COUNT(*) as count, SUM(amount) as at_risk,
           SUM(CASE WHEN status='recovered' THEN amount ELSE 0 END) as recovered
    FROM risk_events
    GROUP BY category
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_failure_reason_counts_db():
    """
    Returns actual failure reason distribution directly from SQLite risk_events table.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT failure_reason, COUNT(*) as count
    FROM risk_events
    GROUP BY failure_reason
    ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize database on import
init_db()
