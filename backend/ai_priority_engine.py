"""
NEX-CIV AI Complaint Prioritization & Emergency Override Engine
Implements the transparent, explainable municipal priority scoring algorithm:

Priority Score =
    0.25 × Severity
  + 0.20 × Safety Risk
  + 0.15 × Public Impact
  + 0.20 × SLA Urgency
  + 0.10 × Infrastructure Criticality
  + 0.10 × Recurrence and Evidence

Includes Statutory Emergency Override Engine:
- Exposed electrical wires
- Major road collapse / sinkhole
- Dangerous open manholes
- Contaminated drinking water
- Severe flooding threatening life
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

# Proposed Weights as per Government Systems Specification
PRIORITY_WEIGHTS = {
    "severity": 0.25,
    "safety_risk": 0.20,
    "public_impact": 0.15,
    "sla_urgency": 0.20,
    "infrastructure_criticality": 0.10,
    "recurrence_and_evidence": 0.10
}

EMERGENCY_OVERRIDE_CONDITIONS = [
    {
        "id": "EMG-01-ELEC",
        "name": "Live Electrical Wire / High Voltage Spark Hazard",
        "check": lambda c: c.get("defect_type") == "exposed_electrical_wires" or any(
            k in (c.get("title", "") + " " + c.get("description", "")).lower()
            for k in ["live wire", "exposed wire", "sparking", "కరెంట్ వైర్లు", "విద్యుత్ ప్రమాదం"]
        ),
        "reason": "Exposed high-voltage electrical wires create an immediate fatal electrocution hazard."
    },
    {
        "id": "EMG-02-ROAD",
        "name": "Major Road Collapse / Severe Highway Cave-In",
        "check": lambda c: c.get("defect_type") in ["road_cave_in", "sinkhole"] or any(
            k in (c.get("title", "") + " " + c.get("description", "")).lower()
            for k in ["cave-in", "sinkhole", "road collapsed", "bridge collapse", "రోడ్డు కుంగిపోయింది"]
        ),
        "reason": "Structural road collapse on transit corridor poses fatal vehicular accident risk."
    },
    {
        "id": "EMG-03-MANHOLE",
        "name": "Open Manhole without Cover in Public Way",
        "check": lambda c: c.get("defect_type") == "open_manhole" or any(
            k in (c.get("title", "") + " " + c.get("description", "")).lower()
            for k in ["open manhole", "manhole cover missing", "uncovered manhole", "మ్యాన్‌హోల్ మూత లేదు"]
        ),
        "reason": "Open manholes on public rights of way constitute an immediate life-safety peril."
    },
    {
        "id": "EMG-04-WATER",
        "name": "Contaminated Drinking Water / Sewage Seepage",
        "check": lambda c: c.get("defect_type") == "water_contamination" or any(
            k in (c.get("title", "") + " " + c.get("description", "")).lower()
            for k in ["contaminated water", "sewage in drinking water", "yellow water", "కలుషిత నీరు", "వాంతులు"]
        ),
        "reason": "Drinking water contamination threatens localized water-borne disease epidemic."
    },
    {
        "id": "EMG-05-FLOOD",
        "name": "Severe Flooding Submerging Inhabited Localities",
        "check": lambda c: any(
            k in (c.get("title", "") + " " + c.get("description", "")).lower()
            for k in ["flash flood", "water entering houses", "severe flooding", "ముంపు ప్రమాదం"]
        ),
        "reason": "Severe stormwater inundation threatening property and resident safety."
    }
]

def calculate_priority(
    severity_info: Dict[str, Any],
    sla_info: Dict[str, Any],
    complaint_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Computes explainable priority score, checks emergency overrides,
    and produces human-readable diagnostic reasoning.
    """
    # 1. Check Emergency Override
    is_emergency = False
    override_reason = None
    override_id = None

    for emg in EMERGENCY_OVERRIDE_CONDITIONS:
        try:
            if emg["check"](complaint_data):
                is_emergency = True
                override_id = emg["id"]
                override_reason = emg["reason"]
                break
        except Exception:
            pass

    # 2. Extract and Normalize Individual Components (0 to 100)
    # Component 1: Severity (from 1-4 scale)
    c_severity = float(severity_info.get("severity_score", 50.0))

    # Component 2: Safety Risk
    c_safety = float(severity_info.get("safety_risk", 30.0))

    # Component 3: Public Impact
    c_impact = float(severity_info.get("public_impact_score", 30.0))

    # Component 4: SLA Urgency
    c_sla = float(sla_info.get("sla_urgency_score", 20.0))

    # Component 5: Infrastructure Criticality
    c_infra = float(severity_info.get("infrastructure_criticality", 40.0))

    # Component 6: Recurrence & Evidence
    duplicate_count = complaint_data.get("duplicate_count", 0)
    upvotes = complaint_data.get("upvote_count", 1)
    has_photo = bool(complaint_data.get("image_url") or complaint_data.get("image_data"))
    c_recurrence = min(100.0, (duplicate_count * 20.0) + (upvotes * 5.0) + (30.0 if has_photo else 0.0))

    # 3. Calculate Weighted Priority Score
    weighted_score = (
        (c_severity * PRIORITY_WEIGHTS["severity"]) +
        (c_safety * PRIORITY_WEIGHTS["safety_risk"]) +
        (c_impact * PRIORITY_WEIGHTS["public_impact"]) +
        (c_sla * PRIORITY_WEIGHTS["sla_urgency"]) +
        (c_infra * PRIORITY_WEIGHTS["infrastructure_criticality"]) +
        (c_recurrence * PRIORITY_WEIGHTS["recurrence_and_evidence"])
    )
    weighted_score = round(max(0.0, min(100.0, weighted_score)), 2)

    # 4. Apply Emergency Override if triggered
    if is_emergency:
        final_score = max(95.0, weighted_score)
        priority_label = "Critical"
    else:
        final_score = weighted_score
        if final_score >= 80.0:
            priority_label = "Critical"
        elif final_score >= 60.0:
            priority_label = "High"
        elif final_score >= 40.0:
            priority_label = "Medium"
        else:
            priority_label = "Low"

    # 5. Build Explainability Reasons ("Why was this complaint assigned this priority?")
    explanation_points = []
    if is_emergency:
        explanation_points.append(f"EMERGENCY OVERRIDE ({override_id}): {override_reason}")

    if severity_info.get("severity_label") in ["Critical", "High"]:
        explanation_points.append(f"High Civic Severity ({severity_info.get('severity_label')}) detected from grievance description.")

    if severity_info.get("vulnerable_tag") and "Standard" not in severity_info.get("vulnerable_tag"):
        explanation_points.append(f"Located in sensitive corridor: {severity_info.get('vulnerable_tag')}.")

    if severity_info.get("estimated_citizens_affected", 0) > 200:
        explanation_points.append(f"Estimated {severity_info.get('estimated_citizens_affected')} citizens directly impacted.")

    if sla_info.get("is_overdue"):
        explanation_points.append(f"SLA breached by {sla_info.get('overdue_duration_hours')} hours. Escalation Level: {sla_info.get('escalation_level')}.")
    elif sla_info.get("remaining_hours") is not None and sla_info.get("remaining_hours") <= 12:
        explanation_points.append(f"Statutory deadline critical: Only {sla_info.get('remaining_hours')} hours remaining before SLA breach.")

    if duplicate_count > 0:
        explanation_points.append(f"Corroborated by {duplicate_count} linked duplicate reports from affected citizens.")

    if not explanation_points:
        explanation_points.append(f"Routine operational grievance. Standard {sla_info.get('prescribed_days', 3)}-day timeline applies.")

    return {
        "priority_score": final_score,
        "priority_label": priority_label,
        "is_emergency_override": is_emergency,
        "emergency_override_id": override_id,
        "emergency_override_reason": override_reason,
        "component_breakdown": {
            "severity": round(c_severity, 1),
            "safety_risk": round(c_safety, 1),
            "public_impact": round(c_impact, 1),
            "sla_urgency": round(c_sla, 1),
            "infrastructure_criticality": round(c_infra, 1),
            "recurrence_and_evidence": round(c_recurrence, 1)
        },
        "weights_applied": PRIORITY_WEIGHTS,
        "explanation": explanation_points,
        "explanation_summary": " | ".join(explanation_points)
    }
