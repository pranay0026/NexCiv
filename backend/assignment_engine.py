"""
Assignment Engine – employee work‑order allocation

Takes a complaint (already enriched with priority, department, municipality, zone, etc.) and returns the best employee_id.
The algorithm follows the weighted formula from the spec:
    Skill Match (30%)
    Workload Availability (25%)
    Geographic Proximity (20%)
    Ward Responsibility (15%)
    Current Schedule Availability (10%)
All scores are normalized 0‑100.
"""
import math
from typing import Dict, Any, List, Optional
from backend.database import get_supabase  # placeholder – actual import may differ

# Helper to fetch eligible employees for a municipality & department
def fetch_eligible_employees(municipality_code: str, department: str) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    res = supabase.table("employees").select("*").eq("municipality_code", municipality_code).eq("department", department).eq("is_active", True).execute()
    if getattr(res, "error", None):
        return []
    return res.data

def skill_match_score(employee: Dict[str, Any], required_skills: List[str]) -> float:
    # employee['skills'] stored as comma‑separated string
    emp_skills = set((employee.get("skills") or "").split(","))
    matches = emp_skills.intersection(set(required_skills))
    if not required_skills:
        return 50.0
    return (len(matches) / len(required_skills)) * 100.0

def workload_score(employee: Dict[str, Any]) -> float:
    max_wl = employee.get("maximum_workload", 10)
    cur = employee.get("current_workload", 0)
    if max_wl <= 0:
        return 0.0
    remaining = max_wl - cur
    return (remaining / max_wl) * 100.0

def proximity_score(emp_lat: Optional[float], emp_lng: Optional[float], comp_lat: Optional[float], comp_lng: Optional[float]) -> float:
    if not all([emp_lat, emp_lng, comp_lat, comp_lng]):
        return 50.0
    # simple haversine (km) – closer = higher score
    from math import radians, sin, cos, sqrt, atan2
    R = 6371.0
    dlat = radians(comp_lat - emp_lat)
    dlon = radians(comp_lng - emp_lng)
    a = sin(dlat/2)**2 + cos(radians(emp_lat))*cos(radians(comp_lat))*sin(dlon/2)**2
    c = 2 * atan2(math.sqrt(a), math.sqrt(1-a))
    dist_km = R * c
    # Assume 0‑20km range maps to 100‑0 score
    return max(0.0, 100.0 - (dist_km/20.0)*100.0)

def ward_score(employee: Dict[str, Any], complaint_ward: Optional[str]) -> float:
    emp_zone = employee.get("zone") or ""
    if not complaint_ward:
        return 50.0
    return 100.0 if emp_zone.lower() in complaint_ward.lower() else 0.0

def schedule_score(employee: Dict[str, Any]) -> float:
    # Simplified – if employee is on leave, score 0
    status = employee.get("availability_status", "available")
    return 100.0 if status == "available" else 0.0

WEIGHTS = {
    "skill": 0.30,
    "workload": 0.25,
    "proximity": 0.20,
    "ward": 0.15,
    "schedule": 0.10,
}

def select_employee_for_complaint(complaint: Dict[str, Any]) -> Optional[str]:
    municipality = complaint.get("municipal_corporation")
    department = complaint.get("department_code") or complaint.get("department")
    if not municipality or not department:
        return None
    employees = fetch_eligible_employees(municipality, department)
    if not employees:
        return None
    required_skills = complaint.get("required_skills", []).split(",") if complaint.get("required_skills") else []
    best_emp = None
    best_score = -1
    for emp in employees:
        # Hard constraints – skip overloaded or unavailable
        if emp.get("status") != "Active":
            continue
        # Compute component scores
        s_skill = skill_match_score(emp, required_skills)
        s_wl = workload_score(emp)
        s_prox = proximity_score(emp.get("location_lat"), emp.get("location_lng"), complaint.get("location_lat"), complaint.get("location_lng"))
        s_ward = ward_score(emp, complaint.get("ward"))
        s_sched = schedule_score(emp)
        total = (
            s_skill * WEIGHTS["skill"] +
            s_wl * WEIGHTS["workload"] +
            s_prox * WEIGHTS["proximity"] +
            s_ward * WEIGHTS["ward"] +
            s_sched * WEIGHTS["schedule"]
        )
        if total > best_score:
            best_score = total
            best_emp = emp
    return best_emp.get("id") if best_emp else None
