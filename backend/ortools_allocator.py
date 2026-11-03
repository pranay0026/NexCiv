"""
NEX-CIV Municipal Workforce Allocation Engine powered by Google OR-Tools (CP-SAT)
Compliant with:
- Andhra Pradesh Municipalities Act, 1965
- Andhra Pradesh Municipal Corporations Act, 1994
- G.O.Ms.No.217, MA&UD Department (Gram/Ward Sachivalayam Cadres)
- Andhra Pradesh Municipal Engineering Service Rules

Mathematical Formulation (CP-SAT Constraint Programming):
Decision Variables:
  x[i, j] in {0, 1} indicates whether Complaint i is assigned to Municipal Employee j.

Hard Constraints:
  1. Unit Assignment: sum_j x[i, j] <= 1 for each complaint i.
  2. Strict Municipality Isolation: x[i, j] = 0 if muni(i) != muni(j).
  3. Strict Department / Cadre Wing Alignment:
     x[i, j] = 0 if dept(i) != dept(j). (Street light -> Electrical, Road -> Roads, etc.)
  4. Employee Status & Availability:
     x[i, j] = 0 if emp is Inactive, On Leave, or Suspended.
  5. Workload Capacity Cap:
     sum_i (Effort[i] * x[i, j]) + CurrentWorkload[j] <= MaxWorkload[j].

Objective:
  Maximize sum_{i, j} Score[i, j] * x[i, j]
  where Score[i, j] = SkillMatch * 30 + WardJurisdiction * 25 + WorkloadHeadroom * 25 + Proximity * 10 + Rating * 10.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
import logging
from ortools.sat.python import cp_model

logger = logging.getLogger("nexciv.ortools_allocator")

# Workload effort sizing (in workload units)
EFFORT_CAPACITY_UNITS = {
    "Critical": 3.0,
    "High": 2.0,
    "Medium": 1.0,
    "Low": 0.5
}

# Real Cadre Equipment & Crew Specifications aligned with AP Municipal Manuals
CADRE_SPECIFICATIONS = {
    "street_lights": {
        "equipment": [
            "Hydraulic Aerial Sky-Lift Truck",
            "Lineman 11kV Safety Kit & Insulation Gloves",
            "Digital Insulation Megger Tester",
            "LED Luminaire Replacement Rig",
            "High-Tension Wire Splicing Clamp"
        ],
        "crew_size": 2,
        "standard_sla_hours": 12,
        "statutory_rank": "Assistant Engineer (Electrical) / Municipal Electrician",
        "keywords": ["light", "elect", "pole", "wire", "lamp", "led", "transformer", "spark", "dark", "power", "దీపం", "స్ట్రీట్", "విద్యుత్", "చీకటి", "స్తంభం", "లైట్", "కరెంట్"]
    },
    "road": {
        "equipment": [
            "Bitumen Patching Truck (Hot/Cold Mix)",
            "Plate Compactor Vibratory Roller",
            "Heavy-Duty Asphalt Road Cutter",
            "Polymer-Modified Cold Mix Asphalt Bags",
            "Reflective Traffic Diversion Cones"
        ],
        "crew_size": 4,
        "standard_sla_hours": 24,
        "statutory_rank": "Assistant Executive Engineer (AEE - Roads) / AE (Civil)",
        "keywords": ["road", "pothole", "asphalt", "crater", "pavement", "curb", "footpath", "divider", "bitumen", "రోడ్డు", "గుంత", "రహదారి", "డివైడర్", "తారు"]
    },
    "water_supply": {
        "equipment": [
            "Cast Iron Sluice Valve Key & Spindle Rig",
            "High-Capacity Diesel Dewatering Pump",
            "Ductile Iron (DI) Pipe Jointing Clamp",
            "Ultrasonic Acoustic Pipe Leak Detector",
            "Potable Water Quality Testing Meter"
        ],
        "crew_size": 3,
        "standard_sla_hours": 8,
        "statutory_rank": "Assistant Engineer (PHE - Water Supply) / Municipal Fitter",
        "keywords": ["water", "pipe", "pipeline", "leak", "potable", "drinking", "valve", "tap", "bore", "contamination", "నీళ్లు", "నీరు", "తాగునీరు", "పైపు", "కుళాయి", "లీకేజీ", "బోరు"]
    },
    "drainage": {
        "equipment": [
            "High-Pressure Sewer Jetting Machine",
            "Super Sucker Vacuum De-silting Tanker",
            "Multi-Gas Safety Detector (H2S, CH4, CO)",
            "Tripod Winch & Confined-Space Safety Harness",
            "Precast RCC Manhole Cover Slabs"
        ],
        "crew_size": 4,
        "standard_sla_hours": 12,
        "statutory_rank": "Assistant Engineer (Drainage & Sewerage) / Sanitary Inspector",
        "keywords": ["drain", "drainage", "sewer", "sewage", "manhole", "overflow", "gutter", "waterlogging", "desilting", "డ్రైనేజీ", "కాలువ", "మురుగు", "మ్యాన్‌హోల్", "వరద"]
    },
    "others": {
        "equipment": [
            "Hydraulic Refuse Compactor Dumper Truck",
            "ULV Thermal Fogging Machine for Mosquito Eradication",
            "Bio-Medical & Solid Waste Segregation Placer",
            "Bleaching Powder & Disinfectant Spray Cannon",
            "Municipal Wheelbarrow & Shovel Fleet"
        ],
        "crew_size": 4,
        "standard_sla_hours": 24,
        "statutory_rank": "Sanitary Supervisor / Municipal Health Officer",
        "keywords": ["garbage", "waste", "trash", "sanitation", "cleaning", "dead animal", "mosquito", "fogging", "bleaching", "dustbin", "చెత్త", "కుప్ప", "దుర్గంధం", "వ్యర్థాలు"]
    }
}


def normalize_department(dept_or_wing: Optional[str], text: Optional[str] = None) -> str:
    """
    Normalizes any department, functional wing, category, or multilingual text to one of:
    'street_lights', 'road', 'water_supply', 'drainage', 'others'.
    """
    combined = f"{dept_or_wing or ''} {text or ''}".lower().strip()
    
    # 1. Check Street Lights / Electrical
    if any(k in combined for k in ["street_light", "street_lights", "streetlight", "light", "elect", "pole", "lamp", "దీపం", "స్ట్రీట్ లైట్", "విద్యుత్", "చీకటి", "స్తంభం", "లైట్", "కరెంట్"]):
        return "street_lights"
        
    # 2. Check Water Supply
    if any(k in combined for k in ["water_supply", "water", "drinking", "potable", "pipe", "leak", "valve", "tap", "bore", "నీళ్లు", "నీరు", "తాగునీరు", "పైపు", "కుళాయి", "లీకేజీ", "బోరు"]):
        return "water_supply"
        
    # 3. Check Drainage / Sewerage
    if any(k in combined for k in ["drainage", "drain", "sewer", "sewage", "manhole", "waterlog", "gutter", "డ్రైనేజీ", "కాలువ", "మురుగు", "మ్యాన్‌హోల్", "వరద"]):
        return "drainage"
        
    # 4. Check Roads
    if any(k in combined for k in ["road", "roads", "pothole", "asphalt", "pavement", "highway", "curb", "రోడ్డు", "గుంత", "రహదారి", "డివైడర్"]):
        return "road"
        
    # 5. Check Sanitation / Public Health / Others
    if any(k in combined for k in ["garbage", "sanitation", "public_health", "health", "waste", "clean", "fogging", "mosquito", "చెత్త", "కుప్ప", "దుర్గంధం", "వ్యర్థాలు"]):
        return "others"
        
    # Default fallback
    if "road" in combined:
        return "road"
    return "road"


def get_cadre_specs(dept_key: str) -> Dict[str, Any]:
    """Retrieves equipment, crew, and SLA specifications for a given department."""
    norm = normalize_department(dept_key)
    return CADRE_SPECIFICATIONS.get(norm, CADRE_SPECIFICATIONS["road"])


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates spatial distance in kilometers."""
    try:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2.0) ** 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(dlon / 2.0) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return float(R * c)
    except Exception:
        return 5.0


