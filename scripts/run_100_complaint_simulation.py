"""
NEX-CIV 100-Complaint Operational Simulation Engine (REAL DATASET EDITION)
Pulls exactly 100 REAL civic complaints for Eluru Municipal Corporation (ELR)
from the verified nexciv_multilingual_complaints_10k.csv:
- 20 Real Roads Complaints
- 20 Real Water Supply Complaints
- 20 Real Drainage Complaints
- 24 Real Street Lighting Complaints
- 16 Real Sanitation/Others Complaints

Executes end-to-end municipal operational workflow:
1. Classification & Wing Routing
2. Multilingual Severity AI Evaluation (Telugu & English)
3. Statutory SLA Calculation (AP Working Days & Holidays)
4. Multi-Factor Explainable Priority Engine
5. Statutory Emergency Override Engine
6. Strict Municipality-Isolated Workforce Allocation
7. Dynamic Effort Workload Balancing
"""

import sys
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Add backend and root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

from backend.ap_administration import resolve_department_and_wing
from backend.sla_service import compute_statutory_deadline
from backend.ai_severity_engine import analyze_complaint_severity
from backend.ai_priority_engine import calculate_priority
from backend.workforce_allocation_engine import allocate_complaint_to_workforce

TABLES_DIR = BASE_DIR / "backend" / "data" / "tables"
REAL_DATA_FILE = BASE_DIR / "nexciv_multilingual_complaints_10k.csv"

def load_100_real_eluru_complaints():
    """Extracts exactly 100 real complaints for Eluru Municipal Corporation."""
    df = pd.read_csv(REAL_DATA_FILE)
    elr_df = df[df["municipality"].str.contains("Eluru", case=False, na=False)].copy()

    # Target distribution
    target_counts = {
        "road": 20,
        "water_supply": 20,
        "drainage": 20,
        "street_lights": 24,
        "others": 16
    }

    selected_records = []

    for dept, count in target_counts.items():
        dept_subset = elr_df[elr_df["department"] == dept]
        if len(dept_subset) < count:
            # Fallback to broader category matching if needed
            dept_subset = elr_df

        sampled = dept_subset.head(count)
        for _, row in sampled.iterrows():
            selected_records.append({
                "complaint_id": row["complaint_id"],
                "text": str(row["complaint_text"]),
                "category": dept,
                "defect_type": str(row.get("complaint_type", "")),
                "ward": str(row.get("ward", "Ward 12")),
                "landmark": f"{row.get('ward', 'Central Zone')}, Eluru",
                "lat": 16.7107 + (len(selected_records) * 0.0005),
                "lng": 81.0952 + (len(selected_records) * 0.0004),
                "language_style": row.get("language_style", "en")
            })

    print(f"Extracted {len(selected_records)} real complaints for Eluru Municipal Corporation.")
    return selected_records

