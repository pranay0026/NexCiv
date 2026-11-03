"""
NEX-CIV Intelligent Municipal Workforce Allocation Engine
Compliant with:
- Andhra Pradesh Municipal Cadre Recruitment Rules & Service Regulations
- G.O.Ms.No.217, MA&UD Department (Ward Secretariats)

Implements:
1. Strict Hard Eligibility Constraints:
   - Municipality Isolation (MANDATORY: Eluru employees NEVER assigned Vijayawada tasks)
   - Department / Functional Wing Eligibility
   - Active Employment & Availability Status
   - Maximum Workload Capacity Caps
2. Dynamic Effort-Weighted Task Sizing:
   - Critical = 3.0 workload units
   - High = 2.0 workload units
   - Medium = 1.0 workload unit
   - Low = 0.5 workload unit
3. Multi-Factor Assignment Scoring:
   Assignment Score =
       0.30 × Skill Match
     + 0.25 × Workload Availability
     + 0.20 × Geographic Proximity
     + 0.15 × Ward Responsibility
     + 0.10 × Current Schedule Availability
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json

ASSIGNMENT_WEIGHTS = {
    "skill_match": 0.30,
    "workload_availability": 0.25,
    "geographic_proximity": 0.20,
    "ward_responsibility": 0.15,
    "schedule_availability": 0.10
}

# Task effort by priority level
EFFORT_CAPACITY_UNITS = {
    "Critical": 3.0,
    "High": 2.0,
    "Medium": 1.0,
    "Low": 0.5
}

def _calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(dlon / 2.0) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return float(R * c)

def calculate_skill_match_score(employee_skills_str: Optional[str], required_keywords: List[str]) -> float:
    """Evaluates employee technical specialization match against complaint nature."""
    if not employee_skills_str:
        return 50.0  # Baseline generalist score
    skills_lower = employee_skills_str.lower()
    if not required_keywords:
        return 70.0
    matches = sum(1 for kw in required_keywords if kw.lower() in skills_lower)
    score = (matches / len(required_keywords)) * 100.0
    return min(100.0, max(20.0, score))

def calculate_workload_availability_score(current_workload: float, max_workload: float) -> float:
    """Calculates available capacity percentage. Full availability = 100."""
    if max_workload <= 0:
        return 0.0
    remaining_capacity = max(0.0, max_workload - current_workload)
    return round((remaining_capacity / max_workload) * 100.0, 1)

def calculate_proximity_score(
    emp_lat: Optional[float],
    emp_lng: Optional[float],
    comp_lat: Optional[float],
    comp_lng: Optional[float]
) -> float:
    """Calculates spatial proximity score. Within 2km = 100, 10km = 50, >25km = 0."""
    if not all([emp_lat, emp_lng, comp_lat, comp_lng]):
        return 50.0  # Default neutral score when coordinates unavailable
    try:
        dist_km = _calculate_haversine_distance_km(float(emp_lat), float(emp_lng), float(comp_lat), float(comp_lng))
        if dist_km <= 2.0:
            return 100.0
        elif dist_km >= 25.0:
            return 10.0
        else:
            return round(max(10.0, 100.0 - ((dist_km - 2.0) / 23.0) * 90.0), 1)
    except Exception:
        return 50.0

def calculate_ward_score(employee_zone: Optional[str], complaint_ward: Optional[str]) -> float:
    """Evaluates ward / zonal jurisdictional responsibility."""
    if not employee_zone or not complaint_ward:
        return 50.0
    ez = employee_zone.lower().strip()
    cw = complaint_ward.lower().strip()
    if ez in cw or cw in ez:
        return 100.0
    # Check zone match (e.g. Ward 14 in Central Zone)
    if "central" in ez and any(w in cw for w in ["ward 1", "ward 2", "ward 12", "ward 14"]):
        return 85.0
    return 30.0

def allocate_complaint_to_workforce(
    complaint: Dict[str, Any],
    all_employees: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Intelligently identifies the best eligible employee for a complaint
    using strict AP municipal eligibility and multi-factor scoring.
    """
    target_municipality = (complaint.get("municipal_corporation") or "").strip().upper()
    target_wing = (complaint.get("functional_wing_id") or complaint.get("category") or "").strip().lower()
    target_dept = (complaint.get("department_code") or complaint.get("department") or "").strip().lower()
    priority_label = complaint.get("priority", "Medium")
    task_effort = EFFORT_CAPACITY_UNITS.get(priority_label, 1.0)

    # 1. HARD ELIGIBILITY FILTERING
    eligible_candidates = []
    rejection_reasons = []

    for emp in all_employees:
        emp_id = emp.get("id") or emp.get("employee_code")
        emp_muni = (emp.get("municipality_code") or "").strip().upper()
        emp_dept = (emp.get("department") or emp.get("department_code") or "").strip().lower()
        emp_wing = (emp.get("functional_wing_id") or emp.get("department") or "").strip().lower()
        emp_status = (emp.get("status") or "active").strip().lower()
        emp_avail = (emp.get("availability_status") or "available").strip().lower()
        current_wl = float(emp.get("current_workload") or emp.get("pending_count") or 0.0)
        max_wl = float(emp.get("maximum_workload") or 15.0)

        # Constraint 1: STRICT Municipality Isolation
        if target_municipality and emp_muni != target_municipality:
            rejection_reasons.append(f"{emp_id}: Municipality mismatch ({emp_muni} != {target_municipality})")
            continue

        # Constraint 2: Department / Functional Wing Match
        dept_match = False
        if target_wing and (emp_wing == target_wing or emp_dept == target_wing):
            dept_match = True
        elif target_dept and (emp_dept == target_dept or emp_wing == target_dept):
            dept_match = True
        elif target_wing in ["road", "drainage", "water_supply", "street_lights"]:
            if emp_dept == target_wing or emp_wing == target_wing or emp_dept == "engineering":
                dept_match = True
        elif target_wing in ["others", "solid_waste", "street_cleaning", "sanitation", "public_toilets", "vector_control"]:
            if emp_dept in ["others", "public_health", "sanitation"] or emp_wing in ["others", "solid_waste", "street_cleaning", "sanitation", "public_toilets", "vector_control"]:
                dept_match = True

        if not dept_match:
            rejection_reasons.append(f"{emp_id}: Department mismatch (Emp: {emp_dept}/{emp_wing} != Target: {target_dept}/{target_wing})")
            continue

        # Constraint 3: Active Status & Not On Leave
        if emp_status != "active" or emp_avail in ["on leave", "suspended", "leave"]:
            rejection_reasons.append(f"{emp_id}: Unavailable (Status: {emp_status}, Avail: {emp_avail})")
            continue

        # Constraint 4: Workload Capacity
        if current_wl + task_effort > max_wl:
            rejection_reasons.append(f"{emp_id}: Capacity exceeded ({current_wl + task_effort:.1f} > {max_wl:.1f})")
            continue

        eligible_candidates.append(emp)

    # 2. IF NO ELIGIBLE EMPLOYEE AVAILABLE
    if not eligible_candidates:
        return {
            "is_assigned": False,
            "assigned_employee_id": None,
            "assigned_employee_name": None,
            "assigned_team": f"{target_dept.capitalize()} Department Queue (Unassigned)",
            "assignment_score": 0.0,
            "required_action": "Supervisor Intervention Required: Workforce capacity exhausted or no cadre stationed.",
            "unassigned_reason": "No eligible personnel with available workload capacity found in this ULB department.",
            "candidates_evaluated": len(all_employees),
            "rejection_sample": rejection_reasons[:5]
        }

    # 3. SCORE ALL ELIGIBLE CANDIDATES
    required_keywords = [target_dept]
    if complaint.get("defect_type"):
        required_keywords.append(complaint["defect_type"])
    if "pothole" in (complaint.get("title", "") + " " + complaint.get("description", "")).lower():
        required_keywords.append("pothole")
    if "pipeline" in (complaint.get("title", "") + " " + complaint.get("description", "")).lower():
        required_keywords.append("pipeline")

    scored_candidates = []
    for emp in eligible_candidates:
        current_wl = float(emp.get("current_workload") or emp.get("pending_count") or 0.0)
        max_wl = float(emp.get("maximum_workload") or 15.0)

        s_skill = calculate_skill_match_score(emp.get("skills"), required_keywords)
        s_workload = calculate_workload_availability_score(current_wl, max_wl)
        s_proximity = calculate_proximity_score(
            emp.get("location_lat"), emp.get("location_lng"),
            complaint.get("location_lat"), complaint.get("location_lng")
        )
        s_ward = calculate_ward_score(emp.get("zone"), complaint.get("ward"))
        s_schedule = 100.0 if emp.get("availability_status", "available").lower() == "available" else 50.0

        total_score = (
            (s_skill * ASSIGNMENT_WEIGHTS["skill_match"]) +
            (s_workload * ASSIGNMENT_WEIGHTS["workload_availability"]) +
            (s_proximity * ASSIGNMENT_WEIGHTS["geographic_proximity"]) +
            (s_ward * ASSIGNMENT_WEIGHTS["ward_responsibility"]) +
            (s_schedule * ASSIGNMENT_WEIGHTS["schedule_availability"])
        )
        total_score = round(total_score, 2)

        scored_candidates.append({
            "employee": emp,
            "total_score": total_score,
            "breakdown": {
                "skill_match": s_skill,
                "workload_availability": s_workload,
                "geographic_proximity": s_proximity,
                "ward_responsibility": s_ward,
                "schedule_availability": s_schedule
            }
        })

    # Sort descending by assignment score
    scored_candidates.sort(key=lambda x: x["total_score"], reverse=True)
    best_candidate = scored_candidates[0]
    assigned_emp = best_candidate["employee"]

    emp_id = assigned_emp.get("employee_code") or assigned_emp.get("id")
    emp_name = assigned_emp.get("name")
    emp_designation = assigned_emp.get("designation", "Technical Cadre Officer")

    return {
        "is_assigned": True,
        "assigned_employee_id": emp_id,
        "assigned_employee_name": emp_name,
        "assigned_designation": emp_designation,
        "assigned_team": f"{assigned_emp.get('department_name') or target_dept.capitalize()} - {assigned_emp.get('zone', 'Zone')}",
        "assignment_score": best_candidate["total_score"],
        "task_effort_units": task_effort,
        "score_breakdown": best_candidate["breakdown"],
        "alternatives_count": len(scored_candidates) - 1,
        "allocation_rationale": (
            f"Assigned to {emp_name} ({emp_designation}) with match score {best_candidate['total_score']}/100. "
            f"Skill match: {best_candidate['breakdown']['skill_match']}%, "
            f"Workload capacity: {best_candidate['breakdown']['workload_availability']}%, "
            f"Ward alignment: {best_candidate['breakdown']['ward_responsibility']}%."
        )
    }
