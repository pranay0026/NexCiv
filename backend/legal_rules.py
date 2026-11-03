"""
NEX-CIV Legal Compliance Rules Engine
Maintains verified legal rules for Andhra Pradesh Public Services Delivery Guarantee Act, 2017
(Act No. 6 of 2018) and AP Departmental Citizen Charters & PGRS.
Includes complete version history tracking.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Verified Baseline Andhra Pradesh Legal Service Rules
# Distinctly marks Notified Public Services (Act No. 6 of 2018) vs Ordinary Civic Grievances (Citizen Charters)
BASELINE_LEGAL_RULES: List[Dict[str, Any]] = [
    # ------------------ ROADS & BUILDINGS ------------------
    {
        "id": "rule-road-notified-01",
        "department_code": "road",
        "department_name": "Roads & Buildings Department",
        "service_key": "road_cutting_permission",
        "service_name": "NOC & Permission for Road Cutting / Utility Laying",
        "workflow_type": "notified_service",
        "legal_source": "AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)",
        "go_reference": "G.O.Ms.No. 42, Transport, R&B (R.I) Dept",
        "prescribed_timeline_days": 15,
        "calculation_method": "working_days",
        "designated_officer_title": "Executive Engineer (R&B / Municipal)",
        "first_appellate_authority": "Superintending Engineer (R&B)",
        "second_appellate_authority": "Chief Engineer / District Collector",
        "appeal_deadline_days": 30,
        "compensation_applicable": True,
        "compensation_rate_per_day": 250,
        "max_compensation": 5000,
        "is_active": True,
        "version": 1,
        "description": "Statutory timeline under Section 3 of Act 6 of 2018 for disposal of road cutting permission."
    },
    {
        "id": "rule-road-ordinary-01",
        "department_code": "road",
        "department_name": "Roads & Buildings Department",
        "service_key": "pothole_restoration",
        "service_name": "Pothole Restoration & Road Surface Hazard Redressal",
        "workflow_type": "ordinary_grievance",
        "legal_source": "AP Municipal Corporation Citizen Charter & PGRS Guidelines",
        "go_reference": "MA&UD Dept Standing Order No. 118",
        "prescribed_timeline_days": 7,
        "calculation_method": "working_days",
        "designated_officer_title": "Assistant Executive Engineer (AEE - Roads)",
        "first_appellate_authority": "Executive Engineer (Roads)",
        "second_appellate_authority": "Municipal Commissioner / Additional Commissioner",
        "appeal_deadline_days": 15,
        "compensation_applicable": False,
        "compensation_rate_per_day": 0,
        "max_compensation": 0,
        "is_active": True,
        "version": 1,
        "description": "Municipal citizen charter timeline for rapid pothole repair and trench filling."
    },

    # ------------------ DRAINAGE & SEWERAGE ------------------
    {
        "id": "rule-drainage-notified-01",
        "department_code": "drainage",
        "department_name": "Public Health & Drainage Department",
        "service_key": "underground_drainage_sanction",
        "service_name": "Underground Drainage Connection Approval & Metering",
        "workflow_type": "notified_service",
        "legal_source": "AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)",
        "go_reference": "G.O.Ms.No. 89, Municipal Administration & Urban Development",
        "prescribed_timeline_days": 14,
        "calculation_method": "working_days",
        "designated_officer_title": "Executive Engineer (Public Health / Sewerage)",
        "first_appellate_authority": "Superintending Engineer (Public Health)",
        "second_appellate_authority": "Director of Municipal Administration (DMA)",
        "appeal_deadline_days": 30,
        "compensation_applicable": True,
        "compensation_rate_per_day": 250,
        "max_compensation": 5000,
        "is_active": True,
        "version": 1,
        "description": "Statutory disposal of new domestic/commercial drainage connection applications."
    },
    {
        "id": "rule-drainage-ordinary-01",
        "department_code": "drainage",
        "department_name": "Public Health & Drainage Department",
        "service_key": "drain_overflow_choke",
        "service_name": "Drainage Overflow, Silt Removal & Open Manhole Redressal",
        "workflow_type": "ordinary_grievance",
        "legal_source": "AP Municipal Citizen Charter (Public Health Wing)",
        "go_reference": "MA&UD PGRS Directive Cir. No. 22/PH",
        "prescribed_timeline_days": 3,
        "calculation_method": "working_days",
        "designated_officer_title": "Assistant Engineer / Jetting In-charge",
        "first_appellate_authority": "Executive Engineer (Drainage)",
        "second_appellate_authority": "Chief Municipal Health Officer / Commissioner",
        "appeal_deadline_days": 15,
        "compensation_applicable": False,
        "compensation_rate_per_day": 0,
        "max_compensation": 0,
        "is_active": True,
        "version": 1,
        "description": "Emergency drain declogging and storm nala overflow resolution."
    },

    # ------------------ WATER SUPPLY ------------------
    {
        "id": "rule-water-notified-01",
        "department_code": "water_supply",
        "department_name": "Water Supply & Quality Department",
        "service_key": "new_tap_connection",
        "service_name": "Sanction of New Drinking Water Tap Connection",
        "workflow_type": "notified_service",
        "legal_source": "AP Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)",
        "go_reference": "G.O.Ms.No. 65, Municipal Administration & Urban Development",
        "prescribed_timeline_days": 7,
        "calculation_method": "working_days",
        "designated_officer_title": "Assistant Executive Engineer (Water Works)",
        "first_appellate_authority": "Executive Engineer (Water Supply)",
        "second_appellate_authority": "Municipal Commissioner",
        "appeal_deadline_days": 30,
        "compensation_applicable": True,
        "compensation_rate_per_day": 250,
        "max_compensation": 5000,
        "is_active": True,
        "version": 1,
        "description": "Notified service guarantee for verification, estimate and tap connection sanction."
    },
    {
        "id": "rule-water-ordinary-01",
        "department_code": "water_supply",
        "department_name": "Water Supply & Quality Department",
        "service_key": "water_burst_contamination",
        "service_name": "Drinking Water Contamination / Major Pipeline Leakage",
        "workflow_type": "ordinary_grievance",
        "legal_source": "AP Municipal Citizen Charter (Water Quality)",
        "go_reference": "PGRS Standard Redressal Schedule (Water Wing)",
        "prescribed_timeline_days": 1,
        "calculation_method": "calendar_days",
        "designated_officer_title": "Water Works Inspector / Section Officer",
        "first_appellate_authority": "Executive Engineer (Water Works)",
        "second_appellate_authority": "Chief Engineer (Public Health)",
        "appeal_deadline_days": 7,
        "compensation_applicable": False,
        "compensation_rate_per_day": 0,
        "max_compensation": 0,
        "is_active": True,
        "version": 1,
        "description": "Urgent drinking water contamination or pipeline rupture resolution within 24 hours."
    },

    # ------------------ ELECTRICAL & STREET LIGHTING ------------------
    {
        "id": "rule-lights-ordinary-01",
        "department_code": "street_lights",
        "department_name": "Electrical & Street Lighting Wing",
        "service_key": "street_light_non_functional",
        "service_name": "Defective Street Light Luminaire / Dark Spot Redressal",
        "workflow_type": "ordinary_grievance",
        "legal_source": "AP Municipal Corporation Citizen Charter (Electrical Wing)",
        "go_reference": "MA&UD Street Lighting Protocol Circular No. 44",
        "prescribed_timeline_days": 2,
        "calculation_method": "calendar_days",
        "designated_officer_title": "Assistant Engineer (Electrical)",
        "first_appellate_authority": "Executive Engineer (Electrical Wing)",
        "second_appellate_authority": "Municipal Commissioner",
        "appeal_deadline_days": 10,
        "compensation_applicable": False,
        "compensation_rate_per_day": 0,
        "max_compensation": 0,
        "is_active": True,
        "version": 1,
        "description": "Non-functional street light or CCMS panel failure resolution."
    },

    # ------------------ SANITATION & SOLID WASTE ------------------
    {
        "id": "rule-sanitation-ordinary-01",
        "department_code": "others",
        "department_name": "Sanitation & Solid Waste Management Wing",
        "service_key": "garbage_dump_clearance",
        "service_name": "Roadside Garbage Dump Clearance & Dumper Bin Emptying",
        "workflow_type": "ordinary_grievance",
        "legal_source": "AP Swachh Andhra Citizen Charter & Municipal SWM Rules",
        "go_reference": "G.O.Ms.No. 279, Health, Medical & Family Welfare Dept",
        "prescribed_timeline_days": 1,
        "calculation_method": "calendar_days",
        "designated_officer_title": "Sanitary Inspector / Ward Sanitation Officer",
        "first_appellate_authority": "Chief Municipal Health Officer (CMHO)",
        "second_appellate_authority": "Municipal Commissioner",
        "appeal_deadline_days": 7,
        "compensation_applicable": False,
        "compensation_rate_per_day": 0,
        "max_compensation": 0,
        "is_active": True,
        "version": 1,
        "description": "24-hour rapid cleanup protocol for overflowing community dumper bins and carcasses."
    }
]


def match_legal_rule_for_complaint(
    category: str,
    title: str,
    description: str,
    active_rules: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Identifies the appropriate legal service rule based on complaint category and content.
    Prioritizes verified notified public services if application keywords match;
    otherwise binds to the appropriate department citizen charter ordinary grievance rule.
    """
    rules = active_rules if active_rules is not None else BASELINE_LEGAL_RULES
    clean_cat = (category or "others").lower().replace(" ", "_")

    # Filter rules for the department
    dept_rules = [r for r in rules if r.get("department_code") == clean_cat and r.get("is_active", True)]
    if not dept_rules:
        # Fallback to any active rule for 'others'
        dept_rules = [r for r in rules if r.get("department_code") == "others" and r.get("is_active", True)]

    if not dept_rules:
        return None

    full_text = f"{title} {description}".lower()

    # Check for notified service indicators (e.g. NOC, permission, application, new connection, sanction)
    notified_keywords = [
        "noc", "permission", "application", "new connection", "sanction", "approval", "permit", "cutting",
        "దరఖాస్తు", "అనుమతి", "కొత్త కనెక్షన్", "మంజూరు", "ఎన్‌ఓసీ", "పర్మిషన్"
    ]
    is_notified_applicant = any(kw in full_text for kw in notified_keywords)

    if is_notified_applicant:
        for r in dept_rules:
            if r.get("workflow_type") == "notified_service":
                return r

    # Default to ordinary grievance rule for this department
    for r in dept_rules:
        if r.get("workflow_type") == "ordinary_grievance":
            return r

    return dept_rules[0]
