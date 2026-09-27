from datetime import datetime, timedelta
from typing import Dict, Any

BANK_UPTIME_MATRIX = {
    "HDFC": {"peak_uptime": "08:00 - 20:00", "maintenance_window": "00:00 - 02:30", "success_rate": 0.96},
    "SBI": {"peak_uptime": "09:00 - 18:00", "maintenance_window": "01:00 - 04:00", "success_rate": 0.91},
    "ICICI": {"peak_uptime": "08:00 - 21:00", "maintenance_window": "02:00 - 03:30", "success_rate": 0.97},
    "AXIS": {"peak_uptime": "08:30 - 20:30", "maintenance_window": "01:30 - 03:00", "success_rate": 0.94},
    "DEFAULT": {"peak_uptime": "09:00 - 19:00", "maintenance_window": "01:00 - 03:00", "success_rate": 0.90}
}

SALARY_DAYS = {1, 2, 3, 4, 5, 7, 30, 31}

def calculate_optimal_retry_schedule(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes optimal e-mandate / payment retry timing based on salary cycle, bank maintenance windows, and peak UPI liquidity.
    """
    now = datetime.now()
    bank_name = event.get("bank_name", "HDFC").upper()
    bank_info = BANK_UPTIME_MATRIX.get(bank_name, BANK_UPTIME_MATRIX["DEFAULT"])

    current_day = now.day
    is_salary_week = current_day in SALARY_DAYS or (current_day + 1) in SALARY_DAYS

    # Base target scheduling
    if is_salary_week:
        target_date = now + timedelta(days=1 if now.hour >= 18 else 0)
        target_time = target_date.replace(hour=8, minute=30, second=0, microsecond=0)
        reason = f"High-confidence Salary Liquidity Slot ({target_time.strftime('%b %d at 08:30 AM')}). Expected account balance peak."
        confidence = 0.96
    else:
        # Avoid bank maintenance windows (usually 00:00 - 04:00)
        target_time = now + timedelta(minutes=45)
        if 0 <= target_time.hour < 5:
            # Shift to morning peak uptime slot (8:45 AM)
            target_time = target_time.replace(hour=8, minute=45, second=0, microsecond=0)
            reason = f"Shifted from bank maintenance window ({bank_info['maintenance_window']}) to peak morning uptime slot ({target_time.strftime('%I:%M %p')})."
            confidence = bank_info["success_rate"]
        else:
            reason = f"Transient gateway recovery slot ({target_time.strftime('%H:%M')}). Bank historical uptime: {int(bank_info['success_rate']*100)}%."
            confidence = bank_info["success_rate"]

    return {
        "event_id": event.get("event_id"),
        "bank_name": bank_name,
        "recommended_retry_time": target_time.isoformat(),
        "display_slot": target_time.strftime("%d %b %Y, %I:%M %p"),
        "salary_cycle_match": is_salary_week,
        "expected_success_probability": round(confidence, 2),
        "reasoning": reason,
        "bank_maintenance_window": bank_info["maintenance_window"],
        "peak_uptime_window": bank_info["peak_uptime"],
        "upi_success_index": "HIGH" if target_time.hour in range(8, 21) else "MEDIUM"
    }