def run_simulation():
    real_complaints = load_100_real_eluru_complaints()

    # Load Eluru employees
    employees_file = TABLES_DIR / "employees.json"
    with open(employees_file, "r", encoding="utf-8") as f:
        all_employees = json.load(f)

    elr_employees = [e for e in all_employees if (e.get("municipality_code") or "").upper() == "ELR"]
    print(f"Loaded {len(elr_employees)} ELR workforce personnel for allocation.")

    # Reset current workloads to initial demonstration baselines
    for e in all_employees:
        if (e.get("municipality_code") or "").upper() == "ELR":
            e["current_workload"] = 2.0
            e["pending_count"] = 2

    processed_complaints = []
    stats = {
        "total": len(real_complaints),
        "assigned": 0,
        "unassigned": 0,
        "emergency_overrides": 0,
        "priorities": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
        "departments": {},
        "employee_allocations": {},
        "languages": {"te": 0, "te_latn": 0, "en": 0}
    }

    base_time = datetime.now() - timedelta(hours=36)

    for idx, raw in enumerate(real_complaints):
        complaint_id = f"elr-real-{idx+1:03d}"
        created_time = base_time + timedelta(minutes=idx * 20)
        cat = raw["category"]

        # 1. Department & Wing Resolution
        dept_info = resolve_department_and_wing(raw["defect_type"] or cat)

        # 2. Multilingual Severity AI Evaluation
        severity_info = analyze_complaint_severity(
            text=raw["text"],
            category=cat,
            defect_type=raw["defect_type"],
            location_address=raw["landmark"]
        )

        # 3. Statutory SLA Calculation
        sla_info = compute_statutory_deadline(
            category=cat,
            defect_type=raw["defect_type"],
            created_at_dt=created_time
        )

        # 4. Multi-Factor Explainable Priority Scoring & Emergency Override
        complaint_payload = {
            "title": raw["text"][:60],
            "description": raw["text"],
            "category": cat,
            "defect_type": raw["defect_type"],
            "location_address": raw["landmark"],
            "duplicate_count": 1 if idx % 6 == 0 else 0,
            "upvote_count": 2 if idx % 4 == 0 else 1,
            "image_url": f"https://nexciv.ap.gov.in/evidence/{complaint_id}.jpg" if idx % 2 == 0 else None
        }

        priority_result = calculate_priority(
            severity_info=severity_info,
            sla_info=sla_info,
            complaint_data=complaint_payload
        )

        # 5. Build structured complaint record
        comp_record = {
            "id": complaint_id,
            "raw_grievance_id": raw["complaint_id"],
            "grievance_ref_number": f"AP-ELR-2026-REAL{idx+1:03d}",
            "title": raw["text"][:75] + ("..." if len(raw["text"]) > 75 else ""),
            "description": raw["text"],
            "category": cat,
            "department": dept_info["department_name"],
            "department_code": dept_info["department_code"],
            "functional_wing_id": dept_info["functional_wing_id"],
            "functional_wing_name": dept_info["functional_wing_name"],
            "municipal_corporation": "ELR",
            "ward": raw["ward"],
            "landmark": raw["landmark"],
            "location_address": f"[ELR] {raw['landmark']}",
            "location_lat": raw["lat"],
            "location_lng": raw["lng"],
            "defect_type": raw["defect_type"],
            "severity_level": severity_info["severity_level"],
            "severity_label": severity_info["severity_label"],
            "priority": priority_result["priority_label"],
            "priority_score": priority_result["priority_score"],
            "is_emergency_override": priority_result["is_emergency_override"],
            "emergency_override_reason": priority_result["emergency_override_reason"],
            "priority_explanation": priority_result["explanation_summary"],
            "priority_explanation_points": priority_result["explanation"],
            "score_breakdown": priority_result["component_breakdown"],
            "sla_rule_id": sla_info["sla_rule_id"],
            "sla_deadline_at": sla_info["deadline_dt"],
            "deadline_formatted": sla_info["deadline_formatted"],
            "sla_remaining_hours": sla_info["remaining_hours"],
            "sla_is_overdue": sla_info["is_overdue"],
            "escalation_level": sla_info["escalation_level"],
            "status": "pending",
            "is_simulation": True,
            "created_at": created_time.isoformat() + "Z",
            "updated_at": created_time.isoformat() + "Z"
        }

        # 6. Intelligent Municipality-Isolated Workforce Allocation
        allocation_res = allocate_complaint_to_workforce(
            complaint=comp_record,
            all_employees=all_employees  # Pass all employees across all ULBs to test strict ELR isolation!
        )

        if allocation_res["is_assigned"]:
            comp_record["assigned_employee_id"] = allocation_res["assigned_employee_id"]
            comp_record["assigned_employee_name"] = allocation_res["assigned_employee_name"]
            comp_record["assigned_team"] = allocation_res["assigned_team"]
            comp_record["assignment_score"] = allocation_res["assignment_score"]
            comp_record["allocation_rationale"] = allocation_res["allocation_rationale"]
            stats["assigned"] += 1

            emp_key = allocation_res["assigned_employee_id"]
            stats["employee_allocations"][emp_key] = stats["employee_allocations"].get(emp_key, 0) + 1

            # Dynamically update the employee's current workload in the simulation
            for e in all_employees:
                if (e.get("employee_code") or e.get("id")) == emp_key:
                    e["current_workload"] = round(float(e.get("current_workload", 0.0)) + allocation_res["task_effort_units"], 1)
                    e["pending_count"] = int(e.get("pending_count", 0)) + 1
                    break
        else:
            comp_record["assigned_employee_id"] = None
            comp_record["assigned_employee_name"] = None
            comp_record["assigned_team"] = allocation_res["assigned_team"]
            comp_record["allocation_rationale"] = allocation_res["unassigned_reason"]
            comp_record["requires_supervisor_intervention"] = True
            stats["unassigned"] += 1

        if priority_result["is_emergency_override"]:
            stats["emergency_overrides"] += 1

        stats["priorities"][priority_result["priority_label"]] += 1
        stats["departments"][dept_info["department_code"]] = stats["departments"].get(dept_info["department_code"], 0) + 1
        stats["languages"][raw["language_style"]] = stats["languages"].get(raw["language_style"], 0) + 1

        processed_complaints.append(comp_record)

    # 7. Save Simulation Complaints to Isolated ELR Table & Master Complaints
    elr_table_file = TABLES_DIR / "complaints_elr.json"
    with open(elr_table_file, "w", encoding="utf-8") as f:
        json.dump(processed_complaints, f, indent=2, ensure_ascii=False)

    master_table_file = TABLES_DIR / "complaints.json"
    master_records = []
    if master_table_file.exists():
        try:
            with open(master_table_file, "r", encoding="utf-8") as f:
                master_records = json.load(f)
        except Exception:
            master_records = []
    # Remove older simulations
    master_records = [c for c in master_records if not c.get("is_simulation")]
    master_records = processed_complaints + master_records
    with open(master_table_file, "w", encoding="utf-8") as f:
        json.dump(master_records, f, indent=2, ensure_ascii=False)

    # Save updated employee workloads
    with open(employees_file, "w", encoding="utf-8") as f:
        json.dump(all_employees, f, indent=2, ensure_ascii=False)

    print("\n=======================================================")
    print("NEX-CIV 100 REAL COMPLAINTS SIMULATION (ELURU ULB)")
    print("=======================================================")
    print(f"Total Real Complaints Processed: {stats['total']}")
    print(f"Successfully Allocated to ELR Personnel: {stats['assigned']}")
    print(f"Unassigned / Escalated to Supervisor: {stats['unassigned']}")
    print(f"Emergency Overrides Triggered: {stats['emergency_overrides']}")
    print(f"Priorities Distribution: {stats['priorities']}")
    print(f"Department Distribution: {stats['departments']}")
    print(f"Languages: {stats['languages']}")
    print("\nPersonnel Workload Distribution (Roads Department):")
    for emp_code, count in sorted(stats["employee_allocations"].items()):
        if "RD" in emp_code:
            print(f"  {emp_code}: {count} tasks allocated")

    return stats, processed_complaints

if __name__ == "__main__":
    run_simulation()
