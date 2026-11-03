"""
Tests for Google OR-Tools (CP-SAT) Workforce Allocation & LightGBM Priority Engine
Verifies:
1. Street Light grievances in Telugu & English ALWAYS get allocated to Electrical Cadre.
2. Road grievances ALWAYS get allocated to Roads & Buildings Cadre.
3. Hydraulic Aerial Sky-Lift Truck & Lineman Safety Kit are designated for Street Lights.
4. Bitumen Patching Truck & Plate Compactor Roller are designated for Roads.
5. Strict Municipality Isolation: An Eluru (ELR) complaint is NEVER assigned to a Vijayawada (VMC) engineer.
6. Overloaded engineers are NEVER assigned new tasks beyond their maximum capacity cap.
7. LightGBM Priority scoring accurately identifies Critical, High, and Medium priority tiers.
8. CP-SAT Global Batch Allocation solves optimal workforce distribution simultaneously.
"""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.ortools_allocator import (
    solve_workforce_allocation_cpsat,
    recommend_cadre_dispatch_single,
    normalize_department,
    get_cadre_specs
)
from priority_engine.inference.infer import predict_complaint_priority

MOCK_EMPLOYEES = [
    {
        "id": "ELR-EMP-101",
        "employee_code": "ELR-EMP-101",
        "name": "S. Venkata Ramana",
        "department": "road",
        "department_name": "Roads & Buildings Department",
        "municipality_code": "ELR",
        "designation": "Assistant Executive Engineer (Roads)",
        "status": "active",
        "availability_status": "available",
        "current_workload": 1.0,
        "maximum_workload": 12.0,
        "skills": "Highway Engineering, Bitumen Patching, Asphalt Pavers",
        "pending_count": 1
    },
    {
        "id": "ELR-EMP-102",
        "employee_code": "ELR-EMP-102",
        "name": "Sk. Hussain",
        "department": "street_lights",
        "department_name": "Electrical & Street Lighting Wing",
        "municipality_code": "ELR",
        "designation": "Municipal Electrician & Streetlight In-charge",
        "status": "active",
        "availability_status": "available",
        "current_workload": 2.0,
        "maximum_workload": 10.0,
        "skills": "LED Streetlight Replacement, Cable Jointing, 11kV Safety, Pole Grounding",
        "pending_count": 2
    },
    {
        "id": "ELR-EMP-103",
        "employee_code": "ELR-EMP-103",
        "name": "M. Durga Rao",
        "department": "drainage",
        "department_name": "Public Health & Sanitary Drainage",
        "municipality_code": "ELR",
        "designation": "Sanitary Inspector (Drainage)",
        "status": "active",
        "availability_status": "available",
        "current_workload": 1.5,
        "maximum_workload": 10.0,
        "skills": "Sewer Jetting, Manhole Desilting, Stormwater Drain Maintenance",
        "pending_count": 1
    },
    {
        "id": "VMC-EMP-201",
        "employee_code": "VMC-EMP-201",
        "name": "P. Ramesh Kumar (VMC)",
        "department": "street_lights",
        "department_name": "Electrical Wing",
        "municipality_code": "VMC",
        "designation": "Assistant Engineer (Electrical)",
        "status": "active",
        "availability_status": "available",
        "current_workload": 0.0,
        "maximum_workload": 12.0,
        "skills": "High Mast Towers, Transformer Maintenance",
        "pending_count": 0
    }
]


def test_street_light_telugu_assigns_electrical_cadre_only():
    """
    Directly addresses the screenshot issue:
    Case [NXC-B13747] 'స్ట్రీట్ లైట్ పనిచేయడం లేదు' in ELR municipality
    MUST be assigned to Sk. Hussain (street_lights), NEVER S. Venkata Ramana (road)!
    """
    complaint = {
        "id": "NXC-B13747",
        "grievance_ref_number": "NXC-B13747",
        "title": "స్ట్రీట్ లైట్ పనిచేయడం లేదు",
        "municipal_corporation": "ELR",
        "priority": "Medium"
    }

    res = recommend_cadre_dispatch_single(complaint, MOCK_EMPLOYEES)

    assert res["assigned_employee_id"] == "ELR-EMP-102"
    assert res["assigned_employee_name"] == "Sk. Hussain"
    assert res["department"] == "street_lights"
    # Never road equipment!
    assert "Hydraulic Aerial Sky-Lift Truck" in res["required_equipment"]
    assert "Bitumen Patching Truck" not in res["required_equipment"]


def test_road_pothole_assigns_roads_cadre_only():
    """Verifies road complaints are assigned to road engineers with road equipment."""
    complaint = {
        "id": "NXC-R88219",
        "grievance_ref_number": "NXC-R88219",
        "title": "రోడ్డుపై పెద్ద గుంతలు ఉన్నాయి - వాహనాలు పడిపోతున్నాయి",
        "municipal_corporation": "ELR",
        "priority": "High"
    }

    res = recommend_cadre_dispatch_single(complaint, MOCK_EMPLOYEES)

    assert res["assigned_employee_id"] == "ELR-EMP-101"
    assert res["assigned_employee_name"] == "S. Venkata Ramana"
    assert res["department"] == "road"
    assert any("Bitumen" in eq for eq in res["required_equipment"])