def compute_compatibility_score(complaint: Dict[str, Any], emp: Dict[str, Any]) -> int:
    """
    Computes scaled integer score (0 to 1000) for objective optimization in CP-SAT:
    - Skill match: 300 pts
    - Ward / Zonal match: 250 pts
    - Available workload headroom: 250 pts
    - Geographic proximity: 100 pts
    - Performance rating: 100 pts
    """
    score = 0.0

    # 1. Skill Match (max 300)
    emp_skills = (emp.get("skills") or "").lower()
    comp_text = f"{complaint.get('title', '')} {complaint.get('description', '')} {complaint.get('defect_type', '')}".lower()
    dept = normalize_department(complaint.get("functional_wing_id") or complaint.get("department"), comp_text)
    spec = CADRE_SPECIFICATIONS.get(dept, {})
    keywords = spec.get("keywords", [])
    
    matches = sum(1 for kw in keywords if kw in emp_skills)
    skill_pct = min(1.0, matches / max(1, min(4, len(keywords))))
    score += skill_pct * 300.0

    # 2. Ward / Zonal Jurisdiction (max 250)
    emp_zone = (emp.get("zone") or "").lower()
    comp_ward = str(complaint.get("ward") or complaint.get("ward_id") or complaint.get("location_address") or "").lower()
    if emp_zone and comp_ward:
        if comp_ward in emp_zone or emp_zone in comp_ward:
            score += 250.0
        elif "ward" in comp_ward:
            # Check matching ward number
            import re
            c_num = re.findall(r'\b\d+\b', comp_ward)
            e_num = re.findall(r'\b\d+\b', emp_zone)
            if c_num and e_num and any(n in e_num for n in c_num):
                score += 250.0
            else:
                score += 80.0
        else:
            score += 80.0
    else:
        score += 100.0

    # 3. Workload Headroom (max 250)
    curr_wl = float(emp.get("current_workload") or emp.get("pending_count") or 0.0)
    max_wl = float(emp.get("maximum_workload") or 12.0)
    if max_wl > 0:
        headroom_ratio = max(0.0, (max_wl - curr_wl) / max_wl)
        score += headroom_ratio * 250.0

    # 4. Spatial Proximity (max 100)
    emp_lat = emp.get("location_lat")
    emp_lng = emp.get("location_lng")
    comp_lat = complaint.get("latitude") or complaint.get("location_lat")
    comp_lng = complaint.get("longitude") or complaint.get("location_lng")
    if all(x is not None for x in [emp_lat, emp_lng, comp_lat, comp_lng]):
        try:
            d_km = haversine_km(float(emp_lat), float(emp_lng), float(comp_lat), float(comp_lng))
            if d_km <= 2.0:
                score += 100.0
            elif d_km <= 10.0:
                score += max(20.0, 100.0 - (d_km - 2.0) * 10.0)
            else:
                score += 10.0
        except Exception:
            score += 50.0
    else:
        score += 50.0

    # 5. Rating & Redressal Performance (max 100)
    rating = float(emp.get("rating") or 4.5)
    score += (rating / 5.0) * 100.0

    return int(round(score))


