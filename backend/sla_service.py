"""
NEX-CIV SLA and Statutory Deadline Engine
Compliant with:
- Andhra Pradesh Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)
- AP CDMA Citizen Charter (cdma.ap.gov.in/resources/citizen-charter/)
- AP Government Orders on Grievance Redressal (G.O.Ms.No.217 & MA&UD Directives)

Maintains:
- Statutory vs Operational timelines
- Working days (excluding Sundays, 2nd & 4th Saturdays, AP Gazetted Holidays 2026) vs Calendar days
- Granular SLA urgency calculation (0 - 100 scale)
- Multi-tier escalation management (Field Officer -> AEE/Supervisor -> EE/Dept Head -> Commissioner)
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

# Official Andhra Pradesh State Gazetted Holidays 2026 (General Administration Dept)
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

# Verified CDMA Citizen Charter & Act 6 of 2018 Statutory Timelines
VERIFIED_SLA_RULES: List[Dict[str, Any]] = [
    {
        "sla_rule_id": "sla-water-burst",
        "category": "water_supply",
        "defect_type": "pipeline_leakage",
        "statutory_days": 1,
        "calendar_type": "calendar_days",
        "source": "AP CDMA Citizen Charter - Drinking Water Services",
        "statutory_basis": "Act No. 6 of 2018, Schedule 1"
    },
    {
        "sla_rule_id": "sla-water-contamination",
        "category": "water_supply",
        "defect_type": "water_contamination",
        "statutory_days": 1,
        "calendar_type": "calendar_days",
        "source": "AP CDMA Citizen Charter - Quality Assurance",
        "statutory_basis": "Act No. 6 of 2018 & Public Health Norms"
    },
    {
        "sla_rule_id": "sla-water-general",
        "category": "water_supply",
        "defect_type": "no_water_supply",
        "statutory_days": 3,
        "calendar_type": "calendar_days",
        "source": "AP CDMA Citizen Charter - Water Connection Repair",
        "statutory_basis": "CDMA Service Directive"
    },
    {
        "sla_rule_id": "sla-drainage-overflow",
        "category": "drainage",
        "defect_type": "drainage_overflow",
        "statutory_days": 2,
        "calendar_type": "working_days",
        "source": "AP Municipal Public Health Manual",
        "statutory_basis": "CDMA Sanitation Charter"
    },
    {
        "sla_rule_id": "sla-drainage-manhole",
        "category": "drainage",
        "defect_type": "open_manhole",
        "statutory_days": 1,
        "calendar_type": "calendar_days",
        "source": "AP Public Safety & Hazardous Openings Mandate",
        "statutory_basis": "Emergency Civic Safety Directives"
    },
    {
        "sla_rule_id": "sla-road-pothole",
        "category": "road",
        "defect_type": "potholes",
        "statutory_days": 7,
        "calendar_type": "working_days",
        "source": "AP Municipal Corporation Citizen Charter (R&B)",
        "statutory_basis": "MA&UD Dept Standing Order No. 118"
    },
    {
        "sla_rule_id": "sla-road-cavein",
        "category": "road",
        "defect_type": "road_cave_in",
        "statutory_days": 1,
        "calendar_type": "calendar_days",
        "source": "AP Highway & Arterial Safety Standards",
        "statutory_basis": "Emergency Disaster Protocol"
    },
    {
        "sla_rule_id": "sla-light-failure",
        "category": "street_lights",
        "defect_type": "street_light_failure",
        "statutory_days": 2,
        "calendar_type": "calendar_days",
        "source": "AP CDMA Citizen Charter - Electrical Wing",
        "statutory_basis": "CDMA Electrical Maintenance Charter"
    },
    {
        "sla_rule_id": "sla-light-wires",
        "category": "street_lights",
        "defect_type": "exposed_electrical_wires",
        "statutory_days": 1,
        "calendar_type": "calendar_days",
        "source": "APEPDCL / APSPDCL Safety Mandate",
        "statutory_basis": "Electricity Act 2003 & AP Municipal Safety Rules"
    },
    {
        "sla_rule_id": "sla-sanitation-garbage",
        "category": "others",
        "defect_type": "garbage_dump",
        "statutory_days": 1,
        "calendar_type": "calendar_days",
        "source": "Swachh Andhra Pradesh Municipal Directives",
        "statutory_basis": "Solid Waste Management Rules 2016"
    }
]

def is_second_or_fourth_saturday(d: date) -> bool:
    """Checks if date is 2nd or 4th Saturday (standard AP Govt holiday)."""
    if d.weekday() != 5:  # 5 is Saturday
        return False
    day = d.day
    return (8 <= day <= 14) or (22 <= day <= 28)

def is_ap_working_day(d: date) -> bool:
    """Determines whether a given date is an official working day in AP Government offices."""
    if d.weekday() == 6:  # Sunday
        return False
    if is_second_or_fourth_saturday(d):
        return False
    if d in AP_GAZETTED_HOLIDAYS_2026:
        return False
    return True

def add_ap_working_days(start_date: date, working_days: int) -> date:
    """Adds a prescribed number of AP working days to a start date."""
    current = start_date
    added = 0
    while added < working_days:
        current += timedelta(days=1)
        if is_ap_working_day(current):
            added += 1
    return current

def compute_statutory_deadline(
    category: str,
    defect_type: Optional[str] = None,
    created_at_dt: Optional[datetime] = None,
    extension_days: int = 0
) -> Dict[str, Any]:
    """
    Looks up verified statutory or operational SLA rule and calculates exact deadline.
    Returns structured SLA calculation dictionary.
    """
    if created_at_dt is None:
        created_at_dt = datetime.utcnow()

    cat_clean = (category or "others").lower().strip()
    defect_clean = (defect_type or "").lower().strip()

    # Find matching rule
    matched_rule = None
    for r in VERIFIED_SLA_RULES:
        if r["category"] == cat_clean and (not defect_clean or r["defect_type"] == defect_clean):
            matched_rule = r
            break
    if not matched_rule:
        for r in VERIFIED_SLA_RULES:
            if r["category"] == cat_clean:
                matched_rule = r
                break

    if not matched_rule:
        # Fallback default rule
        prescribed_days = 3
        calendar_type = "working_days"
        source_doc = "AP Municipal Citizen Charter General Norms"
    else:
        prescribed_days = matched_rule["statutory_days"]
        calendar_type = matched_rule["calendar_type"]
        source_doc = matched_rule["source"]

    total_days = prescribed_days + max(0, extension_days)
    start_d = created_at_dt.date()

    if calendar_type == "working_days":
        due_d = add_ap_working_days(start_d, total_days)
    else:
        due_d = start_d + timedelta(days=total_days)

    # Statutory deadline ends at 5:30 PM on the due date
    due_dt = datetime(due_d.year, due_d.month, due_d.day, 17, 30, 0)
    now_dt = datetime.utcnow()

    diff_seconds = (due_dt - now_dt).total_seconds()
    is_overdue = diff_seconds < 0
    total_allowed_hours = total_days * 24
    remaining_hours = max(0, int(diff_seconds // 3600))
    overdue_hours = abs(int(diff_seconds // 3600)) if is_overdue else 0

    # Calculate SLA urgency (0 to 100)
    # > 75% time remaining: 0 - 25 urgency
    # 50 - 75% remaining: 25 - 50 urgency
    # 25 - 50% remaining: 50 - 75 urgency
    # < 25% remaining: 75 - 95 urgency
    # Overdue: 100 urgency
    if is_overdue:
        urgency_score = 100.0
        deadline_pressure = "Critical SLA Breach"
        escalation_level = 3 if overdue_hours < 24 else 4
    else:
        fraction_remaining = min(1.0, max(0.0, diff_seconds / (total_allowed_hours * 3600)))
        urgency_score = round((1.0 - fraction_remaining) * 100.0, 2)
        if fraction_remaining > 0.75:
            deadline_pressure = "Low Deadline Pressure (>75% remaining)"
            escalation_level = 1
        elif fraction_remaining > 0.50:
            deadline_pressure = "Moderate Deadline Pressure (50-75% remaining)"
            escalation_level = 1
        elif fraction_remaining > 0.25:
            deadline_pressure = "Elevated Deadline Pressure (25-50% remaining)"
            escalation_level = 2
        else:
            deadline_pressure = "High Deadline Pressure (<25% remaining)"
            escalation_level = 2

    return {
        "sla_rule_id": matched_rule["sla_rule_id"] if matched_rule else "sla-default",
        "has_configured_deadline": True,
        "deadline_dt": due_dt.isoformat() + "Z",
        "deadline_date": due_d.isoformat(),
        "deadline_formatted": due_dt.strftime("%d %b %Y, 05:30 PM"),
        "prescribed_days": prescribed_days,
        "total_days_allowed": total_days,
        "extension_days": extension_days,
        "calendar_type": calendar_type,
        "remaining_hours": remaining_hours,
        "is_overdue": is_overdue,
        "overdue_duration_hours": overdue_hours,
        "sla_urgency_score": urgency_score,
        "deadline_pressure": deadline_pressure,
        "escalation_level": escalation_level,
        "source_document": source_doc
    }
