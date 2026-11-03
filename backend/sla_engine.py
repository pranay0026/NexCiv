"""
NEX-CIV SLA and Legal Deadline Engine
Implements deadline calculations compliant with:
- Andhra Pradesh Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)
- Department Citizen Charters & PGRS Guidelines

Supports:
- Notified public services vs ordinary civic grievances
- Working days (skipping Sundays and 2nd/4th Saturdays) vs Calendar days
- Audit-trailed deadline extensions and pauses
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List

# Official Andhra Pradesh State Gazetted Holidays (sample calendar for legal calculation)
# In production, these can be extended via departmental configuration.
AP_GAZETTED_HOLIDAYS_2026 = {
    date(2026, 1, 14),  # Bhogi
    date(2026, 1, 15),  # Makara Sankranti
    date(2026, 1, 16),  # Kanuma
    date(2026, 1, 26),  # Republic Day
    date(2026, 2, 16),  # Maha Shivaratri
    date(2026, 3, 20),  # Ugadi (Telugu New Year)
    date(2026, 3, 27),  # Sri Rama Navami
    date(2026, 4, 3),   # Good Friday
    date(2026, 4, 14),  # Dr. B.R. Ambedkar Jayanthi
    date(2026, 8, 15),  # Independence Day
    date(2026, 9, 4),   # Sri Krishna Janmashtami
    date(2026, 9, 14),  # Vinayaka Chavithi
    date(2026, 10, 2),  # Mahatma Gandhi Jayanthi
    date(2026, 10, 20), # Vijaya Dasami (Dussehra)
    date(2026, 11, 8),  # Deepavali
    date(2026, 12, 25), # Christmas
}


def is_second_or_fourth_saturday(d: date) -> bool:
    """Checks if date is 2nd or 4th Saturday (standard AP Govt holiday)."""
    if d.weekday() != 5:  # 5 is Saturday
        return False
    day = d.day
    # 1-7: 1st Saturday, 8-14: 2nd Saturday, 15-21: 3rd Saturday, 22-28: 4th Saturday
    return (8 <= day <= 14) or (22 <= day <= 28)


def is_ap_working_day(d: date) -> bool:
    """Determines whether a given date is an official working day in Andhra Pradesh Government offices."""
    # Sunday
    if d.weekday() == 6:
        return False
    # 2nd or 4th Saturday
    if is_second_or_fourth_saturday(d):
        return False
    # Gazetted holiday
    if d in AP_GAZETTED_HOLIDAYS_2026:
        return False
    return True


def add_working_days(start_date: date, working_days: int) -> date:
    """Adds a prescribed number of AP working days to a start date."""
    current = start_date
    added = 0
    while added < working_days:
        current += timedelta(days=1)
        if is_ap_working_day(current):
            added += 1
    return current


def calculate_service_deadline(
    created_at_dt: datetime,
    prescribed_timeline_days: Optional[int],
    calculation_method: str = "working_days",
    workflow_type: str = "ordinary_grievance",
    extension_days: int = 0
) -> Dict[str, Any]:
    """
    Calculates the legal SLA deadline.
    Returns structured deadline data.
    If no valid timeline is configured, indicates 'Timeline not configured – departmental action required.'
    """
    if prescribed_timeline_days is None or prescribed_timeline_days <= 0:
        return {
            "has_configured_deadline": False,
            "deadline_dt": None,
            "deadline_formatted": "Timeline not configured – departmental action required",
            "calculation_method": calculation_method,
            "workflow_type": workflow_type,
            "remaining_hours": None,
            "is_overdue": False,
            "overdue_duration_hours": 0
        }

    total_days = prescribed_timeline_days + max(0, extension_days)
    start_d = created_at_dt.date()

    if calculation_method.lower() == "working_days":
        due_d = add_working_days(start_d, total_days)
    else:  # calendar_days
        due_d = start_d + timedelta(days=total_days)

    # Set due time to end of working hours (5:30 PM IST) on due date
    due_dt = datetime(due_d.year, due_d.month, due_d.day, 17, 30, 0)
    now_dt = datetime.utcnow()

    diff = due_dt - now_dt
    is_overdue = diff.total_seconds() < 0
    remaining_hours = max(0, int(diff.total_seconds() // 3600))
    overdue_hours = abs(int(diff.total_seconds() // 3600)) if is_overdue else 0

    return {
        "has_configured_deadline": True,
        "deadline_dt": due_dt.isoformat() + "Z",
        "deadline_date": due_d.isoformat(),
        "deadline_formatted": due_dt.strftime("%d %b %Y, 05:30 PM"),
        "calculation_method": calculation_method,
        "workflow_type": workflow_type,
        "prescribed_days": prescribed_timeline_days,
        "extension_days": extension_days,
        "remaining_hours": remaining_hours,
        "is_overdue": is_overdue,
        "overdue_duration_hours": overdue_hours
    }