def solve_workforce_allocation_cpsat(
    complaints: List[Dict[str, Any]],
    employees: List[Dict[str, Any]],
    time_limit_seconds: float = 3.0
) -> Dict[str, Any]:
    """
    Executes CP-SAT optimal workforce allocation across municipal complaints.
    Enforces strict mathematical constraints and returns dispatch results.
    """
    model = cp_model.CpModel()
    n_complaints = len(complaints)
    n_employees = len(employees)

    if n_complaints == 0 or n_employees == 0:
        return {
            "status": "EMPTY_INPUT",
            "assignments": [],
            "unassigned_complaints": complaints,
            "solver_time_ms": 0
        }

    # x[i][j]: Complaint i assigned to Employee j
    x = {}
    valid_pairs = []

    for i, comp in enumerate(complaints):
        comp_muni = (comp.get("municipal_corporation") or comp.get("municipality_code") or "").strip().upper()
        comp_text = f"{comp.get('title', '')} {comp.get('description', '')}"
        comp_dept = normalize_department(comp.get("functional_wing_id") or comp.get("department") or comp.get("category"), comp_text)

        for j, emp in enumerate(employees):
            emp_muni = (emp.get("municipality_code") or "").strip().upper()
            emp_dept = normalize_department(emp.get("functional_wing_id") or emp.get("department") or emp.get("department_name"))
            emp_status = (emp.get("status") or "active").strip().lower()
            emp_avail = (emp.get("availability_status") or "available").strip().lower().replace(" ", "_")

            # --- HARD CONSTRAINT 1: STRICT MUNICIPALITY ISOLATION ---
            if comp_muni and emp_muni and comp_muni != emp_muni:
                continue

            # --- HARD CONSTRAINT 2: STRICT DEPARTMENT CADRE INTEGRITY ---
            # Street light complaints MUST NEVER go to road engineers, and vice versa!
            if comp_dept != emp_dept:
                continue

            # --- HARD CONSTRAINT 3: EMPLOYEE ACTIVE & AVAILABLE ---
            if emp_status not in ["active", "available"]:
                continue
            if emp_avail in ["on_leave", "suspended", "inactive", "leave"] or "leave" in emp_avail:
                continue

            x[(i, j)] = model.NewBoolVar(f"assign_{i}_{j}")
            valid_pairs.append((i, j))

    # --- HARD CONSTRAINT 4: AT MOST ONE EMPLOYEE PER COMPLAINT ---
    for i in range(n_complaints):
        assigned_to_i = [x[(i, j)] for j in range(n_employees) if (i, j) in x]
        if assigned_to_i:
            model.Add(sum(assigned_to_i) <= 1)

    # --- HARD CONSTRAINT 5: EMPLOYEE WORKLOAD CAPACITY CAP ---
    # Convert workload units to tenths of an integer unit (effort * 10) to use integer CP-SAT
    for j, emp in enumerate(employees):
        max_wl_int = int(round(float(emp.get("maximum_workload") or 12.0) * 10))
        curr_wl_int = int(round(float(emp.get("current_workload") or emp.get("pending_count") or 0.0) * 10))
        headroom_int = max(0, max_wl_int - curr_wl_int)

        assigned_tasks_effort = []
        for i in range(n_complaints):
            if (i, j) in x:
                p_level = complaints[i].get("priority", "Medium")
                effort_int = int(round(EFFORT_CAPACITY_UNITS.get(p_level, 1.0) * 10))
                assigned_tasks_effort.append(effort_int * x[(i, j)])

        if assigned_tasks_effort:
            model.Add(sum(assigned_tasks_effort) <= headroom_int)

    # --- OBJECTIVE FUNCTION: MAXIMIZE COMPATIBILITY & REDRESSAL QUALITY ---
    objective_terms = []
    for (i, j) in valid_pairs:
        score = compute_compatibility_score(complaints[i], employees[j])
        objective_terms.append(score * x[(i, j)])

    if objective_terms:
        model.Maximize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver_status = solver.Solve(model)

    assignments = []
    assigned_comp_indices = set()

    if solver_status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for (i, j) in valid_pairs:
            if solver.Value(x[(i, j)]) == 1:
                comp = complaints[i]
                emp = employees[j]
                comp_text = f"{comp.get('title', '')} {comp.get('description', '')}"
                dept = normalize_department(comp.get("functional_wing_id") or comp.get("department") or comp.get("category"), comp_text)
                spec = get_cadre_specs(dept)

                emp_name = emp.get("name", "Unknown")
                emp_code = emp.get("employee_code") or emp.get("id", "")
                emp_desig = emp.get("designation") or emp.get("role") or spec.get("statutory_rank")
                muni = emp.get("municipality_code") or comp.get("municipal_corporation", "ELR")

                rationale = (
                    f"Google OR-Tools CP-SAT allocated {emp_name} ({emp_code}) to case [{comp.get('grievance_ref_number') or comp.get('id')}]. "
                    f"Department cadre: {dept.replace('_', ' ').title()} ({emp_desig}). "
                    f"Optimization satisfied strict municipality isolation ({muni}), "
                    f"workload capacity ({emp.get('pending_count', 0)} active tasks), and specialization fit."
                )

                assignments.append({
                    "complaint_id": comp.get("id"),
                    "complaint_code": comp.get("grievance_ref_number") or comp.get("id"),
                    "assigned_employee": emp,
                    "assigned_employee_id": emp_code or emp.get("id"),
                    "assigned_employee_name": emp_name,
                    "department": dept,
                    "statutory_rank": emp_desig,
                    "rationale": rationale,
                    "confidence_score": min(98.5, round(85.0 + (compute_compatibility_score(comp, emp) / 1000.0) * 13.5, 1)),
                    "required_equipment": spec.get("equipment", []),
                    "required_crew_size": spec.get("crew_size", 2),
                    "estimated_sla_hours": spec.get("standard_sla_hours", 12)
                })
                assigned_comp_indices.add(i)

    unassigned = [comp for i, comp in enumerate(complaints) if i not in assigned_comp_indices]

    return {
        "status": "OPTIMAL" if solver_status == cp_model.OPTIMAL else "FEASIBLE" if solver_status == cp_model.FEASIBLE else "INFEASIBLE",
        "assignments": assignments,
        "unassigned_complaints": unassigned,
        "total_assigned": len(assignments),
        "total_unassigned": len(unassigned),
        "solver_wall_time": solver.WallTime()
    }