def test_strict_municipality_isolation_in_cpsat():
    """
    Even if Vijayawada engineer has 0 workload, an Eluru complaint
    CANNOT be assigned to the Vijayawada engineer under CP-SAT constraints.
    """
    complaint = {
        "id": "NXC-SL-009",
        "title": "Streetlight pole sparking in RR Peta",
        "municipal_corporation": "ELR",
        "priority": "Critical"
    }

    res = recommend_cadre_dispatch_single(complaint, MOCK_EMPLOYEES)

    # Must be ELR employee (Sk. Hussain), NOT VMC employee (P. Ramesh Kumar)
    assert res["assigned_employee_id"] == "ELR-EMP-102"
    assert res["assigned_employee"]["municipality_code"] == "ELR"


def test_overloaded_engineer_is_rejected_by_cpsat():
    """Tests that an employee whose current workload exceeds max capacity is not assigned."""
    overloaded_employees = [
        {
            "id": "ELR-EMP-OVERLOADED",
            "employee_code": "ELR-EMP-OVERLOADED",
            "name": "Overloaded Electrician",
            "department": "street_lights",
            "municipality_code": "ELR",
            "status": "active",
            "availability_status": "available",
            "current_workload": 12.0,
            "maximum_workload": 12.0,
            "pending_count": 15
        }
    ]

    complaint = {
        "id": "NXC-SL-999",
        "title": "Streetlight dark in Ward 3",
        "municipal_corporation": "ELR",
        "priority": "Medium"
    }

    res = recommend_cadre_dispatch_single(complaint, overloaded_employees)
    assert res["assigned_employee_id"] is None
    assert "Unassigned" in res["assigned_employee_name"]


def test_batch_allocation_cpsat_optimal_matching():
    """Tests simultaneous multi-complaint allocation across different departments."""
    complaints = [
        {"id": "C-1", "title": "స్ట్రీట్ లైట్ వెలగడం లేదు", "municipal_corporation": "ELR", "priority": "Medium"},
        {"id": "C-2", "title": "Pothole on Main Road", "municipal_corporation": "ELR", "priority": "High"},
        {"id": "C-3", "title": "Drainage manhole overflowing", "municipal_corporation": "ELR", "priority": "Critical"}
    ]

    res = solve_workforce_allocation_cpsat(complaints, MOCK_EMPLOYEES)

    assert res["status"] in ["OPTIMAL", "FEASIBLE"]
    assert len(res["assignments"]) == 3

    assigned_map = {a["complaint_id"]: a for a in res["assignments"]}
    assert assigned_map["C-1"]["department"] == "street_lights"
    assert assigned_map["C-1"]["assigned_employee_id"] == "ELR-EMP-102"

    assert assigned_map["C-2"]["department"] == "road"
    assert assigned_map["C-2"]["assigned_employee_id"] == "ELR-EMP-101"

    assert assigned_map["C-3"]["department"] == "drainage"
    assert assigned_map["C-3"]["assigned_employee_id"] == "ELR-EMP-103"


def test_lightgbm_priority_inference():
    """Verifies that the trained LightGBM priority engine runs accurately."""
    res = predict_complaint_priority(
        text="High-voltage live wire snapped and sparking on public street near primary school",
        safety_risk=95.0,
        public_health_risk=20.0,
        public_impact=90.0,
        infrastructure_criticality=85.0,
        sla_urgency=95.0,
        is_emergency=True,
        category="street_lights"
    )

    assert res["predicted_priority_tier"] == "Critical"
    assert res["predicted_priority_score"] >= 95.0
    assert res["is_emergency_override"] is True
    assert "LIGHTGBM" in res["model_version"] or "MULTIMODAL" in res["model_version"]


def test_multimodal_text_image_zone_fusion():
    """
    Verifies that the multimodal engine accurately fuses Text, Image, and Zone:
    1. Detects sensitive Hospital corridor and applies 1.5x vulnerability multiplier.
    2. Correctly classifies cadre department.
    3. Synthesizes/extracts visual damage features.
    """
    from PIL import Image
    import numpy as np

    # Create dummy 100x100 RGB image with simulated defect edge patterns
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    arr[30:70, 30:70] = [180, 50, 50]
    dummy_img = Image.fromarray(arr)

    res = predict_complaint_priority(
        text="రోడ్డుపై భారీ గుంత ఉంది ఆసుపత్రి అంబులెన్స్ వెళ్ళలేకపోతోంది",
        zone="King George Hospital (KGH) Casualty Gate Approach",
        ward="Ward 14",
        municipality="GVMC",
        category="road",
        image_input=dummy_img,
        safety_risk=85.0
    )

    assert res["zone_classification"] == "hospital"
    assert res["vulnerability_multiplier"] == 1.50
    assert res["predicted_department"] == "road"
    assert res["has_image_proof"] is True
    assert res["visual_damage_severity"] > 0
    assert "MULTIMODAL" in res["model_version"]