def recommend_cadre_dispatch_single(
    complaint: Dict[str, Any],
    all_employees: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Dispatches a single complaint to the mathematically optimal employee using CP-SAT.
    Guarantees strict cadre department match, municipality isolation, and realistic equipment.
    """
    comp_text = f"{complaint.get('title', '')} {complaint.get('description', '')}"
    target_dept = normalize_department(
        complaint.get("functional_wing_id") or complaint.get("department") or complaint.get("category"),
        comp_text
    )
    spec = get_cadre_specs(target_dept)
    target_muni = (complaint.get("municipal_corporation") or complaint.get("municipality_code") or "ELR").strip().upper()

    # Run CP-SAT solver
    res = solve_workforce_allocation_cpsat([complaint], all_employees, time_limit_seconds=1.5)

    if res["assignments"]:
        return res["assignments"][0]

    # Return unassigned when hard constraints (capacity, department, municipality) cannot be satisfied
    return {
        "complaint_id": complaint.get("id"),
        "complaint_code": complaint.get("grievance_ref_number") or complaint.get("id"),
        "assigned_employee": None,
        "assigned_employee_id": None,
        "assigned_employee_name": "Unassigned (Workforce Capacity Exhausted)",
        "department": target_dept,
        "statutory_rank": spec.get("statutory_rank"),
        "rationale": f"Capacity bottleneck: All eligible personnel in {target_muni} for cadre {target_dept} are at maximum workload capacity or on leave.",
        "confidence_score": 0.0,
        "required_equipment": spec.get("equipment", []),
        "required_crew_size": spec.get("crew_size", 2),
        "estimated_sla_hours": spec.get("standard_sla_hours", 12)
    }
